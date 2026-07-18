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


def get_terminal_status() -> list[dict]:
    """
    Return every terminal with its gate usage summary.
    """
    terminals = TerminalRepository.get_all()
    report = []

    for terminal in terminals:
        gates = terminal.gates or []
        available = [gate for gate in gates if gate.status == "available"]

        report.append(
            {
                "id": terminal.id,
                "name": terminal.name,
                "capacity": terminal.capacity,
                "total_gates": len(gates),
                "available_gates": len(available),
                "available_gate_numbers": [
                    gate.gate_number for gate in available
                ],
            }
        )

    return report