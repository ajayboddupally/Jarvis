# Jarvis Intelligence

Jarvis is an AI platform being built as a modular intelligence system.

## Architecture

```
Client
  |
  v
Jarvis API Gateway :8000
  |
  v
Jarvis Intelligence Service :8001
  |
  +--> Context
  +--> Conversation Memory
  +--> Reasoning Planner
  +--> Model Provider
  |
  v
PostgreSQL

Redis
  |
  +--> Gateway rate limiting
```

## Implemented

### Gateway

- API-key authentication
- Admin API-key creation
- Request IDs
- Request-size protection
- Redis-backed rate limiting
- PostgreSQL usage metering
- CORS
- API versioning
- Service routing
- Health endpoints

### Intelligence Service

- Conversation persistence
- Context loading
- Message history
- Request classification
- Reasoning-plan abstraction
- Model-provider interface
- Local provider placeholder
- Optional external HTTP model provider
- Token usage tracking
- Conversation IDs
- Model routing foundation

The local provider is intentionally a deterministic placeholder. It is not presented as a trained Jarvis model.

## Run with Docker

Copy the environment file:

```bash
cp .env.example .env
```

Set strong values for:

```
JWT_SECRET
ADMIN_API_KEY
API_KEY_PEPPER
```

Start everything:

```bash
docker compose up --build
```

Gateway:

```
http://127.0.0.1:8000
```

Gateway docs:

```
http://127.0.0.1:8000/docs
```

Intelligence service:

```
http://127.0.0.1:8001
```

## Create an API key

```bash
curl -X POST http://127.0.0.1:8000/v1/admin/api-keys \
  -H "X-Admin-Key: YOUR_ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"local-dev","owner":"aj"}'
```

Copy the returned API key.

## Send a request

```bash
curl -X POST http://127.0.0.1:8000/v1/chat \
  -H "Authorization: Bearer YOUR_JARVIS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"jarvis-local","message":"Hello Jarvis"}'
```

The gateway forwards the request to the intelligence service.

## Current limitation

Jarvis does not have a proprietary trained foundation model yet. The intelligence service currently provides the architecture around the model layer and uses a deterministic local provider unless an external HTTP provider is configured.

The next stage is the tool system and agent runtime.
