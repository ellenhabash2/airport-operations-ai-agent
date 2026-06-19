from flask import Blueprint, jsonify

from models.flight import Flight

flight_bp = Blueprint("flights", __name__)


@flight_bp.get("")
def list_flights():
    flights = Flight.query.order_by(Flight.departure_time.asc()).all()
    return jsonify({"data": [flight.to_dict() for flight in flights]}), 200


@flight_bp.get("/<int:flight_id>")
def get_flight(flight_id):
    flight = Flight.query.get_or_404(flight_id)
    return jsonify({"data": flight.to_dict()}), 200
