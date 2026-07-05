# Analytics Dashboard - Hermezgan Intelligent

## Overview

The Analytics Dashboard provides real-time insights into system performance, user interactions, and knowledge base metrics.

## Architecture

```
┌────────────────────────────────────────────────┐
│       Analytics Dashboard Frontend             │
│  (React + Chart.js/Plotly)                     │
└─────────────────────┬──────────────────────────┘
                      │
        ┌─────────────┴──────────────┐
        │                            │
   ┌────▼──────┐           ┌────────▼────��┐
   │Analytics   │           │WebSocket     │
   │API Service │           │Connection    │
   └────┬───────┘           └──────────────┘
        │
   ┌────▼───────────────────────────────────┐
   │  Backend Analytics Module              │
   ├─────────────────────────────────────────┤
   │ • Chat Statistics                       │
   │ • NLP Metrics                           │
   │ • Location Queries                      │
   │ • User Interactions                     │
   │ • System Performance                    │
   └────┬──────────────┬──────────┬──────────┘
        │              │          │
   ┌────▼──┐    ┌─────▼────┐   ┌─▼────────┐
   │Database│    │Redis     │   │Log Files │
   │Queries │    │Cache     │   │Analysis  │
   └────────┘    └──────────┘   └──────────┘
```

## Features

### 1. Real-Time Chat Analytics
- Total conversations
- Average response time
- Intent distribution
- Success/failure rates
- Top intents

### 2. NLP Performance Metrics
- Text processing speed
- Entity extraction accuracy
- Intent classification accuracy
- Embedding generation time

### 3. Location Services Metrics
- Most searched locations
- Average distance queries
- Location query volume
- Route calculation statistics

### 4. User Behavior
- Active users
- Session duration
- User retention
- Geographic distribution

### 5. System Performance
- API response times
- CPU/Memory usage
- Database query performance
- Error rates

## API Endpoints

### Statistics
```bash
GET /api/v1/analytics/stats
GET /api/v1/analytics/stats?period=24h|7d|30d
```

Response:
```json
{
  "total_conversations": 1234,
  "total_users": 456,
  "avg_response_time_ms": 234,
  "intent_distribution": {
    "greeting": 0.25,
    "location_query": 0.45,
    "direction": 0.20,
    "service_inquiry": 0.10
  },
  "success_rate": 0.92
}
```

### Reports
```bash
GET /api/v1/analytics/report/{report_type}
GET /api/v1/analytics/report/daily
GET /api/v1/analytics/report/weekly
GET /api/v1/analytics/report/monthly
```

### Performance Metrics
```bash
GET /api/v1/analytics/performance
GET /api/v1/analytics/performance?metric=cpu|memory|response_time
```

## Dashboard Components

### 1. Summary Cards
- Total Conversations
- Active Users
- Success Rate
- Avg Response Time

### 2. Charts
- Intent Distribution (Pie Chart)
- Conversation Trend (Line Chart)
- Response Time Distribution (Histogram)
- User Growth (Area Chart)

### 3. Tables
- Top Queries
- Recent Conversations
- Performance Logs
- Error Logs

### 4. Filters
- Date Range
- Intent Type
- User ID
- Location
- Performance Level

## Technology Stack

### Frontend
- React.js
- Chart.js / Plotly.js
- Material-UI
- Redux (State Management)
- Axios (API Client)

### Backend
- Python
- FastAPI
- SQLAlchemy (ORM)
- Redis (Caching)
- Pandas (Data Analysis)

### Database
- PostgreSQL (Primary)
- Redis (Cache)
- InfluxDB (Time-Series Data)

## Installation

### Backend Setup

```bash
# Add analytics packages
pip install pandas plotly sqlalchemy redis influxdb

# Create analytics tables
python scripts/create_analytics_schema.py
```

### Frontend Setup

```bash
cd frontend
npm install chart.js react-chartjs-2 plotly.js
npm start
```

## Usage

### Access Dashboard

```
http://localhost:3000/dashboard
```

### Real-Time Updates

```javascript
// WebSocket connection
const ws = new WebSocket('ws://localhost:8000/ws/analytics');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Updated stats:', data);
};
```

### Custom Reports

```bash
# Generate daily report
curl GET http://localhost:8000/api/v1/analytics/report/daily

# Export to CSV
curl GET http://localhost:8000/api/v1/analytics/export/csv?date=2026-07-05
```

## Metrics & KPIs

### Response Quality
- Intent Classification Accuracy
- Entity Recognition Rate
- Response Relevance Score
- User Satisfaction (if feedback available)

### Performance
- P95 Response Time
- P99 Response Time
- Throughput (queries/min)
- Error Rate

### Engagement
- Daily Active Users
- Session Duration
- Conversation Frequency
- User Retention Rate

## Alerts & Notifications

### Critical Alerts
- Error rate > 5%
- Response time > 5s
- Service down
- High memory usage

### Warning Alerts
- Response time > 2s
- Low accuracy < 80%
- High CPU usage

## Data Export

```bash
# Export raw data
GET /api/v1/analytics/export/csv
GET /api/v1/analytics/export/json
GET /api/v1/analytics/export/excel

# With filters
GET /api/v1/analytics/export/csv?start_date=2026-06-01&end_date=2026-07-05
```

## Dashboard Screenshots

### Main Dashboard
- Summary metrics at top
- Intent distribution pie chart
- Conversation trend line chart
- Recent conversations table

### Performance Dashboard
- Response time trends
- CPU/Memory usage
- Database performance
- Error rate over time

### User Analytics
- Active users over time
- User geographic distribution
- Session duration distribution
- User retention cohort

## Configuration

```python
# backend/config.py

ANALYTICS_CONFIG = {
    "enabled": True,
    "retention_days": 90,
    "update_interval_seconds": 60,
    "alert_thresholds": {
        "error_rate": 0.05,
        "response_time_ms": 5000,
        "cpu_percent": 80,
        "memory_percent": 85,
    },
    "dashboards": {
        "main": ["summary", "intents", "trends"],
        "performance": ["response_time", "cpu", "memory"],
        "users": ["active_users", "retention", "geographic"],
    },
}
```

## Future Enhancements

1. ✅ Machine Learning-based anomaly detection
2. ✅ Predictive analytics
3. ✅ A/B testing framework
4. ✅ Advanced segmentation
5. ✅ Custom dashboard builder
6. ✅ Data visualization templates
7. ✅ Real-time alerts dashboard
8. ✅ Export to BI tools (Tableau, Power BI)

## References

- [Plotly Documentation](https://plotly.com/python/)
- [Chart.js Documentation](https://www.chartjs.org/docs/latest/)
- [Redux Documentation](https://redux.js.org/)
