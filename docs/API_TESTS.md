# AeroMind API Tests

These sample requests assume the API is running at `http://localhost:5000`.

## Health

```bash
curl http://localhost:5000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "AeroMind API"
}
```

## Register

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ops_admin",
    "email": "ops_admin@aeromind.local",
    "password": "password123"
  }'
```

## Login

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ops_admin@aeromind.local",
    "password": "password123"
  }'
```

## Get Flights

```bash
curl http://localhost:5000/flights
```

## Get Flight By ID

```bash
curl http://localhost:5000/flights/1
```

## Get Gates

```bash
curl http://localhost:5000/gates
```

## Get Runways

```bash
curl http://localhost:5000/runways
```

## Get Incidents

```bash
curl http://localhost:5000/incidents
```

## Create Incident

```bash
curl -X POST http://localhost:5000/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Gate boarding delay",
    "description": "Boarding paused while ground staff inspect the jet bridge.",
    "severity": "medium",
    "location": "Gate B11"
  }'
```

## Get Weather

```bash
curl http://localhost:5000/weather
```

## Create Weather Report

```bash
curl -X POST http://localhost:5000/weather \
  -H "Content-Type: application/json" \
  -d '{
    "condition": "partly cloudy",
    "visibility": 8.5,
    "wind_speed": 14.2,
    "temperature": 22.8
  }'
```
