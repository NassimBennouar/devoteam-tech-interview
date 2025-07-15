import os
import time
import json
from datetime import datetime
from typing import Dict, Any, List
import logging
import asyncio

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.schema.runnable import RunnableParallel
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
        
        # Original chain for simple analysis
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("human", self._get_human_prompt())
        ])
        
        self.output_parser = JsonOutputParser()
        self.chain = self.prompt_template | self.llm | self.output_parser
        
        self._setup_historical_chains()
        
        logger.info("LLM Analysis Service initialized with historical analysis capabilities")

    def _setup_historical_chains(self):
        """Setup LangChain chains for historical pattern analysis"""
        
        self.pattern_interpretation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert infrastructure monitoring analyst. Analyze anomaly patterns from historical data.

Your task is to interpret patterns in infrastructure anomalies and identify the main issues.

Response format must be valid JSON:
{{
    "main_pattern": "Brief description of the primary pattern",
    "probable_cause": "Most likely root cause",
    "priority_metric": "Which metric needs immediate attention",
    "metrics_to_watch": ["metric1", "metric2", "metric3"],
    "pattern_type": "recurring|escalating|sporadic|stable"
}}"""),
            ("human", """Historical Anomaly Patterns:

FREQUENCY ANALYSIS:
{frequency}

TEMPORAL PATTERNS:
{temporal}

CO-OCCURRENCE ANALYSIS:
{cooccurrence}

Analyze these patterns and provide insights in JSON format. For metrics_to_watch, include 2-3 metrics that need close monitoring based on frequency, severity, or correlation patterns.""")
        ])
        
        # Chain 2: Severity Assessment
        self.severity_assessment_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert SRE. Assess the severity and urgency of infrastructure issues based on patterns and current state.

Response format must be valid JSON:
{{
    "criticality": 1-5,
    "urgency": "immediate|24h|week|monitoring",
    "business_impact": "users|performance|costs|availability",
    "escalation_risk": "low|medium|high"
}}"""),
            ("human", """HISTORICAL PATTERNS:
{patterns}

CURRENT STATE:
{current_state}

Evaluate the severity and urgency of this situation.""")
        ])
        
        self.historical_recommendations_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert infrastructure architect. Provide strategic recommendations based on historical patterns and current analysis.

Response format must be valid JSON:
{{
    "analysis_summary": "Brief overview incorporating historical context",
    "root_cause_analysis": "Detailed analysis with historical patterns",
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
}}"""),
            ("human", """PATTERN INTERPRETATION:
{pattern_interpretation}

SEVERITY ASSESSMENT:
{severity_assessment}

CURRENT METRICS:
{current_metrics}

HISTORICAL CONTEXT:
{historical_context}

ANOMALY BREAKDOWN:
{anomaly_breakdown}

