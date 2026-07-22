"""
Shared pytest fixtures for the AeroMind test suite.
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import create_app  # noqa: E402
from config import Config  # noqa: E402
from database import db as _db  # noqa: E402
from models import (  # noqa: E402
    Aircraft,
    Airline,
    Flight,
    Gate,
    Incident,
    Runway,
    Terminal,
    WeatherReport,
)


class TestConfig(Config):
    """Configuration used by the test suite."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    JWT_SECRET_KEY = "test-only-jwt-secret-at-least-32-bytes-long"
    GEMINI_API_KEY = "test-key"


@pytest.fixture
def app():
    """
    Return a Flask app bound to a fresh in-memory database.

    Every test gets its own schema and its own seed data, so tests
    cannot leak state into each other.
    """
    application = create_app(TestConfig)

    with application.app_context():
        _db.create_all()
        _seed_minimal_data()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Return a test client for the app."""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Register a user and return an Authorization header."""
    client.post(
        "/auth/register",
        json={
            "username": "tester",
            "email": "tester@example.com",
            "password": "password123",
        },
    )
    response = client.post(
        "/auth/login",
        json={"email": "tester@example.com", "password": "password123"},
    )
    token = response.get_json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def _seed_minimal_data():
    """
    Insert a small, predictable dataset.

    The production seed script relies on PostgreSQL TRUNCATE, so the
    tests build their own fixtures instead of reusing it.
    """
    airline = Airline(name="Test Air", iata_code="TA", country="Israel")
    terminal_a = Terminal(name="Terminal A", capacity=100)
    terminal_b = Terminal(name="Terminal B", capacity=200)
    _db.session.add_all([airline, terminal_a, terminal_b])
    _db.session.commit()

    aircraft = Aircraft(
        registration_number="4X-TST",
        aircraft_type="A320neo",
        airline_id=airline.id,
        status="available",
    )
    gate_free = Gate(
        gate_number="A01", terminal_id=terminal_a.id, status="available"
    )
    gate_spare = Gate(
        gate_number="A02", terminal_id=terminal_a.id, status="available"
    )
    gate_busy = Gate(
        gate_number="B01", terminal_id=terminal_b.id, status="occupied"
    )
    runway = Runway(runway_code="08L/26R", status="available", length=4000)
    _db.session.add_all(
        [aircraft, gate_free, gate_spare, gate_busy, runway]
    )
    _db.session.commit()

    now = datetime.now(timezone.utc)

    _db.session.add_all(
        [
            Flight(
                flight_number="TA1000",
                airline_id=airline.id,
                aircraft_id=aircraft.id,
                gate_id=gate_free.id,
                runway_id=runway.id,
                origin="TLV",
                destination="CDG",
                departure_time=now,
                arrival_time=now + timedelta(hours=4),
                status="delayed",
            ),
            Flight(
                flight_number="TA1001",
                airline_id=airline.id,
                aircraft_id=aircraft.id,
                gate_id=gate_busy.id,
                runway_id=runway.id,
                origin="CDG",
                destination="TLV",
                departure_time=now,
                arrival_time=now + timedelta(hours=4),
                status="scheduled",
            ),
            WeatherReport(
                condition="fog",
                visibility=1.2,
                wind_speed=15.0,
                temperature=18.0,
            ),
            Incident(
                title="Gate inspection",
                description="Routine jet bridge inspection.",
                severity="low",
                location="Gate A01",
            ),
        ]
    )
    _db.session.commit()
