# Enterprise Document Copilot

An AI-powered **Internal Knowledge Assistant** designed to help users within an enterprise to search, understand, and interact with their internal documents such as policies.  

### Vision
- To enable employees to ask natural language questions and get **instant answers** from enterprise documents.  
- To improve onboarding, compliance, and productivity by centralizing knowledge access.  
- To securely integrate with enterprise tools e.g Google Drive.  

### Planned Features
- Importing documents from multiple sources (Google drive, Dropbox, onedrive)
- AI-powered search & Q&A with source citations.  
- Role-based access control for secure usage.  
- Analytics on frequently asked questions & documentation gaps.  
- Building web portal where users log in, upload/search documents, and ask questions.

# Overview of how it will work
This is to help you understand the codebase.
## Deployment

Two docker containers will be used to run the project:
- 'frontend' - will serve Streamlit app
- 'backend' - will serve RESTFUL API which will handle search queries

Use `docker compose up` to start the project.

# Project Roadmap & Todo List

## High Priority
- [ ] foundation (security + ingestion + search)

## Medium Priority
- [ ] enhancements that make it more useful.

## Low Priority
- [ ] add-ons/future expansion.

---
**Legend:**
- [x] Todo
- [ ] Completed

> This is a **work-in-progress project**. Contributions and ideas are welcome!  
