# 📚 API Reference

## Base URL

```
http://localhost:8000/api/v1
```

## Chat Endpoints

### Send Message
**POST** `/chat/message`

Request:
```json
{
  "message": "نزدیک‌ترین بیمارستان کجاست؟",
  "user_id": "user123"
}
```

Response:
```json
{
  "response": "نزدیک‌ترین بیمارستان...",
  "intent": "location_query",
  "confidence": 0.95
}
```

## Knowledge Graph Endpoints

### Get Entities
**GET** `/graph/entities?type=hospital&limit=10`

### Get Relations
**GET** `/graph/relations`

## Location Endpoints

### Search Locations
**GET** `/locations/search?query=بیمارستان`

### Nearest Services
**GET** `/locations/nearest?latitude=27.2158&longitude=56.2808&type=hospital`

## Analytics Endpoints

### Get Statistics
**GET** `/analytics/stats`