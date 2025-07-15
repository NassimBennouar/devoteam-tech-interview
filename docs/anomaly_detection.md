# Anomaly Detection System

## Overview

Automated infrastructure monitoring that detects anomalies using absolute thresholds, relative thresholds, and service status monitoring.

## Detection Methods

### Absolute Thresholds
Fixed values that trigger alerts regardless of historical context:

| Metric | Warning | Critical | Type |
|--------|---------|----------|------|
| CPU Usage | 80% | 90% | Performance |
| Memory Usage | 80% | 85% | Performance |
| Latency | 200ms | 500ms | Performance |
| Disk Usage | 80% | 90% | Capacity |
| IO Wait | 5% | 10% | Performance |
| Error Rate | 2% | 5% | Capacity |
| Temperature | 70°C | 80°C | Health |
| Power Consumption | 300W | 400W | Health |
| Active Connections | 100 | 150 | Capacity |

### Relative Thresholds
Dynamic thresholds based on historical data (last 5 points):

| Metric | Warning Multiplier | Critical Multiplier | Type |
|--------|-------------------|-------------------|------|
| Network In | 1.5x average | 2.0x average | Capacity |
| Network Out | 1.5x average | 2.0x average | Capacity |
| Thread Count | 1.5x average | 2.0x average | Capacity |

### Service Status Monitoring
Required services with valid states:
- **Database**: online, degraded, offline
- **API Gateway**: online, degraded, offline  
- **Cache**: online, degraded, offline

### Uptime Monitoring
- **Warning**: Uptime < 86400 seconds (24 hours)
- **Critical**: Uptime < 3600 seconds (1 hour)

## Anomaly Types

- **Performance**: Resource utilization issues
- **Capacity**: Resource exhaustion or limits
- **Health**: Hardware or service health problems

## Severity Levels

- **1-2**: Warning level anomalies
- **3-4**: Critical level anomalies  
- **5**: Service offline or extreme values

## Historical Analysis

### Pattern Detection
- **Frequency**: Count anomalies per metric, identify most problematic
- **Temporal**: Hourly distribution, peak problem times
- **Co-occurrence**: Metrics that alert together frequently

### Analysis Output
- Timeline with anomaly results per historical point
- Pattern summary with frequency, temporal, and co-occurrence data
- Most frequent problematic metrics and peak hours 