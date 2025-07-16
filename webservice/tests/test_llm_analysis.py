import pytest
from unittest.mock import Mock, patch, MagicMock
from services.llm_analysis import LLMAnalysisService
from models.analysis import AnalysisResult, Recommendation, RecommendationCategory
from models.anomaly import AnomalyResult, Anomaly, AnomalyType


@pytest.fixture
def mock_env_vars():
    with patch.dict("os.environ", {
        "OPENAI_API_KEY": "test-openai-key",
        "LANGSMITH_API_KEY": "test-langsmith-key"
    }):
        yield


@pytest.fixture
def mock_llm_response():
    return {
        "analysis_summary": "System shows high CPU and memory usage",
        "root_cause_analysis": "High CPU usage is causing memory pressure and increased latency",
        "recommendations": [
            {
                "priority": 1,
                "category": "immediate",
                "action": "Scale up CPU resources",
                "impact": "Reduce CPU usage by 30%",
                "effort": "low",
                "technical_details": "Add 2 more CPU cores"
            },
            {
                "priority": 2,
                "category": "monitoring",
                "action": "Set up CPU usage alerts",
                "impact": "Early warning system",
                "effort": "medium"
            }
        ],
        "confidence_score": 0.85
    }


@pytest.fixture
def sample_anomaly_result():
    return AnomalyResult(
        has_anomalies=True,
        anomalies=[
            Anomaly(
                metric="cpu_usage",
                value=95,
                threshold=90,
                severity=5,
                type=AnomalyType.PERFORMANCE,
                message="CPU usage is critically high"
            ),
            Anomaly(
                metric="memory_usage",
                value=88,
                threshold=85,
                severity=5,
                type=AnomalyType.PERFORMANCE,
                message="Memory usage is critically high"
            )
        ],
        summary="2 anomalies detected (2 critical, 0 warning)",
        total_count=2
    )


@pytest.fixture
def sample_metrics():
    return {
        "timestamp": "2023-10-01T12:00:00Z",
        "cpu_usage": 95,
        "memory_usage": 88,
        "latency_ms": 300,
        "disk_usage": 70,
        "network_in_kbps": 1000,
        "network_out_kbps": 800,
        "service_status": {
            "database": "online",
            "api_gateway": "degraded",
            "cache": "online"
        }
    }


@pytest.fixture
def sample_history():
    return {
        "network_in_kbps": {
            "count": 3,
            "values": [900, 950, 1000],
            "average": 950.0
        },
        "network_out_kbps": {
            "count": 3,
            "values": [750, 775, 800],
            "average": 775.0
        },
        "thread_count": {
            "count": 0,
            "values": [],
            "average": None
        }
    }


@patch('webservice.services.llm_analysis.load_dotenv')
@patch('webservice.services.llm_analysis.ChatOpenAI')
@patch('webservice.services.llm_analysis.Client')
def test_llm_service_initialization(mock_client, mock_chat_openai, mock_load_dotenv, mock_env_vars):
    service = LLMAnalysisService()
    
    assert service.openai_api_key == "test-openai-key"
    assert service.langsmith_api_key == "test-langsmith-key"
    mock_chat_openai.assert_called_once()
    mock_client.assert_called_once()


@patch('webservice.services.llm_analysis.load_dotenv')
def test_llm_service_missing_openai_key(mock_load_dotenv):
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="OPENAI_API_KEY not found"):
            LLMAnalysisService()


@patch('webservice.services.llm_analysis.load_dotenv')
@patch('webservice.services.llm_analysis.ChatOpenAI')
@patch('webservice.services.llm_analysis.Client')
def test_format_metrics(mock_client, mock_chat_openai, mock_load_dotenv, mock_env_vars, sample_metrics):
    service = LLMAnalysisService()
    
    formatted = service._format_metrics(sample_metrics)
    
    assert "cpu_usage: 95" in formatted
    assert "memory_usage: 88" in formatted
    assert "service_status: database:online, api_gateway:degraded, cache:online" in formatted


