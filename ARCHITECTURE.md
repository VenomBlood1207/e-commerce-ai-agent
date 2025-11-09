# System Architecture

## Overview

The E-commerce Intelligence Agent is a multi-agent system built with LangGraph that processes natural language queries about e-commerce data.

## Component Architecture

### 1. Frontend Layer (React + Tailwind CSS)
- **ChatInterface**: Main conversation UI
- **MessageBubble**: Displays user/assistant messages
- **DataTable**: Renders query results in table format
- **ChartDisplay**: Visualizes data with Recharts (bar, line, pie, scatter)
- **Sidebar**: Navigation and statistics

### 2. API Layer (FastAPI)
- **REST Endpoints**: `/query`, `/conversation`, `/stats`, `/health`
- **WebSocket**: Real-time streaming at `/ws/{session_id}`
- **CORS Middleware**: Handles cross-origin requests
- **Connection Manager**: Manages WebSocket connections

### 3. Agent Layer (LangGraph Workflow)

#### Router Agent
- Classifies queries into: data_query, knowledge_search, translation, utility
- Routes to appropriate specialized agent

#### SQL Agent
- Generates SQL from natural language using Groq LLM
- Schema-aware query generation
- Error handling with retry logic
- Executes queries against SQLite database

#### Knowledge Agent
- Web search using DuckDuckGo
- RAG (Retrieval Augmented Generation) with ChromaDB
- Combines external and internal knowledge

#### Translator Agent
- Portuguese ↔ English translation
- Category name translation from database
- Uses Groq LLM for general translation

#### Visualizer Agent
- Auto-detects appropriate chart type
- Generates chart configurations
- Supports bar, line, pie, scatter plots

### 4. LLM Layer (Groq)
- **Reasoning Model**: gpt-oss-120b for complex queries
- **SQL Model**: llama-3.3-70b-versatile for SQL generation
- **Embeddings**: sentence-transformers for vector search

### 5. Data Layer

#### SQLite Database (9 tables)
- orders, order_items, order_payments, order_reviews
- customers, sellers, products
- product_category_name_translation, geolocation

#### ChromaDB Vector Store
- Product embeddings for semantic search
- Fast similarity search with HNSW indexing

#### Conversation Memory
- Session-based chat history
- Context-aware responses
- Configurable history length

## Data Flow

```
User Query
    ↓
Frontend (React)
    ↓ HTTP POST /query
FastAPI Server
    ↓
LangGraph Workflow
    ↓
Router Agent (classify query)
    ↓
[Conditional Routing]
    ├─→ SQL Agent → Database → Results
    ├─→ Knowledge Agent → Web/RAG → Information
    ├─→ Translator Agent → Translation
    └─→ Utility Response
    ↓
Visualizer Agent (if data query)
    ↓
Response Generator
    ↓
Conversation Memory (save)
    ↓
FastAPI Response
    ↓
Frontend Display
```

## Key Design Decisions

### 1. Multi-Agent Architecture
- **Why**: Separation of concerns, specialized agents for specific tasks
- **Benefit**: Easier to maintain, test, and extend

### 2. LangGraph for Orchestration
- **Why**: Declarative workflow definition, state management
- **Benefit**: Clear data flow, easy to visualize and debug

### 3. Groq for LLM
- **Why**: Fast inference, cost-effective, good model selection
- **Benefit**: Sub-second response times, reliable API

### 4. SQLite Database
- **Why**: Serverless, embedded, perfect for demo/prototype
- **Benefit**: No separate database server, easy setup

### 5. ChromaDB for Vector Store
- **Why**: Lightweight, embedded, good for small-medium datasets
- **Benefit**: Fast semantic search, easy integration

### 6. React + Tailwind Frontend
- **Why**: Modern, component-based, utility-first CSS
- **Benefit**: Fast development, responsive design, clean UI

## Scalability Considerations

### Current Limitations
- Single SQLite database (not suitable for concurrent writes)
- In-memory conversation storage (lost on restart)
- No authentication/authorization
- Single server instance

### Production Improvements
1. **Database**: PostgreSQL with connection pooling
2. **Caching**: Redis for query results and sessions
3. **Memory**: Persistent storage (PostgreSQL/Redis)
4. **Authentication**: JWT tokens, user management
5. **Scaling**: Load balancer, multiple workers
6. **Monitoring**: Logging, metrics, error tracking

## Security Features

- Environment variables for API keys
- Parameterized SQL queries (SQL injection prevention)
- Input validation with Pydantic
- CORS configuration
- No sensitive data in logs

## Performance Optimizations

1. **Query Caching**: Frequently asked questions cached
2. **Lazy Loading**: Database connections on-demand
3. **Streaming**: WebSocket for real-time updates
4. **Batch Processing**: Bulk vector operations
5. **Connection Pooling**: Reuse database connections

## Error Handling

- Try-catch blocks at each agent level
- Retry logic for SQL generation errors
- Graceful degradation (fallback responses)
- Error messages returned to user
- Logging for debugging

## Testing Strategy

1. **Unit Tests**: Individual agent functions
2. **Integration Tests**: Complete workflow
3. **API Tests**: FastAPI endpoints
4. **Manual Testing**: Test script provided

## Future Enhancements

- [ ] Streaming LLM responses
- [ ] Query result caching
- [ ] Advanced RAG with reranking
- [ ] Multi-language support
- [ ] Voice input/output
- [ ] Export to PDF/Excel
- [ ] Scheduled insights
- [ ] Predictive analytics
