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

The interface will be available at: `http://localhost:8501`

## 📋 Features

### 📥 Ingestion Page
- **Upload JSON**: Select a `.json` file with metrics
- **Preview**: Visualize the JSON before sending
- **Validation**: Send to FastAPI for formal validation
- **Example**: Download a sample JSON file

### 🔍 Analysis Page
- **Anomaly detection**: Calls `/api/anomalies`
- **LLM analysis**: Calls `/api/analysis`
- **Structured results**: Displays recommendations
- **Error handling**: Clear error messages

## 📁 Structure

```
streamlit_app/
├── main.py                 # Landing page
├── pages/
│   ├── 1_ingestion.py      # JSON upload + API call
│   └── 2_analysis.py       # LLM analysis + display
├── components/
│   ├── api_client.py       # FastAPI HTTP client
│   └── display.py          # Display components
├── example_metrics.json    # Example for testing
└── README.md               # This documentation
```

## 🧪 Quick Test

1. **Start FastAPI** (in webservice/):
   ```bash
   uv run python main.py
   ```

2. **Start Streamlit** (in streamlit_app/):
   ```bash
   uv run streamlit run main.py
   ```

3. **Test ingestion**:
   - Go to "Ingestion"
   - Upload `example_metrics.json`
   - Click "Send to API"

4. **Test analysis**:
   - Go to "Analysis"
   - Click "Run LLM Analysis"

## ⚠️ Current Limitations

- **Temporary persistence**: Data is lost when FastAPI restarts
- **Streamlit session**: Basic tracking of ingested metrics
- **No authentication**: Open access (planned for next phases)
- **Single user**: Only one active session

## 📋 Next Phases

- **Phase 1.6B**: SQLite persistence
- **Phase 1.6C**: "jean/jean" authentication
- **Phase 2.1**: Real-time mode
- **Phase 2.2**: Historical analysis + charts 