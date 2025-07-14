import streamlit as st
import plotly.graph_objects as go
import json

def display_anomalies(anomalies_data):
    """Display anomalies in a structured format"""
    st.subheader("🚨 Anomalies détectées")
    
    if not anomalies_data.get("has_anomalies", False):
        st.success("✅ Aucune anomalie détectée")
        return
    
    anomalies = anomalies_data.get("anomalies", [])
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total anomalies", anomalies_data.get("total_count", 0))
    with col2:
        critical_count = len([a for a in anomalies if a.get("severity", 0) >= 4])
        st.metric("Critiques", critical_count)
    with col3:
        warning_count = len([a for a in anomalies if a.get("severity", 0) == 3])
        st.metric("Warnings", warning_count)
    
    st.write(f"**Résumé:** {anomalies_data.get('summary', 'N/A')}")
    
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
                st.write(f"**Seuil:** {anomaly['threshold']}")

def display_analysis_results(analysis_data):
    """Display LLM analysis results"""
    st.subheader("🧠 Résultats de l'analyse LLM")
    
    metadata = analysis_data.get("analysis_metadata", {})
    col1, col2, col3 = st.columns(3)
    
    with col1:
        confidence = analysis_data.get("confidence_score", 0)
        st.metric("Confiance", f"{confidence:.2f}")
    
    with col2:
        anomaly_count = metadata.get("anomaly_count", 0)
        st.metric("Anomalies analysées", anomaly_count)
    
    with col3:
        response_time = metadata.get("response_time", 0)
        st.metric("Temps de réponse", f"{response_time:.1f}s")
    
    st.subheader("📝 Résumé de l'analyse")
    summary = analysis_data.get("analysis_summary", "Aucun résumé disponible")
    st.info(summary)
    
    st.subheader("🔍 Analyse des causes racines")
    root_cause = analysis_data.get("root_cause_analysis", "Aucune analyse des causes disponible")
    st.write(root_cause)
    
    st.subheader("💡 Recommandations")
    recommendations = analysis_data.get("recommendations", [])
    
    if not recommendations:
        st.warning("Aucune recommandation disponible")
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
        
        with st.expander(f"{priority_color} {i}. {action} (Priorité {priority})"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Catégorie:** {category}")
                st.write(f"**Effort:** {effort}")
            with col2:
                st.write(f"**Impact attendu:** {impact}")
            
            if technical_details:
                st.write(f"**Détails techniques:** {technical_details}")

def display_json_preview(json_data):
    """Display JSON data in a formatted way"""
    st.subheader("👀 Aperçu du JSON")
    
    try:
        formatted_json = json.dumps(json_data, indent=2, ensure_ascii=False)
        st.code(formatted_json, language="json", height=300)
        return True
    except Exception as e:
        st.error(f"Erreur lors du formatage JSON: {e}")
        return False 