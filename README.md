# AeroMind - Airport Operations AI Agent

AeroMind is a university final project backend for airport operations management.
This repository contains the Phase 1 foundation plus Phase 2 backend hardening:
project setup, database architecture, authentication, API foundations, Docker
infrastructure, migrations, JSON error handling, and realistic seed data.

Future phases will add AI-agent capabilities. Gemini integration, tool calling,
agent loops, and advanced operations logic are intentionally not implemented yet.

## Tech Stack

- Python 3.12
- Flask
- SQLAlchemy
- PostgreSQL
- Flask-Migrate
- Flask-JWT-Extended
- Docker and Docker Compose

## Project Structure

```text
backend/
├── app.py
├── config.py
├── models/
├── routes/
├── services/
├── database/
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

Build and start the API plus PostgreSQL:

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:5000
```

Health check:

```bash
curl http://localhost:5000/health
```

## Environment Variables

Copy the example file when running locally:

```bash
cp .env.example .env
```

Variables:

- `DATABASE_URL`: SQLAlchemy PostgreSQL connection URL
- `JWT_SECRET_KEY`: secret used to sign JWT access tokens
- `FLASK_ENV`: Flask environment name

Docker Compose provides development defaults, so `docker compose up` works even
before a local `.env` file exists.

## Database Setup

Start the containers:

```bash
docker compose up --build
```

Create migrations the first time:

```bash
docker compose exec api flask db init
docker compose exec api flask db migrate -m "Initial database schema"
docker compose exec api flask db upgrade
```

Equivalent local commands from the `backend/` directory:

```bash
flask db init
flask db migrate -m "Initial database schema"
flask db upgrade
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

## Local Development

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env
cd backend
flask --app app run --debug
```

For local development without Docker, make sure PostgreSQL is running and
`DATABASE_URL` points to your database.

## API Endpoints

Authentication:

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/auth/register` | Register a user with username, email, and password |
| POST | `/auth/login` | Login and receive a JWT access token |

Operations:

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/flights` | List flights |
| GET | `/flights/<id>` | Get one flight |
| GET | `/gates` | List gates |
| GET | `/runways` | List runways |
| GET | `/incidents` | List incidents |
| POST | `/incidents` | Create an incident |
| GET | `/weather` | List weather reports |
| POST | `/weather` | Create a weather report |

See [docs/API_TESTS.md](docs/API_TESTS.md) for copy-pasteable curl requests.

Example register request:

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@example.com","password":"password123"}'
```

Example login request:

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password123"}'
```

Example incident request:

```bash
curl -X POST http://localhost:5000/incidents \
  -H "Content-Type: application/json" \
  -d '{"title":"Gate equipment delay","description":"Jet bridge inspection required.","severity":"medium","location":"Gate A04"}'
```

## Future AI Placeholders

The `backend/services/` package is reserved for future AI-agent services,
including Gemini integration, function tools, tool adapters, and agent
orchestration. The Flask app also contains a Phase 3 TODO where future agent
endpoints can be registered.

Do not add Gemini, tool calling, function tools, or agentic loops to this phase.
