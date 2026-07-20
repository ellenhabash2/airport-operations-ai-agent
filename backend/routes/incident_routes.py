from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from repositories.incident_repository import IncidentRepository
from services.incident_tools import is_valid_severity, search_incidents

incident_bp = Blueprint("incidents", __name__)


@incident_bp.get("")
def list_incidents():
    """
    Return every incident, newest first.
    """
    incidents = IncidentRepository.get_all()
    return jsonify(
        {"data": [incident.to_dict() for incident in incidents]}
    ), 200


@incident_bp.get("/search")
def search_incidents_endpoint():
    """
    Search incidents by free text across title, description and location.
    """
    keyword = request.args.get("q", "")
    result = search_incidents(keyword)

    if isinstance(result, dict) and "error" in result:
        return jsonify(result), 400

    return jsonify({"data": result, "count": len(result)}), 200


@incident_bp.post("")
@jwt_required()
def create_incident():
    """
    Log a new incident.
    """
    payload = request.get_json(silent=True) or {}
    required_fields = ["title", "description", "severity", "location"]
    missing_fields = [
        field for field in required_fields if not payload.get(field)
    ]

    if missing_fields:
        return jsonify(
            {"error": "missing required fields", "fields": missing_fields}
        ), 400

    severity = payload["severity"].lower()

    if not is_valid_severity(severity):
        return jsonify(
            {
                "error": "invalid severity",
                "allowed": ["low", "medium", "high", "critical"],
            }
        ), 400

    incident = IncidentRepository.create(
        title=payload["title"],
        description=payload["description"],
        severity=severity,
        location=payload["location"],
    )

    return jsonify({"data": incident.to_dict()}), 201