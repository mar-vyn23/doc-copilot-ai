import os
import io
import pickle
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from langchain_groq import ChatGroq
from langchain.tools import tool
from langgraph.graph import StateGraph
from langgraph.prebuilt.chat_agent_executor import AgentState, create_react_agent

load_dotenv()

#Google Drive Auth Helper
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")


def get_drive_service():
    """Authenticate user and return a Google Drive service client."""
    creds = None
    token_path = os.path.expanduser("~/.credentials/token.pkl")

    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credential/client_secret.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

    return build("drive", "v3", credentials=creds)


#File Fetching Logic
def fetch_drive_files(query: str, max_results: int = 5):
    """
    Search for files in the given Drive folder and return text snippets.
    Handles Google Docs, Sheets, PDFs, and Word documents.
    Tries to match regardless of extension.
    """
    service = get_drive_service()

    # Looser search: matches partial names, regardless of extension
    q = f"'{DRIVE_FOLDER_ID}' in parents and name contains '{query}' and trashed=false"
    results = service.files().list(
        q=q,
        pageSize=max_results,
        fields="files(id, name, mimeType)"
    ).execute()

    files = results.get("files", [])
    texts = []

    for f in files:
        file_id = f["id"]
        mime = f["mimeType"]
        name = f["name"]

        try:
            if mime == "application/vnd.google-apps.document":
                # Google Docs → export as plain text
                doc = service.files().export(fileId=file_id, mimeType="text/plain").execute()
                content = doc.decode("utf-8")

            elif mime == "application/pdf":
                # PDFs → download and extract
                request = service.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
                fh.seek(0)
                try:
                    import PyPDF2
                    reader = PyPDF2.PdfReader(fh)
                    content = "\n".join(page.extract_text() or "" for page in reader.pages)
                except Exception:
                    content = "[PDF content could not be extracted]"

            elif mime in [
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/msword"
            ]:
                # Word docs
                request = service.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
                fh.seek(0)
                try:
                    import docx
                    doc = docx.Document(fh)
                    content = "\n".join(p.text for p in doc.paragraphs)
                except Exception:
                    content = "[Word content could not be extracted]"

            else:
                content = f"[Unsupported file type: {mime}]"

        except Exception as e:
            content = f"[Error reading file {name}: {str(e)}]"

        texts.append(f"{name}\n{content[:2000]}") 

    return texts


#LangChain setup
model = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",
)


class State(AgentState):
    thread_id: str


@tool
def drive_search(query: str) -> str:
    """Search documents in the Mak Policies Google Drive folder and return raw text only."""
    docs = fetch_drive_files(query)
    if not docs:
        return "No matching files found."
    return "\n\n".join(docs[:5])




supervisor_graph: StateGraph = create_react_agent(
    model=model,
    prompt=(
        "You are a helpful assistant. You have access to a Google Drive folder called "
        "\"Mak Policies\". You can use the relevant documents within this folder" 
        "To onboard a new employee of Makerere University. "
        "When you don't know an answer, you MUST call the tool `drive_search` with the query. "
        "Do not attempt to summarize or write content in the same step as the tool call. "
        "Wait until the tool returns data, then summarize in your next step. "
        "Do not include any raw tool call syntax in your final response."
    ),
    state_schema=State,
    tools=[drive_search],
)



def process_messages(state: State) -> State:
    return supervisor_graph.invoke(
        state,
        config={"configurable": {"thread_id": state['thread_id']}},
    )
