# Historical Analysis Chain Documentation

## Overview

The Historical Analysis Chain is an advanced infrastructure monitoring system that analyzes patterns in historical anomaly data to provide strategic insights and recommendations. This system extends the basic anomaly detection with temporal pattern recognition and LLM-powered analysis.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Historical Analysis Chain                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐     │
│  │   Anomaly        │    │   Pattern        │    │   LLM Analysis   │     │
│  │   Detection      │───▶│   Analysis       │───▶│   Service        │     │
│  │   Service        │    │   Service        │    │   (Historical)   │     │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Historical Metrics (50+ points)
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Phase 1: Anomaly Detection                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  For each historical point:                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│  │   Metrics       │───▶│   Anomaly       │───▶│   Anomaly       │        │
│  │   Point         │    │   Detection     │    │   Results       │        │
│  │   (JSON)        │    │   (Thresholds)  │    │   (Structured)  │        │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Phase 2: Pattern Analysis                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│  │   Frequency     │    │   Temporal      │    │   Co-occurrence │        │
│  │   Analysis      │    │   Analysis      │    │   Analysis      │        │
│  │                 │    │                 │    │                 │        │
│  │ • Count/metric  │    │ • Hourly dist.  │    │ • Metric pairs  │        │
│  │ • Severity avg  │    │ • Peak hours    │    │ • Correlation   │        │
│  │ • Most frequent │    │ • Problem times │    │ • Frequency     │        │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Phase 3: LLM Analysis (Parallel)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐              ┌─────────────────┐                      │
│  │   Pattern       │              │   Severity      │                      │
│  │   Interpretation│              │   Assessment    │                      │
│  │                 │              │                 │                      │
│  │ • Main pattern  │              │ • Criticality   │                      │
│  │ • Root cause    │              │ • Urgency       │                      │
│  │ • Priority      │              │ • Business      │                      │
│  │ • Pattern type  │              │ • Escalation    │                      │
│  └─────────────────┘              └─────────────────┘                      │
│           │                                │                               │
│           └────────────────┬───────────────┘                               │
│                            ▼                                               │
│                   ┌─────────────────┐                                      │
│                   │   Final         │                                      │
│                   │   Recommendations│                                      │
│                   │                 │                                      │
│                   │ • Strategic     │                                      │
│                   │ • Tactical      │                                      │
│                   │ • Monitoring    │                                      │
│                   │ • Optimization  │                                      │
│                   └─────────────────┘                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Implementation Details

### 1. Anomaly Detection Service Extension

**File**: `webservice/services/anomaly_detection.py`

#### New Methods

##### `analyze_historical_anomalies(metrics_list: List[Dict[str, Any]])`
- **Purpose**: Apply anomaly detection to a list of historical metrics
- **Input**: List of metric dictionaries with timestamps
- **Output**: Analyzed timeline with anomaly results for each point
- **Process**:
  ```python
  for metrics in metrics_list:
      anomaly_result = self.detect_anomalies(metrics)
      analyzed_timeline.append({
          "timestamp": metrics.get("timestamp"),
          "anomalies": [anomaly.model_dump() for anomaly in anomaly_result.anomalies],
          "has_issues": anomaly_result.has_anomalies,
          "total_count": anomaly_result.total_count
      })
  ```

##### `analyze_anomaly_patterns(analyzed_timeline: List[Dict[str, Any]])`
- **Purpose**: Extract patterns from historical anomaly data
- **Input**: Timeline of anomaly results
- **Output**: Structured patterns (frequency, temporal, co-occurrence)
- **Components**:
  - `_analyze_frequency()`: Count anomalies per metric, calculate severity averages
  - `_analyze_temporal_patterns()`: Identify problematic hours and peak times
  - `_analyze_cooccurrence()`: Find metrics that alert together

### 2. Pattern Analysis Algorithms

#### Frequency Analysis
```python
def _analyze_frequency(self, analyzed_timeline):
    frequency = {}
    severity_distribution = defaultdict(list)
    
    for point in analyzed_timeline:
        for anomaly in point["anomalies"]:
            metric = anomaly["metric"]
            severity = anomaly["severity"]
            
            frequency[metric] = frequency.get(metric, 0) + 1
            severity_distribution[metric].append(severity)
    
    return {
        "counts": frequency,
        "severity_avg": {k: sum(v)/len(v) for k, v in severity_distribution.items()},
        "most_frequent": max(frequency.items(), key=lambda x: x[1]) if frequency else None
    }
```

