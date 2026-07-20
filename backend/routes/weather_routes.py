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

    report = WeatherRepository.create(
        condition=payload["condition"],
        visibility=payload["visibility"],
        wind_speed=payload["wind_speed"],
        temperature=payload["temperature"],
    )

    return jsonify({"data": report.to_dict()}), 201