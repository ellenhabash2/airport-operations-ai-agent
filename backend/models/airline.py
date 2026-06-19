from database import db


class Airline(db.Model):
    __tablename__ = "airlines"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    iata_code = db.Column(db.String(3), unique=True, nullable=False, index=True)
    country = db.Column(db.String(80), nullable=False)

    aircraft = db.relationship("Aircraft", back_populates="airline", lazy=True)
    flights = db.relationship("Flight", back_populates="airline", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "iata_code": self.iata_code,
            "country": self.country,
        }