#### Temporal Analysis
```python
def _analyze_temporal_patterns(self, analyzed_timeline):
    hourly_anomalies = defaultdict(list)
    
    for point in analyzed_timeline:
        if point["timestamp"]:
            dt = datetime.fromisoformat(point["timestamp"].replace('Z', '+00:00'))
            hour = dt.hour
            anomaly_count = point["total_count"]
            hourly_anomalies[hour].append(anomaly_count)
    
    # Calculate averages and identify problematic hours
    hourly_avg = {hour: sum(counts)/len(counts) for hour, counts in hourly_anomalies.items()}
    overall_avg = sum(hourly_avg.values()) / len(hourly_avg) if hourly_avg else 0
    problematic_hours = [hour for hour, avg in hourly_avg.items() if avg > overall_avg * 1.5]
    
    return {
        "hourly_distribution": hourly_avg,
        "problematic_hours": sorted(problematic_hours),
        "peak_hour": max(hourly_avg.items(), key=lambda x: x[1]) if hourly_avg else None
    }
```

#### Co-occurrence Analysis
```python
def _analyze_cooccurrence(self, analyzed_timeline):
    cooccurrences = defaultdict(int)
    
    for point in analyzed_timeline:
        metrics_in_alert = [anomaly["metric"] for anomaly in point["anomalies"]]
        
        # Count pairwise co-occurrences
        for i, metric1 in enumerate(metrics_in_alert):
            for metric2 in metrics_in_alert[i+1:]:
                pair = tuple(sorted([metric1, metric2]))
                cooccurrences[pair] += 1
    
    sorted_cooccurrences = sorted(cooccurrences.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "pairs": dict(cooccurrences),
        "most_common": sorted_cooccurrences[:5],
        "total_pairs": len(cooccurrences)
    }
```

### 3. LLM Analysis Service Extension

**File**: `webservice/services/llm_analysis.py`

#### LangChain Architecture

The system uses three specialized LangChain chains:

##### Chain 1: Pattern Interpretation
- **Purpose**: Analyze historical patterns and identify main issues
- **Input**: Frequency, temporal, and co-occurrence data
- **Output**: JSON with main pattern, probable cause, priority metric, pattern type
- **Prompt**: Expert infrastructure monitoring analyst persona

##### Chain 2: Severity Assessment
- **Purpose**: Evaluate criticality and urgency
- **Input**: Pattern summary and current system state
- **Output**: JSON with criticality (1-5), urgency, business impact, escalation risk
- **Prompt**: Expert SRE persona

##### Chain 3: Final Recommendations
- **Purpose**: Generate strategic recommendations
- **Input**: Pattern interpretation + severity assessment + current metrics
- **Output**: Complete analysis with summary, root cause, and recommendations
- **Prompt**: Expert infrastructure architect persona

#### Parallel Execution
```python
# Chains 1 & 2 run in parallel
self.parallel_chains = RunnableParallel(
    pattern_interpretation=self.pattern_chain,
    severity_assessment=self.severity_chain
)

# Chain 3 runs sequentially after 1 & 2
parallel_results = self.parallel_chains.invoke(parallel_input)
final_result = self.recommendations_chain.invoke(final_input)
```

### 4. Data Formatting for LLM

#### Frequency Analysis Formatting
```python
def _format_frequency_analysis(self, frequency):
    formatted = ["Anomaly frequency analysis:"]
    
    for metric, count in frequency["counts"].items():
        severity_avg = frequency["severity_avg"].get(metric, 0)
        formatted.append(f"- {metric}: {count} anomalies (avg severity: {severity_avg:.1f})")
    
    if frequency.get("most_frequent"):
        metric, count = frequency["most_frequent"]
        formatted.append(f"\nMost problematic metric: {metric} ({count} anomalies)")
    
    return "\n".join(formatted)
```

