from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum


class RecommendationCategory(str, Enum):
    IMMEDIATE = "immediate"
    SHORT_TERM = "short_term"
    MONITORING = "monitoring"
    OPTIMIZATION = "optimization"


class Recommendation(BaseModel):
    priority: int = Field(..., ge=1, le=5, description="Priority level (1=highest, 5=lowest)")
    category: RecommendationCategory = Field(..., description="Recommendation category")
    action: str = Field(..., description="Specific action to take")
    impact: str = Field(..., description="Expected impact of the action")
    effort: str = Field(..., description="Effort required (low/medium/high)")
    technical_details: Optional[str] = Field(None, description="Technical implementation details")


class AnalysisResult(BaseModel):
    analysis_summary: str = Field(..., description="High-level summary of the analysis")
    root_cause_analysis: str = Field(..., description="Root cause analysis of detected issues")
    recommendations: List[Recommendation] = Field(default=[], description="List of recommendations")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in the analysis")
    analysis_metadata: Dict[str, Any] = Field(default={}, description="Analysis metadata")


class HistoricalAnalysisMetadata(BaseModel):
    response_time: float
    analysis_type: str
    total_points: int
    pattern_interpretation: Dict[str, Any]
    severity_assessment: Dict[str, Any]
    timestamp: str


class HistoricalAnalysisResult(AnalysisResult):
    analysis_metadata: HistoricalAnalysisMetadata


class LLMAnalysisMetrics(BaseModel):
    total_tokens: int = Field(..., description="Total tokens used")
    prompt_tokens: int = Field(..., description="Tokens used in prompt")
    completion_tokens: int = Field(..., description="Tokens used in completion")
    cost_estimate: float = Field(..., description="Estimated cost in USD")
    response_time: float = Field(..., description="Response time in seconds")
    model_used: str = Field(..., description="LLM model used")
    timestamp: str = Field(..., description="Analysis timestamp") 