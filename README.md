# 🚀 SupaQuery - AI-Powered Document Analysis Platform

<div align="center">

**Intelligent Document Analysis with Knowledge Graphs • Fully Offline • Privacy-First**

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Documentation](#-documentation)

</div>

## 📖 Overview

**SupaQuery** is an advanced document analysis platform that combines **GraphRAG (Graph-based Retrieval Augmented Generation)** with **Knowledge Graph** technology to provide intelligent, context-aware answers to questions about your documents. Built for privacy and offline operation, it processes PDFs, DOCX files, images, and audio entirely on your infrastructure.

### 🎯 Key Differentiators

- **🧠 Knowledge Graph Architecture**: Uses Memgraph to build semantic relationships between document entities
- **🔒 100% Offline**: All AI processing happens locally using Ollama - no external API calls
- **📊 Advanced Citations**: Page numbers for PDFs, timestamps for audio, quality scores for every answer
- **🎯 Intelligent Query Routing**: Automatically optimizes retrieval strategy based on query type
- **🔄 Multi-Query Generation**: Generates multiple variations to improve retrieval quality
- **✨ Answer Evaluation**: AI-powered quality assessment with automatic retry on poor answers
- **👥 Enterprise RBAC**: Role-based access control with Admin, User, and Viewer roles
- **📁 Multi-Modal Support**: Text, images (OCR), and audio (speech-to-text) processingQuery - Offline Multimodal RAG System



**AI-Powered Offline Document Analysis with GraphRAG**---



SupaQuery is an intelligent document analysis platform that lets you upload various file types (PDFs, DOCX, images, audio) and interact with an AI assistant powered by GraphRAG to extract insights, answer questions, and analyze your data - completely offline.# **Offline Multimodal RAG System**





## ✨ Features

### 🔍 Advanced RAG Pipeline
- **Multi-Query Generation**: Automatically generates 2-3 query variations for better retrieval
- **Intelligent Routing**: Queries are classified and routed (retrieve, clarify, direct_reply)
- **Answer Evaluation**: AI assesses answer quality (relevance, completeness, grounding)
- **Automatic Retry**: Expands context and retries if answer quality is insufficient
- **Quality Scores**: Every answer includes a quality percentage (e.g., ✨ 87%)

### 📄 Document Processing
- **PDF Support**: Full text extraction with page number tracking
- **DOCX Support**: Microsoft Word document processing
- **Image Processing**: Hybrid approach with Tesseract OCR (text) + CLIP (visual embeddings)
- **Audio Transcription**: Speech-to-text with Whisper (tiny model)
- **Smart Chunking**: 512-character chunks with 50-character overlap for context

### 🧠 Knowledge Graph
- **Entity Extraction**: Named Entity Recognition with spaCy (18+ entity types)
- **Relationship Mapping**: Entities linked across documents in Memgraph
- **Graph Queries**: Cypher-based semantic search and traversal
- **Citation Networks**: Track document relationships and references

### 💬 Chat Interface
- **Conversational AI**: Natural language queries with context awareness
- **Rich Citations**: 
  - PDFs: Page numbers (e.g., "📄 p. 5-7")
  - Audio: Timestamps (e.g., "🕐 02:15 - 02:45")
  - Text previews from source content
- **Session Management**: Persistent chat history
- **Real-time Responses**: Streaming answers with progress indicators

### 🔐 Security & Privacy
- **JWT Authentication**: Secure token-based auth with expiration
- **Role-Based Access Control (RBAC)**: Admin, User, and Viewer roles
- **Permission System**: Granular controls (create, read, update, delete, share)
- **Document Isolation**: Users can only access their own documents
- **Password Security**: bcrypt hashing with salt

### 🎨 User Experience
- **Modern UI**: Built with Next.js 15, TypeScript, and shadcn/ui
- **Dark/Light Mode**: Theme switching with persistence
- **Drag & Drop Upload**: Intuitive file upload interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live processing status and notifications

---

## 🚀 Quick Start

### Prerequisites

Ensure you have the following installed:

- **Python 3.13+**
- **Node.js 18+** and npm
- **PostgreSQL** (running locally or via Docker)
- **Docker** (for Memgraph)
- **Ollama** with llama3.2 model
- **FFmpeg** (for audio processing)
- **Tesseract** (for OCR)

### Option 1: Automatic Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/anishks07/SupaQuery.git
cd SupaQuery

# Run the setup script
chmod +x setup.sh
./setup.sh

```
---**Tech Stack:**



## 🚀 Quick Start* **Backend:** Python, FastAPI

* **Database:** PostgreSQL

### Option 1: Docker (Recommended)* **Vector Store:** FAISS for embedding indexing and search

* **LLM Models:** LLaMA 7B (4-bit quantized), MPT-7B, Dia / OpenLLaMA 3B

**Embeddings:** `all-MiniLM-L6-v2` (text), CLIP ViT-B-32 (image - hybrid with Tesseract)

# Clone the repository* **Speech-to-Text:** Whisper Tiny (audio)

git clone https://github.com/anishks07/SupaQuery.git* **Frontend:** React / Streamlit for interactive UI

cd SupaQuery* **Deployment:** Fully offline, Dockerized



# Start all services with Docker Compose**Use Case:**

docker-compose up --buildThis system is ideal for environments where **data privacy is critical**, including **research organizations, intelligence agencies, or offline enterprise solutions**. It enables users to **search and summarize information across multiple data formats quickly**, without relying on cloud services.



# Wait for services to start, then visit:**Getting Started:**

# Frontend: http://localhost:3000

# Backend API: http://localhost:80001. Clone the repository

```2. Set up Python virtual environment and install dependencies```

3. Run the backend API (FastAPI)

### Option 2: Manual Setup4. Start the frontend interface (React / Streamlit)

5. Upload your files and start querying

#### 1. Install Ollama and Download Models

**Note:** All models are **offline and pre-downloaded**, ensuring the system works without internet access.

```bash

# Run the setup script---

chmod +x setup.sh

./setup.sh

# The script will:
# - Install Ollama and download llama3.2 model
# - Set up PostgreSQL database
# - Start Memgraph container
# - Install Python dependencies
# - Install Node.js dependencies
# - Create necessary directories
# - Initialize the database with roles and permissions
```

### Option 2: Manual Setup

#### 1. Install and Configure Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama (keep this running in a terminal)
ollama serve

# In another terminal, pull the model
ollama pull llama3.2:latest
```

#### 2. Set Up PostgreSQL

```bash
# macOS
brew install postgresql
brew services start postgresql

# Create database
createdb supaquery

# Linux
sudo apt-get install postgresql
sudo systemctl start postgresql
sudo -u postgres createdb supaquery
```

#### 3. Start Memgraph (Knowledge Graph)

```bash
docker run -d \
  --name memgraph \
  -p 7687:7687 \
  -p 7444:7444 \
  -p 3001:3000 \
  -v mg_data:/var/lib/memgraph \
  memgraph/memgraph-platform:latest
```

#### 4. Set Up Backend

```bash
cd backend

# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model for entity extraction
python -m spacy download en_core_web_sm

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://mac@localhost/supaquery
SECRET_KEY=$(openssl rand -hex 32)
ACCESS_TOKEN_EXPIRE_MINUTES=30
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
MEMGRAPH_HOST=localhost
MEMGRAPH_PORT=7687
EOF

# Initialize database
python init_db.py

# Start the backend
python main.py
```

Backend API available at: **http://localhost:8000**  
API Documentation: **http://localhost:8000/docs**

#### 5. Set Up Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start the development server
npm run dev
```

Frontend available at: **http://localhost:3000**

#### 6. Install Optional Dependencies

```bash
# macOS
brew install tesseract  # For OCR
brew install ffmpeg     # For audio processing

# Ubuntu/Debian
sudo apt-get install tesseract-ocr
sudo apt-get install ffmpeg

# Windows (via Chocolatey)
choco install tesseract
choco install ffmpeg
```

### First Steps

1. **Open the app**: Navigate to http://localhost:3000
2. **Register**: Create an account (first user gets admin role)
3. **Login**: Sign in with your credentials
4. **Upload**: Drag and drop a PDF or DOCX file
5. **Chat**: Ask questions about your documents!

**Default Admin Credentials** (if using `init_db.py`):
- Username: `admin`
- Password: `admin123`

> ⚠️ **Change the default password immediately in production!**

---

## 🏗️ Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────┐
│                   Frontend (Next.js 15)                  │
│  TypeScript • React 19 • shadcn/ui • Tailwind CSS       │
└────────────────────┬─────────────────────────────────────┘
                     │ REST API (JWT Auth)
┌────────────────────▼─────────────────────────────────────┐
│                Backend (FastAPI + Python 3.13)           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Enhanced GraphRAG Pipeline                        │  │
│  │  • Multi-Query Generator                           │  │
│  │  • Intelligent Router (factual/general/greeting)   │  │
│  │  • Answer Evaluator (quality scoring)             │  │
│  │  • Citation Extractor (pages/timestamps)          │  │
│  └────────────────────────────────────────────────────┘  │
└────────┬──────────────────┬──────────────────┬───────────┘
         │                  │                  │
┌────────▼────────┐ ┌──────▼────────┐ ┌──────▼────────┐
│   PostgreSQL    │ │   Memgraph    │ │    Ollama     │
│   (Metadata)    │ │ (Knowledge    │ │  (llama3.2)   │
│                 │ │   Graph)      │ │               │
│ • Users/Roles   │ │ • Entities    │ │ • Local LLM   │
│ • Documents     │ │ • Relations   │ │ • Embeddings  │
│ • Permissions   │ │ • Chunks      │ │ • Inference   │
└─────────────────┘ └───────────────┘ └───────────────┘
```

### Key Components

**GraphRAG Pipeline:**
1. **Query Classification** → Determines query type (factual, general, greeting, unclear)
2. **Multi-Query Generation** → Creates 2-3 query variations for better retrieval
3. **Intelligent Retrieval** → Fetches relevant chunks from knowledge graph
4. **Answer Generation** → LLM creates response with context
5. **Quality Evaluation** → AI scores answer (relevance, completeness, grounding)
6. **Retry Logic** → Expands context and regenerates if quality < threshold

**Citation System:**
- PDF citations include page numbers
- Audio citations include timestamps
- Each citation links to source location
- Quality scores displayed for transparency

---

## 🛠️ Technology Stack

### Frontend
| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Next.js | 15.3.5 |
| Language | TypeScript | 5.x |
| UI Library | React | 19.0 |
| Styling | Tailwind CSS | 4.x |
| Components | shadcn/ui (Radix UI) | Latest |
| Animation | Framer Motion | 12.x |
| State | Zustand + React Query | Latest |

### Backend
| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | FastAPI | Latest |
| Language | Python | 3.13+ |
| LLM Framework | LlamaIndex | Latest |
| Vector Store | FAISS | Latest |
| Reranking | BM25 | Latest |

### AI/ML Stack
| Component | Technology | Purpose |
|-----------|-----------|---------|
| LLM | Ollama (llama3.2) | Answer generation |
| Text Embeddings | all-MiniLM-L6-v2 | Sentence embeddings (384-dim) |
| Image Embeddings | CLIP ViT-B-32 | Visual embeddings (512-dim) |
| NER | spaCy (en_core_web_sm) | Entity extraction |
| OCR | Tesseract | Image text extraction |
| Speech-to-Text | OpenAI Whisper (tiny) | Audio transcription |

### Databases
| Database | Type | Purpose |
|----------|------|---------|
| PostgreSQL | SQL | User auth, metadata, RBAC |
| Memgraph | Graph | Knowledge graph, entities, relations |

### Infrastructure
- **Process Manager**: Uvicorn (ASGI)
- **Containerization**: Docker + Docker Compose
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: bcrypt

---

## 📖 Usage Guide

### Basic Workflow

1. **📤 Upload Documents**
   ```
   • Drag and drop files or click "Upload Files"
   • Supported: PDF, DOCX, images (JPG, PNG), audio (MP3, WAV, OGG)
   • Wait for processing (you'll see progress indicators)
   ```

2. **💬 Ask Questions**
   ```
   • Type your question in the chat interface
   • Examples:
     - "What is this document about?"
     - "Summarize the key findings"
     - "What did the speaker say about X?"
   ```

3. **📊 Review Answers**
   ```
   • Read the AI-generated answer
   • Check quality score (e.g., ✨ 87%)
   • Click citations to see sources:
     - PDFs: Page numbers (📄 p. 5)
     - Audio: Timestamps (🕐 02:15)
   • View text previews from sources
   ```

4. **🔍 Explore Knowledge Graph**
   ```
   • Open Memgraph Lab: http://localhost:3001
   • Run Cypher queries to visualize relationships
   • Explore entity connections across documents
   ```

### Advanced Features

**Multi-Document Queries:**
```
"Compare the findings in report.pdf and study.docx"
```

**Follow-up Questions:**
```
User: "What are the main findings?"
AI: [Answer with citations]
User: "Tell me more about finding #2"
AI: [Contextual follow-up answer]
```

**Document Management:**
- View all uploaded documents
- Delete documents (removes from graph)
- Track processing status
- See chunk counts and metadata

---

## 🔧 Configuration

### Environment Variables

#### Backend (`.env`)
```bash
# PostgreSQL Database
DATABASE_URL=postgresql+asyncpg://username@localhost/supaquery

SECRET_KEY=your-secret-key-here-use-openssl-rand-hex-32
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Ollama LLM Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest

# Memgraph Configuration
MEMGRAPH_HOST=localhost
MEMGRAPH_PORT=7687

# Server Configuration
BACKEND_PORT=8000
BACKEND_HOST=0.0.0.0

# CORS (add your frontend URLs)
CORS_ORIGINS=http://localhost:3000,http://frontend:3000

# File Processing
CHUNK_SIZE=512
CHUNK_OVERLAP=50
MAX_FILE_SIZE=52428800  # 50MB

# OCR (Tesseract path)
TESSERACT_CMD=/opt/homebrew/bin/tesseract  # macOS
# TESSERACT_CMD=/usr/bin/tesseract          # Linux

# Audio (Whisper model size)
WHISPER_MODEL=tiny  # Options: tiny, base, small, medium, large

# Storage Paths
UPLOAD_DIR=./uploads
STORAGE_DIR=./storage
```

#### Frontend (`.env.local`)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Customization Options

**Adjust Quality Threshold** (backend/app/services/graph_rag_enhanced.py):
```python
# Lower = more lenient, higher = stricter
self.quality_threshold = 0.7  # Default: 0.7 (70%)
```

**Change Max Retries** (backend/app/services/graph_rag_enhanced.py):
```python
# How many times to retry on poor quality
self.max_retries = 2  # Default: 2
```

**Modify Chunk Size** (backend/.env):
```bash
CHUNK_SIZE=1024        # Larger chunks = more context
CHUNK_OVERLAP=100      # More overlap = better continuity
```

---

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Clean restart (removes volumes)
docker-compose down -v && docker-compose up --build

# Scale backend
docker-compose up -d --scale backend=3
```

### Docker Compose Services

The `docker-compose.yml` includes:
- **backend**: FastAPI application
- **frontend**: Next.js application
- **postgres**: PostgreSQL database
- **memgraph**: Knowledge graph database
- **ollama**: LLM inference engine

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Ollama Connection Errors

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start Ollama
ollama serve

# Verify model is downloaded
ollama list

# Pull model if missing
ollama pull llama3.2:latest

# Test model
ollama run llama3.2 "Hello"
```

#### 2. Database Connection Failed

```bash
# Check PostgreSQL status
# macOS
brew services list | grep postgresql

# Linux
sudo systemctl status postgresql

# Start PostgreSQL if stopped
# macOS
brew services start postgresql

# Linux
sudo systemctl start postgresql

# Create database if missing
createdb supaquery

# Test connection
psql -h localhost -U mac -d supaquery
```

#### 3. Memgraph Not Responding

```bash
# Check Docker container
docker ps | grep memgraph

# If not running, start it
docker start memgraph

# View logs
docker logs memgraph

# Restart if needed
docker restart memgraph

# Connect to Memgraph Lab
open http://localhost:3001
```

#### 4. Permission Denied on Upload

**Issue**: 403 Forbidden when uploading documents

**Solution**:
```bash
# Re-initialize database permissions
cd backend
python init_db.py

# Or manually check user roles
psql -d supaquery -c "SELECT u.username, r.name FROM users u JOIN user_roles ur ON u.id=ur.user_id JOIN roles r ON ur.role_id=r.id;"
```

#### 5. spaCy Model Missing

```bash
# Error: Can't find model 'en_core_web_sm'
python -m spacy download en_core_web_sm

# Verify installation
python -c "import spacy; spacy.load('en_core_web_sm')"
```

#### 6. OCR Not Working

```bash
# Install Tesseract
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Windows (requires manual install)
# Download from: https://github.com/UB-Mannheim/tesseract/wiki

# Test OCR
tesseract --version

# Update TESSERACT_CMD in .env if needed
which tesseract  # Use this path
```

#### 7. Audio Processing Fails

```bash
# Install FFmpeg
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows (via Chocolatey)
choco install ffmpeg

# Test FFmpeg
ffmpeg -version
```

#### 8. Frontend Won't Start

```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json .next
npm install
npm run dev

# Check for port conflicts
lsof -i :3000
# Kill process if needed
kill -9 <PID>
```

#### 9. Backend Crashes on Startup

```bash
# Check Python version
python --version  # Should be 3.13+

# Reinstall dependencies
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Check for missing environment variables
cat .env

# View detailed error logs
python main.py --log-level debug
```

#### 10. No Citations in Responses

**Check**:
1. Document was processed successfully (check backend logs)
2. Chunks were created (verify in PostgreSQL)
3. Page numbers were extracted (check document_chunks table)

**Solution**:
```bash
# Re-upload document
# Or reindex existing documents
cd backend
python reindex_documents.py
```

### Debug Mode

Enable verbose logging for troubleshooting:

```python
# backend/main.py
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## 📚 API Documentation

### Base URL
- Development: `http://localhost:8000`
- Interactive Docs: `http://localhost:8000/docs` (Swagger UI)
- ReDoc: `http://localhost:8000/redoc`

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "SecurePass123!"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "john_doe",
    "roles": ["user"]
  }
}
```

#### Get Current User
```http
GET /api/users/me
Authorization: Bearer <token>

