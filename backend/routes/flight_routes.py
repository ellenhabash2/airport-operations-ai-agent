from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from database import db
from models.flight import Flight
from services.flight_tools import (
    assign_flight_to_gate,
    search_flights,
    update_flight_status,
)

flight_bp = Blueprint("flights", __name__)


@flight_bp.get("")
def list_flights():
    flights = Flight.query.order_by(Flight.departure_time.asc()).all()
    return jsonify({"data": [flight.to_dict() for flight in flights]}), 200


@flight_bp.get("/search")
def search_flights_endpoint():
    """
    Search flights by origin, destination, status or airline name.
    """
    result = search_flights(
        origin=request.args.get("origin"),
        destination=request.args.get("destination"),
        status=request.args.get("status"),
        airline_name=request.args.get("airline"),
    )

    if isinstance(result, dict) and "error" in result:
        return jsonify(result), 400

    return jsonify({"data": result, "count": len(result)}), 200


@flight_bp.get("/<int:flight_id>")
def get_flight(flight_id):
    flight = db.session.get(Flight, flight_id)

    if flight is None:
        return jsonify({"error": "resource not found"}), 404

    return jsonify({"data": flight.to_dict()}), 200


@flight_bp.patch("/<int:flight_id>/status")
@jwt_required()
def update_status(flight_id):
    """
    Change the operational status of a flight.
    """
    flight = db.session.get(Flight, flight_id)

    if flight is None:
        return jsonify({"error": "resource not found"}), 404

    payload = request.get_json(silent=True) or {}
    status = (payload.get("status") or "").strip()

    if not status:
        return jsonify({"error": "status is required"}), 400

    result = update_flight_status(flight.flight_number, status)

    if "error" in result:
        return jsonify(result), 400

    return jsonify({"data": result}), 200


@flight_bp.patch("/<int:flight_id>/gate")
@jwt_required()
def reassign_gate(flight_id):
    """
    Move a flight to a different gate.
    """
    flight = db.session.get(Flight, flight_id)

    if flight is None:
        return jsonify({"error": "resource not found"}), 404

    payload = request.get_json(silent=True) or {}
    gate_number = (payload.get("gate_number") or "").strip()

    if not gate_number:
        return jsonify({"error": "gate_number is required"}), 400

    result = assign_flight_to_gate(flight.flight_number, gate_number)

    if "error" in result:
        return jsonify(result), 409

    return jsonify({"data": result}), 200