#### Temporal Analysis Formatting
```python
def _format_temporal_analysis(self, temporal):
    formatted = ["Temporal pattern analysis:"]
    
    if temporal.get("problematic_hours"):
        hours = ", ".join(map(str, temporal["problematic_hours"]))
        formatted.append(f"- Problematic hours: {hours}")
    
    if temporal.get("peak_hour"):
        hour, avg_anomalies = temporal["peak_hour"]
        formatted.append(f"- Peak anomaly hour: {hour}h ({avg_anomalies:.1f} avg anomalies)")
    
    # Show hourly distribution
    formatted.append("\nHourly anomaly distribution:")
    for hour in sorted(temporal["hourly_distribution"].keys()):
        avg = temporal["hourly_distribution"][hour]
        formatted.append(f"- {hour}h: {avg:.1f} avg anomalies")
    
    return "\n".join(formatted)
```

## API Integration

### New Endpoint: `/api/analysis/historical`

**Method**: GET
**Parameters**: 
- `points` (optional): Number of historical points to analyze (default: 50)

**Workflow**:
1. Retrieve last N metrics from database
2. Apply anomaly detection to each point
3. Analyze patterns in the anomaly data
4. Run LLM analysis with historical context
5. Return comprehensive analysis result

**Response Structure**:
```json
{
    "analysis_summary": "Historical analysis shows...",
    "root_cause_analysis": "Pattern analysis reveals...",
    "recommendations": [
        {
            "priority": 1,
            "category": "immediate",
            "action": "Scale resources during peak hours",
            "impact": "Reduce incidents by 70%",
            "effort": "medium",
            "technical_details": "Configure auto-scaling for 17h-19h"
        }
    ],
    "confidence_score": 0.85,
    "analysis_metadata": {
        "analysis_type": "historical",
        "total_points": 50,
        "response_time": 3.2,
        "pattern_interpretation": {...},
        "severity_assessment": {...}
    }
}
```

## Performance Considerations

### Parallel Processing
- Pattern interpretation and severity assessment run in parallel
- Reduces total analysis time
- LangChain RunnableParallel manages concurrent execution

### Caching Strategy
- Historical data is fetched once per analysis
- Pattern analysis results could be cached for similar datasets
- LLM responses cached by LangSmith for identical inputs

### Scalability
- Analysis complexity scales linearly with number of points
- Recommended maximum: 200 points (performance vs accuracy trade-off)
- Database queries optimized with proper indexing

## Error Handling

### Graceful Degradation
1. **Database Errors**: Return fallback analysis with error details
2. **LLM API Errors**: Provide basic pattern analysis without AI insights
3. **Pattern Analysis Errors**: Return simple anomaly counts
4. **Parsing Errors**: Use fallback response structure

### Monitoring
- LangSmith integration for LLM call tracing
- Comprehensive logging at DEBUG level
- Performance metrics collection
- Error rate monitoring

## Testing Strategy

### Unit Tests
- Pattern analysis algorithms
- Data formatting functions
- Error handling scenarios
- Edge cases (empty data, single points)

### Integration Tests
- End-to-end analysis workflow
- Database integration
- LLM chain execution
- API endpoint functionality

### Performance Tests
- Analysis time with varying point counts
- Memory usage with large datasets
- Concurrent analysis requests

## Usage Examples

### Simple Historical Analysis
```python
# Analyze last 50 points
patterns = anomaly_service.analyze_anomaly_patterns(analyzed_timeline)
result = llm_service.analyze_historical_patterns(patterns, current_metrics)
```

### Custom Point Count
```python
# Analyze last 100 points for deeper insights
metrics_list = get_last_n_metrics(100)
analyzed_timeline = anomaly_service.analyze_historical_anomalies(metrics_list)
patterns = anomaly_service.analyze_anomaly_patterns(analyzed_timeline)
result = llm_service.analyze_historical_patterns(patterns, current_metrics)
```

### API Usage
```bash
# Get historical analysis
curl "http://localhost:8000/api/analysis/historical?points=75"
```

## Future Enhancements

### Planned Features
1. **Machine Learning Integration**: Pattern recognition with ML models
2. **Seasonal Analysis**: Weekly/monthly pattern detection
3. **Predictive Alerting**: Forecast potential issues
4. **Custom Thresholds**: User-defined anomaly detection rules
5. **Multi-tenant Support**: Isolated analysis per customer

### Optimization Opportunities
1. **Streaming Analysis**: Real-time pattern updates
2. **Distributed Processing**: Parallel analysis across multiple workers
3. **Advanced Caching**: Redis-based pattern cache
4. **Batch Processing**: Scheduled historical analysis jobs

---

*This documentation covers the complete historical analysis chain implementation as of Phase 2 completion.* 