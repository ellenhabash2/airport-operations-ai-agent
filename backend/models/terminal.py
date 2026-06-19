from database import db


class Terminal(db.Model):
    __tablename__ = "terminals"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    gates = db.relationship("Gate", back_populates="terminal", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "capacity": self.capacity,
        }