Provide comprehensive recommendations based on this analysis. Pay special attention to the priority metric and metrics to watch when formulating strategic actions. Use the detailed anomaly breakdown to understand which specific metrics are most problematic.""")
        ])
        
        self.pattern_chain = self.pattern_interpretation_prompt | self.llm | self.output_parser
        self.severity_chain = self.severity_assessment_prompt | self.llm | self.output_parser
        self.recommendations_chain = self.historical_recommendations_prompt | self.llm | self.output_parser
        
        self.parallel_chains = RunnableParallel(
            pattern_interpretation=self.pattern_chain,
            severity_assessment=self.severity_chain
        )

    @traceable(name="analyze_historical_patterns")
    def analyze_historical_patterns(
        self, 
        patterns: Dict[str, Any], 
        current_metrics: Dict[str, Any]
    ) -> AnalysisResult:
        start_time = time.time()
        
        try:
            logger.info(f"Starting historical pattern analysis for {patterns['total_points']} points")
            
            parallel_input = {
                "frequency": self._format_frequency_analysis(patterns["frequency"]),
                "temporal": self._format_temporal_analysis(patterns["temporal"]),
                "cooccurrence": self._format_cooccurrence_analysis(patterns["cooccurrence"]),
                "patterns": self._format_patterns_summary(patterns),
                "current_state": self._format_metrics(current_metrics)
            }
            
            parallel_results = self.parallel_chains.invoke(parallel_input)
            
            final_input = {
                "pattern_interpretation": json.dumps(parallel_results["pattern_interpretation"]),
                "severity_assessment": json.dumps(parallel_results["severity_assessment"]),
                "current_metrics": self._format_metrics(current_metrics),
                "historical_context": self._format_historical_context(patterns),
                "anomaly_breakdown": self._format_anomaly_breakdown(patterns.get("breakdown", {}))
            }
            
            final_result = self.recommendations_chain.invoke(final_input)
            
            analysis_result = self._parse_historical_response(final_result)
            
            response_time = time.time() - start_time
            analysis_result.analysis_metadata = {
                "response_time": response_time,
                "analysis_type": "historical",
                "total_points": patterns["total_points"],
                "pattern_interpretation": parallel_results["pattern_interpretation"],
                "severity_assessment": parallel_results["severity_assessment"],
                "anomaly_breakdown": patterns.get("breakdown", {}),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Historical analysis completed in {response_time:.2f}s with confidence {analysis_result.confidence_score}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in historical analysis: {str(e)}")
            return self._create_fallback_analysis_historical(patterns, str(e))

    def analyze_historical_data(
        self,
        historical_metrics: List[Dict[str, Any]],
        anomaly_service
    ) -> AnalysisResult:
        if len(historical_metrics) < 10:
            raise ValueError(f"Insufficient historical data. Need at least 10 points, found {len(historical_metrics)}")
        
        analyzed_timeline = anomaly_service.analyze_historical_anomalies(historical_metrics)
        patterns = anomaly_service.analyze_anomaly_patterns(analyzed_timeline)
        current_metrics = historical_metrics[-1] if historical_metrics else {}
        
        return self.analyze_historical_patterns(patterns, current_metrics)

    def _format_frequency_analysis(self, frequency: Dict[str, Any]) -> str:
        """Format frequency analysis for LLM"""
        if not frequency.get("counts"):
            return "No anomalies detected in historical data"
        
        formatted = ["Anomaly frequency analysis:"]
        
        for metric, count in frequency["counts"].items():
            severity_avg = frequency["severity_avg"].get(metric, 0)
            formatted.append(f"- {metric}: {count} anomalies (avg severity: {severity_avg:.1f})")
        
        if frequency.get("most_frequent"):
            metric, count = frequency["most_frequent"]
            formatted.append(f"\nMost problematic metric: {metric} ({count} anomalies)")
        
        return "\n".join(formatted)

    def _format_temporal_analysis(self, temporal: Dict[str, Any]) -> str:
        """Format temporal analysis for LLM"""
        if not temporal.get("hourly_distribution"):
            return "No temporal patterns detected"
        
        formatted = ["Temporal pattern analysis:"]
        
        if temporal.get("problematic_hours"):
            hours = ", ".join(map(str, temporal["problematic_hours"]))
            formatted.append(f"- Problematic hours: {hours}")
        
        if temporal.get("peak_hour"):
            hour, avg_anomalies = temporal["peak_hour"]
            formatted.append(f"- Peak anomaly hour: {hour}h ({avg_anomalies:.1f} avg anomalies)")
        
        formatted.append("\nHourly anomaly distribution:")
        for hour in sorted(temporal["hourly_distribution"].keys()):
            avg = temporal["hourly_distribution"][hour]
            formatted.append(f"- {hour}h: {avg:.1f} avg anomalies")
        
        return "\n".join(formatted)

    def _format_cooccurrence_analysis(self, cooccurrence: Dict[str, Any]) -> str:
        """Format co-occurrence analysis for LLM"""
        if not cooccurrence.get("pairs"):
            return "No metric correlations detected"
        
        formatted = ["Metric co-occurrence analysis:"]
        
        if cooccurrence.get("most_common"):
            formatted.append("Most common anomaly pairs:")
            for i, (pair, count) in enumerate(cooccurrence["most_common"][:3], 1):
                metric1, metric2 = pair
                formatted.append(f"{i}. {metric1} + {metric2}: {count} times")
        
        formatted.append(f"\nTotal correlation pairs detected: {cooccurrence['total_pairs']}")
        
        return "\n".join(formatted)

    def _format_patterns_summary(self, patterns: Dict[str, Any]) -> str:
        """Format patterns summary for severity assessment"""
        summary = [f"Analysis of {patterns['total_points']} historical points:"]
        
        frequency = patterns["frequency"]
        if frequency.get("counts"):
            total_anomalies = sum(frequency["counts"].values())
            summary.append(f"- Total anomalies: {total_anomalies}")
            
            if frequency.get("most_frequent"):
                metric, count = frequency["most_frequent"]
                percentage = (count / patterns["total_points"]) * 100
                summary.append(f"- Most frequent issue: {metric} ({percentage:.1f}% of time)")
        
        temporal = patterns["temporal"]
        if temporal.get("problematic_hours"):
            hours = len(temporal["problematic_hours"])
            summary.append(f"- Problematic time periods: {hours} hours identified")
        
        cooccurrence = patterns["cooccurrence"]
        if cooccurrence.get("total_pairs"):
            summary.append(f"- Metric correlations: {cooccurrence['total_pairs']} pairs detected")
        
        return "\n".join(summary)

    def _format_historical_context(self, patterns: Dict[str, Any]) -> str:
        """Format historical context for final recommendations"""
        context = [f"Historical analysis context ({patterns['total_points']} data points):"]
        
        # Add key insights
        frequency = patterns["frequency"]
        if frequency.get("most_frequent"):
            metric, count = frequency["most_frequent"]
            context.append(f"- Primary concern: {metric} (anomalous {count} times)")
        
        temporal = patterns["temporal"]
        if temporal.get("peak_hour"):
            hour, avg = temporal["peak_hour"]
            context.append(f"- Peak issue time: {hour}h ({avg:.1f} avg anomalies)")
        
        cooccurrence = patterns["cooccurrence"]
        if cooccurrence.get("most_common"):
            pair, count = cooccurrence["most_common"][0]
            context.append(f"- Strongest correlation: {pair[0]} + {pair[1]} ({count} times)")
        
        return "\n".join(context)

    def _format_anomaly_breakdown(self, breakdown: Dict[str, Any]) -> str:
        """Format anomaly breakdown for historical recommendations"""
        if not breakdown:
            return "No specific anomaly breakdown available"
        
        formatted = ["Anomaly Breakdown:"]
        for metric, data in breakdown.items():
            warnings = data.get("warnings", 0)
            critical = data.get("critical", 0)
            total = data.get("total", 0)
            formatted.append(f"- {metric}: {total} anomalies ({warnings} warnings, {critical} critical)")
        
        return "\n".join(formatted)

    def _parse_historical_response(self, response: Dict[str, Any]) -> AnalysisResult:
        """Parse LLM response from historical analysis"""
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
            logger.error(f"Error parsing historical LLM response: {str(e)}")
            raise ValueError(f"Invalid historical LLM response format: {str(e)}")

    def _create_fallback_analysis_historical(self, patterns: Dict[str, Any], error_msg: str) -> AnalysisResult:
        """Create fallback analysis for historical analysis errors"""
        return AnalysisResult(
            analysis_summary=f"Historical analysis failed: {error_msg}",
            root_cause_analysis="Unable to perform detailed historical analysis due to technical error",
            recommendations=[
                Recommendation(
                    priority=1,
                    category=RecommendationCategory.IMMEDIATE,
                    action="Check system logs and investigate technical issues",
                    impact="Restore historical monitoring capabilities",
                    effort="medium"
                )
            ],
            confidence_score=0.0,
            analysis_metadata={"error": error_msg, "analysis_type": "historical"}
        )

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
}}

IMPORTANT: Use ONLY these exact category values: "immediate", "short_term", "monitoring", "optimization"."""

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
                "analysis_type": "simple",
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
            analysis_metadata={"error": error_msg, "analysis_type": "simple"}
        )

    def get_analysis_metrics(self) -> Dict[str, Any]:
        """Get LLM usage metrics - placeholder for now"""
        return {
            "total_analyses": 0,
            "average_response_time": 0.0,
            "total_cost_estimate": 0.0,
            "last_analysis": None
        } 