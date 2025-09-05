# Anti-Bot Bypass Server 🚀

A powerful FastAPI-based web scraping service that bypasses anti-bot measures using multiple scraping backends including BrightData CDP and Camoufox browser automation.

## 🌟 Features

- **Multiple Scraping Backends**: Support for BrightData CDP and Camoufox scrapers
- **Anti-Bot Bypass**: Advanced techniques to bypass bot detection systems
- **API Authentication**: Secure Bearer token authentication (optional)
- **Proxy Support**: Built-in proxy authentication and rotation
- **Human-like Behavior**: Simulates natural mouse movements and scrolling
- **Retry Logic**: Automatic retry with exponential backoff
- **Health Monitoring**: Built-in health checks and monitoring endpoints
- **Docker Ready**: Fully containerized with Docker and Docker Compose
- **Security Focused**: Runs with non-root user and security profiles
- **RESTful API**: Clean REST API with comprehensive documentation

## 🏗️ Architecture

```
anti-bot-bypass-server/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── models.py            # Pydantic data models
│   ├── constants/
│   │   └── app_data.py      # Application constants
│   └── services/
│       ├── base.py          # Abstract scraper interface
│       ├── factory.py       # Scraper factory pattern
│       ├── brightdata.py    # BrightData CDP scraper
│       └── camoufox_scraper.py # Camoufox scraper
├── Dockerfile               # Docker container configuration
├── docker-compose.yml       # Docker Compose orchestration
├── seccomp_profile.json     # Security profile for containers
└── pyproject.toml          # Python project configuration
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- BrightData CDP endpoint (for BrightData scraper)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd anti-bot-bypass-server
```

### 2. Environment Configuration

Copy the example environment file and configure it:

```bash
cp environment.example .env
```

Then edit the `.env` file with your configuration:

```env
# Required for BrightData scraper
BRIGHTDATA_CDP_ENDPOINT=wss://your-brightdata-endpoint

# Optional configurations
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false
DEFAULT_TIMEOUT=30000
MAX_RETRIES=3
```

### 3. Run with Docker Compose

```bash
# Build and start the service
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### 4. Verify Installation

Check if the service is running:

```bash
curl http://localhost:8001/health
```

Expected response:

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "available_scrapers": ["brightdata_cdp", "camoufox"]
}
```

## 📖 API Documentation

### Interactive API Documentation

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

### Core Endpoints

#### Health Check

```http
GET /health
```

#### List Available Scrapers

```http
GET /scrapers
```

#### Scrape URL

```http
POST /scrape
Content-Type: application/json
Authorization: Bearer your_api_key_here

{
  "url": "https://example.com",
  "scraper_type": "camoufox",
  "selector_to_wait_for": "h1.title",
  "timeout": 30000,
  "headless": true,
  "headers": {
    "User-Agent": "Custom User Agent"
  },
  "cookies": {
    "session": "abc123"
  },
  "proxy_server": "proxy.example.com:8080",
  "proxy_username": "username",
  "proxy_password": "password",
  "proxy_url": "http://proxy.example.com:8080"
}
```

**Note**: The `Authorization` header is only required if authentication is enabled (see configuration section).

## 🛠️ Configuration

### Environment Variables

| Variable                   | Description                   | Default           | Required |
| -------------------------- | ----------------------------- | ----------------- | -------- |
| `API_HOST`                 | API server host               | `0.0.0.0`         | No       |
| `API_PORT`                 | API server port               | `8000`            | No       |
| `API_DEBUG`                | Enable debug mode             | `false`           | No       |
| `BRIGHTDATA_CDP_ENDPOINT`  | BrightData CDP endpoint       | -                 | Yes\*    |
| `DEFAULT_TIMEOUT`          | Default request timeout (ms)  | `30000`           | No       |
| `MAX_RETRIES`              | Maximum retry attempts        | `3`               | No       |
| `ENABLE_AUTH`              | Enable API key authentication | `false`           | No       |
| `API_KEY`                  | API key for authentication    | -                 | Yes\*\*  |
| `PLAYWRIGHT_BROWSERS_PATH` | Browser installation path     | `/tmp/playwright` | No       |
| `XDG_CACHE_HOME`           | Cache directory path          | `/app/cache`      | No       |

