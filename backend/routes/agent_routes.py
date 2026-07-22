import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from repositories.conversation_repository import ConversationRepository
from services.agent_service import AgentService
from services.gemini_service import GeminiUnavailableError
from services.memory_service import MemoryService
from services.presentation_service import PresentationService

agent_bp = Blueprint("agent", __name__)
logger = logging.getLogger(__name__)


def _public_tool_calls(tool_calls):
    """Remove internal tool results before persistence and API exposure."""
    return [
        {key: value for key, value in call.items() if key != "result"}
        for call in (tool_calls or [])
    ]


@agent_bp.post("/query")
@jwt_required()
def query_agent():
    """
    Answer an airport operations question using the AI agent.

    Pass `conversation_id` to continue an existing thread. Omit it to
    start a new one; the id is returned so the next call can continue.
    """
    user_id = int(get_jwt_identity())
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()
    conversation_id = payload.get("conversation_id")

    if not message:
        return jsonify({"error": "message is required"}), 400

    conversation = None
    if conversation_id is not None:
        try:
            conversation_id = int(conversation_id)
        except (TypeError, ValueError):
            return jsonify({"error": "conversation_id must be an integer"}), 400

        conversation = ConversationRepository.get_for_user(
            conversation_id, user_id
        )

        if conversation is None:
            return jsonify({"error": "conversation not found"}), 404

    history = MemoryService.load_history(conversation) if conversation else []

    try:
        agent = AgentService()
    except RuntimeError:
        logger.warning("Agent service is not configured")
        return jsonify({"error": "agent unavailable"}), 503

    try:
        result = agent.chat(message, history=history)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except GeminiUnavailableError:
        return jsonify(
            {
                "error": "ai service unavailable",
                "retryable": True,
            }
        ), 503
    except Exception:  # noqa: BLE001 - log upstream failure, return stable error
        logger.exception("Agent request failed")
        return jsonify({"error": "agent request failed"}), 502

    if conversation is None:
        conversation = ConversationRepository.create(
            user_id=user_id, title=MemoryService.build_title(message)
        )

    presentation = PresentationService.from_tool_calls(result["tool_calls"])
    tool_calls = _public_tool_calls(result["tool_calls"])
    MemoryService.record_turns(
        conversation,
        result["history"][len(history):],
        tool_calls=tool_calls,
        presentation=presentation,
    )

    return jsonify(
        {
            "data": {
                "answer": result["response"],
                "tool_calls": tool_calls,
                "presentation": presentation,
                "conversation_id": conversation.id,
            }
        }
    ), 200


@agent_bp.get("/conversations")
@jwt_required()
def list_conversations():
    """
    Return the signed-in user's conversations, most recent first.
    """
    user_id = int(get_jwt_identity())
    conversations = ConversationRepository.list_for_user(user_id)

    return jsonify(
        {
            "data": [
                conversation.to_dict() for conversation in conversations
            ],
            "count": len(conversations),
        }
    ), 200


@agent_bp.get("/conversations/<int:conversation_id>")
@jwt_required()
def get_conversation(conversation_id):
    """
    Return one conversation with its messages.
    """
    user_id = int(get_jwt_identity())
    conversation = ConversationRepository.get_for_user(conversation_id, user_id)

    if conversation is None:
        return jsonify({"error": "conversation not found"}), 404

    messages = ConversationRepository.get_messages(conversation.id)

    return jsonify(
        {
            "data": {
                **conversation.to_dict(),
                "messages": [message.to_dict() for message in messages],
            }
        }
    ), 200


@agent_bp.delete("/conversations/<int:conversation_id>")
@jwt_required()
def delete_conversation(conversation_id):
    """
    Delete a conversation and its messages.
    """
    user_id = int(get_jwt_identity())
    conversation = ConversationRepository.get_for_user(conversation_id, user_id)

    if conversation is None:
        return jsonify({"error": "conversation not found"}), 404

    ConversationRepository.delete(conversation)

    return jsonify({"message": "conversation deleted"}), 200