Response:
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "roles": ["user"],
  "created_at": "2025-10-08T10:30:00Z"
}
```

### Document Endpoints

#### Upload Documents
```http
POST /api/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

files: [File, File, ...]
is_public: false (optional)

Response:
{
  "success": true,
  "files": [
    {
      "id": 1,
      "file_id": "uuid",
      "name": "report.pdf",
      "type": "pdf",
      "size": 1024000,
      "status": "processed",
      "chunks": 45,
      "is_public": false
    }
  ]
}
```

#### List Documents
```http
GET /api/documents?skip=0&limit=100
Authorization: Bearer <token>

Response:
{
  "documents": [
    {
      "id": 1,
      "filename": "report.pdf",
      "file_type": "pdf",
      "file_size": 1024000,
      "status": "processed",
      "total_chunks": 45,
      "created_at": "2025-10-08T10:30:00Z"
    }
  ],
  "total": 1
}
```

#### Delete Document
```http
DELETE /api/documents/{id}
Authorization: Bearer <token>

Response:
{
  "success": true,
  "message": "Document deleted successfully"
}
```

### Chat Endpoints

#### Send Query
```http
POST /api/chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "What is the main topic?",
  "session_id": null,
  "document_ids": [1, 2]
}

Response:
{
  "answer": "The main topic is...",
  "citations": [
    {
      "document_id": 1,
      "filename": "report.pdf",
      "page_number": 5,
      "chunk_text": "Relevant excerpt..."
    }
  ],
  "entities": [
    {"name": "Apple Inc.", "type": "ORG"}
  ],
  "quality_score": 0.87,
  "retry_count": 0,
  "session_id": "uuid"
}
```

#### Get Chat Sessions
```http
GET /api/chat/sessions
Authorization: Bearer <token>

