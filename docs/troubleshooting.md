# Troubleshooting

## Docker startup fails on occupied ports

If `docker compose up` fails with `address already in use`, override host ports:

```bash
REDIS_PORT=16379 docker compose up -d
```

Available overrides in `docker-compose.yml`:

- `POSTGRES_PORT` (default `5432`)
- `REDIS_PORT` (default `6379`)
- `WEAVIATE_HTTP_PORT` (default `8080`)
- `WEAVIATE_GRPC_PORT` (default `50051`)
- `BACKEND_PORT` (default `8000`)
- `FRONTEND_PORT` (default `3000`)

## Backend fails with ALLOWED_ORIGINS parse error

Use JSON array syntax in `backend/.env`:

```bash
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:3001"]
```

Comma-separated strings are not accepted by the current `pydantic-settings` loader.

## Weaviate marked unhealthy in Docker

If health checks fail with `curl: executable file not found`, use a `wget` healthcheck in compose:

```yaml
test: ["CMD", "wget", "--spider", "-q", "http://localhost:8080/v1/.well-known/ready"]
```

## Frontend returns 500 due Tailwind plugin

If logs show `Cannot find module 'tailwindcss-animate'`, install/lock dependencies:

```bash
cd frontend
npm install
```

Then recreate the frontend container:

```bash
docker compose up -d --build frontend
```

## Backend image fails dependency resolution

If pip reports conflicts or missing versions, ensure these pins:

- `voyageai==0.2.4`
- `httpx==0.24.1` (compatible with `supabase==2.3.0`)

## Run end-to-end smoke test

After services are running:

```bash
./infra/scripts/smoke-test.sh
```

Protected endpoints now require JWT auth. Pass a valid Supabase access token for full API coverage:

```bash
AUTH_TOKEN=your-jwt ./infra/scripts/smoke-test.sh
```

By default, the script exits successfully if auth token and/or AI provider keys are missing and reports skipped protected/AI-dependent steps. To require full AI flow success:

```bash
AUTH_TOKEN=your-jwt STRICT_AI=1 ./infra/scripts/smoke-test.sh
```
