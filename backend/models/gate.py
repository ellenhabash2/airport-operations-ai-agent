from database import db


class Gate(db.Model):
    __tablename__ = "gates"

    id = db.Column(db.Integer, primary_key=True)
    gate_number = db.Column(db.String(10), unique=True, nullable=False, index=True)
    terminal_id = db.Column(db.Integer, db.ForeignKey("terminals.id"), nullable=False)
    status = db.Column(db.String(40), nullable=False, default="available")

    terminal = db.relationship("Terminal", back_populates="gates")
    flights = db.relationship("Flight", back_populates="gate", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "gate_number": self.gate_number,
            "terminal_id": self.terminal_id,
            "terminal": self.terminal.name if self.terminal else None,
            "status": self.status,
        }
