import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://aeromind:aeromind@localhost:5432/aeromind",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-in-production")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    JSON_SORT_KEYS = False
