from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from database import db
from models.incident import Incident

incident_bp = Blueprint("incidents", __name__)


@incident_bp.get("")
def list_incidents():
    incidents = Incident.query.order_by(Incident.created_at.desc()).all()
    return jsonify({"data": [incident.to_dict() for incident in incidents]}), 200


@incident_bp.post("")
@jwt_required()
def create_incident():
    payload = request.get_json(silent=True) or {}
    required_fields = ["title", "description", "severity", "location"]
    missing_fields = [field for field in required_fields if not payload.get(field)]

    if missing_fields:
        return jsonify({"error": "missing required fields", "fields": missing_fields}), 400

    incident = Incident(
        title=payload["title"],
        description=payload["description"],
        severity=payload["severity"],
        location=payload["location"],
    )

    db.session.add(incident)
    db.session.commit()

    return jsonify({"data": incident.to_dict()}), 201
