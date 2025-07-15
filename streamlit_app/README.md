# Infrastructure Monitoring - Streamlit Dashboard

## 🚀 Quick Start

### Prerequisites
- FastAPI server running on `localhost:8000`
- API keys configured (`OPENAI_API_KEY`, `LANGSMITH_API_KEY`)

### Start the App
```bash
cd streamlit_app/
uv run streamlit run main.py --server.port 8501
```

Access: `http://localhost:8501`

## 📋 Features

### 📥 Ingestion Page
- **Single metrics**: Upload one JSON file with current infrastructure metrics
- **Batch metrics**: Upload multiple data points for historical analysis
- Preview before sending
- API validation
- Example file download

### 🔍 Analysis Page
- **Latest Point Analysis**: Real-time anomaly detection and LLM analysis of current metrics
- **Historical Analysis**: Pattern analysis across multiple data points with configurable history depth
- Toggle between analysis modes
- Collapsible anomaly breakdown display
- Structured recommendations with priority levels

### 📊 Dashboards
- **Anomaly Summary**: Warning/critical counts per metric
- **Recommendations Table**: Prioritized actions with effort/impact
- **Analysis Metadata**: Response times, confidence scores, pattern insights

## 📁 Structure

```
streamlit_app/
├── main.py                 # Landing page
├── pages/
│   ├── 1_ingestion.py      # JSON upload + validation
│   └── 2_analysis.py       # Latest + historical analysis
├── components/
│   ├── api_client.py       # FastAPI client
│   └── display.py          # UI components
└── example_metrics.json    # Test data
```

## 🧪 Test Flow

1. **Start FastAPI**: `uv run python main.py` (in webservice/)
2. **Start Streamlit**: `uv run streamlit run main.py` (in streamlit_app/)
3. **Test ingestion**: Upload `example_metrics.json`
4. **Test analysis**: Run both latest and historical analysis modes

## ⚠️ Current State

- **Temporary persistence**: Data lost on FastAPI restart
- **No authentication**: Open access
- **Single user session**: Basic tracking

## 📋 Next Phases

- **Phase 1.6B**: SQLite persistence
- **Phase 1.6C**: Authentication
- **Phase 2.1**: Real-time mode
- **Phase 2.2**: Historical charts 