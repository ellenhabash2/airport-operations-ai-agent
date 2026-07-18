"""
AI tools for querying, creating and searching incidents.
"""

from repositories.incident_repository import IncidentRepository


VALID_SEVERITIES = {
    "low",
    "medium",
    "high",
    "critical",
}


def is_valid_severity(severity: str) -> bool:
    """
    Check whether the severity value is valid.
    """
    return severity.lower() in VALID_SEVERITIES


def get_all_incidents() -> list[dict]:
    """
    Return all incidents.
    """
    incidents = IncidentRepository.get_all()
    return [incident.to_dict() for incident in incidents]


def get_incidents_by_severity(severity: str) -> list[dict]:
    """
    Return all incidents with the given severity.
    """
    severity = severity.lower()

    if not is_valid_severity(severity):
        return [
            {
                "error": (
                    "Invalid severity. "
                    "Allowed values are: low, medium, high, critical."
                )
            }
        ]

    incidents = IncidentRepository.get_by_severity(severity)

    return [incident.to_dict() for incident in incidents]


def create_incident(
    title: str,
    description: str,
    severity: str,
    location: str,
) -> dict:
    """
    Create a new incident.
    """
    severity = severity.lower()

    if not is_valid_severity(severity):
        return {
            "error": (
                "Invalid severity. "
                "Allowed values are: low, medium, high, critical."
            )
        }

    incident = IncidentRepository.create(
        title=title,
        description=description,
        severity=severity,
        location=location,
    )

    return incident.to_dict()

def search_incidents(keyword: str) -> list[dict] | dict:
    """
    Search incidents by free text across title, description and location.
    """
    keyword = (keyword or "").strip()

    if not keyword:
        return {"error": "Provide a keyword to search for."}

    incidents = IncidentRepository.search(keyword)

    return [incident.to_dict() for incident in incidents]