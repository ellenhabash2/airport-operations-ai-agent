# AeroMind - Airport Operations AI Agent

AeroMind is a university final project: an airport operations backend with an
AI agent layer built on the Gemini API.

The backend provides the data foundation (PostgreSQL schema, JWT
authentication, migrations, seed data, REST endpoints) and the agent layer
turns natural-language questions into answers grounded in that data.

The agent exposes 17 function tools and runs a full agentic loop: Gemini
decides which tools to call, the backend executes them against PostgreSQL, the
results are fed back, and the loop repeats until Gemini can answer. Multi-step
reasoning across several tools in a single request is supported.

## Tech Stack

- Python 3.12
- Flask
- SQLAlchemy
- PostgreSQL
- Flask-Migrate
- Flask-JWT-Extended
- Docker and Docker Compose
- Google Gemini API (google-genai)

## Project Structure

```text
backend/
├── app.py
├── config.py
├── models/
├── routes/
├── repositories/
├── services/
├── database/
├── migrations/
├── seed/
├── tests/
└── requirements.txt
docker-compose.yml
Dockerfile
.env.example
README.md
docs/API_TESTS.md
```

## Quick Start With Docker

Copy the environment file and add your Gemini API key:

```bash
cp .env.example .env
```

Build and start the API plus PostgreSQL:

```bash
docker compose up --build
```

The API will be available at `http://localhost:5000`.

Health check:

```bash
curl http://localhost:5000/health
```

## Environment Variables

- `DATABASE_URL`: SQLAlchemy PostgreSQL connection URL
- `JWT_SECRET_KEY`: secret used to sign JWT access tokens
- `FLASK_DEBUG`: set to `1` to enable the reloader and debug output
- `GEMINI_API_KEY`: API key used by the agent, required for `/agent/query`
- `GEMINI_MODEL`: model name, defaults to `gemini-3.5-flash`

Docker Compose provides development defaults for the database and JWT secret,
but `GEMINI_API_KEY` must come from your own `.env` file.

## Database Setup

Apply the migrations:

```bash
docker compose exec api flask db upgrade
```

Seed the database:

```bash
docker compose exec api python seed/seed_data.py
```

The seed script creates:

- 5 airlines
- 25 aircraft
- 3 terminals
- 36 gates
- 3 runways
- 150 flights
- 30 weather reports
- 30 incidents

## AI Agent

The agent is composed of five services under `backend/services/`:

| File | Responsibility |
| --- | --- |
| `gemini_service.py` | Gemini client, tool declarations, model calls |
| `agent_service.py` | The agentic loop and system prompt |
| `tool_registry.py` | Maps tool names to functions and JSON schemas |
| `tool_executor.py` | Executes a tool by name and normalises errors |
| `*_tools.py` | The tools themselves, backed by the repositories |

### How the loop works

```text
User question
    ↓
Gemini (sees all 17 tool declarations)
    ↓
requests one or more tools
    ↓
ToolExecutor → repositories → PostgreSQL
    ↓
results returned to Gemini
    ↓
repeat until Gemini answers (max 5 iterations)
    ↓
Final answer
```

### Available tools

Flights: `get_all_flights`, `get_flight_by_id`, `get_flight_by_number`,
`find_delayed_flights`

Gates: `get_all_gates`, `get_gate_by_id`, `get_gate_by_number`,
`get_available_gates`

Runways: `get_runway_status`, `get_runway_by_id`, `get_runway_by_code`

Terminals: `get_flights_by_terminal`, `get_terminal_status`

Incidents: `get_all_incidents`, `get_incidents_by_severity`, `create_incident`

Weather: `get_latest_weather`

## API Endpoints

Authentication:

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| POST | `/auth/register` | - | Register a user |
| POST | `/auth/login` | - | Login and receive a JWT access token |

AI agent:

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| POST | `/agent/query` | JWT | Ask the agent an operations question |

Operations:

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| GET | `/flights` | - | List flights |
| GET | `/flights/<id>` | - | Get one flight |
| GET | `/gates` | - | List gates |
| GET | `/runways` | - | List runways |
| GET | `/incidents` | - | List incidents |
| POST | `/incidents` | JWT | Create an incident |
| GET | `/weather` | - | List weather reports |
| POST | `/weather` | JWT | Create a weather report |

See [docs/API_TESTS.md](docs/API_TESTS.md) for copy-pasteable curl requests.

### Example: register and login

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@example.com","password":"password123"}'

curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password123"}'
```

### Example: ask the agent

```bash
curl -X POST http://localhost:5000/agent/query \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"message":"Which flights are delayed and which gates are free?"}'
```

The response contains the answer plus the tools the agent executed:

```json
{
  "data": {
    "answer": "...",
    "tool_calls": [
      {"tool": "find_delayed_flights", "arguments": {}, "failed": false},
      {"tool": "get_available_gates", "arguments": {}, "failed": false}
    ]
  }
}
```

## Roadmap

- Conversation memory so the agent can follow up on previous turns
- Automated tests under `backend/tests/`
- React frontend