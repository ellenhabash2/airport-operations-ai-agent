import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from faker import Faker
from sqlalchemy import text

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import create_app
from database import db
from models import (
    Aircraft,
    Airline,
    Flight,
    Gate,
    Incident,
    Runway,
    Terminal,
    WeatherReport,
)

fake = Faker()

AIRPORT_NAME = "AeroMind International Airport"
AIRPORT_CODE = "AMI"


def clear_data():
    db.session.execute(
        text(
            """
            TRUNCATE TABLE
                flights,
                weather_reports,
                incidents,
                gates,
                aircraft,
                runways,
                terminals,
                airlines
            RESTART IDENTITY CASCADE
            """
        )
    )
    db.session.commit()


def seed_airlines():
    airlines = [
        Airline(name="AeroMind Connect", iata_code="AM", country="United States"),
        Airline(name="SkyBridge Airways", iata_code="SB", country="United States"),
        Airline(name="Northstar Air", iata_code="NS", country="Canada"),
        Airline(name="Pacific Wings", iata_code="PW", country="Japan"),
        Airline(name="Atlantic Jet", iata_code="AJ", country="United Kingdom"),
    ]
    db.session.add_all(airlines)
    db.session.commit()
    return airlines


def seed_aircraft(airlines):
    aircraft_types = [
        "Airbus A220-300",
        "Airbus A320neo",
        "Airbus A321neo",
        "Boeing 737-800",
        "Boeing 737 MAX 8",
        "Boeing 787-9",
        "Embraer E195-E2",
    ]
    statuses = ["available", "in_service", "maintenance"]
    aircraft = []

    for airline_index, airline in enumerate(airlines):
        for fleet_index in range(5):
            plane = Aircraft(
                registration_number=f"N{airline_index + 1}{fleet_index + 1:02d}AM",
                aircraft_type=random.choice(aircraft_types),
                airline=airline,
                status=random.choices(statuses, weights=[35, 55, 10], k=1)[0],
            )
            aircraft.append(plane)

    db.session.add_all(aircraft)
    db.session.commit()
    return aircraft


def seed_terminals_and_gates():
    terminals = [
        Terminal(name="Terminal A", capacity=18000),
        Terminal(name="Terminal B", capacity=22000),
        Terminal(name="Terminal C", capacity=16000),
    ]
    db.session.add_all(terminals)
    db.session.commit()

    statuses = ["available", "occupied", "maintenance"]
    gates = []
    for terminal in terminals:
        terminal_letter = terminal.name[-1]
        for gate_index in range(1, 13):
            gate = Gate(
                gate_number=f"{terminal_letter}{gate_index:02d}",
                terminal_id=terminal.id,
                status=random.choices(statuses, weights=[45, 45, 10], k=1)[0],
            )
            gates.append(gate)

    db.session.add_all(gates)
    db.session.commit()
    return terminals, gates


def seed_runways():
    runways = [
        Runway(runway_code="08L/26R", status="available", length=4100),
        Runway(runway_code="08R/26L", status="available", length=3950),
        Runway(runway_code="17/35", status="maintenance", length=3300),
    ]
    db.session.add_all(runways)
    db.session.commit()
    return runways


def seed_flights(airlines, aircraft, gates, runways):
    statuses = ["scheduled", "boarding", "departed", "arrived", "delayed", "cancelled"]
    destinations = [
        "ATL - Hartsfield-Jackson Atlanta International Airport",
        "BOS - Boston Logan International Airport",
        "DEN - Denver International Airport",
        "DFW - Dallas Fort Worth International Airport",
        "JFK - John F. Kennedy International Airport",
        "LAX - Los Angeles International Airport",
        "MIA - Miami International Airport",
        "ORD - Chicago O'Hare International Airport",
        "SEA - Seattle-Tacoma International Airport",
        "SFO - San Francisco International Airport",
        "YYZ - Toronto Pearson International Airport",
        "LHR - London Heathrow Airport",
        "NRT - Narita International Airport",
    ]
    hub = f"{AIRPORT_CODE} - {AIRPORT_NAME}"
    now = datetime.now(timezone.utc)
    flights = []

    aircraft_by_airline = {
        airline.id: [plane for plane in aircraft if plane.airline_id == airline.id]
        for airline in airlines
    }

    for index in range(150):
        airline = airlines[index % len(airlines)]
        plane = random.choice(aircraft_by_airline[airline.id])
        departure_time = now + timedelta(minutes=random.randint(-720, 2160))
        arrival_time = departure_time + timedelta(minutes=random.randint(55, 780))
        paired_airport = random.choice(destinations)

        if index % 2 == 0:
            origin = hub
            destination = paired_airport
        else:
            origin = paired_airport
            destination = hub

        flight = Flight(
            flight_number=f"{airline.iata_code}{2000 + index}",
            airline=airline,
            aircraft=plane,
            gate=random.choice(gates),
            runway=random.choice(runways),
            origin=origin,
            destination=destination,
            departure_time=departure_time,
            arrival_time=arrival_time,
            status=random.choices(
                statuses,
                weights=[35, 12, 18, 18, 13, 4],
                k=1,
            )[0],
        )
        flights.append(flight)

    db.session.add_all(flights)
    db.session.commit()


def seed_weather_reports():
    conditions = [
        "clear",
        "partly cloudy",
        "overcast",
        "light rain",
        "fog",
        "thunderstorms nearby",
        "crosswinds",
    ]
    reports = []

    for _ in range(30):
        report = WeatherReport(
            condition=random.choice(conditions),
            visibility=round(random.uniform(0.4, 10.0), 1),
            wind_speed=round(random.uniform(3, 38), 1),
            temperature=round(random.uniform(-3, 36), 1),
            created_at=fake.date_time_between(
                start_date="-3d",
                end_date="now",
                tzinfo=timezone.utc,
            ),
        )
        reports.append(report)

    db.session.add_all(reports)
    db.session.commit()


def seed_incidents():
    severities = ["low", "medium", "high", "critical"]
    titles = [
        "Passenger assistance request",
        "Ground equipment inspection",
        "Gate boarding delay",
        "Baggage belt service interruption",
        "Runway lighting maintenance",
        "Fuel truck scheduling conflict",
        "Security checkpoint queue alert",
    ]
    locations = [
        "Terminal A departures",
        "Terminal B baggage claim",
        "Terminal C security checkpoint",
        "Gate A04",
        "Gate B11",
        "Gate C08",
        "Runway 08L/26R",
        "Runway 17/35",
        "AeroMind ramp operations",
    ]
    incidents = []

    for _ in range(30):
        incident = Incident(
            title=random.choice(titles),
            description=fake.paragraph(nb_sentences=3),
            severity=random.choices(severities, weights=[45, 35, 15, 5], k=1)[0],
            location=random.choice(locations),
            created_at=fake.date_time_between(
                start_date="-10d",
                end_date="now",
                tzinfo=timezone.utc,
            ),
        )
        incidents.append(incident)

    db.session.add_all(incidents)
    db.session.commit()


def seed_database():
    clear_data()
    airlines = seed_airlines()
    aircraft = seed_aircraft(airlines)
    _, gates = seed_terminals_and_gates()
    runways = seed_runways()
    seed_flights(airlines, aircraft, gates, runways)
    seed_weather_reports()
    seed_incidents()


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_database()
        print("Seed data created successfully for AeroMind International Airport.")
