# Frontend Workflows

## Authentication

### Login Process
- **Username**: admin
- **Password**: password
- **Session**: Maintained across pages until logout
- **Access Control**: All pages require authentication

### Logout
- Clears session state
- Redirects to login page

## Ingestion Page

### Metrics Upload
- **Format**: JSON file upload
- **Validation**: Client-side format check
- **Example**: `example_metrics.json` provided
- **Response**: Success/error message with timing details

### Upload Workflow
1. Select JSON file
2. Validate format
3. Send to `/api/metrics/ingest`
4. Display results with anomaly count

## Analysis Page

### Analysis Types
- **Latest Point**: Analyze single current metrics
- **Historical**: Analyze patterns across multiple points

### Historical Analysis Controls
- **Points Slider**: 10-200 historical points
- **Analysis Trigger**: Button to start analysis
- **Results Display**: Pattern insights and recommendations

### Analysis Workflow
1. Select analysis type (latest/historical)
2. Configure parameters (points count)
3. Trigger analysis via API
4. Display results with confidence scores

## Dashboard Page

### Visualization Options
- **Radio Buttons**: Switch between chart types
- **Line Charts**: Last 100 metrics points
- **Correlation Matrix**: Pearson correlations between metrics

### Chart Controls
- **Metrics Selection**: Choose metrics to display
- **Points Count**: Slider for correlation matrix (10-100)
- **Auto-refresh**: Real-time data updates

### Data Sources
- **History API**: `/api/metrics/history` for chart data
- **Info API**: `/api/metrics/info` for statistics
- **Real-time**: Latest metrics from session

## Navigation

### Page Structure
- **Ingestion**: Upload and validate metrics
- **Analysis**: Run LLM analysis on data
- **Dashboard**: Visualize historical data

### State Management
- **Session State**: Authentication and latest metrics
- **Page State**: Current analysis results and charts
- **Data Persistence**: Metrics stored in database

## Error Handling

### Client-side Validation
- JSON format validation
- Required field checks
- File size limits

### API Error Display
- Network error messages
- Validation error details
- Server error notifications

### User Feedback
- Loading indicators during API calls
- Success/error message display
- Progress bars for long operations 