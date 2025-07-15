# API Endpoints

## Metrics Endpoints

### POST /api/metrics/ingest
Ingest infrastructure metrics with validation and persistence.

**Request Format:**
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "cpu_usage": 75,
  "memory_usage": 80,
  "latency_ms": 150,
  "disk_usage": 85,
  "network_in_kbps": 1000,
  "network_out_kbps": 500,
  "io_wait": 3,
  "thread_count": 50,
  "active_connections": 120,
  "error_rate": 0.02,
  "uptime_seconds": 86400,
  "temperature_celsius": 65,
  "power_consumption_watts": 250,
  "service_status": {
    "database": "online",
    "api_gateway": "online", 
    "cache": "online"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Metrics ingested successfully",
  "validation_time": 0.002,
  "persistence_time": 0.015,
  "anomaly_detection_time": 0.003,
  "total_time": 0.020,
  "anomalies": {
    "has_anomalies": true,
    "total_count": 2,
    "summary": "2 anomalies detected (1 critical, 1 warning)"
  }
}
```

### GET /api/metrics/history
Retrieve historical metrics with optional filters.

**Query Parameters:**
- `limit`: Number of points (1-1000, default: 100)
- `start_time`: ISO timestamp filter
- `end_time`: ISO timestamp filter

**Response:**
```json
{
  "total_retrieved": 50,
  "limit": 100,
  "start_time": "2024-01-01T00:00:00Z",
  "end_time": "2024-01-01T23:59:59Z",
  "data": [
    {
      "id": 1,
      "timestamp": "2024-01-01T12:00:00Z",
      "cpu_usage": 75,
      "memory_usage": 80,
      // ... all metrics fields
      "created_at": "2024-01-01T12:00:01Z"
    }
  ]
}
```

### GET /api/metrics/info
Get metrics database statistics.

**Response:**
```json
{
  "total_count": 1250,
  "latest_timestamp": "2024-01-01T12:00:00Z"
}
```

## Analysis Endpoints

### POST /api/analysis/latest
Analyze latest metrics point with LLM.

**Request:**
```json
{
  "metrics": {
    // metrics object
  }
}
```

**Response:**
```json
{
  "analysis_summary": "High CPU and memory usage detected",
  "root_cause_analysis": "Resource exhaustion due to high load",
  "recommendations": [
    {
      "priority": 1,
      "category": "immediate",
      "action": "Scale up resources",
      "impact": "Reduce performance issues",
      "effort": "medium"
    }
  ],
  "confidence_score": 0.85
}
```

### POST /api/analysis/historical
Analyze historical patterns with advanced LLM chains.

**Request:**
```json
{
  "points_count": 50,
  "current_metrics": {
    // current metrics object
  }
}
```

**Response:**
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
    "total_points": 50,
    "pattern_interpretation": {
      "main_pattern": "High frequency of error_rate anomalies",
      "pattern_type": "recurring"
    },
    "severity_assessment": {
      "criticality": 4,
      "urgency": "immediate"
    }
  }
}
```

## Anomalies Endpoints

### GET /api/anomalies/latest
Get latest anomaly detection results.

**Response:**
```json
{
  "has_anomalies": true,
  "anomalies": [
    {
      "metric": "cpu_usage",
      "value": 95,
      "threshold": 90,
      "severity": 4,
      "type": "PERFORMANCE",
      "message": "CPU usage exceeds critical threshold"
    }
  ],
  "summary": "1 anomaly detected (1 critical, 0 warning)",
  "total_count": 1
}
```

## Health Endpoints

### GET /api/health
Service health check.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z"
}
``` 