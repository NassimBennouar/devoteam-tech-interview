from typing import Dict, Any, List
import logging
from collections import deque, defaultdict
from webservice.models.anomaly import Anomaly, AnomalyResult, AnomalyType
import statistics
import os
from datetime import datetime

logger = logging.getLogger(__name__)
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


class AnomalyDetectionService:
    def __init__(self):
        self.history = {
            "network_in_kbps": deque(maxlen=5),
            "network_out_kbps": deque(maxlen=5),
            "thread_count": deque(maxlen=5)
        }
        
        self.absolute_thresholds = {
            "cpu_usage": {"warning": 80, "critical": 90, "type": AnomalyType.PERFORMANCE},
            "memory_usage": {"warning": 80, "critical": 85, "type": AnomalyType.PERFORMANCE},
            "latency_ms": {"warning": 200, "critical": 500, "type": AnomalyType.PERFORMANCE},
            "disk_usage": {"warning": 80, "critical": 90, "type": AnomalyType.CAPACITY},
            "io_wait": {"warning": 5, "critical": 10, "type": AnomalyType.PERFORMANCE},
            "error_rate": {"warning": 0.02, "critical": 0.05, "type": AnomalyType.CAPACITY},
            "temperature_celsius": {"warning": 70, "critical": 80, "type": AnomalyType.HEALTH},
            "power_consumption_watts": {"warning": 300, "critical": 400, "type": AnomalyType.HEALTH},
            "active_connections": {"warning": 100, "critical": 150, "type": AnomalyType.CAPACITY}
        }
        
        self.relative_thresholds = {
            "network_in_kbps": {"warning": 1.5, "critical": 2.0, "type": AnomalyType.CAPACITY},
            "network_out_kbps": {"warning": 1.5, "critical": 2.0, "type": AnomalyType.CAPACITY},
            "thread_count": {"warning": 1.5, "critical": 2.0, "type": AnomalyType.CAPACITY}
        }

    def detect_anomalies(self, metrics: Dict[str, Any]) -> AnomalyResult:
        anomalies = []
        
        if DEBUG:
            logger.debug("Starting anomaly detection")
        
        for metric, value in metrics.items():
            if metric in self.absolute_thresholds:
                anomaly = self._check_absolute_threshold(metric, value)
                if anomaly:
                    anomalies.append(anomaly)
            
            elif metric in self.relative_thresholds:
                anomaly = self._check_relative_threshold(metric, value)
                if anomaly:
                    anomalies.append(anomaly)
            
            elif metric == "service_status":
                service_anomalies = self._check_service_status(value)
                anomalies.extend(service_anomalies)
            
            elif metric == "uptime_seconds":
                anomaly = self._check_uptime(value)
                if anomaly:
                    anomalies.append(anomaly)
        
        self._update_history(metrics)
        
        total_count = len(anomalies)
        has_anomalies = total_count > 0
        
        if has_anomalies:
            critical_count = sum(1 for a in anomalies if a.severity >= 4)
            warning_count = total_count - critical_count
            summary = f"{total_count} anomalies detected ({critical_count} critical, {warning_count} warning)"
        else:
            summary = "No anomalies detected"
        
        if DEBUG:
            logger.debug(f"Anomaly detection completed: {summary}")
        
        return AnomalyResult(
            has_anomalies=has_anomalies,
            anomalies=anomalies,
            summary=summary,
            total_count=total_count
        )

    def analyze_historical_anomalies(self, metrics_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze anomalies on a list of historical metrics"""
        analyzed_timeline = []
        
        if DEBUG:
            logger.debug(f"Starting historical anomaly analysis on {len(metrics_list)} points")
        
        for metrics in metrics_list:
            anomaly_result = self.detect_anomalies(metrics)
            analyzed_timeline.append({
                "timestamp": metrics.get("timestamp"),
                "anomalies": [anomaly.model_dump() for anomaly in anomaly_result.anomalies],
                "has_issues": anomaly_result.has_anomalies,
                "total_count": anomaly_result.total_count
            })
        
        if DEBUG:
            total_anomalies = sum(point["total_count"] for point in analyzed_timeline)
            logger.debug(f"Historical analysis completed: {total_anomalies} total anomalies across {len(metrics_list)} points")
        
        return analyzed_timeline

    def analyze_anomaly_patterns(self, analyzed_timeline: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in detected anomalies"""
        if DEBUG:
            logger.debug("Starting pattern analysis")
        
        frequency = self._analyze_frequency(analyzed_timeline)
        temporal = self._analyze_temporal_patterns(analyzed_timeline)
        cooccurrence = self._analyze_cooccurrence(analyzed_timeline)
        
        patterns = {
            "frequency": frequency,
            "temporal": temporal,
            "cooccurrence": cooccurrence,
            "total_points": len(analyzed_timeline)
        }
        
        if DEBUG:
            logger.debug(f"Pattern analysis completed: {len(frequency)} metrics analyzed")
        
        return patterns

    def _analyze_frequency(self, analyzed_timeline: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze frequency of anomalies per metric"""
        frequency = {}
        severity_distribution = defaultdict(list)
        
        for point in analyzed_timeline:
            for anomaly in point["anomalies"]:
                metric = anomaly["metric"]
                severity = anomaly["severity"]
                
                frequency[metric] = frequency.get(metric, 0) + 1
                severity_distribution[metric].append(severity)
        
        severity_avg = {}
        for metric, severities in severity_distribution.items():
            severity_avg[metric] = sum(severities) / len(severities)
        
        return {
            "counts": frequency,
            "severity_avg": severity_avg,
            "most_frequent": max(frequency.items(), key=lambda x: x[1]) if frequency else None
        }

    def _analyze_temporal_patterns(self, analyzed_timeline: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal patterns in anomalies"""
        hourly_anomalies = defaultdict(list)
        
        for point in analyzed_timeline:
            if point["timestamp"]:
                try:
                    if isinstance(point["timestamp"], str):
                        dt = datetime.fromisoformat(point["timestamp"].replace('Z', '+00:00'))
                    else:
                        dt = point["timestamp"]
                    
                    hour = dt.hour
                    anomaly_count = point["total_count"]
                    hourly_anomalies[hour].append(anomaly_count)
                except Exception as e:
                    if DEBUG:
                        logger.debug(f"Error parsing timestamp {point['timestamp']}: {e}")
                    continue
        
        hourly_avg = {}
        for hour, counts in hourly_anomalies.items():
            hourly_avg[hour] = sum(counts) / len(counts)
        
        overall_avg = sum(hourly_avg.values()) / len(hourly_avg) if hourly_avg else 0
        problematic_hours = [hour for hour, avg in hourly_avg.items() if avg > overall_avg * 1.5]
        
        return {
            "hourly_distribution": dict(hourly_avg),
            "problematic_hours": sorted(problematic_hours),
            "peak_hour": max(hourly_avg.items(), key=lambda x: x[1]) if hourly_avg else None
        }

    def _analyze_cooccurrence(self, analyzed_timeline: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze co-occurrence of anomalies"""
        cooccurrences = defaultdict(int)
        
        for point in analyzed_timeline:
            metrics_in_alert = [anomaly["metric"] for anomaly in point["anomalies"]]
            
            for i, metric1 in enumerate(metrics_in_alert):
                for metric2 in metrics_in_alert[i+1:]:
                    pair = tuple(sorted([metric1, metric2]))
                    cooccurrences[pair] += 1
        
        cooccurrence_dict = dict(cooccurrences)
        sorted_cooccurrences = sorted(cooccurrence_dict.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "pairs": cooccurrence_dict,
            "most_common": sorted_cooccurrences[:5],
            "total_pairs": len(cooccurrence_dict)
        }

    def _check_absolute_threshold(self, metric: str, value: Any) -> Anomaly:
        thresholds = self.absolute_thresholds[metric]
        
        if value >= thresholds["critical"]:
            return Anomaly(
                metric=metric,
                value=value,
                threshold=thresholds["critical"],
                severity=5,
                type=thresholds["type"],
                message=f"{metric} is critically high: {value} >= {thresholds['critical']}"
            )
        elif value >= thresholds["warning"]:
            return Anomaly(
                metric=metric,
                value=value,
                threshold=thresholds["warning"],
                severity=3,
                type=thresholds["type"],
                message=f"{metric} is high: {value} >= {thresholds['warning']}"
            )
        
        return None

    def _check_relative_threshold(self, metric: str, value: Any) -> Anomaly:
        history = self.history[metric]
        
        if len(history) < 2:
            return None
        
        avg_historical = statistics.mean(history)
        thresholds = self.relative_thresholds[metric]
        
        if value >= avg_historical * thresholds["critical"]:
            return Anomaly(
                metric=metric,
                value=value,
                threshold=f"{thresholds['critical']}x avg ({avg_historical:.1f})",
                severity=5,
                type=thresholds["type"],
                message=f"{metric} is critically high: {value} >= {thresholds['critical']}x historical average"
            )
        elif value >= avg_historical * thresholds["warning"]:
            return Anomaly(
                metric=metric,
                value=value,
                threshold=f"{thresholds['warning']}x avg ({avg_historical:.1f})",
                severity=3,
                type=thresholds["type"],
                message=f"{metric} is high: {value} >= {thresholds['warning']}x historical average"
            )
        
        return None

    def _check_service_status(self, service_status: Dict[str, str]) -> List[Anomaly]:
        anomalies = []
        
        for service, status in service_status.items():
            if status == "offline":
                anomalies.append(Anomaly(
                    metric=f"service_status.{service}",
                    value=status,
                    threshold="online",
                    severity=5,
                    type=AnomalyType.STABILITY,
                    message=f"Service {service} is offline"
                ))
            elif status == "degraded":
                anomalies.append(Anomaly(
                    metric=f"service_status.{service}",
                    value=status,
                    threshold="online",
                    severity=3,
                    type=AnomalyType.STABILITY,
                    message=f"Service {service} is degraded"
                ))
        
        return anomalies

    def _check_uptime(self, uptime_seconds: int) -> Anomaly:
        one_hour = 3600
        
        if uptime_seconds < one_hour:
            return Anomaly(
                metric="uptime_seconds",
                value=uptime_seconds,
                threshold=one_hour,
                severity=3,
                type=AnomalyType.STABILITY,
                message=f"System recently restarted: uptime {uptime_seconds}s < 1 hour"
            )
        
        return None

    def _update_history(self, metrics: Dict[str, Any]):
        for metric in self.history.keys():
            if metric in metrics:
                self.history[metric].append(metrics[metric])
                if DEBUG:
                    logger.debug(f"Updated history for {metric}: {list(self.history[metric])}")

    def get_history_summary(self) -> Dict[str, Any]:
        return {
            metric: {
                "count": len(history),
                "values": list(history),
                "average": statistics.mean(history) if len(history) > 0 else None
            }
            for metric, history in self.history.items()
        } 