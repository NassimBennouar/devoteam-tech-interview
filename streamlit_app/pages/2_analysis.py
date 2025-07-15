import streamlit as st
from components.api_client import APIClient
from components.display import display_anomalies, display_analysis_results, display_historical_analysis_results

st.set_page_config(page_title="Analysis", page_icon="🔍")
    
if not st.session_state.get("authenticated", False):
    st.error("Please login first.")
    st.stop()

st.title("LLM Analysis")

client = APIClient()
        
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

st.subheader("🔍 Analysis Controls")
analysis_type = st.radio(
    "Choose analysis type:",
    ["Latest Point Analysis", "Historical Analysis"],
    help="Latest Point: Analyze only the most recent metrics. Historical: Analyze patterns across multiple data points."
)

if analysis_type == "Historical Analysis":
    points = st.slider(
        "Number of historical points to analyze:",
        min_value=10,
        max_value=200,
        value=50,
        step=10,
        help="More points provide better pattern detection but take longer to analyze"
    )

if st.button("Run Analysis", type="primary"):
    if metrics_info["success"] and data["total_count"] > 0:
        if analysis_type == "Latest Point Analysis":
            st.subheader("Step 1: Anomaly Detection")
            with st.spinner("Detecting anomalies..."):
                anomalies_result = client.get_anomalies()
                if anomalies_result["success"]:
                    display_anomalies(anomalies_result["data"])
                else:
                    st.error(f"Error: {anomalies_result['error']}")
                    st.stop()
            st.divider()
            st.subheader("Step 2: LLM Analysis")
            with st.spinner("Running LLM analysis... (may take a few seconds)"):
                analysis_result = client.get_analysis()
                if analysis_result["success"]:
                    display_analysis_results(analysis_result["data"])
                    st.success("Analysis completed successfully!")
                else:
                    st.error(f"Error: {analysis_result['error']}")
                    error_msg = analysis_result['error']
                    if "No metrics available" in error_msg:
                        st.info("It seems metrics are no longer available. Try ingesting new metrics from the Ingestion page.")
                    elif "OPENAI_API_KEY" in error_msg:
                        st.info("OpenAI API key is not configured. Check FastAPI server configuration.")
                    elif "Cannot connect" in error_msg:
                        st.info("FastAPI server is not accessible. Make sure it is running on localhost:8000.")
        else:
            st.subheader("Historical Analysis")
            with st.spinner(f"Running historical analysis on {points} points... (may take 10-20 seconds)"):
                analysis_result = client.get_historical_analysis(points)
                if analysis_result["success"]:
                    display_historical_analysis_results(analysis_result["data"])
                    st.success("Historical analysis completed successfully!")
                else:
                    st.error(f"Error: {analysis_result['error']}")
                    error_msg = analysis_result['error']
                    if "Insufficient historical data" in error_msg:
                        st.info("Not enough historical data available. Try ingesting more metrics first.")
                    elif "OPENAI_API_KEY" in error_msg:
                        st.info("OpenAI API key is not configured. Check FastAPI server configuration.")
                    elif "Cannot connect" in error_msg:
                        st.info("FastAPI server is not accessible. Make sure it is running on localhost:8000.")
    else:
        st.error("No metrics available. Please ingest metrics first.") 