# Jarvis Intelligence

Jarvis is an AI platform being built as a modular intelligence system.

## Current component

This repository starts with the Jarvis API Gateway. It provides:

- API-key authentication
- Request IDs
- CORS configuration
- Request-size protection
- Redis-backed rate limiting
- Usage metering
- Service routing
- Health checks
- API versioning
- Secure configuration

The gateway is deliberately separated from intelligence, agent, and model services.

## Architecture

```
Client
  |
  v
Jarvis API Gateway
  |-- Authentication
  |-- Rate limiting
  |-- Request IDs
  |-- Usage metering
  |-- Routing
  |
  +--> Intelligence Service
  +--> Agent Service
  +--> Future Model Services
```

## Local development

Create a virtual environment:

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\\Scripts\\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and replace every secret.

Start PostgreSQL and Redis:

```bash
docker compose up -d postgres redis
```

Start the gateway:

```bash
uvicorn app.main:app --reload --port 8000
```

Open:

```
http://127.0.0.1:8000/docs
```

## Authentication

Client requests use:

```
Authorization: Bearer <jarvis-api-key>
```

The gateway stores only a keyed HMAC digest of an API key. The raw key is returned once when the key is created.

Admin key creation uses:

```
X-Admin-Key: <ADMIN_API_KEY>
```

## API

Health:

```
GET /health
GET /v1/health
```

Models:

```
GET /v1/models
Authorization: Bearer <key>
```

Chat:

```
POST /v1/chat
Authorization: Bearer <key>
Content-Type: application/json

{
  "model": "jarvis-1",
  "message": "Hello Jarvis"
}
```

Create API key:

```
POST /v1/admin/api-keys
X-Admin-Key: <ADMIN_API_KEY>
Content-Type: application/json

{
  "name": "local-development",
  "owner": "aj"
}
```

## Security

Never commit `.env`, production secrets, private keys, or real API keys.

The gateway is the first layer. Future releases will add organization/project isolation, quotas, billing, model routing, streaming, tool execution, and the Jarvis intelligence service.
