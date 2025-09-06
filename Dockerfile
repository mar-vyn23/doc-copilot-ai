FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential git && \
    rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock* ./

RUN uv pip install --system -e .

COPY . .

EXPOSE 8000

CMD ["uv", "run", "streamlit", "run", "app/main.py"]