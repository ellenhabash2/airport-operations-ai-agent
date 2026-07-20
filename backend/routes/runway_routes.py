from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from repositories.runway_repository import RunwayRepository
from services.runway_tools import update_runway_status

runway_bp = Blueprint("runways", __name__)


@runway_bp.get("")
def list_runways():
    """
    Return every runway with its current status.
    """
    runways = RunwayRepository.get_all()
    return jsonify({"data": [runway.to_dict() for runway in runways]}), 200


@runway_bp.patch("/<int:runway_id>/status")
@jwt_required()
def update_status(runway_id):
    """
    Open or close a runway and report the flights it affects.
    """
    runway = RunwayRepository.get_by_id(runway_id)

    if runway is None:
        return jsonify({"error": "resource not found"}), 404

    payload = request.get_json(silent=True) or {}
    status = (payload.get("status") or "").strip()

    if not status:
        return jsonify({"error": "status is required"}), 400

    result = update_runway_status(runway.runway_code, status)

    if "error" in result:
        return jsonify(result), 400

    return jsonify({"data": result}), 200