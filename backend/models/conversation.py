from datetime import datetime, timezone

from database import db


class Conversation(db.Model):
    """A single chat thread between a user and the agent."""

    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    title = db.Column(db.String(160), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("User", backref="conversations")
    messages = db.relationship(
        "Message",
        backref="conversation",
        cascade="all, delete-orphan",
        order_by="Message.id",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "message_count": len(self.messages),
            "created_at": self.created_at.isoformat()
            if self.created_at
            else None,
            "updated_at": self.updated_at.isoformat()
            if self.updated_at
            else None,
        }