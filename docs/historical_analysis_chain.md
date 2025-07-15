# Historical Analysis Chain

## Overview

Advanced infrastructure monitoring that analyzes historical anomaly patterns to provide strategic insights and recommendations.

## Workflow

```
Historical Metrics (50+ points)
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Phase 1: Anomaly Detection                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  For each historical point:                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│  │   Metrics       │───▶│   Anomaly       │───▶│   Anomaly       │        │
│  │   Point         │    │   Detection     │    │   Results       │        │
│  │   (JSON)        │    │   (Thresholds)  │    │   (Structured)  │        │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Phase 2: Pattern Analysis                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│  │   Frequency     │    │   Temporal      │    │   Co-occurrence │        │
│  │   Analysis      │    │   Analysis      │    │   Analysis      │        │
│  │                 │    │                 │    │                 │        │
│  │ • Count/metric  │    │ • Hourly dist.  │    │ • Metric pairs  │        │
│  │ • Severity avg  │    │ • Peak hours    │    │ • Correlation   │        │
│  │ • Most frequent │    │ • Problem times │    │ • Frequency     │        │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Phase 3: LLM Analysis (Parallel)                        │
├─────────────────────────────────────────────────────────────────────────────┤
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
└─────────────────────────────────────────────────────────────────────────────┘
```

## Functionality

### Phase 1: Anomaly Detection
- **Input**: List of historical metrics (50-200 points)
- **Process**: Apply existing anomaly detection to each point
- **Output**: Timeline with anomaly results per point

### Phase 2: Pattern Analysis
- **Frequency**: Count anomalies per metric, identify most problematic
- **Temporal**: Find problematic hours, peak times, hourly distribution
- **Co-occurrence**: Detect metrics that alert together

### Phase 3: LLM Analysis
- **Parallel Execution**: Pattern interpretation + Severity assessment run simultaneously
- **Sequential**: Final recommendations use both parallel results
- **Output**: Strategic recommendations with historical context

## Output Format

### API Response
```json
{
  "analysis_summary": "Recurring pattern of high error rates during peak hours",
  "root_cause_analysis": "Database service resource constraints",
  "recommendations": [
    {
      "priority": 1,
      "category": "immediate",
      "action": "Scale up database resources",
      "impact": "Reduce error rates",
      "effort": "medium"
    }
  ],
  "confidence_score": 0.85,
  "analysis_metadata": {
    "response_time": 13.7,
    "analysis_type": "historical",
    "total_points": 20,
    "pattern_interpretation": {
      "main_pattern": "High frequency of error_rate anomalies",
      "pattern_type": "recurring",
      "probable_cause": "Database service issues",
      "priority_metric": "error_rate"
    },
    "severity_assessment": {
      "criticality": 4,
      "urgency": "immediate",
      "business_impact": "availability",
      "escalation_risk": "high"
    }
  }
}
```

## Example

### Input: 20 historical metrics points
- Error rates: 0.02-0.05 (threshold: 0.02)
- CPU usage: 45-75%
- Database service: online/offline patterns

### Pattern Detection
- **Frequency**: Error rate anomalous 15/20 times
- **Temporal**: Peak issues at 12h and 17h
- **Co-occurrence**: Error rate + database status correlation

### LLM Analysis
- **Pattern**: Recurring database performance issues
- **Severity**: Critical (4/5), immediate action required
- **Recommendations**: Scale database, optimize queries, implement monitoring

### Frontend Display
- Toggle: Latest Point vs Historical Analysis
- Slider: 10-200 points selection
- Results: Pattern insights, severity metrics, actionable recommendations 