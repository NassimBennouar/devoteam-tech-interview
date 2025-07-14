import streamlit as st
from components.api_client import APIClient
from components.display import display_anomalies, display_analysis_results

st.set_page_config(page_title="Analysis", page_icon="🔍")

if not st.session_state.get("authenticated", False):
    st.error("Please login first.")
    st.stop()

st.title("LLM Analysis")

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
    st.subheader("🔍 Analysis Controls")
    if st.button("Run LLM Analysis", type="primary"):
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
                    st.info("It seems metrics are no longer available. Try re-ingesting from the Ingestion page.")
                elif "OPENAI_API_KEY" in error_msg:
                    st.info("OpenAI API key is not configured. Check FastAPI server configuration.")
                elif "Cannot connect" in error_msg:
                    st.info("FastAPI server is not accessible. Make sure it is running on localhost:8000.")

st.divider()
st.info("Click the button above to run LLM analysis on the available metrics.")
col1, col2 = st.columns(2)
with col1:
    st.write("**Analysis process:**")
    st.write("1. Anomaly detection")
    st.write("2. LLM analysis")
    st.write("3. Actionable recommendations")
with col2:
    if st.button("Go to Ingestion"):
        st.switch_page("pages/1_ingestion.py") 