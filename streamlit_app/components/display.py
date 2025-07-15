import streamlit as st
import plotly.graph_objects as go
import json

def display_anomalies(anomalies_data):
    """Display anomalies in a structured format"""
    st.subheader("🚨 Detected Anomalies")
    
    if not anomalies_data.get("has_anomalies", False):
        st.success("✅ No anomalies detected")
        return
    
    anomalies = anomalies_data.get("anomalies", [])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total anomalies", anomalies_data.get("total_count", 0))
    with col2:
        critical_count = len([a for a in anomalies if a.get("severity", 0) >= 4])
        st.metric("Critical", critical_count)
    with col3:
        warning_count = len([a for a in anomalies if a.get("severity", 0) == 3])
        st.metric("Warnings", warning_count)
    
    st.write(f"**Summary:** {anomalies_data.get('summary', 'N/A')}")
    
    for i, anomaly in enumerate(anomalies, 1):
        severity = anomaly.get("severity", 0)
        metric = anomaly.get("metric", "Unknown")
        value = anomaly.get("value", "N/A")
        message = anomaly.get("message", "No message")
        anomaly_type = anomaly.get("type", "unknown")
        
        if severity >= 4:
            alert_type = "error"
            emoji = "🔴"
        elif severity == 3:
            alert_type = "warning"
            emoji = "🟡"
        else:
            alert_type = "info"
            emoji = "🔵"
        
        with st.expander(f"{emoji} {metric} = {value} (Severity {severity})"):
            st.write(f"**Type:** {anomaly_type}")
            st.write(f"**Message:** {message}")
            if anomaly.get("threshold"):
                st.write(f"**Threshold:** {anomaly['threshold']}")

