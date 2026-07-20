"""
Conversation memory for the AI agent.

Gemini is stateless: every request must carry the whole conversation.
This service persists each turn and replays it on the next question, so
the agent can answer follow-ups like "and which of those are delayed?".

Turns are stored as the serialised Gemini Content object rather than as
plain text, so tool calls and tool results survive the round trip and the
model sees exactly what it saw the first time.
"""

from google.genai import types

from models.conversation import Conversation
from models.message import Message
from repositories.conversation_repository import ConversationRepository


# How many stored turns are replayed. Older turns are dropped so a long
# thread cannot grow the prompt without bound.
HISTORY_LIMIT = 30

TITLE_MAX_LENGTH = 80


class MemoryService:
    """Loads and stores conversation history."""

    @staticmethod
    def build_title(first_message: str) -> str:
        """
        Derive a readable conversation title from the opening question.
        """
        title = " ".join(first_message.split())

        if len(title) > TITLE_MAX_LENGTH:
            title = f"{title[:TITLE_MAX_LENGTH - 3].rstrip()}..."

        return title or "New conversation"

    @staticmethod
    def load_history(conversation: Conversation) -> list[types.Content]:
        """
        Return the stored turns as Gemini content, oldest first.

        A turn that cannot be parsed is skipped rather than failing the
        request, so one bad row never blocks a conversation.
        """
        messages = ConversationRepository.get_messages(
            conversation.id, limit=HISTORY_LIMIT
        )
        history = []

        for message in messages:
            try:
                history.append(types.Content.model_validate_json(message.payload))
            except ValueError:
                continue

        return history

    @staticmethod
    def record_turns(
        conversation: Conversation,
        contents: list[types.Content],
    ) -> None:
        """
        Persist the turns produced by one exchange.

        Args:
            conversation: The thread the turns belong to.
            contents: The Gemini content added during this exchange.
        """
        messages = [
            Message(
                role=content.role or "user",
                text=MemoryService._readable_text(content),
                payload=content.model_dump_json(exclude_none=True),
            )
            for content in contents
        ]

        ConversationRepository.add_messages(conversation, messages)

    @staticmethod
    def _readable_text(content: types.Content) -> str | None:
        """
        Return the plain text of a turn, if it has any.

        Tool calls and tool results have no text, and are stored with the
        payload only.
        """
        parts = [part.text for part in (content.parts or []) if part.text]

        return "\n".join(parts) if parts else None