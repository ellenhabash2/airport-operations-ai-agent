from flask import Blueprint, jsonify

from models.gate import Gate

gate_bp = Blueprint("gates", __name__)


@gate_bp.get("")
def list_gates():
    gates = Gate.query.order_by(Gate.gate_number.asc()).all()
    return jsonify({"data": [gate.to_dict() for gate in gates]}), 200
