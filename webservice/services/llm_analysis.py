import os
import time
import json
from datetime import datetime
from typing import Dict, Any, List
import logging

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langsmith import Client
from langsmith.run_helpers import traceable

from webservice.models.analysis import AnalysisResult, Recommendation, LLMAnalysisMetrics, RecommendationCategory
from webservice.models.anomaly import AnomalyResult
from webservice.models.metrics import InfrastructureMetrics

load_dotenv()
logger = logging.getLogger(__name__)


class LLMAnalysisService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        if self.langsmith_api_key:
            os.environ["LANGSMITH_API_KEY"] = self.langsmith_api_key
            os.environ["LANGSMITH_TRACING"] = "true"
            os.environ["LANGSMITH_PROJECT"] = "infrastructure-monitoring"
        
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            openai_api_key=self.openai_api_key
        )
        
        self.langsmith_client = Client() if self.langsmith_api_key else None
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("human", self._get_human_prompt())
        ])
        
        self.output_parser = JsonOutputParser()
        self.chain = self.prompt_template | self.llm | self.output_parser
        
        logger.info("LLM Analysis Service initialized")

    def _get_system_prompt(self) -> str:
        return """You are an expert infrastructure monitoring analyst. Your role is to analyze system metrics and anomalies to provide actionable recommendations.

You will receive:
1. Current infrastructure metrics (CPU, memory, network, etc.)
2. Detected anomalies with severity levels
3. Limited historical context

Your analysis should:
- Identify root causes of performance issues
- Provide prioritized, actionable recommendations
- Consider both immediate fixes and long-term optimizations
- Be specific and technical when appropriate

IMPORTANT: Base your analysis only on the provided data. Acknowledge when historical data is limited.

Response format must be valid JSON with this structure:
{{
    "analysis_summary": "Brief overview of the current state",
    "root_cause_analysis": "Detailed analysis of identified issues",
    "recommendations": [
        {{
            "priority": 1-5,
            "category": "immediate|short_term|monitoring|optimization",
            "action": "Specific action to take",
            "impact": "Expected impact",
            "effort": "low|medium|high",
            "technical_details": "Implementation details if needed"
        }}
    ],
    "confidence_score": 0.0-1.0
}}"""

    def _get_human_prompt(self) -> str:
        return """Current Infrastructure Metrics:
{metrics}

Detected Anomalies:
{anomalies}

Historical Context (Limited):
{history_summary}

Please analyze this infrastructure state and provide recommendations."""

    @traceable(name="analyze_infrastructure_anomalies")
    def analyze_anomalies(
        self, 
        anomaly_result: AnomalyResult, 
        metrics: Dict[str, Any], 
        history_summary: Dict[str, Any]
    ) -> AnalysisResult:
        start_time = time.time()
        
        try:
            logger.info(f"Starting LLM analysis for {anomaly_result.total_count} anomalies")
            
            input_data = {
                "metrics": self._format_metrics(metrics),
                "anomalies": self._format_anomalies(anomaly_result),
                "history_summary": self._format_history(history_summary)
            }
            
            response = self.chain.invoke(input_data)
            
            analysis_result = self._parse_llm_response(response)
            
            response_time = time.time() - start_time
            analysis_result.analysis_metadata = {
                "response_time": response_time,
                "anomaly_count": anomaly_result.total_count,
                "critical_anomalies": len([a for a in anomaly_result.anomalies if a.severity >= 4]),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"LLM analysis completed in {response_time:.2f}s with confidence {analysis_result.confidence_score}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in LLM analysis: {str(e)}")
            return self._create_fallback_analysis(anomaly_result, str(e))

    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        formatted = []
        for key, value in metrics.items():
            if key == "service_status":
                services = ", ".join([f"{k}:{v}" for k, v in value.items()])
                formatted.append(f"- {key}: {services}")
            else:
                formatted.append(f"- {key}: {value}")
        return "\n".join(formatted)

    def _format_anomalies(self, anomaly_result: AnomalyResult) -> str:
        if not anomaly_result.has_anomalies:
            return "No anomalies detected"
        
        formatted = [f"Summary: {anomaly_result.summary}\n"]
        
        for anomaly in anomaly_result.anomalies:
            formatted.append(
                f"- {anomaly.metric}: {anomaly.value} "
                f"(severity: {anomaly.severity}, type: {anomaly.type.value})"
                f"\n  Message: {anomaly.message}"
            )
        
        return "\n".join(formatted)

    def _format_history(self, history_summary: Dict[str, Any]) -> str:
        if not history_summary:
            return "No historical data available"
        
        formatted = ["Historical data (last 5 values):"]
        for metric, data in history_summary.items():
            if data["count"] > 0:
                avg = data["average"]
                values = data["values"]
                formatted.append(f"- {metric}: avg={avg:.1f}, recent={values}")
        
        return "\n".join(formatted)

    def _parse_llm_response(self, response: Dict[str, Any]) -> AnalysisResult:
        try:
            recommendations = []
            for rec_data in response.get("recommendations", []):
                recommendation = Recommendation(
                    priority=rec_data["priority"],
                    category=RecommendationCategory(rec_data["category"]),
                    action=rec_data["action"],
                    impact=rec_data["impact"],
                    effort=rec_data["effort"],
                    technical_details=rec_data.get("technical_details")
                )
                recommendations.append(recommendation)
            
            return AnalysisResult(
                analysis_summary=response["analysis_summary"],
                root_cause_analysis=response["root_cause_analysis"],
                recommendations=recommendations,
                confidence_score=response["confidence_score"]
            )
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            raise ValueError(f"Invalid LLM response format: {str(e)}")

    def _create_fallback_analysis(self, anomaly_result: AnomalyResult, error_msg: str) -> AnalysisResult:
        return AnalysisResult(
            analysis_summary=f"Analysis failed: {error_msg}",
            root_cause_analysis="Unable to perform detailed analysis due to technical error",
            recommendations=[
                Recommendation(
                    priority=1,
                    category=RecommendationCategory.IMMEDIATE,
                    action="Check system logs and investigate technical issues",
                    impact="Restore monitoring capabilities",
                    effort="medium"
                )
            ],
            confidence_score=0.0,
            analysis_metadata={"error": error_msg}
        )

    def get_analysis_metrics(self) -> Dict[str, Any]:
        """Get LLM usage metrics - placeholder for now"""
        return {
            "total_analyses": 0,
            "average_response_time": 0.0,
            "total_cost_estimate": 0.0,
            "last_analysis": None
        } 