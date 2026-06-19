from flask import Blueprint, jsonify

from models.runway import Runway

runway_bp = Blueprint("runways", __name__)


@runway_bp.get("")
def list_runways():
    runways = Runway.query.order_by(Runway.runway_code.asc()).all()
    return jsonify({"data": [runway.to_dict() for runway in runways]}), 200
