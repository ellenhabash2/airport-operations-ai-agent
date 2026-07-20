# AeroMind API Tests

Sample requests for every endpoint. They assume the API is running at
`http://localhost:5000`.

Endpoints marked **JWT** need an `Authorization: Bearer <token>` header.
Get a token from `/auth/login` first.

## Contents

- [Service](#service)
- [Authentication](#authentication)
- [AI agent](#ai-agent)
- [Flights](#flights)
- [Gates](#gates)
- [Runways](#runways)
- [Incidents](#incidents)
- [Weather](#weather)
- [Testing from PowerShell](#testing-from-powershell)

## Service

### Index

```bash
curl http://localhost:5000/
```

Lists every available endpoint.

### Health

```bash
curl http://localhost:5000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "AeroMind API",
  "database": "ok"
}
```

Returns `503` with `"database": "unreachable"` when PostgreSQL cannot be
reached.

## Authentication

### Register

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ops_admin",
    "email": "ops_admin@aeromind.local",
    "password": "password123"
  }'
```

### Login

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ops_admin@aeromind.local",
    "password": "password123"
  }'
```

Returns an `access_token`. Every request below marked **JWT** needs it.

```bash
TOKEN="paste-the-access-token-here"
```

### Update your profile (JWT)

Send any combination of `username`, `email` and `password`.

```bash
curl -X PATCH http://localhost:5000/auth/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "duty_manager"}'
```

## AI agent

### Ask a question (JWT)

```bash
curl -X POST http://localhost:5000/agent/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Which flights are delayed?"}'
```

The response holds the answer and the tools the agent executed:

```json
{
  "data": {
    "answer": "...",
    "tool_calls": [
      {"tool": "find_delayed_flights", "arguments": {}, "failed": false}
    ]
  }
}
```

### Continue a conversation

The response includes a `conversation_id`. Send it back to keep the
context, so follow-up questions work.

```bash
curl -X POST http://localhost:5000/agent/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "And which of those are at Terminal B?", "conversation_id": 1}'
```

Omit `conversation_id` to start a fresh thread.

### List your conversations (JWT)

```bash
curl http://localhost:5000/agent/conversations \
  -H "Authorization: Bearer $TOKEN"
```

### Read one conversation (JWT)

Returns the thread with its turns in order.

```bash
curl http://localhost:5000/agent/conversations/1 \
  -H "Authorization: Bearer $TOKEN"
```

### Delete a conversation (JWT)

```bash
curl -X DELETE http://localhost:5000/agent/conversations/1 \
  -H "Authorization: Bearer $TOKEN"
```

### Multi-step reasoning

This question cannot be answered by a single tool, so the agent chains
several calls before replying.

```bash
curl -X POST http://localhost:5000/agent/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Look up flight AM2005. Which terminal is its gate in, and what other flights use that terminal?"}'
```

### Acting on the data

The agent can change records, not only read them.

```bash
curl -X POST http://localhost:5000/agent/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Runway 08L/26R is closed for maintenance. Update it, tell me how many flights are affected, and log a high severity incident about the closure."}'
```

## Flights

### List flights

```bash
curl http://localhost:5000/flights
```

### Search flights

Any combination of `origin`, `destination`, `status` and `airline`.
At least one is required.

```bash
curl "http://localhost:5000/flights/search?status=delayed"
curl "http://localhost:5000/flights/search?destination=LHR&status=boarding"
curl "http://localhost:5000/flights/search?airline=pacific"
```

### Get one flight

```bash
curl http://localhost:5000/flights/1
```

### Update a flight's status (JWT)

Allowed values: `scheduled`, `boarding`, `departed`, `arrived`, `delayed`,
`cancelled`.

```bash
curl -X PATCH http://localhost:5000/flights/1/status \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "boarding"}'
```

### Move a flight to another gate (JWT)

Returns `409` when the target gate is not available.

```bash
curl -X PATCH http://localhost:5000/flights/1/gate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"gate_number": "B07"}'
```

## Gates

### List gates

```bash
curl http://localhost:5000/gates
```

## Runways

### List runways

```bash
curl http://localhost:5000/runways
```

### Open or close a runway (JWT)

Allowed values: `available`, `maintenance`, `closed`. The response also
lists the flights assigned to the runway.

```bash
curl -X PATCH http://localhost:5000/runways/1/status \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "closed"}'
```

## Incidents

### List incidents

```bash
curl http://localhost:5000/incidents
```

### Search incidents

Free text across title, description and location.

```bash
curl "http://localhost:5000/incidents/search?q=bird"
```

### Create an incident (JWT)

Severity is one of `low`, `medium`, `high`, `critical`.

```bash
curl -X POST http://localhost:5000/incidents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Gate boarding delay",
    "description": "Boarding paused while ground staff inspect the jet bridge.",
    "severity": "medium",
    "location": "Gate B11"
  }'
```

## Weather

### List weather reports

```bash
curl http://localhost:5000/weather
```

### Create a weather report (JWT)

```bash
curl -X POST http://localhost:5000/weather \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "condition": "partly cloudy",
    "visibility": 8.5,
    "wind_speed": 14.2,
    "temperature": 22.8
  }'
```

## Testing from PowerShell

On Windows, `curl` is an alias for `Invoke-WebRequest` and handles JSON
differently. Use `Invoke-RestMethod` instead.

Get a token once:

```powershell
$login = @{ email = "ops_admin@aeromind.local"; password = "password123" } | ConvertTo-Json
$token = (Invoke-RestMethod -Uri http://localhost:5000/auth/login -Method Post -ContentType "application/json" -Body $login).access_token
$headers = @{ Authorization = "Bearer $token" }
```

Then call any endpoint:

```powershell
# Ask the agent and keep the conversation id
$body = @{ message = "Which flights are delayed?" } | ConvertTo-Json
$answer = Invoke-RestMethod -Uri http://localhost:5000/agent/query -Method Post -ContentType "application/json" -Headers $headers -Body $body
$conversationId = $answer.data.conversation_id
$answer | ConvertTo-Json -Depth 5

# Follow up in the same conversation
$followUp = @{ message = "And which of those are at Terminal B?"; conversation_id = $conversationId } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:5000/agent/query -Method Post -ContentType "application/json" -Headers $headers -Body $followUp | ConvertTo-Json -Depth 5

# Search flights
Invoke-RestMethod -Uri "http://localhost:5000/flights/search?status=delayed"

# Update a flight status
$status = @{ status = "boarding" } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:5000/flights/1/status -Method Patch -ContentType "application/json" -Headers $headers -Body $status
```

The access token expires after one hour; rerun the login block to refresh it.