Response:
{
  "sessions": [
    {
      "id": "uuid",
      "title": "Discussion about report.pdf",
      "created_at": "2025-10-08T10:30:00Z",
      "message_count": 5
    }
  ]
}
```

### Health Check
```http
GET /api/health

Response:
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "memgraph": "connected",
    "ollama": "connected"
  }
}
```

---

## 📁 Project Structure

```
SupaQuery/
├── backend/                          # Python FastAPI backend
│   ├── app/
│   │   ├── services/
│   │   │   ├── graph_rag_enhanced.py    # Enhanced GraphRAG pipeline
│   │   │   ├── multi_query_generator.py # Multi-query generation
│   │   │   ├── evaluation_agent.py      # Answer quality evaluation
│   │   │   ├── document_processor.py    # File processing + citations
│   │   │   ├── faiss_reranker_service.py # Vector search + BM25
│   │   │   └── auth_service.py          # JWT authentication
│   │   ├── models/
│   │   │   ├── database.py              # SQLAlchemy models
│   │   │   └── schemas.py               # Pydantic schemas
│   │   └── routers/
│   │       ├── auth.py                  # Auth endpoints
│   │       ├── documents.py             # Document endpoints
│   │       └── chat.py                  # Chat endpoints
│   ├── main.py                       # FastAPI application
│   ├── init_db.py                    # Database initialization
│   ├── requirements.txt              # Python dependencies
│   └── .env                          # Environment configuration
│
├── frontend/                         # Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx             # Main chat interface
│   │   │   ├── login/               # Login page
│   │   │   └── register/            # Registration page
│   │   ├── components/
│   │   │   ├── ui/                  # shadcn/ui components
│   │   │   ├── chat/                # Chat components
│   │   │   └── documents/           # Document components
│   │   └── lib/
│   │       └── api.ts               # API client
│   ├── package.json                 # Node dependencies
│   └── .env.local                   # Frontend config
│
├── docker-compose.yml               # Multi-container setup
├── setup.sh                         # Automated setup script
└── README.md                        # This file
```

---

## 📊 Performance Characteristics

### Response Times (Typical)

| Operation | Time | Notes |
|-----------|------|-------|
| User Login | 50-100ms | JWT generation |
| Document Upload (1MB PDF) | 2-5s | Including processing & indexing |
| Entity Extraction | 100-500ms | Per 1000 words with spaCy |
| Knowledge Graph Query | 50-200ms | Cypher traversal in Memgraph |
| LLM Inference | 2-10s | Depends on context size |
| Full Chat Response | 3-12s | End-to-end with evaluation |
| Multi-Query Generation | 500ms-2s | Creates 2-3 variations |
| Answer Evaluation | 1-3s | Quality scoring by LLM |

### Scalability Limits

| Resource | Limit | Notes |
|----------|-------|-------|
| Concurrent Users | 100-500 | Single backend instance |
| Documents per User | 10,000+ | Limited by storage |
| Total Documents | 1M+ | With graph partitioning |
| Queries per Second | 50-200 | With caching + load balancing |
| Max Document Size | 50MB | Configurable |
| Chunk Count per Doc | Unlimited | 512-char chunks |

### Resource Usage

```
Backend Process:
- Base: ~200MB (FastAPI + libraries)
- Per Request: +5-20MB (document processing)
- spaCy Model: ~50MB (loaded once)
- Connection Pools: ~50MB

