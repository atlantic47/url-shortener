# Quick Start Guide

## Installation Complete! ✅

The URL Shortener Service is now fully installed and configured.

## Running the Application

### Start the Server

```powershell
# Make sure you're in the project directory
cd c:\Users\Public\Documents\url-shortener

# Start the server
python -m uvicorn app.main:app --reload
```

The server will start at: **http://localhost:8000**

### Access the Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Quick API Examples

### 1. Create a Short URL

```powershell
# Using Invoke-WebRequest (PowerShell)
$body = @{
    original_url = "https://www.example.com"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/shorten" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

### 2. Create Short URL with Custom Alias

```powershell
$body = @{
    original_url = "https://www.example.com"
    custom_alias = "my-link"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/shorten" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

### 3. Create Short URL with TTL (Expires in 1 hour)

```powershell
$body = @{
    original_url = "https://www.example.com"
    ttl_seconds = 3600
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/shorten" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

### 4. Create A/B Test URL

```powershell
$body = @{
    original_url = "https://www.example.com/variant-a"
    ab_test = @{
        url_b = "https://www.example.com/variant-b"
        split = 70
    }
} | ConvertTo-Json -Depth 3

Invoke-WebRequest -Uri "http://localhost:8000/shorten" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

### 5. Visit a Short URL

Simply open in browser:
```
http://localhost:8000/abc1234
```

Or using PowerShell:
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/abc1234" -MaximumRedirection 0
```

### 6. Get Analytics

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/analytics/abc1234"
```

## Using Python for Testing

```python
import httpx
import json

# Create short URL
data = {"original_url": "https://www.example.com"}
response = httpx.post("http://localhost:8000/shorten", json=data)
result = response.json()
print(f"Short URL: {result['short_url']}")
print(f"Short Code: {result['short_code']}")

# Get analytics
short_code = result['short_code']
analytics = httpx.get(f"http://localhost:8000/analytics/{short_code}")
print(json.dumps(analytics.json(), indent=2))
```

## Running Tests

```powershell
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_shortener.py -v

# Run with coverage
python -m pytest --cov=app
```

## Project Features

✅ **URL Shortening** - Generate 7-character Base62 codes
✅ **Custom Aliases** - Use your own short codes
✅ **TTL Support** - URLs can expire after a set time
✅ **A/B Testing** - Split traffic between two URLs
✅ **Analytics** - Track clicks, devices, browsers, locations
✅ **Rate Limiting** - 10/min for shortening, 100/min for redirects
✅ **GeoIP Support** - Track geographic location (optional)
✅ **User-Agent Parsing** - Extract device, browser, OS info

## Database

The application uses SQLite by default with the database file at:
```
c:\Users\Public\Documents\url-shortener\url_shortener.db
```

For production, switch to PostgreSQL by updating the `.env` file:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/url_shortener
```

## Configuration

All settings are in `.env` file:
```env
BASE_URL=http://localhost:8000
DATABASE_URL=sqlite+aiosqlite:///./url_shortener.db
SHORT_CODE_LENGTH=7
SHORTEN_RATE_LIMIT=10/minute
REDIRECT_RATE_LIMIT=100/minute
```

## Troubleshooting

### Server won't start
- Make sure virtual environment is activated
- Check that port 8000 is not in use
- Verify all dependencies are installed: `python -m pip list`

### Import errors
- Reinstall dependencies: `python -m pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.10+)

### Database errors
- Delete `url_shortener.db` and restart the server to create a fresh database
- Check file permissions in the project directory

## Next Steps

1. ✅ Server is running
2. Visit http://localhost:8000/docs to explore the interactive API
3. Create your first short URL
4. Check analytics for your URLs
5. Read [README.md](README.md) for full documentation

## Support

For detailed documentation, see [README.md](README.md)

For FastAPI documentation: https://fastapi.tiangolo.com/
