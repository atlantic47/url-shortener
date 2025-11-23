# URL Shortener Service

A production-ready URL shortening service built with FastAPI, featuring analytics tracking, A/B testing, rate limiting, and GeoIP enrichment.

## Features

### Core Features
- **URL Shortening**: Generate short, 7-character Base62 codes or use custom aliases
- **Custom Aliases**: User-defined short codes (3-20 alphanumeric characters + hyphens)
- **TTL Support**: Set expiration times for URLs
- **Rate Limiting**: 10/min for shortening, 100/min for redirects
- **Analytics Tracking**: Comprehensive click analytics with enrichment

### Advanced Features
- **A/B Testing**: Split traffic between two URL variants with configurable percentages
- **GeoIP Enrichment**: Track country and city (optional, requires GeoIP database)
- **User-Agent Parsing**: Extract device type, browser, and OS information
- **Async Architecture**: Non-blocking database operations and background task processing
- **RESTful API**: Clean, documented API with automatic OpenAPI/Swagger docs

## Project Structure

```
url-shortener/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── database.py          # Database setup
│   ├── models/              # SQLAlchemy models
│   │   ├── url.py
│   │   └── click.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── url.py
│   │   └── analytics.py
│   ├── routers/             # API endpoints
│   │   ├── shortener.py
│   │   ├── redirect.py
│   │   └── analytics.py
│   ├── services/            # Business logic
│   │   ├── url_service.py
│   │   ├── analytics_service.py
│   │   └── enrichment.py
│   └── utils/               # Utilities
│       ├── shortcode.py
│       └── rate_limiter.py
├── tests/                   # Comprehensive tests
│   ├── conftest.py
│   ├── test_shortener.py
│   ├── test_redirect.py
│   ├── test_analytics.py
│   └── test_rate_limiting.py
├── requirements.txt
├── .env                     # Environment variables
└── README.md
```

## Quick Start (Windows)

### 1. Prerequisites
- Python 3.10+ (tested with Python 3.14)
- Virtual environment (venv)

### 2. Installation

```powershell
# Clone or navigate to the project directory
cd url-shortener

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
python -m pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file in the project root:

```env
DATABASE_URL=sqlite+aiosqlite:///./url_shortener.db
BASE_URL=http://localhost:8000
SHORT_CODE_LENGTH=7
SHORTEN_RATE_LIMIT=10/minute
REDIRECT_RATE_LIMIT=100/minute
GEOIP_DB_PATH=
CORS_ORIGINS=["*"]
```

### 4. Run the Application

```powershell
# Start the server
python -m uvicorn app.main:app --reload

# Server will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

## API Usage

### 1. Shorten a URL

**Basic Example:**
```bash
curl -X POST "http://localhost:8000/shorten" \
  -H "Content-Type: application/json" \
  -d "{\"original_url\": \"https://www.example.com\"}"
```

**Response:**
```json
{
  "short_url": "http://localhost:8000/aBc1234",
  "short_code": "aBc1234",
  "expires_at": null,
  "created_at": "2024-01-15T10:30:00"
}
```

**With TTL (1 hour):**
```bash
curl -X POST "http://localhost:8000/shorten" \
  -H "Content-Type: application/json" \
  -d "{\"original_url\": \"https://www.example.com\", \"ttl_seconds\": 3600}"
```

**With Custom Alias:**
```bash
curl -X POST "http://localhost:8000/shorten" \
  -H "Content-Type: application/json" \
  -d "{\"original_url\": \"https://www.example.com\", \"custom_alias\": \"my-link\"}"
```

**With A/B Testing:**
```bash
curl -X POST "http://localhost:8000/shorten" \
  -H "Content-Type: application/json" \
  -d "{\"original_url\": \"https://www.example.com/variant-a\", \"ab_test\": {\"url_b\": \"https://www.example.com/variant-b\", \"split\": 70}}"
```

### 2. Redirect (Use Short URL)

```bash
curl -L "http://localhost:8000/aBc1234"
# Returns HTTP 307 redirect to original URL
```

### 3. Get Analytics

```bash
curl "http://localhost:8000/analytics/aBc1234"
```

