from database import db


class Flight(db.Model):
    __tablename__ = "flights"

    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(12), unique=True, nullable=False, index=True)
    airline_id = db.Column(db.Integer, db.ForeignKey("airlines.id"), nullable=False)
    aircraft_id = db.Column(db.Integer, db.ForeignKey("aircraft.id"), nullable=False)
    gate_id = db.Column(db.Integer, db.ForeignKey("gates.id"), nullable=False)
    runway_id = db.Column(db.Integer, db.ForeignKey("runways.id"), nullable=False)
    origin = db.Column(db.String(80), nullable=False)
    destination = db.Column(db.String(80), nullable=False)
    departure_time = db.Column(db.DateTime(timezone=True), nullable=False)
    arrival_time = db.Column(db.DateTime(timezone=True), nullable=False)
    status = db.Column(db.String(40), nullable=False, default="scheduled")

    airline = db.relationship("Airline", back_populates="flights")
    aircraft = db.relationship("Aircraft", back_populates="flights")
    gate = db.relationship("Gate", back_populates="flights")
    runway = db.relationship("Runway", back_populates="flights")

    def to_dict(self):
        return {
            "id": self.id,
            "flight_number": self.flight_number,
            "airline_id": self.airline_id,
            "airline_name": self.airline.name if self.airline else None,
            "aircraft_id": self.aircraft_id,
            "aircraft_registration": self.aircraft.registration_number
            if self.aircraft
            else None,
            "aircraft_type": self.aircraft.aircraft_type if self.aircraft else None,
            "gate_id": self.gate_id,
            "gate_number": self.gate.gate_number if self.gate else None,
            "terminal": self.gate.terminal.name if self.gate and self.gate.terminal else None,
            "runway_id": self.runway_id,
            "runway_code": self.runway.runway_code if self.runway else None,
            "origin": self.origin,
            "destination": self.destination,
            "departure_time": self.departure_time.isoformat()
            if self.departure_time
            else None,
            "arrival_time": self.arrival_time.isoformat() if self.arrival_time else None,
            "status": self.status,
        }
