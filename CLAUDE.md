# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Python Core Package
```bash
# Install in development mode
pip install -e .

# Install with API dependencies  
pip install -e ".[api]"

# Install development dependencies
pip install pytest ruff

# Run tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_lightrag_ollama_chat.py -v

# Run tests with coverage
python -m pytest tests/ --cov=lightrag

# Lint code
ruff check lightrag/
ruff format lightrag/

# Run examples
cd examples/
python lightrag_openai_demo.py
```

### Web UI Frontend
```bash
cd lightrag_webui/

# Install dependencies (with Bun - preferred)
bun install

# Install dependencies (with npm)
npm install

# Development (with Bun - preferred)
bun run dev

# Development (with Node.js)
npm run dev-no-bun

# Build
bun run build

# Lint
bun run lint

# Type check
bunx tsc --noEmit
```

### API Server
```bash
# Start LightRAG server
lightrag-server

# Start with Gunicorn
lightrag-gunicorn

# Docker deployment
docker compose up
```

## Architecture Overview

### Core Components

**LightRAG Core** (`lightrag/lightrag.py`)
- Main RAG orchestration engine
- Handles document indexing and querying
- Supports multiple storage backends
- Requires explicit initialization: `await rag.initialize_storages()` and `await initialize_pipeline_status()`

**Storage Layer** (`lightrag/kg/`)
- **Vector Storage**: NanoVectorDB (default), Milvus, Qdrant, Faiss, PostgreSQL, MongoDB
- **Graph Storage**: NetworkX (default), Neo4j, PostgreSQL AGE, Memgraph  
- **KV Storage**: JSON files (default), PostgreSQL, Redis, MongoDB
- **Document Status**: JSON (default), PostgreSQL, MongoDB

**LLM Integration** (`lightrag/llm/`)
- OpenAI, Azure OpenAI, Anthropic, Gemini
- Ollama, Hugging Face, LlamaIndex
- AWS Bedrock, NVIDIA, SiliconCloud
- Configurable via embedding and LLM model functions

**Query Processing** (`lightrag/operate.py`)
- Entity extraction and knowledge graph construction
- Multiple query modes: local, global, hybrid, naive, mix
- Chunking, embedding, and retrieval operations

### API Server (`lightrag/api/`)
- FastAPI-based REST API
- Web UI for document management and graph visualization
- Ollama-compatible chat interface
- Authentication and multi-user support

### Web UI (`lightrag_webui/`)
- React + TypeScript frontend
- Built with Vite and Tailwind CSS
- Features: document upload, graph visualization, query interface
- Uses Zustand for state management

## Key Concepts

**Initialization Pattern**
```python
from lightrag import LightRAG
from lightrag.operate import initialize_pipeline_status

rag = LightRAG(
    working_dir="./storage",
    llm_model_func=...,  # Required: LLM function
    embedding_func=...,  # Required: Embedding function
    vector_storage=...,  # Optional: Vector storage type
    graph_storage=...,   # Optional: Graph storage type
    kv_storage=...,      # Optional: Key-value storage type
)
await rag.initialize_storages()  # Required!
await initialize_pipeline_status()  # Required!
```

**Storage Selection**
- Set storage types during LightRAG initialization
- Each storage type has multiple implementations
- Workspace parameter provides data isolation

**Query Modes**
- `local`: Context-dependent information
- `global`: Global knowledge utilization  
- `hybrid`: Combines local and global
- `naive`: Basic vector search
- `mix`: Integrates knowledge graph and vector retrieval

**Document Processing**
- Documents are chunked by token size (default 1200 tokens)
- Entities and relationships extracted via LLM
- Knowledge graph constructed automatically
- Vector embeddings generated for retrieval

## Environment Configuration

Key environment variables:
- `OPENAI_API_KEY`: OpenAI API access
- `WORKING_DIR`: Storage directory
- `TOP_K`: Number of top items to retrieve (default 60)
- `MAX_TOKENS`: Maximum tokens for LLM summary (default 32000)
- `MAX_ASYNC`: Maximum concurrent LLM processes (default 4)
- Storage-specific: `NEO4J_URI`, `POSTGRES_URL`, `REDIS_URL`, etc.