**Response:**
```json
{
  "short_code": "aBc1234",
  "total_clicks": 150,
  "unique_visitors": 45,
  "first_click": "2024-01-01T10:00:00",
  "last_click": "2024-01-05T15:30:00",
  "clicks_by_day": [
    {"date": "2024-01-01", "count": 30},
    {"date": "2024-01-02", "count": 45}
  ],
  "top_countries": [
    {"country": "United States", "count": 50},
    {"country": "United Kingdom", "count": 30}
  ],
  "top_cities": [
    {"city": "New York", "count": 20},
    {"city": "London", "count": 15}
  ],
  "devices": [
    {"device": "mobile", "count": 80},
    {"device": "desktop", "count": 70}
  ],
  "browsers": [
    {"browser": "Chrome", "count": 100},
    {"browser": "Safari", "count": 30}
  ],
  "operating_systems": [
    {"os": "Windows", "count": 70},
    {"os": "iOS", "count": 40}
  ],
  "ab_test_results": {
    "variant_a_clicks": 105,
    "variant_b_clicks": 45
  }
}
```

### 4. Health Check

```bash
curl "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

## Running Tests

```powershell
# Install test dependencies (already in requirements.txt)
python -m pip install pytest pytest-asyncio httpx

# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_shortener.py

# Run with coverage
python -m pip install pytest-cov
python -m pytest --cov=app --cov-report=html
```

## Design Decisions

### 1. Architecture
- **Async/Await**: All database operations are async for better performance under load
- **Background Tasks**: Analytics capture runs in background to avoid slowing redirects
- **Layered Architecture**: Clear separation between routers, services, and data layers

### 2. Database
- **SQLite for Demo**: Easy setup, no external dependencies
- **PostgreSQL for Production**: Recommended for production deployments
- **Lazy TTL**: URLs checked for expiry on access, no background cleanup needed

### 3. Short Code Generation
- **Base62 Encoding**: Uses a-z, A-Z, 0-9 (case-sensitive)
- **7 Characters**: Provides 62^7 = 3.5 trillion unique codes
- **Collision Retry**: Max 3 attempts to generate unique code

### 4. Rate Limiting
- **In-Memory Storage**: For demo purposes
- **Redis for Production**: Replace `memory://` with Redis URL for distributed systems
- **Per-IP Limiting**: Tracks requests by client IP address

### 5. A/B Testing
- **Weighted Random Selection**: `random.random() * 100 < split` determines variant
- **Variant Tracking**: Each click records which variant was served
- **Analytics Split**: Separate click counts for each variant

### 6. Analytics Enrichment
- **Optional GeoIP**: Works without database, doesn't crash if unavailable
- **User-Agent Parsing**: Extracts device, browser, OS using `user-agents` library
- **Graceful Degradation**: Missing enrichment data stored as NULL

## Scaling Considerations

### For Production Deployment:

1. **Database**
   - Switch to PostgreSQL with connection pooling
   - Add database indexes on frequently queried columns
   - Consider read replicas for analytics queries

2. **Caching**
   - Add Redis for:
     - Rate limiting (distributed)
     - Caching frequently accessed URLs
     - Session management

3. **Performance**
   - Use CDN for static redirect pages
   - Deploy multiple app instances behind load balancer
   - Implement database query optimization

4. **Monitoring**
   - Add structured logging (JSON format)
   - Integrate APM (e.g., Sentry, DataDog)
   - Set up health check monitoring

5. **Security**
   - Add HTTPS/TLS
   - Implement API authentication for /shorten
   - Add CAPTCHA to prevent abuse
   - Validate and sanitize URLs (check for malicious content)

6. **GeoIP**
   - Download MaxMind GeoLite2 database
   - Set `GEOIP_DB_PATH` in .env
   - Update database monthly

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Error Codes

| Code | Description |
|------|-------------|
| 200  | Success (GET requests) |
| 201  | Created (POST /shorten) |
| 307  | Temporary Redirect |
| 400  | Bad Request (invalid input) |
| 404  | Not Found |
| 410  | Gone (URL expired) |
| 422  | Unprocessable Entity (validation error) |
| 429  | Too Many Requests (rate limit) |
| 500  | Internal Server Error |

## License

This project is provided as-is for demonstration purposes.

## Contributing

This is a demonstration project. Feel free to fork and modify for your needs.

## Support

For issues or questions, please refer to the FastAPI documentation at https://fastapi.tiangolo.com/
