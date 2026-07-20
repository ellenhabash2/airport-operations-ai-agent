from flask import Blueprint, jsonify

from repositories.gate_repository import GateRepository

gate_bp = Blueprint("gates", __name__)


@gate_bp.get("")
def list_gates():
    """
    Return every gate with its terminal.
    """
    gates = GateRepository.get_all()
    return jsonify({"data": [gate.to_dict() for gate in gates]}), 200