## Testing and Examples

**Test Files**
- `tests/test_graph_storage.py`: Graph storage implementation tests
- `tests/test_lightrag_ollama_chat.py`: Ollama integration tests

**Example Usage**
- `examples/lightrag_openai_demo.py`: Basic OpenAI integration
- `examples/lightrag_ollama_demo.py`: Ollama model usage  
- `examples/graph_visual_*.py`: Graph visualization examples
- `examples/rerank_example.py`: Reranking functionality

## Deployment Options

**Local Development**: Use JSON-based storage (default)
**Production**: PostgreSQL for unified storage or specialized databases (Neo4j for graphs, Milvus for vectors)
**Containerized**: Docker Compose with database services
**Kubernetes**: Helm charts available in `k8s-deploy/`

## Common Patterns

**Multi-modal Integration**: Use RAG-Anything for document parsing and multimodal RAG
**Conversation History**: Pass conversation context via QueryParam
**Custom Models**: Implement embedding_func and llm_model_func for any provider
**Data Export**: Built-in export to CSV, Excel, Markdown formats
**Entity Management**: Create, edit, merge, and delete entities/relationships programmatically
**Document Processing**: New track_id feature for tracking document processing pipeline

## Troubleshooting

**Storage Issues**
- Ensure `await rag.initialize_storages()` is called before any operations
- Check that storage directories have write permissions
- For PostgreSQL/Neo4j: verify connection strings are correct

**Async Initialization**
- All LightRAG operations require async/await
- Use `asyncio.run()` for synchronous contexts
- Always initialize pipeline status: `await initialize_pipeline_status()`

**Common Errors**
- "Storages not initialized": Call `await rag.initialize_storages()` first
- "Pipeline status not initialized": Call `await initialize_pipeline_status()`
- "No LLM/embedding function provided": Required parameters missing from LightRAG init
## AI Team Configuration (autogenerated by team-configurator, 2025-07-31)

**Important: YOU MUST USE subagents when available for the task.**

### Technology Stack Overview
- **Backend**: Python 3.10+ with FastAPI, async/await patterns
- **Frontend**: React 19 + TypeScript + Vite + Tailwind CSS
- **Storage**: Multi-backend (Neo4j, PostgreSQL, MongoDB, Redis, Milvus, Qdrant, Faiss)
- **LLM Integrations**: OpenAI, Anthropic, Gemini, Ollama, AWS Bedrock, Hugging Face
- **Deployment**: Docker, Kubernetes (Helm), Gunicorn
- **Graph Visualization**: Sigma.js + React integration

### AI Team Task Assignments

| Task Category | Recommended Agent | Notes & Best Practices |
|---------------|-------------------|------------------------|
| **Python Core Development** | `backend-developer` | For LightRAG core engine, storage implementations, and LLM integrations |
| **FastAPI API Design** | `api-architect` | Use for REST API contracts, OpenAPI specs, and route design |
| **React Frontend Development** | `react-component-architect` | For React components, hooks, TypeScript patterns, and UI state management |
| **Storage Backend Implementation** | `backend-developer` | Specialized in Neo4j, PostgreSQL, MongoDB, Redis integrations |
| **LLM Provider Integration** | `backend-developer` | For adding new LLM providers (OpenAI, Anthropic, Gemini, etc.) |
| **Graph Visualization** | `react-component-architect` | For Sigma.js integration and interactive graph features |
| **Performance Optimization** | `performance-optimizer` | Critical for vector search, graph queries, and async operations |
| **Code Review** | `code-reviewer` | MUST be used before merging any PRs - security-focused |
| **Documentation** | `documentation-specialist` | For API docs, README updates, and technical guides |
| **Complex Architecture** | `tech-lead-orchestrator` | For cross-component features spanning Python+React+Database |

### Specialized Agent Commands

