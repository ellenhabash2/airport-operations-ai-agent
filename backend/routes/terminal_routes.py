from flask import Blueprint, jsonify

from repositories.terminal_repository import TerminalRepository
from services.terminal_tools import get_terminal_status

terminal_bp = Blueprint("terminals", __name__)


@terminal_bp.get("")
def list_terminals():
    """
    Return every terminal with its capacity and gate availability.
    """
    return jsonify({"data": get_terminal_status()}), 200


@terminal_bp.get("/<int:terminal_id>/flights")
def list_terminal_flights(terminal_id):
    """
    Return every flight departing from or arriving at a terminal.
    """
    terminal = TerminalRepository.get_by_id(terminal_id)

    if terminal is None:
        return jsonify({"error": "resource not found"}), 404

    flights = TerminalRepository.get_flights(terminal_id)

    return jsonify(
        {
            "data": [flight.to_dict() for flight in flights],
            "count": len(flights),
            "terminal": terminal.to_dict(),
        }
    ), 200