@patch('webservice.services.llm_analysis.load_dotenv')
@patch('webservice.services.llm_analysis.ChatOpenAI')
@patch('webservice.services.llm_analysis.Client')
def test_format_anomalies(mock_client, mock_chat_openai, mock_load_dotenv, mock_env_vars, sample_anomaly_result):
    service = LLMAnalysisService()
    
    formatted = service._format_anomalies(sample_anomaly_result)
    
    assert "2 anomalies detected" in formatted
    assert "cpu_usage: 95" in formatted
    assert "severity: 5" in formatted
    assert "CPU usage is critically high" in formatted


@patch('webservice.services.llm_analysis.load_dotenv')
@patch('webservice.services.llm_analysis.ChatOpenAI')
@patch('webservice.services.llm_analysis.Client')
def test_format_history(mock_client, mock_chat_openai, mock_load_dotenv, mock_env_vars, sample_history):
    service = LLMAnalysisService()
    
    formatted = service._format_history(sample_history)
    
    assert "Historical data" in formatted
    assert "network_in_kbps: avg=950.0" in formatted
    assert "network_out_kbps: avg=775.0" in formatted


@patch('webservice.services.llm_analysis.load_dotenv')
@patch('webservice.services.llm_analysis.ChatOpenAI')
@patch('webservice.services.llm_analysis.Client')
def test_parse_llm_response(mock_client, mock_chat_openai, mock_load_dotenv, mock_env_vars, mock_llm_response):
    service = LLMAnalysisService()
    
    result = service._parse_llm_response(mock_llm_response)
    
    assert isinstance(result, AnalysisResult)
    assert result.analysis_summary == "System shows high CPU and memory usage"
    assert result.confidence_score == 0.85
    assert len(result.recommendations) == 2
    
    rec1 = result.recommendations[0]
    assert rec1.priority == 1
    assert rec1.category == RecommendationCategory.IMMEDIATE
    assert rec1.action == "Scale up CPU resources"


@patch('webservice.services.llm_analysis.load_dotenv')
@patch('webservice.services.llm_analysis.ChatOpenAI')
@patch('webservice.services.llm_analysis.Client')
def test_create_fallback_analysis(mock_client, mock_chat_openai, mock_load_dotenv, mock_env_vars, sample_anomaly_result):
    service = LLMAnalysisService()
    
    result = service._create_fallback_analysis(sample_anomaly_result, "Test error")
    
    assert isinstance(result, AnalysisResult)
    assert "Analysis failed: Test error" in result.analysis_summary
    assert result.confidence_score == 0.0
    assert len(result.recommendations) == 1
    assert result.recommendations[0].category == RecommendationCategory.IMMEDIATE


@patch('webservice.services.llm_analysis.load_dotenv')
@patch('webservice.services.llm_analysis.ChatOpenAI')
@patch('webservice.services.llm_analysis.Client')
def test_analyze_anomalies_success(mock_client, mock_chat_openai, mock_load_dotenv, mock_env_vars, 
                                  sample_anomaly_result, sample_metrics, sample_history, mock_llm_response):
    # Mock the chain response
    mock_chain = Mock()
    mock_chain.invoke.return_value = mock_llm_response
    
    service = LLMAnalysisService()
    service.chain = mock_chain
    
    result = service.analyze_anomalies(sample_anomaly_result, sample_metrics, sample_history)
    
    assert isinstance(result, AnalysisResult)
    assert result.confidence_score == 0.85
    assert len(result.recommendations) == 2
    assert "response_time" in result.analysis_metadata
    assert "anomaly_count" in result.analysis_metadata


@patch('webservice.services.llm_analysis.load_dotenv')
@patch('webservice.services.llm_analysis.ChatOpenAI')
@patch('webservice.services.llm_analysis.Client')
def test_analyze_anomalies_error_handling(mock_client, mock_chat_openai, mock_load_dotenv, mock_env_vars,
                                         sample_anomaly_result, sample_metrics, sample_history):
    # Mock the chain to raise an exception
    mock_chain = Mock()
    mock_chain.invoke.side_effect = Exception("LLM API error")
    
    service = LLMAnalysisService()
    service.chain = mock_chain
    
    result = service.analyze_anomalies(sample_anomaly_result, sample_metrics, sample_history)
    
    assert isinstance(result, AnalysisResult)
    assert result.confidence_score == 0.0
    assert "Analysis failed" in result.analysis_summary
    assert "error" in result.analysis_metadata 