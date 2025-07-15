# Database Schema

## Metrics Table

### Structure
```sql
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    cpu_usage INTEGER NOT NULL,
    memory_usage INTEGER NOT NULL,
    latency_ms INTEGER NOT NULL,
    disk_usage INTEGER NOT NULL,
    network_in_kbps INTEGER NOT NULL,
    network_out_kbps INTEGER NOT NULL,
    io_wait INTEGER NOT NULL,
    thread_count INTEGER NOT NULL,
    active_connections INTEGER NOT NULL,
    error_rate REAL NOT NULL,
    uptime_seconds INTEGER NOT NULL,
    temperature_celsius INTEGER NOT NULL,
    power_consumption_watts INTEGER NOT NULL,
    service_status_database TEXT NOT NULL,
    service_status_api_gateway TEXT NOT NULL,
    service_status_cache TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Field Types
- **Primary Key**: `id` (auto-incrementing integer)
- **Timestamp**: ISO format string
- **Numeric Fields**: Integer for percentages, counts, measurements
- **Float Fields**: Real for ratios (error_rate)
- **Service Status**: Text for service states
- **Created At**: Auto-generated timestamp

### Constraints
- **Required Fields**: All fields except `created_at` are NOT NULL
- **Service States**: Limited to "online", "degraded", "offline"
- **Value Ranges**: Enforced by application validation
- **Timestamp Format**: ISO 8601 standard

## Data Relationships

### Current Implementation
- **Single Table**: All metrics in one table
- **No Foreign Keys**: Self-contained metrics records
- **Time-based Queries**: Primary access pattern via timestamp

### Query Patterns
- **Latest Metrics**: `ORDER BY timestamp DESC LIMIT 1`
- **Historical Data**: `ORDER BY timestamp DESC LIMIT N`
- **Time Range**: `WHERE timestamp BETWEEN start AND end`
- **Statistics**: `COUNT(*)`, `MAX(timestamp)`

## Performance Considerations

### Indexes
- **Primary Key**: `id` (automatic)
- **Timestamp**: Most queries filter by time
- **Service Status**: For service health queries

### Data Volume
- **Record Size**: ~200 bytes per metrics record
- **Storage**: SQLite file-based storage
- **Retention**: No automatic cleanup implemented

### Query Optimization
- **Limit Clauses**: All historical queries use LIMIT
- **Ordering**: Consistent DESC timestamp ordering
- **Filtering**: Time-based filters for large datasets

## Backup and Recovery

### Current State
- **File-based**: Single SQLite database file
- **No Replication**: Single point of failure
- **Manual Backup**: File system backup required

### Data Integrity
- **ACID Compliance**: SQLite provides transaction safety
- **Validation**: Application-level validation before insert
- **Error Handling**: Failed inserts logged and reported 