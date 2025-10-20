# RAG Chatbot Backend - API Documentation

## Base URL

```
http://localhost:8000
```

## Table of Contents

1. [Document Management APIs](#document-management-apis)
2. [Chat & RAG APIs](#chat--rag-apis)
3. [Voice APIs](#voice-apis)
4. [FAISS Management APIs](#faiss-management-apis)
5. [Error Responses](#error-responses)
6. [Testing with Postman](#testing-with-postman)

---

## Document Management APIs

### 1. Upload PDF Document

Upload a PDF file for processing and indexing.

**Endpoint:** `POST /api/documents/upload/`

**Content-Type:** `multipart/form-data`

**Request Body:**

```
file: [PDF File]
```

**Postman Setup:**

1. Method: `POST`
2. URL: `http://localhost:8000/api/documents/upload/`
3. Body Tab → Select `form-data`
4. Add key: `file` (change type to `File` from dropdown)
5. Choose your PDF file

**cURL Example:**

```bash
curl -X POST http://localhost:8000/api/documents/upload/ \
  -F "file=@/path/to/your/document.pdf"
```

**Success Response (201 Created):**

```json
{
  "message": "Document uploaded successfully",
  "document": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "filename": "uuid-generated-filename.pdf",
    "original_filename": "your-document.pdf",
    "file_path": "/path/to/storage/pdfs/uuid-generated-filename.pdf",
    "file_size": 1024000,
    "mime_type": "application/pdf",
    "page_count": 0,
    "upload_timestamp": "2025-10-20T10:30:00Z",
    "processing_status": "pending",
    "processing_error": null,
    "metadata": {},
    "chunk_count": 0
  }
}
```

**Error Response (400 Bad Request):**

```json
{
  "file": ["Only PDF files are allowed"]
}
```

**Validation Rules:**

- File must be PDF format
- Maximum file size: 50MB
- File field is required

---

### 2. List All Documents

Get a paginated list of all uploaded documents.

**Endpoint:** `GET /api/documents/`

**Query Parameters:**

- `status` (optional): Filter by processing status (`pending`, `processing`, `completed`, `failed`)
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20)

**Postman Setup:**

1. Method: `GET`
2. URL: `http://localhost:8000/api/documents/`
3. Optional: Add query params in Params tab

**cURL Examples:**

```bash
# Get all documents
curl -X GET http://localhost:8000/api/documents/

# Filter by status
curl -X GET "http://localhost:8000/api/documents/?status=completed"

# Pagination
curl -X GET "http://localhost:8000/api/documents/?page=2&page_size=10"
```

**Success Response (200 OK):**

```json
{
  "count": 25,
  "next": "http://localhost:8000/api/documents/?page=2",
  "previous": null,
  "results": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "filename": "uuid-generated-filename.pdf",
      "original_filename": "your-document.pdf",
      "file_path": "/path/to/storage/pdfs/uuid-generated-filename.pdf",
      "file_size": 1024000,
      "mime_type": "application/pdf",
      "page_count": 15,
      "upload_timestamp": "2025-10-20T10:30:00Z",
      "processing_status": "completed",
      "processing_error": null,
      "metadata": {},
      "chunk_count": 45
    }
  ]
}
```

---

### 3. Get Document Details

Get detailed information about a specific document including all chunks.

**Endpoint:** `GET /api/documents/{document_id}/`

**Path Parameters:**

- `document_id`: UUID of the document

**Postman Setup:**

1. Method: `GET`
2. URL: `http://localhost:8000/api/documents/a1b2c3d4-e5f6-7890-abcd-ef1234567890/`

**cURL Example:**

```bash
curl -X GET http://localhost:8000/api/documents/a1b2c3d4-e5f6-7890-abcd-ef1234567890/
```

**Success Response (200 OK):**

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "filename": "uuid-generated-filename.pdf",
  "original_filename": "your-document.pdf",
  "file_path": "/path/to/storage/pdfs/uuid-generated-filename.pdf",
  "file_size": 1024000,
  "mime_type": "application/pdf",
  "page_count": 15,
  "upload_timestamp": "2025-10-20T10:30:00Z",
  "processing_status": "completed",
  "processing_error": null,
  "metadata": {},
  "chunk_count": 45,
  "chunks": [
    {
      "id": "chunk-uuid-1",
      "document": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "chunk_index": 0,
      "page_number": 1,
      "chunk_text": "This is the first chunk of text...",
      "chunk_token_count": 256,
      "start_char_index": 0,
      "end_char_index": 1000,
      "embedding_vector_id": "0",
      "created_at": "2025-10-20T10:35:00Z"
    }
  ]
}
```

**Error Response (404 Not Found):**

```json
{
  "detail": "Not found."
}
```

---

### 4. Get Document Chunks

Get all text chunks for a specific document (paginated).

**Endpoint:** `GET /api/documents/{document_id}/chunks/`

**Path Parameters:**

- `document_id`: UUID of the document

**Postman Setup:**

1. Method: `GET`
2. URL: `http://localhost:8000/api/documents/a1b2c3d4-e5f6-7890-abcd-ef1234567890/chunks/`

**cURL Example:**

```bash
curl -X GET http://localhost:8000/api/documents/a1b2c3d4-e5f6-7890-abcd-ef1234567890/chunks/
```

**Success Response (200 OK):**

```json
{
  "count": 45,
  "next": "http://localhost:8000/api/documents/a1b2c3d4-e5f6-7890-abcd-ef1234567890/chunks/?page=2",
  "previous": null,
  "results": [
    {
      "id": "chunk-uuid-1",
      "document": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "chunk_index": 0,
      "page_number": 1,
      "chunk_text": "This is the first chunk of text from the PDF document. It contains important information about the topic...",
      "chunk_token_count": 256,
      "start_char_index": 0,
      "end_char_index": 1000,
      "embedding_vector_id": "0",
      "created_at": "2025-10-20T10:35:00Z"
    },
    {
      "id": "chunk-uuid-2",
      "document": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "chunk_index": 1,
      "page_number": 1,
      "chunk_text": "This is the second chunk continuing from the previous text...",
      "chunk_token_count": 245,
      "start_char_index": 900,
      "end_char_index": 1950,
      "embedding_vector_id": "1",
      "created_at": "2025-10-20T10:35:00Z"
    }
  ]
}
```

---

### 5. Delete Document

Delete a document and all its associated data.

**Endpoint:** `DELETE /api/documents/{document_id}/`

**Path Parameters:**

- `document_id`: UUID of the document

**Postman Setup:**

1. Method: `DELETE`
2. URL: `http://localhost:8000/api/documents/a1b2c3d4-e5f6-7890-abcd-ef1234567890/`

**cURL Example:**

```bash
curl -X DELETE http://localhost:8000/api/documents/a1b2c3d4-e5f6-7890-abcd-ef1234567890/
```

**Success Response (204 No Content):**

```json
{
  "message": "Document deleted successfully"
}
```

**What Gets Deleted:**

- Document record from database
- All associated chunks
- Physical PDF file from storage
- Embeddings from FAISS index (when implemented)

---

## Chat & RAG APIs

### 6. Create Conversation

Create a new conversation session.

**Endpoint:** `POST /api/chat/conversations/`

**Content-Type:** `application/json`

**Request Body:**

```json
{
  "session_id": "optional-custom-session-id",
  "metadata": {
    "user_id": "user123",
    "context": "research"
  }
}
```

**Postman Setup:**

1. Method: `POST`
2. URL: `http://localhost:8000/api/chat/conversations/`
3. Body Tab → Select `raw` → Select `JSON`
4. Enter the JSON request body (or leave empty for auto-generation)

**cURL Example:**

```bash
# Auto-generate session_id
curl -X POST http://localhost:8000/api/chat/conversations/ \
  -H "Content-Type: application/json" \
  -d '{}'

# Custom session_id
curl -X POST http://localhost:8000/api/chat/conversations/ \
  -H "Content-Type: application/json" \
  -d '{"session_id": "my-session-123"}'
```

**Success Response (201 Created):**

```json
{
  "id": "conv-uuid-1234",
  "session_id": "auto-generated-uuid",
  "created_at": "2025-10-20T11:00:00Z",
  "last_updated": "2025-10-20T11:00:00Z",
  "metadata": {},
  "message_count": 0
}
```

---

### 7. Ask Question (RAG Query)

Submit a question to the RAG system and get an AI-generated response.

**Endpoint:** `POST /api/chat/query/`

**Content-Type:** `application/json`

**Request Body:**

```json
{
  "question": "What is the main topic discussed in the document?",
  "conversation_id": "conv-uuid-1234",
  "document_filter": ["doc-uuid-1", "doc-uuid-2"],
  "top_k": 5
}
```

**Field Descriptions:**

- `question` (required): The user's question
- `conversation_id` (optional): UUID of existing conversation, creates new if not provided
- `document_filter` (optional): Array of document UUIDs to search within
- `top_k` (optional): Number of chunks to retrieve (1-20, default: 5)

**Postman Setup:**

1. Method: `POST`
2. URL: `http://localhost:8000/api/chat/query/`
3. Body Tab → Select `raw` → Select `JSON`
4. Enter the JSON request body

**cURL Example:**

```bash
# Simple query (creates new conversation)
curl -X POST http://localhost:8000/api/chat/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is machine learning?"
  }'

# Query with conversation context
curl -X POST http://localhost:8000/api/chat/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Tell me more about that",
    "conversation_id": "conv-uuid-1234",
    "top_k": 5
  }'

# Query specific documents
curl -X POST http://localhost:8000/api/chat/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the key findings?",
    "document_filter": ["doc-uuid-1", "doc-uuid-2"],
    "top_k": 10
  }'
```

**Success Response (200 OK):**

```json
{
  "answer": "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed. The main techniques include supervised learning, unsupervised learning, and reinforcement learning.",
  "conversation_id": "conv-uuid-1234",
  "sources": [
    {
      "chunk_id": "chunk-uuid-1",
      "document_id": "doc-uuid-1",
      "page_number": 3,
      "text": "Machine learning is a method of data analysis...",
      "relevance_score": 0.95
    },
    {
      "chunk_id": "chunk-uuid-2",
      "document_id": "doc-uuid-1",
      "page_number": 5,
      "text": "The three main categories of ML are...",
      "relevance_score": 0.87
    }
  ],
  "metadata": {
    "top_k": 5,
    "document_filter": [],
    "message_id": "msg-uuid-5678"
  }
}
```

**Error Response (400 Bad Request):**

```json
{
  "question": ["This field is required."]
}
```

**Error Response (404 Not Found):**

```json
{
  "error": "Conversation not found"
}
```

---

### 8. Get Conversation Messages

Retrieve all messages in a conversation.

**Endpoint:** `GET /api/chat/conversations/{conversation_id}/messages/`

**Path Parameters:**

- `conversation_id`: UUID of the conversation

**Postman Setup:**

1. Method: `GET`
2. URL: `http://localhost:8000/api/chat/conversations/conv-uuid-1234/messages/`

**cURL Example:**

```bash
curl -X GET http://localhost:8000/api/chat/conversations/conv-uuid-1234/messages/
```

**Success Response (200 OK):**

```json
{
  "count": 6,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "msg-uuid-1",
      "conversation": "conv-uuid-1234",
      "role": "user",
      "content": "What is machine learning?",
      "timestamp": "2025-10-20T11:05:00Z",
      "source_chunks": [],
      "audio_file_path": null,
      "metadata": {}
    },
    {
      "id": "msg-uuid-2",
      "conversation": "conv-uuid-1234",
      "role": "assistant",
      "content": "Machine learning is a subset of artificial intelligence...",
      "timestamp": "2025-10-20T11:05:05Z",
      "source_chunks": ["chunk-uuid-1", "chunk-uuid-2"],
      "audio_file_path": null,
      "metadata": {
        "model": "gpt-3.5-turbo",
        "confidence": 0.95
      }
    },
    {
      "id": "msg-uuid-3",
      "conversation": "conv-uuid-1234",
      "role": "user",
      "content": "Can you give me examples?",
      "timestamp": "2025-10-20T11:06:00Z",
      "source_chunks": [],
      "audio_file_path": null,
      "metadata": {}
    }
  ]
}
```

---

### 9. Get Conversation Details

Get detailed conversation information with all messages.

**Endpoint:** `GET /api/chat/conversations/{conversation_id}/`

**Path Parameters:**

- `conversation_id`: UUID of the conversation

**Postman Setup:**

1. Method: `GET`
2. URL: `http://localhost:8000/api/chat/conversations/conv-uuid-1234/`

**cURL Example:**

```bash
curl -X GET http://localhost:8000/api/chat/conversations/conv-uuid-1234/
```

**Success Response (200 OK):**

```json
{
  "id": "conv-uuid-1234",
  "session_id": "session-abc-123",
  "created_at": "2025-10-20T11:00:00Z",
  "last_updated": "2025-10-20T11:06:00Z",
  "metadata": {},
  "message_count": 6,
  "messages": [
    {
      "id": "msg-uuid-1",
      "conversation": "conv-uuid-1234",
      "role": "user",
      "content": "What is machine learning?",
      "timestamp": "2025-10-20T11:05:00Z",
      "source_chunks": [],
      "audio_file_path": null,
      "metadata": {}
    }
  ]
}
```

---

### 10. Delete Conversation

Delete a conversation and all its messages.

**Endpoint:** `DELETE /api/chat/conversations/{conversation_id}/`

**Path Parameters:**

- `conversation_id`: UUID of the conversation

**Postman Setup:**

1. Method: `DELETE`
2. URL: `http://localhost:8000/api/chat/conversations/conv-uuid-1234/`

**cURL Example:**

```bash
curl -X DELETE http://localhost:8000/api/chat/conversations/conv-uuid-1234/
```

**Success Response (204 No Content):**

```
(Empty response body)
```

---

## Voice APIs

### 11. Text-to-Speech

Convert text to speech audio file.

**Endpoint:** `POST /api/voice/text-to-speech/`

**Content-Type:** `application/json`

**Request Body:**

```json
{
  "text": "Hello, this is a test of the text to speech functionality.",
  "voice": "alloy",
  "speed": 1.0
}
```

**Voice Options:**

- `alloy` (default)
- `echo`
- `fable`
- `onyx`
- `nova`
- `shimmer`

**Postman Setup:**

1. Method: `POST`
2. URL: `http://localhost:8000/api/voice/text-to-speech/`
3. Body Tab → Select `raw` → Select `JSON`
4. Enter the JSON request body

**cURL Example:**

```bash
curl -X POST http://localhost:8000/api/voice/text-to-speech/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "voice": "nova",
    "speed": 1.0
  }'
```

**Success Response (200 OK):**

```json
{
  "audio_url": "http://localhost:8000/media/audio/tts/uuid-audio-file.mp3",
  "audio_path": "/path/to/storage/audio/uuid-audio-file.mp3",
  "duration_seconds": 3.5,
  "voice_model": "nova",
  "text_length": 18
}
```

---

### 12. Speech-to-Text

Convert audio file to text transcription.

**Endpoint:** `POST /api/voice/speech-to-text/`

**Content-Type:** `multipart/form-data`

**Request Body:**

```
audio_file: [Audio File - mp3, wav, m4a, webm]
```

**Postman Setup:**

1. Method: `POST`
2. URL: `http://localhost:8000/api/voice/speech-to-text/`
3. Body Tab → Select `form-data`
4. Add key: `audio_file` (change type to `File` from dropdown)
5. Choose your audio file

**cURL Example:**

```bash
curl -X POST http://localhost:8000/api/voice/speech-to-text/ \
  -F "audio_file=@/path/to/your/audio.mp3"
```

**Success Response (200 OK):**

```json
{
  "transcribed_text": "Hello, this is the transcribed text from the audio file.",
  "duration_seconds": 5.2,
  "language": "en",
  "confidence": 0.98
}
```

---

### 13. Voice Chat (Combined STT + RAG + TTS)

Send audio question, get audio response with RAG context.

**Endpoint:** `POST /api/voice/chat/`

**Content-Type:** `multipart/form-data`

**Request Body:**

```
audio_file: [Audio File]
conversation_id: [UUID] (optional)
voice: alloy (optional)
```

**Postman Setup:**

1. Method: `POST`
2. URL: `http://localhost:8000/api/voice/chat/`
3. Body Tab → Select `form-data`
4. Add key: `audio_file` (type: `File`)
5. Add key: `conversation_id` (type: `Text`, optional)
6. Add key: `voice` (type: `Text`, optional)

**cURL Example:**

```bash
curl -X POST http://localhost:8000/api/voice/chat/ \
  -F "audio_file=@/path/to/question.mp3" \
  -F "voice=nova"
```

**Success Response (200 OK):**

```json
{
  "question": "What is artificial intelligence?",
  "answer": "Artificial intelligence is the simulation of human intelligence...",
  "audio_url": "http://localhost:8000/media/audio/tts/response-uuid.mp3",
  "conversation_id": "conv-uuid-5678",
  "sources": [
    {
      "chunk_id": "chunk-uuid-10",
      "text": "AI is defined as...",
      "page_number": 2
    }
  ]
}
```

---

## FAISS Management APIs

### 14. Get FAISS Index Status

Get statistics and status of the FAISS vector database.

**Endpoint:** `GET /api/faiss/status/`

**Postman Setup:**

1. Method: `GET`
2. URL: `http://localhost:8000/api/faiss/status/`

**cURL Example:**

```bash
curl -X GET http://localhost:8000/api/faiss/status/
```

**Success Response (200 OK):**

```json
{
  "index_name": "global_index",
  "total_vectors": 1250,
  "dimension": 384,
  "last_updated": "2025-10-20T12:00:00Z",
  "documents_included": ["doc-uuid-1", "doc-uuid-2", "doc-uuid-3"],
  "index_size_mb": 4.8,
  "is_loaded": true
}
```

---

### 15. Rebuild FAISS Index

Rebuild the FAISS index from scratch (admin operation).

**Endpoint:** `POST /api/faiss/rebuild/`

**Content-Type:** `application/json`

**Request Body:**

```json
{
  "confirm": true
}
```

**Postman Setup:**

1. Method: `POST`
2. URL: `http://localhost:8000/api/faiss/rebuild/`
3. Body Tab → Select `raw` → Select `JSON`
4. Enter: `{"confirm": true}`

**cURL Example:**

```bash
curl -X POST http://localhost:8000/api/faiss/rebuild/ \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'
```

**Success Response (200 OK):**

```json
{
  "message": "FAISS index rebuild started",
  "task_id": "celery-task-uuid",
  "status": "processing",
  "estimated_time_minutes": 5
}
```

---

## Error Responses

### Common HTTP Status Codes

| Status Code               | Meaning              | When It Occurs                             |
| ------------------------- | -------------------- | ------------------------------------------ |
| 200 OK                    | Success              | Successful GET, PUT, PATCH requests        |
| 201 Created               | Resource created     | Successful POST requests                   |
| 204 No Content            | Success with no body | Successful DELETE requests                 |
| 400 Bad Request           | Invalid input        | Validation errors, missing required fields |
| 404 Not Found             | Resource not found   | Invalid UUID, deleted resource             |
| 500 Internal Server Error | Server error         | Unexpected server errors                   |

### Error Response Format

```json
{
  "field_name": ["Error message describing the issue"]
}
```

**Example:**

```json
{
  "question": ["This field is required."],
  "top_k": ["Ensure this value is less than or equal to 20."]
}
```

---

## Testing with Postman

### Step-by-Step: Complete Workflow Test

#### 1. Upload a PDF Document

```
POST http://localhost:8000/api/documents/upload/
Body: form-data
  - file: [Select your PDF]
```

✅ Save the `document.id` from response

#### 2. Check Document Status

```
GET http://localhost:8000/api/documents/{document_id}/
```

✅ Wait until `processing_status` is `completed`

#### 3. View Document Chunks

```
GET http://localhost:8000/api/documents/{document_id}/chunks/
```

✅ Verify chunks were created

#### 4. Create a Conversation

```
POST http://localhost:8000/api/chat/conversations/
Body: raw (JSON)
{}
```

✅ Save the `conversation_id` from response

#### 5. Ask a Question

```
POST http://localhost:8000/api/chat/query/
Body: raw (JSON)
{
  "question": "What is the main topic of this document?",
  "conversation_id": "your-conversation-id",
  "top_k": 5
}
```

✅ Check the answer and sources

#### 6. View Conversation History

```
GET http://localhost:8000/api/chat/conversations/{conversation_id}/messages/
```

✅ See all messages in the conversation

#### 7. Delete Document (Cleanup)

```
DELETE http://localhost:8000/api/documents/{document_id}/
```

---

### Postman Collection Import

Create a new collection in Postman with these folders:

1. **Documents** - All document management endpoints
2. **Chat** - All chat and RAG endpoints
3. **Voice** - All voice-related endpoints
4. **FAISS** - FAISS management endpoints

Save common variables:

- `base_url`: `http://localhost:8000`
- `document_id`: (set after upload)
- `conversation_id`: (set after creation)

---

### Environment Variables for Postman

Create a new Environment in Postman:

| Variable        | Initial Value         | Current Value              |
| --------------- | --------------------- | -------------------------- |
| base_url        | http://localhost:8000 |                            |
| document_id     |                       | (populated after upload)   |
| conversation_id |                       | (populated after creation) |
| chunk_id        |                       | (populated from responses) |

---

## Quick Test Script

```bash
#!/bin/bash
BASE_URL="http://localhost:8000"

# 1. Upload document
echo "Uploading document..."
UPLOAD_RESPONSE=$(curl -s -X POST $BASE_URL/api/documents/upload/ \
  -F "file=@test.pdf")
DOC_ID=$(echo $UPLOAD_RESPONSE | jq -r '.document.id')
echo "Document ID: $DOC_ID"

# 2. Wait for processing (check status)
echo "Checking document status..."
curl -s -X GET $BASE_URL/api/documents/$DOC_ID/ | jq

# 3. Create conversation
echo "Creating conversation..."
CONV_RESPONSE=$(curl -s -X POST $BASE_URL/api/chat/conversations/ \
  -H "Content-Type: application/json" -d '{}')
CONV_ID=$(echo $CONV_RESPONSE | jq -r '.id')
echo "Conversation ID: $CONV_ID"

# 4. Ask question
echo "Asking question..."
curl -s -X POST $BASE_URL/api/chat/query/ \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"What is this document about?\", \"conversation_id\": \"$CONV_ID\"}" | jq

# 5. Get conversation messages
echo "Getting conversation messages..."
curl -s -X GET $BASE_URL/api/chat/conversations/$CONV_ID/messages/ | jq
```

---

## Notes

1. **Document Processing**: Currently documents are marked as "pending". Once PDF processing is implemented, they will be automatically processed and status will change to "completed".

2. **RAG Responses**: The RAG pipeline returns placeholder responses until the full implementation is complete (FAISS + OpenAI integration).

3. **Voice APIs**: Voice endpoints are defined but require OpenAI API key configuration in `.env` file.

4. **Pagination**: All list endpoints support pagination with `?page=N` query parameter.

5. **UUIDs**: All resource IDs are UUIDs (e.g., `a1b2c3d4-e5f6-7890-abcd-ef1234567890`).

---

## Support

If you encounter issues:

1. Check Django server logs
2. Verify database migrations are applied
3. Ensure Redis is running (for Celery)
4. Check `.env` file configuration
5. Verify OpenAI API key is set (for voice/LLM features)

---

**Last Updated:** October 20, 2025  
**API Version:** 1.0  
**Server:** Django 5.0 + DRF
