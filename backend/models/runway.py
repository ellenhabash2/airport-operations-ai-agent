from database import db


class Runway(db.Model):
    __tablename__ = "runways"

    id = db.Column(db.Integer, primary_key=True)
    runway_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    status = db.Column(db.String(40), nullable=False, default="available")
    length = db.Column(db.Integer, nullable=False)

    flights = db.relationship("Flight", back_populates="runway", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "runway_code": self.runway_code,
            "status": self.status,
            "length": self.length,
        }
