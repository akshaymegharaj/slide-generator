# Slide Generator API Documentation

## Overview
A RESTful API for generating customizable presentation slides using LLMs, with support for themes, aspect ratios, and export to PPTX.

---

## Authentication
- **Type:** API Key (Bearer or X-API-Key header)
- **How:**
  - `Authorization: Bearer <your-api-key>`
  - `X-API-Key: <your-api-key>`
- **Required:** Yes (unless `AUTH_REQUIRED=false`)

---

## Rate Limiting & Concurrency
- **Rate Limit Headers:**
  - `X-RateLimit-Minute-Limit`, `X-RateLimit-Minute-Remaining`, `X-RateLimit-Hour-Limit`, `X-RateLimit-Hour-Remaining`
- **Concurrency Headers:**
  - `X-Concurrency-User-ID`, `X-Concurrency-Global-Limit`, `X-Concurrency-User-Limit`
- **Errors:**
  - `429 Too Many Requests` (rate limit exceeded)
  - `503 Service Unavailable` (concurrency exceeded)

---

## Endpoints

### Health Check
- `GET /`
- **Response:** `{ "message": "Slide Generator API is running" }`

### Create Presentation
- `POST /api/v1/presentations`
- **Body:**
```json
{
  "topic": "string",
  "num_slides": 1-20,
  "custom_content": "string (optional)",
  "theme": "modern|classic|minimal|corporate" (optional),
  "font": "string" (optional),
  "colors": { ... } (optional),
  "aspect_ratio": "16:9|4:3|A4|A4_L|1:1|custom" (optional),
  "custom_width": float (if custom),
  "custom_height": float (if custom)
}
```
- **Response:** Presentation object (see below)

### Get Presentation
- `GET /api/v1/presentations/{id}`
- **Response:** Presentation object

### List Presentations
- `GET /api/v1/presentations?limit=100&offset=0`
- **Response:** `[Presentation, ...]`

### Search Presentations
- `GET /api/v1/presentations/search/{topic}`
- **Response:** `[Presentation, ...]`

### Delete Presentation
- `DELETE /api/v1/presentations/{id}`
- **Response:** `{ "message": "Presentation deleted successfully" }`

### Download Presentation as PPTX
- `GET /api/v1/presentations/{id}/download`
- **Response:** PPTX file (Content-Type: application/vnd.openxmlformats-officedocument.presentationml.presentation)

### Configure Presentation
- `POST /api/v1/presentations/{id}/configure`
- **Body:**
```json
{
  "theme": "modern|classic|minimal|corporate" (optional),
  "font": "string" (optional),
  "colors": { ... } (optional),
  "aspect_ratio": "16:9|4:3|A4|A4_L|1:1|custom" (optional),
  "custom_width": float (if custom),
  "custom_height": float (if custom)
}
```
- **Response:** Updated Presentation object

### Get Available Aspect Ratios
- `GET /api/v1/aspect-ratios`
- **Response:**
```json
{
  "available_aspect_ratios": {
    "16:9": { ... },
    "4:3": { ... },
    ...
  },
  "custom_support": true,
  "custom_limits": { "min_width": 5.0, "max_width": 20.0, ... }
}
```

### Get Cache Stats
- `GET /api/v1/cache/stats`
- **Response:** Cache statistics

### Clear Cache
- `POST /api/v1/cache/clear`
- **Response:** `{ "message": "All caches cleared" }`

### Get LLM Status
- `GET /api/v1/llm/status`
- **Response:** LLM service info

### Switch LLM Service
- `POST /api/v1/llm/switch`
- **Body:** `{ "llm_type": "openai|dummy", "api_key": "..." (if openai) }`
- **Response:** Status message

### Get Concurrency Stats
- `GET /api/v1/concurrency/stats`
- **Response:** Concurrency statistics

---

## Presentation Object Example
```json
{
  "id": "string",
  "topic": "string",
  "num_slides": 5,
  "slides": [ ... ],
  "custom_content": "string",
  "theme": "modern",
  "font": "Arial",
  "colors": { ... },
  "aspect_ratio": "16:9",
  "custom_width": null,
  "custom_height": null,
  "created_at": "2024-06-01T12:00:00Z",
  "updated_at": "2024-06-01T12:00:00Z"
}
```

---

## Error Responses
- `401 Unauthorized`: Missing or invalid API key
- `429 Too Many Requests`: Rate limit exceeded
- `503 Service Unavailable`: Too many concurrent requests
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Unexpected error

---

## Notes
- All endpoints return JSON unless downloading a PPTX file.
- Use `/docs` for interactive Swagger UI.
- See `MIDDLEWARE_GUIDE.md` for details on authentication, rate limiting, and concurrency. 