Memgraph:
- Base: ~100MB
- Per 1000 Documents: ~50-100MB
- Per 10K Entities: ~10-20MB
- Indexes: ~10% of data size

Ollama (llama3.2):
- Model: ~2GB (loaded once)
- Per Inference: +50-200MB (context window)
- Max Context: 2048 tokens
```

---

## � Security Features

### Authentication & Authorization
- **JWT Tokens**: Secure token-based authentication with HS256 signing
- **Token Expiration**: 30-minute default (configurable)
- **Password Hashing**: bcrypt with salt rounds
- **RBAC**: Role-based access control with granular permissions
- **Permission Checks**: Every endpoint protected by dependencies

### Data Security
- **SQL Injection Prevention**: Parameterized queries via SQLAlchemy ORM
- **XSS Protection**: Content sanitization in responses
- **CORS Configuration**: Restricted to allowed origins
- **File Validation**: Type and size checks on upload
- **Document Isolation**: Users can only access their own documents

### Privacy
- **Offline Processing**: All AI operations run locally
- **No External APIs**: No data sent to third parties
- **Secure Storage**: Files stored in protected directories
- **Session Management**: Secure session handling with JWT

---

## 📈 Monitoring & Logging

### Backend Logging

The backend provides detailed logging for debugging:

```
================================================================================
🔍 NEW QUERY: What are the findings?
================================================================================
📋 Query Type: factual
🎯 Routing Strategy: retrieve