def display_analysis_results(analysis_data):
    """Display LLM analysis results"""
    st.subheader("🧠 LLM Analysis Results")
    
    metadata = analysis_data.get("analysis_metadata", {})
    col1, col2, col3 = st.columns(3)
    
    with col1:
        confidence = analysis_data.get("confidence_score", 0)
        st.metric("Confidence", f"{confidence:.2f}")
    
    with col2:
        anomaly_count = metadata.get("anomaly_count", 0)
        st.metric("Analyzed Anomalies", anomaly_count)
    
    with col3:
        response_time = metadata.get("response_time", 0)
        st.metric("Response Time", f"{response_time:.1f}s")
    
    st.subheader("📝 Analysis Summary")
    summary = analysis_data.get("analysis_summary", "No summary available")
    st.info(summary)
    
    st.subheader("🔍 Root Cause Analysis")
    root_cause = analysis_data.get("root_cause_analysis", "No root cause analysis available")
    st.write(root_cause)
    
    st.subheader("💡 Recommendations")
    recommendations = analysis_data.get("recommendations", [])
    
    if not recommendations:
        st.warning("No recommendations available")
        return
    
    for i, rec in enumerate(recommendations, 1):
        priority = rec.get("priority", 5)
        category = rec.get("category", "unknown")
        action = rec.get("action", "No action specified")
        impact = rec.get("impact", "No impact specified")
        effort = rec.get("effort", "unknown")
        technical_details = rec.get("technical_details")
        
        if priority <= 2:
            priority_color = "🔴"
        elif priority <= 3:
            priority_color = "🟡"
        else:
            priority_color = "🟢"
        
        with st.expander(f"{priority_color} {i}. {action} (Priority {priority})"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Category:** {category}")
                st.write(f"**Effort:** {effort}")
            with col2:
                st.write(f"**Expected Impact:** {impact}")
            
            if technical_details:
                st.write(f"**Technical Details:** {technical_details}")

def display_historical_analysis_results(analysis_data):
    """Display historical LLM analysis results with pattern insights"""
    st.subheader("🧠 Historical Analysis Results")
    
    metadata = analysis_data.get("analysis_metadata", {})
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        confidence = analysis_data.get("confidence_score", 0)
        st.metric("Confidence", f"{confidence:.2f}")
    
    with col2:
        total_points = metadata.get("total_points", 0)
        st.metric("Points Analyzed", total_points)
    
    with col3:
        response_time = metadata.get("response_time", 0)
        st.metric("Response Time", f"{response_time:.1f}s")
    
    with col4:
        analysis_type = metadata.get("analysis_type", "unknown")
        st.metric("Analysis Type", analysis_type.title())
    
    st.subheader("📝 Analysis Summary")
    summary = analysis_data.get("analysis_summary", "No summary available")
    st.info(summary)
    
    st.subheader("🔍 Root Cause Analysis")
    root_cause = analysis_data.get("root_cause_analysis", "No root cause analysis available")
    st.write(root_cause)
    
    pattern_interpretation = metadata.get("pattern_interpretation", {})
    severity_assessment = metadata.get("severity_assessment", {})
    
    if pattern_interpretation:
        st.subheader("📊 Pattern Interpretation")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Main Pattern:** {pattern_interpretation.get('main_pattern', 'N/A')}")
            st.write(f"**Pattern Type:** {pattern_interpretation.get('pattern_type', 'N/A')}")
        with col2:
            st.write(f"**Probable Cause:** {pattern_interpretation.get('probable_cause', 'N/A')}")
            st.write(f"**Priority Metric:** {pattern_interpretation.get('priority_metric', 'N/A')}")
    
    if severity_assessment:
        st.subheader("⚠️ Severity Assessment")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            criticality = severity_assessment.get("criticality", 0)
            st.metric("Criticality", f"{criticality}/5")
        with col2:
            urgency = severity_assessment.get("urgency", "N/A")
            st.metric("Urgency", urgency.title())
        with col3:
            business_impact = severity_assessment.get("business_impact", "N/A")
            st.metric("Business Impact", business_impact.title())
        with col4:
            escalation_risk = severity_assessment.get("escalation_risk", "N/A")
            st.metric("Escalation Risk", escalation_risk.title())
    
    anomaly_breakdown = metadata.get("anomaly_breakdown", {})
    if anomaly_breakdown:
        st.subheader("📊 Historical Anomaly Breakdown")
        
        breakdown_data = []
        for metric, data in anomaly_breakdown.items():
            warnings = data.get("warnings", 0)
            critical = data.get("critical", 0)
            total = data.get("total", 0)
            avg_threshold = data.get("avg_threshold")
            
            threshold_display = f"{avg_threshold:.1f}" if avg_threshold else "N/A"
            
            breakdown_data.append({
                "Metric": metric,
                "Warnings": warnings,
                "Critical": critical,
                "Total": total,
                "Avg Threshold": threshold_display
            })
    
        breakdown_data.sort(key=lambda x: x["Total"], reverse=True)
        
        if breakdown_data:
            st.table(breakdown_data)
        else:
            st.info("No anomaly breakdown data available")
    
    st.subheader("💡 Recommendations")
    recommendations = analysis_data.get("recommendations", [])
    
    if not recommendations:
        st.warning("No recommendations available")
        return
    
    for i, rec in enumerate(recommendations, 1):
        priority = rec.get("priority", 5)
        category = rec.get("category", "unknown")
        action = rec.get("action", "No action specified")
        impact = rec.get("impact", "No impact specified")
        effort = rec.get("effort", "unknown")
        technical_details = rec.get("technical_details")
        
        if priority <= 2:
            priority_color = "🔴"
        elif priority <= 3:
            priority_color = "🟡"
        else:
            priority_color = "🟢"
        
        with st.expander(f"{priority_color} {i}. {action} (Priority {priority})"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Category:** {category}")
                st.write(f"**Effort:** {effort}")
            with col2:
                st.write(f"**Expected Impact:** {impact}")
            
            if technical_details:
                st.write(f"**Technical Details:** {technical_details}")

def display_json_preview(json_data):
    """Display JSON data in a formatted way"""
    st.subheader("👀 JSON Preview")
    
    try:
        formatted_json = json.dumps(json_data, indent=2, ensure_ascii=False)
        st.code(formatted_json, language="json", height=300)
        return True
    except Exception as e:
        st.error(f"Error formatting JSON: {e}")
        return False 