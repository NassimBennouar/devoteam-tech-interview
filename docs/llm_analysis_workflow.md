# LLM Analysis Workflow

## Overview

Advanced analysis using LangChain with parallel and sequential execution patterns for infrastructure monitoring insights.

## Chain Architecture

### Simple Analysis Chain
Single chain for latest point analysis:
```
Prompt Template → LLM → JSON Parser → Analysis Result
```

### Historical Analysis Chains
Three specialized chains with parallel execution:

#### Chain 1: Pattern Interpretation
- **Input**: Frequency, temporal, co-occurrence data
- **Output**: Main pattern, probable cause, priority metric, pattern type
- **Purpose**: Identify primary issues from historical data

#### Chain 2: Severity Assessment  
- **Input**: Historical patterns and current state
- **Output**: Criticality (1-5), urgency, business impact, escalation risk
- **Purpose**: Evaluate severity and urgency of issues

#### Chain 3: Final Recommendations
- **Input**: Pattern interpretation + severity assessment + current metrics
- **Output**: Strategic recommendations with confidence score
- **Purpose**: Generate actionable recommendations

## Execution Flow

### Parallel Execution
```
Pattern Interpretation ─┐
                       ├─→ Final Recommendations
Severity Assessment ────┘
```

### Sequential Steps
1. **Historical Data Processing**: Anomaly detection on each point
2. **Pattern Analysis**: Frequency, temporal, co-occurrence extraction
3. **Parallel LLM Calls**: Pattern + severity assessment simultaneously
4. **Sequential LLM Call**: Final recommendations using parallel results
5. **Response Assembly**: Combine all results with metadata

## Prompt Structure

### Pattern Interpretation Prompt
- **System**: Expert infrastructure analyst role
- **Human**: Historical anomaly patterns (frequency, temporal, co-occurrence)
- **Output**: JSON with main pattern, cause, priority, type

### Severity Assessment Prompt
- **System**: Expert SRE role
- **Human**: Historical patterns + current state
- **Output**: JSON with criticality, urgency, impact, escalation risk

### Recommendations Prompt
- **System**: Expert infrastructure architect role
- **Human**: Pattern interpretation + severity + current metrics + historical context
- **Output**: JSON with analysis summary, root cause, recommendations, confidence

## Model Configuration

### LLM Settings
- **Model**: GPT-4o-mini
- **Temperature**: 0.1 (low creativity, high consistency)
- **API Key**: Required environment variable
- **Tracing**: LangSmith integration when available

### Output Parsing
- **Format**: JSON output parser
- **Validation**: Pydantic model validation
- **Fallback**: Error handling with default responses

## Performance Metrics

### Response Times
- **Simple Analysis**: ~2-5 seconds
- **Historical Analysis**: ~10-15 seconds
- **Parallel Execution**: Reduces total time by ~40%

### Error Handling
- **API Failures**: Fallback analysis with error message
- **Parsing Errors**: Default response structure
- **Timeout**: 30-second timeout per chain

## Data Flow

### Input Processing
- **Metrics Formatting**: Human-readable metric descriptions
- **Anomaly Formatting**: Structured anomaly summaries
- **Pattern Formatting**: Frequency, temporal, co-occurrence summaries

### Output Processing
- **JSON Parsing**: Structured response extraction
- **Validation**: Pydantic model validation
- **Metadata**: Response time, analysis type, confidence scores 