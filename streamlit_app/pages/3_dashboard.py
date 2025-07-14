import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from components.api_client import APIClient

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

if not st.session_state.get("authenticated", False):
    st.error("Please login first.")
    st.stop()

st.title("📊 Metrics Dashboard")

client = APIClient()

if "dashboard_data" not in st.session_state:
    st.session_state.dashboard_data = None

if st.button("Refresh Data"):
    st.session_state.dashboard_data = None

if st.session_state.dashboard_data is None:
    with st.spinner("Loading metrics data..."):
        history_result = client.get_history(limit=500)
        if history_result["success"]:
            st.session_state.dashboard_data = history_result["data"]["data"]
        else:
            st.error(f"Error loading data: {history_result['error']}")
            st.stop()

if st.session_state.dashboard_data:
    data = st.session_state.dashboard_data
    
    col1, col2 = st.columns([1, 4])
    with col1:
        view_mode = st.radio("View Mode", ["Charts", "Correlation Matrix"])
    
    with col2:
        st.write(f"Loaded {len(data)} data points")
    
    if view_mode == "Charts":
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        metrics = [
            ('cpu_usage', 'CPU Usage (%)', '#FF6B6B'),
            ('memory_usage', 'Memory Usage (%)', '#4ECDC4'),
            ('latency_ms', 'Latency (ms)', '#45B7D1'),
            ('disk_usage', 'Disk Usage (%)', '#96CEB4'),
            ('network_in_kbps', 'Network In (kbps)', '#FFEAA7'),
            ('network_out_kbps', 'Network Out (kbps)', '#DDA0DD'),
            ('io_wait', 'I/O Wait (%)', '#98D8C8'),
            ('thread_count', 'Thread Count', '#F7DC6F'),
            ('active_connections', 'Active Connections', '#BB8FCE'),
            ('error_rate', 'Error Rate', '#E74C3C'),
            ('uptime_seconds', 'Uptime (seconds)', '#3498DB'),
            ('temperature_celsius', 'Temperature (°C)', '#E67E22'),
            ('power_consumption_watts', 'Power (W)', '#9B59B6')
        ]
        
        tab_names = [metric[1] for metric in metrics]
        tabs = st.tabs(tab_names)
        
        for i, (metric_col, metric_name, color) in enumerate(metrics):
            with tabs[i]:
                recent_data = df.tail(100)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=recent_data['timestamp'],
                    y=recent_data[metric_col],
                    mode='lines',
                    name=metric_name,
                    line=dict(color=color, width=2)
                ))
                
                fig.update_layout(
                    title=f"{metric_name} - Last 100 Points",
                    xaxis_title="Time",
                    yaxis_title=metric_name,
                    height=400,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Current", f"{recent_data[metric_col].iloc[-1]:.2f}")
                with col2:
                    st.metric("Average", f"{recent_data[metric_col].mean():.2f}")
                with col3:
                    st.metric("Max", f"{recent_data[metric_col].max():.2f}")
    
    else:
        df = pd.DataFrame(data)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            correlation_points = st.slider("Data points for correlation", 5, len(data), min(500, len(data)), step=5)
        
        with col2:
            st.write(f"Using last {correlation_points} points for correlation analysis")
        
        recent_df = df.tail(correlation_points)
        
        numeric_columns = [
            'cpu_usage', 'memory_usage', 'latency_ms', 'disk_usage',
            'network_in_kbps', 'network_out_kbps', 'io_wait',
            'active_connections', 'error_rate',
            'temperature_celsius', 'power_consumption_watts'
        ]
        
        correlation_matrix = recent_df[numeric_columns].corr().round(2)
        
        fig = px.imshow(
            correlation_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdBu",
            color_continuous_midpoint=0
        )
        
        fig.update_layout(
            title="Metrics Correlation Matrix",
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Correlation Details")
        st.dataframe(correlation_matrix, use_container_width=True)
else:
    st.info("No data available. Please refresh the data.") 