# RAG Chatbot Backend

A Django-based backend for a PDF document RAG (Retrieval-Augmented Generation) chatbot with voice functionality.

## Features

- **PDF Processing**: Upload and process PDF documents with text extraction and chunking
- **Embeddings**: Local embedding generation using sentence-transformers (all-MiniLM-L6-v2)
- **Vector Search**: FAISS-based semantic search for efficient document retrieval
- **RAG Pipeline**: Integration with OpenAI GPT models for context-aware responses
- **Voice Support**: Text-to-Speech and Speech-to-Text using OpenAI APIs
- **Real-time Chat**: WebSocket support for streaming responses
- **Async Processing**: Celery-based background task processing

## Tech Stack

- **Framework**: Django 5.0 + Django REST Framework
- **Database**: PostgreSQL (or SQLite for development)
- **Task Queue**: Celery + Redis
- **Vector DB**: FAISS (local, in-memory)
- **Embeddings**: sentence-transformers
- **LLM**: OpenAI GPT-3.5-turbo / GPT-4
- **Voice**: OpenAI TTS & Whisper

## Project Structure

```
backend/
├── config/              # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   ├── asgi.py
│   └── wsgi.py
├── documents/           # Document management app
├── chat/               # Chat and conversation app
├── voice/              # Voice processing app
├── faiss_manager/      # FAISS vector database management
├── storage/            # Local storage for files
│   ├── pdfs/
│   ├── faiss_indexes/
│   └── audio/
├── manage.py
└── requirements.txt
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- PostgreSQL (optional, can use SQLite)
- Redis Server
- OpenAI API Key

### Installation

1. **Create virtual environment**:

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
```

2. **Install dependencies**:

```bash
pip install -r requirements.txt
```

3. **Configure environment variables**:

```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run migrations**:

```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser** (optional):

```bash
python manage.py createsuperuser
```

6. **Start Redis** (in separate terminal):

```bash
redis-server
```

7. **Start Celery worker** (in separate terminal):

```bash
celery -A config worker --loglevel=info --pool=solo  # Windows
```

8. **Start Django development server**:

```bash
python manage.py runserver
```

## API Endpoints

### Documents

- `POST /api/documents/upload` - Upload PDF document
- `GET /api/documents` - List all documents
- `GET /api/documents/{id}` - Get document details
- `DELETE /api/documents/{id}` - Delete document

### Chat

- `POST /api/chat/query` - Ask question to RAG system
- `POST /api/chat/conversations` - Create conversation
- `GET /api/chat/conversations/{id}/messages` - Get conversation history
- `WS /ws/chat/{id}` - WebSocket for real-time chat

### Voice

- `POST /api/voice/text-to-speech` - Convert text to speech
- `POST /api/voice/speech-to-text` - Transcribe audio to text
- `POST /api/voice/chat` - Combined voice chat (STT + RAG + TTS)

### FAISS

- `GET /api/faiss/status` - Get FAISS index statistics
- `POST /api/faiss/rebuild` - Rebuild FAISS index

## Development

### Running Tests

```bash
pytest
```

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Configure PostgreSQL database
3. Set strong `SECRET_KEY`
4. Use Gunicorn: `gunicorn config.wsgi:application`
5. Use Daphne for WebSockets: `daphne config.asgi:application`
6. Set up supervisor for Celery workers
7. Configure nginx as reverse proxy
