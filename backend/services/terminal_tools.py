"""
AI tools for querying terminals information.
"""

from repositories.terminal_repository import TerminalRepository


def get_flights_by_terminal(terminal_id: int) -> list[dict] | dict:
    """
    Return all flights assigned to a terminal.
    """
    terminal = TerminalRepository.get_by_id(terminal_id)

    if terminal is None:
        return {
            "error": f"Terminal with id {terminal_id} was not found."
        }

    flights = TerminalRepository.get_flights(terminal_id)

    return [flight.to_dict() for flight in flights]
