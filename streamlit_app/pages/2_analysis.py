import streamlit as st
from components.api_client import APIClient
from components.display import display_anomalies, display_analysis_results

st.set_page_config(page_title="Analysis", page_icon="🔍")

if not st.session_state.get("authenticated", False):
    st.error("Please login first.")
    st.stop()

st.title("LLM Analysis")

if not st.session_state.get('metrics_ingested', False):
    st.warning("No metrics ingested in this session. Go to the Ingestion page first.")
    st.stop()

if st.button("Run LLM Analysis", type="primary"):
    client = APIClient()
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
else:
    st.info("Click the button above to run LLM analysis on the ingested metrics.")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Session status:**")
        if st.session_state.get('metrics_ingested', False):
            st.success("Metrics available")
        else:
            st.error("No metrics")
    with col2:
        st.write("**Analysis process:**")
        st.write("1. Anomaly detection")
        st.write("2. LLM analysis")
        st.write("3. Actionable recommendations")
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to Ingestion"):
            st.switch_page("main.py")
    with col2:
        if st.button("Reset session"):
            if 'metrics_ingested' in st.session_state:
                del st.session_state.metrics_ingested
            st.success("Session reset")
            st.rerun() 