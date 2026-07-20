from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from services.agent_service import AgentService
from services.gemini_service import GeminiUnavailableError

agent_bp = Blueprint("agent", __name__)


@agent_bp.post("/query")
@jwt_required()
def query_agent():
    """
    Answer an airport operations question using the AI agent.
    """
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()

    if not message:
        return jsonify({"error": "message is required"}), 400

    try:
        agent = AgentService()
    except RuntimeError as error:
        return jsonify(
            {"error": "agent unavailable", "message": str(error)}
        ), 503

    try:
        result = agent.chat(message)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except GeminiUnavailableError as error:
        return jsonify(
            {
                "error": "ai service unavailable",
                "message": str(error),
                "retryable": True,
            }
        ), 503
    except Exception as error:  # noqa: BLE001 - upstream model failure
        return jsonify(
            {"error": "agent request failed", "message": str(error)}
        ), 502

    return jsonify(
        {
            "data": {
                "answer": result["response"],
                "tool_calls": result["tool_calls"],
            }
        }
    ), 200