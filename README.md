# Infrastructure Monitoring System

## 🏗️ Architecture

```
/
├── webservice/           # FastAPI Backend
│   ├── pyproject.toml    # API dependencies
│   └── ...
├── streamlit_app/        # Streamlit Frontend  
│   ├── pyproject.toml    # Frontend dependencies
│   └── ...
├── notebooks/            # Jupyter Analysis
│   ├── pyproject.toml    # Data analysis dependencies
│   └── ...
├── docker-compose.yml    # Orchestration
└── nginx.conf           # Reverse proxy
```

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# Start all services
docker-compose up -d

# Access:
# - Frontend: http://localhost
# - API: http://localhost/api
# - API Docs: http://localhost/api/docs
```

### Option 2: Local Development
```bash
# Terminal 1: API
cd webservice/
uv run python main.py

# Terminal 2: Frontend  
cd streamlit_app/
uv run streamlit run main.py

# Terminal 3: Notebooks (optional)
cd notebooks/
uv run jupyter lab
```

## 📋 Services

### 🔧 API (Port 8000)
- FastAPI backend with anomaly detection
- LLM analysis with OpenAI
- SQLite database
- RESTful endpoints

### 🎨 Frontend (Port 8501)
- Streamlit dashboard
- Metrics ingestion
- Analysis visualization
- Real-time monitoring

### 📊 Notebooks
- Jupyter environment
- Data analysis tools
- Custom visualizations

## 🔧 Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_key
LANGSMITH_API_KEY=your_langsmith_key
DATABASE_URL=sqlite+aiosqlite:///./infra_monitoring.db
```

### Ports
- **80**: Nginx (Frontend + API proxy)
- **3000**: FastAPI (Direct access)
- **3001**: Streamlit (Direct access)

## 📁 Project Structure

- **webservice/**: Backend API and services
- **streamlit_app/**: Frontend dashboard
- **notebooks/**: Data analysis environment
- **docker-compose.yml**: Service orchestration
- **nginx.conf**: Reverse proxy configuration
