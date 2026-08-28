# Service Health Monitor

Flask monitoring API with a background worker that checks HTTP services and stores results in Redis.

## Run

```bash
docker compose up --build
```

API: http://localhost:5000

List services:
```bash
curl http://localhost:5000/services
```

View one:
```bash
curl http://localhost:5000/services/api
```

Add one:
```bash
curl -X POST http://localhost:5000/services -H "Content-Type: application/json" -d '{"name":"example","url":"https://example.com"}'
```

Health:
```bash
curl http://localhost:5000/health
```

The worker checks services every 10 seconds.

Day 313 / 365
