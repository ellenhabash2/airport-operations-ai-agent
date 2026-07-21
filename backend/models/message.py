from datetime import datetime, timezone

from database import db


class Message(db.Model):
    """
    One turn of a conversation, stored exactly as Gemini exchanged it.

    `payload` holds the serialised Gemini Content object, so tool calls and
    tool results survive a round trip and can be replayed as history.
    `text` is the readable part, kept separately so the history endpoint
    does not have to parse the payload.
    """

    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey("conversations.id"),
        nullable=False,
        index=True,
    )
    role = db.Column(db.String(20), nullable=False)
    text = db.Column(db.Text, nullable=True)
    payload = db.Column(db.Text, nullable=False)
    tool_calls = db.Column(db.JSON, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "role": self.role,
            "text": self.text,
            "tool_calls": self.tool_calls or [],
            "created_at": self.created_at.isoformat()
            if self.created_at
            else None,
        }