📝 Generated 3 query variations:
   1. What are the findings?
   2. What are the key results?
   3. What conclusions were reached?

🔎 Retrieving with 3 queries...
   Retrieved 12 unique chunks

🤖 Generating answer...
   ✓ Generated 456 chars

🔍 Evaluating answer quality...
   Quality: 0.85 | Completeness: 0.92 | Relevance: 0.90
   Overall Score: 0.89
   Sufficient: ✅ YES

✅ Query completed in 4.2s
```

### Metrics to Monitor

- **Query Response Time**: Track P50, P95, P99 latencies
- **Document Processing Time**: Upload to indexed time
- **LLM Inference Time**: Time spent in Ollama
- **Retry Rate**: How often answers need regeneration
- **Quality Scores**: Distribution of answer quality
- **Error Rate**: Failed requests by endpoint
- **Database Query Time**: PostgreSQL + Memgraph performance

---

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

### Run Frontend Tests
```bash
cd frontend
npm run test
npm run test:e2e
```

### Manual Testing Checklist

- [ ] User registration and login
- [ ] Document upload (PDF, DOCX, image, audio)
- [ ] Document listing and deletion
- [ ] Basic query with citations
- [ ] Multi-query generation (check logs)
- [ ] Answer quality evaluation
- [ ] Retry on poor quality
- [ ] Page number citations (PDF)
- [ ] Timestamp citations (audio)
- [ ] Entity extraction
- [ ] Knowledge graph queries
- [ ] Permission checks (RBAC)
- [ ] Session management

---

## 🚀 Deployment

### Production Checklist

- [ ] Change default admin password
- [ ] Generate secure SECRET_KEY (32+ characters)
- [ ] Configure production DATABASE_URL
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up backup strategy
- [ ] Enable rate limiting
- [ ] Configure log rotation
- [ ] Set up monitoring/alerts
- [ ] Document recovery procedures

### Environment-Specific Configs

**Development:**
```bash
DEBUG=True
CORS_ORIGINS=http://localhost:3000
```

**Production:**
```bash
DEBUG=False
CORS_ORIGINS=https://yourdomain.com
ACCESS_TOKEN_EXPIRE_MINUTES=15
```

### Scaling Strategies

1. **Horizontal Scaling**: Add more backend instances behind load balancer
2. **Database Scaling**: PostgreSQL read replicas, Memgraph sharding
3. **Caching Layer**: Redis for session/query caching
4. **CDN**: Serve static frontend assets via CDN
5. **Queue System**: Celery for async document processing

---

## 📖 Documentation

### Comprehensive Guides

- **[QUICK_START_ENHANCED.md](QUICK_START_ENHANCED.md)** - 5-minute getting started guide
- **[HYBRID_IMAGE_PROCESSING.md](HYBRID_IMAGE_PROCESSING.md)** - Tesseract + CLIP hybrid approach
- **[ENHANCED_ARCHITECTURE.md](ENHANCED_ARCHITECTURE.md)** - Detailed architecture documentation
- **[VISUAL_ARCHITECTURE_GUIDE.md](VISUAL_ARCHITECTURE_GUIDE.md)** - Visual diagrams and workflows
- **[TESTING_ENHANCED_FEATURES.md](TESTING_ENHANCED_FEATURES.md)** - Testing guide
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Complete project documentation
- **[DATABASE.md](DATABASE.md)** - Database schemas and setup
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture details

### API Documentation

- Interactive API Docs: http://localhost:8000/docs (Swagger UI)
- Alternative Docs: http://localhost:8000/redoc (ReDoc)

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript strict mode for frontend
- Write tests for new features
- Update documentation
- Add type hints to Python functions
- Use meaningful commit messages

---

## 🙏 Acknowledgments

### Technologies & Frameworks
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[Next.js](https://nextjs.org/)** - React framework for production
- **[Ollama](https://ollama.ai/)** - Local LLM inference
- **[LlamaIndex](https://www.llamaindex.ai/)** - RAG framework
- **[Memgraph](https://memgraph.com/)** - High-performance graph database
- **[spaCy](https://spacy.io/)** - Industrial-strength NLP
- **[shadcn/ui](https://ui.shadcn.com/)** - Beautiful UI components

### Open Source Libraries
- **OpenAI Whisper** - Speech recognition
- **Tesseract OCR** - Optical character recognition
- **FAISS** - Vector similarity search
- **SQLAlchemy** - Python SQL toolkit
- **Zustand** - React state management
- **React Query** - Server state management

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0** (GPLv3).

### What this means:
- ✅ **Freedom to use**: You can use this software for any purpose
- ✅ **Freedom to study**: You can examine and modify the source code  
- ✅ **Freedom to distribute**: You can share copies with others
- ✅ **Freedom to improve**: You can distribute modified versions

### Key Requirements:
- 📋 **Share Source Code**: If you distribute this software, you must make the source code available
- 🏷️ **License Notice**: Include the GPL license notice in derivative works
- 📝 **State Changes**: Document any modifications you make to the code
- 🔓 **Keep Open**: Derivative works must also be licensed under GPLv3

### Commercial Use:
- You **can** use this software commercially
- You **can** charge for distribution or support services
- You **must** still comply with GPLv3 requirements (share source code)

For the complete license text, see the [LICENSE](LICENSE) file.

**TLDR**: This is free and open-source software. You can use, modify, and distribute it freely, but any derivative work must also be open-source under GPLv3.

---

## 📞 Support

### Getting Help

- **Documentation**: Read the comprehensive guides in the repo
- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions and share ideas

### Common Questions

**Q: Can I use this in production?**  
A: Yes, but change default passwords and follow the production checklist.

**Q: Does it require internet access?**  
A: No, everything runs offline once models are downloaded.

**Q: What's the difference between this and ChatGPT?**  
A: SupaQuery is specialized for document analysis with citations, runs offline, and uses knowledge graphs for better context understanding.

**Q: Can I use different LLM models?**  
A: Yes, modify `OLLAMA_MODEL` in `.env` to use mistral, phi, or other Ollama models.

**Q: How accurate are the citations?**  
A: Citations are extracted directly from document metadata and are highly accurate for PDFs and audio files.

---

## 🗺️ Roadmap

### v2.0 (Current)
- ✅ Enhanced GraphRAG with multi-query
- ✅ Answer quality evaluation
- ✅ PDF page number citations
- ✅ Audio timestamp citations
- ✅ Knowledge graph with Memgraph
- ✅ RBAC with JWT auth
- ✅ Hybrid image processing (Tesseract + CLIP)

### v2.1 (Planned)
- [ ] Visual image search (similarity-based)
- [ ] Advanced graph visualizations
- [ ] Document comparison features
- [ ] Batch document upload
- [ ] Export chat history to PDF
- [ ] Mobile-responsive improvements

### v3.0 (Future)
- [ ] Multi-language support
- [ ] Custom entity types
- [ ] Advanced analytics dashboard
- [ ] Team collaboration features
- [ ] API webhooks
- [ ] Plugin system

---

<div align="center">

**Built with ❤️ for intelligent document analysis**

⭐ Star this repo if you find it useful!

[Report Bug](https://github.com/anishks07/SupaQuery/issues) • [Request Feature](https://github.com/anishks07/SupaQuery/issues) • [Documentation](https://github.com/anishks07/SupaQuery)

</div>

