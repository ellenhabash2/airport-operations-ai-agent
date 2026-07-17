"""
AI tools for querying gates information.
"""

from repositories.gate_repository import GateRepository


def get_all_gates() -> list[dict]:
    """
    Return all gates.
    """
    gates = GateRepository.get_all()
    return [gate.to_dict() for gate in gates]


def get_gate_by_id(gate_id: int) -> dict:
    """
    Return a gate by its ID.
    """
    gate = GateRepository.get_by_id(gate_id)

    if gate is None:
        return {
            "error": f"Gate with id {gate_id} was not found."
        }

    return gate.to_dict()


def get_gate_by_number(gate_number: str) -> dict:
    """
    Return a gate by its gate number.
    """
    gate = GateRepository.get_by_gate_number(gate_number)

    if gate is None:
        return {
            "error": f"Gate '{gate_number}' was not found."
        }

    return gate.to_dict()


def get_available_gates() -> list[dict]:
    """
    Return all available gates.
    """
    gates = GateRepository.get_available()
    return [gate.to_dict() for gate in gates]