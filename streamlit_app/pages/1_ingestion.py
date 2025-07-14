import streamlit as st
import json
from components.api_client import APIClient
from components.display import display_json_preview

st.set_page_config(page_title="Ingestion", page_icon="📥")

if not st.session_state.get("authenticated", False):
    st.error("Please login first.")
    st.stop()

st.title("Ingestion")

client = APIClient()

col1, col2 = st.columns(2)
with col1:
    st.subheader("📊 Current Metrics Status")
    metrics_info = client.get_metrics_info()
    if metrics_info["success"]:
        data = metrics_info["data"]
        st.metric("Total Points", data["total_count"])
        if data["latest_timestamp"]:
            st.metric("Latest Point", data["latest_timestamp"])
        else:
            st.metric("Latest Point", "None")
    else:
        st.error(f"Error loading metrics info: {metrics_info['error']}")

with col2:
    st.subheader("📤 Upload New Metrics")
    uploaded_file = st.file_uploader(
        "Upload a JSON file with infrastructure metrics",
        type=['json'],
        help="The file must contain all required metrics in JSON format"
    )

if uploaded_file is not None:
    try:
        file_content = uploaded_file.read()
        json_data = json.loads(file_content.decode('utf-8'))
        with st.expander("Show JSON preview"):
            st.code(json.dumps(json_data, indent=2), language="json", height=300)
        if st.button("Send to API", type="primary"):
            with st.spinner("Sending..."):
                result = client.ingest_metrics(json_data)
                if result["success"]:
                    st.success("Metrics successfully sent!")
                    st.rerun()
                else:
                    st.error(f"Error: {result['error']}")
    except json.JSONDecodeError as e:
        st.error(f"JSON format error: {e}")
    except Exception as e:
        st.error(f"Error reading file: {e}")
else:
    st.info("No file selected. Here is an example of the expected JSON structure:")
    example_json = {
        "timestamp": "2023-10-01T12:00:00Z",
        "cpu_usage": 95,
        "memory_usage": 90,
        "latency_ms": 600,
        "disk_usage": 95,
        "network_in_kbps": 1000,
        "network_out_kbps": 800,
        "io_wait": 15,
        "thread_count": 100,
        "active_connections": 200,
        "error_rate": 0.08,
        "uptime_seconds": 1800,
        "temperature_celsius": 85,
        "power_consumption_watts": 450,
        "service_status": {
            "database": "offline",
            "api_gateway": "degraded",
            "cache": "online"
        }
    }
    st.code(json.dumps(example_json, indent=2), language="json") 