# Validation Rules

## Required Fields

All 15 fields must be present in metrics data:

- timestamp
- cpu_usage
- memory_usage  
- latency_ms
- disk_usage
- network_in_kbps
- network_out_kbps
- io_wait
- thread_count
- active_connections
- error_rate
- uptime_seconds
- temperature_celsius
- power_consumption_watts
- service_status

## Field Constraints

| Field | Type | Min | Max | Unit |
|-------|------|-----|-----|------|
| cpu_usage | int | 0 | 100 | % |
| memory_usage | int | 0 | 100 | % |
| latency_ms | int | 1 | - | milliseconds |
| disk_usage | int | 0 | 100 | % |
| network_in_kbps | int | 0 | - | kbps |
| network_out_kbps | int | 0 | - | kbps |
| io_wait | int | 0 | 100 | % |
| thread_count | int | 0 | - | count |
| active_connections | int | 0 | - | count |
| error_rate | float | 0.0 | 1.0 | ratio |
| uptime_seconds | int | 0 | - | seconds |
| temperature_celsius | int | 0 | 200 | °C |
| power_consumption_watts | int | 0 | - | watts |

## Service Status Requirements

### Required Services
- database
- api_gateway  
- cache

### Valid States
- online
- degraded
- offline

## Validation Process

1. **Type Check**: Verify data types match expected types
2. **Range Check**: Validate min/max constraints
3. **Service Status**: Ensure all required services present with valid states
4. **Pydantic Validation**: Final validation using InfrastructureMetrics model

## Error Handling

- Missing fields: Field name and "required" message
- Type mismatches: Expected type vs actual type
- Range violations: Min/max values with actual value
- Service status: Invalid service or state with actual value 