#### Python Backend Tasks
```bash
# Use backend-developer for:
# - Storage backend implementations (Neo4j, MongoDB, PostgreSQL)
# - LLM provider integrations
# - Core LightRAG engine modifications
# - Async/await optimization

Try: "@backend-developer implement Redis vector storage backend"
```

#### React Frontend Tasks
```bash
# Use react-component-architect for:
# - New React components and hooks
# - TypeScript type definitions
# - State management with Zustand
# - Graph visualization features
# - Tailwind CSS styling

Try: "@react-component-architect create document upload component with drag-and-drop"
```

#### API Design Tasks
```bash
# Use api-architect for:
# - REST API endpoint design
# - OpenAPI specification updates
# - Authentication and authorization patterns
# - Pagination and filtering standards

Try: "@api-architect design API for entity relationship management"
```

### Project-Specific Considerations

#### 1. **Async/Await Patterns**
All LightRAG operations are async. Always use:
- `await rag.initialize_storages()` before operations
- `await initialize_pipeline_status()` for pipeline setup
- Proper async context managers for database connections

#### 2. **Storage Abstraction**
The project uses a storage abstraction layer with multiple backends:
- **Vector Storage**: Use `backend-developer` for new implementations
- **Graph Storage**: Neo4j/NetworkX implementations require graph expertise
- **KV Storage**: Redis/MongoDB/PostgreSQL options available

#### 3. **LLM Integration Patterns**
New LLM providers must implement the standard interface:
- Follow existing patterns in `lightrag/llm/` directory
- Use `tenacity` for retry logic
- Implement proper error handling and rate limiting

#### 4. **React Architecture**
Frontend follows modern React patterns:
- **State Management**: Zustand stores in `lightrag_webui/src/stores/`
- **Component Library**: Radix UI + Tailwind CSS (shadcn/ui style)
- **Graph Visualization**: Sigma.js with React integration
- **Routing**: React Router with tab-based navigation

#### 5. **Type Safety**
- **Backend**: Use Python type hints throughout
- **Frontend**: Strict TypeScript configuration
- **API Contracts**: Pydantic models for request/response validation

### Quick Start Commands

#### For Backend Development
```bash
# New storage backend
@backend-developer "create Milvus vector storage implementation following nano_vector_db_impl.py pattern"

# New LLM provider
@backend-developer "add Claude 3.5 Sonnet support to lightrag/llm/anthropic.py"

# Performance optimization
@performance-optimizer "optimize Neo4j graph queries for entity extraction"
```

#### For Frontend Development
```bash
# New feature component
@react-component-architect "build entity editor modal with form validation"

# State management
@react-component-architect "add conversation history store to Zustand"

# Graph enhancement
@react-component-architect "implement node clustering in graph visualization"
```

#### For API Development
```bash
# New endpoint design
@api-architect "design REST API for document chunk management"

# Authentication
@api-architect "add JWT authentication to FastAPI routes"
```

### File Structure Guidelines

#### Backend (`lightrag/`)  
- `lightrag.py` - Core orchestration (use `backend-developer`)
- `kg/` - Storage implementations (use `backend-developer`)
- `llm/` - LLM provider integrations (use `backend-developer`)
- `api/` - FastAPI server (use `api-architect` + `backend-developer`)

#### Frontend (`lightrag_webui/`)  
- `src/features/` - Page-level components (use `react-component-architect`)
- `src/components/` - Reusable UI components (use `react-component-architect`)
- `src/stores/` - State management (use `react-component-architect`)
- `src/api/` - API client code (use `react-component-architect`)

#### Cross-Cutting Concerns
- **Testing**: Use `backend-developer` for Python tests, `react-component-architect` for frontend tests
- **Documentation**: Use `documentation-specialist` for all documentation
- **Performance**: Use `performance-optimizer` for optimization across all layers
- **Security**: Use `code-reviewer` for security-focused reviews

### Emergency Protocols

For critical issues spanning multiple components:
1. **Start with** `tech-lead-orchestrator` to analyze scope
2. **Delegate to specialists** based on component boundaries
3. **Use** `code-reviewer` **before any production deployment**

EOF < /dev/null
