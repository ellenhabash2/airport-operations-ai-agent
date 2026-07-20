"""
Database access layer for Conversation and Message entities.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import joinedload

from database import db
from models.conversation import Conversation
from models.message import Message


class ConversationRepository:
    """Repository for conversation database operations."""

    @staticmethod
    def create(user_id: int, title: str) -> Conversation:
        """
        Start a new conversation for a user.
        """
        conversation = Conversation(user_id=user_id, title=title)

        db.session.add(conversation)
        db.session.commit()

        return conversation

    @staticmethod
    def get_for_user(conversation_id: int, user_id: int) -> Conversation | None:
        """
        Return a conversation only if it belongs to the given user.

        Scoping the lookup by owner keeps one user from reading another
        user's history by guessing an id.
        """
        return (
            Conversation.query
            .options(joinedload(Conversation.messages))
            .filter(Conversation.id == conversation_id)
            .filter(Conversation.user_id == user_id)
            .first()
        )

    @staticmethod
    def list_for_user(user_id: int) -> list[Conversation]:
        """
        Return a user's conversations, most recently used first.
        """
        return (
            Conversation.query
            .options(joinedload(Conversation.messages))
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .all()
        )

    @staticmethod
    def get_messages(conversation_id: int, limit: int | None = None) -> list[Message]:
        """
        Return a conversation's messages in order.

        When a limit is given the most recent messages are returned, still
        in chronological order, so a long thread does not grow the prompt
        without bound.
        """
        query = (
            Message.query
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.id.desc())
        )

        if limit is not None:
            query = query.limit(limit)

        return list(reversed(query.all()))

    @staticmethod
    def add_messages(conversation: Conversation, messages: list[Message]) -> None:
        """
        Append messages to a conversation and mark it as just used.
        """
        for message in messages:
            message.conversation_id = conversation.id
            db.session.add(message)

        conversation.updated_at = datetime.now(timezone.utc)
        db.session.commit()

    @staticmethod
    def delete(conversation: Conversation) -> None:
        """
        Delete a conversation and everything in it.
        """
        db.session.delete(conversation)
        db.session.commit()