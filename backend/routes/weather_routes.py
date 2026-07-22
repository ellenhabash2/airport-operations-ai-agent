import math

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from repositories.weather_repository import WeatherRepository

weather_bp = Blueprint("weather", __name__)


@weather_bp.get("")
def list_weather_reports():
    """
    Return every weather report, newest first.
    """
    reports = WeatherRepository.get_all()
    return jsonify({"data": [report.to_dict() for report in reports]}), 200


@weather_bp.post("")
@jwt_required()
def create_weather_report():
    """
    Record a new weather report.
    """
    payload = request.get_json(silent=True) or {}
    required_fields = ["condition", "visibility", "wind_speed", "temperature"]
    missing_fields = [
        field for field in required_fields if payload.get(field) is None
    ]

    if missing_fields:
        return jsonify(
            {"error": "missing required fields", "fields": missing_fields}
        ), 400

    condition = str(payload["condition"]).strip()
    if not condition:
        return jsonify({"error": "condition is required"}), 400

    try:
        visibility = float(payload["visibility"])
        wind_speed = float(payload["wind_speed"])
        temperature = float(payload["temperature"])
    except (TypeError, ValueError):
        return jsonify({"error": "weather measurements must be numeric"}), 400

    measurements = (visibility, wind_speed, temperature)
    if not all(math.isfinite(value) for value in measurements):
        return jsonify({"error": "weather measurements must be finite"}), 400

    if visibility < 0 or wind_speed < 0:
        return jsonify({"error": "visibility and wind_speed cannot be negative"}), 400

    report = WeatherRepository.create(
        condition=condition,
        visibility=visibility,
        wind_speed=wind_speed,
        temperature=temperature,
    )

    return jsonify({"data": report.to_dict()}), 201