\*Required only if using BrightData scraper  
\*\*Required only if `ENABLE_AUTH=true`

### Scraper Types

1. **`brightdata_cdp`**: Uses BrightData's CDP endpoint for scraping
2. **`camoufox`**: Uses Camoufox browser with stealth capabilities

## 🔧 Development

### Local Development Setup

1. **Install PDM** (Python Dependency Manager):

```bash
pip install pdm
```

2. **Install Dependencies**:

```bash
pdm install
```

3. **Run Development Server**:

```bash
pdm run dev
```

### Project Structure

- **`app/main.py`**: FastAPI application with lifecycle management
- **`app/config.py`**: Pydantic settings for configuration management
- **`app/models.py`**: Request/response models and enums
- **`app/services/`**: Scraper implementations following factory pattern
- **`app/constants/`**: Application constants and metadata

### Adding New Scrapers

1. Create a new scraper class inheriting from `BaseScraper`
2. Implement required methods: `scrape()`, `initialize()`, `cleanup()`, `name`
3. Register the scraper in `ScraperFactory`
4. Add the scraper type to `ScraperType` enum

## 🐳 Docker Configuration

### Build Arguments

The Dockerfile supports the following build arguments:

- `PLAYWRIGHT_VERSION`: Playwright Docker image version (default: `v1.55.0-noble`)

### Security Features

- **API Authentication**: Optional Bearer token authentication
- **Security profiles**: Configurable security restrictions
- **Resource limits**: Memory and CPU constraints
- **Network isolation**: Custom Docker network

### Performance Optimizations

- **Shared memory**: 2GB shared memory for browser processes
- **Browser cache**: Persistent volume for browser data
- **Tmpfs mounts**: In-memory temporary storage

## 🔐 Security Considerations

### Container Security

- Optional API key authentication
- Configurable security profiles
- Minimal attack surface with specific capability grants
- Resource limits to prevent DoS

### Network Security

- Custom Docker network isolation
- Health check endpoints for monitoring
- Configurable timeouts and rate limiting

## 📊 Monitoring & Logging

### Health Checks

The service includes comprehensive health checks:

- **Container health**: Docker health check every 30s
- **Application health**: `/health` endpoint
- **Scraper availability**: Lists available scrapers

### Logging

- Structured logging with different levels
- Container logs accessible via Docker Compose
- Persistent log storage in `./logs` directory

```bash
# View real-time logs
docker-compose logs -f anti-bot-bypass-server

# View logs for specific timeframe
docker-compose logs --since="1h" anti-bot-bypass-server
```

## 🚨 Troubleshooting

### Common Issues

#### 1. BrightData Connection Issues

```bash
# Check if BRIGHTDATA_CDP_ENDPOINT is set
docker-compose exec anti-bot-bypass-server env | grep BRIGHTDATA

# Test connectivity (without auth)
curl -X POST http://localhost:8001/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/ip", "scraper_type": "brightdata_cdp"}'

# Test connectivity (with auth)
curl -X POST http://localhost:8001/scrape \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key_here" \
  -d '{"url": "https://httpbin.org/ip", "scraper_type": "brightdata_cdp"}'
```

#### 2. Browser Launch Failures

```bash
# Check browser dependencies
docker-compose exec anti-bot-bypass-server playwright install-deps

# Check container logs for errors
docker-compose logs anti-bot-bypass-server
```

#### 3. Memory Issues

```bash
# Increase shared memory
# Edit docker-compose.yml: shm_size: 4gb

# Monitor memory usage
docker stats anti-bot-bypass-server
```

### Debug Mode

Enable debug logging by setting environment variable:

```env
API_DEBUG=true
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [Playwright](https://playwright.dev/) - Browser automation library
- [Camoufox](https://github.com/daijro/camoufox) - Stealth browser automation
- [BrightData](https://brightdata.com/) - Proxy and data collection platform

## 📞 Support

For support, please open an issue on GitHub or contact the maintainers.

---

**Made with ❤️ by Nirav Joshi**
