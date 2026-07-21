from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest

from config import Config
from database import db, migrate
import models  # noqa: F401
from routes.agent_routes import agent_bp
from routes.auth_routes import auth_bp
from routes.flight_routes import flight_bp
from routes.gate_routes import gate_bp
from routes.incident_routes import incident_bp
from routes.runway_routes import runway_bp
from routes.terminal_routes import terminal_bp
from routes.weather_routes import weather_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.json.sort_keys = False

    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager(app)

    # The React client runs on a different origin, so browser requests
    # need explicit CORS permission for the Authorization header.
    CORS(
        app,
        origins=app.config["CORS_ORIGINS"],
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        supports_credentials=False,
    )

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(agent_bp, url_prefix="/agent")
    app.register_blueprint(flight_bp, url_prefix="/flights")
    app.register_blueprint(gate_bp, url_prefix="/gates")
    app.register_blueprint(runway_bp, url_prefix="/runways")
    app.register_blueprint(terminal_bp, url_prefix="/terminals")
    app.register_blueprint(incident_bp, url_prefix="/incidents")
    app.register_blueprint(weather_bp, url_prefix="/weather")

    @app.get("/")
    def index():
        return jsonify(
            {
                "service": "AeroMind API",
                "status": "running",
                "health": "/health",
                "endpoints": [
                    "POST /auth/register",
                    "POST /auth/login",
                    "PATCH /auth/me",
                    "POST /agent/query",
                    "GET /agent/conversations",
                    "GET /agent/conversations/<id>",
                    "DELETE /agent/conversations/<id>",
                    "GET /flights",
                    "GET /flights/search",
                    "GET /flights/<id>",
                    "PATCH /flights/<id>/status",
                    "PATCH /flights/<id>/gate",
                    "GET /gates",
                    "GET /runways",
                    "PATCH /runways/<id>/status",
                    "GET /terminals",
                    "GET /terminals/<id>/flights",
                    "GET /incidents",
                    "GET /incidents/search",
                    "POST /incidents",
                    "GET /weather",
                    "POST /weather",
                ],
            }
        ), 200

    @app.get("/health")
    def health_check():
        """
        Report service health, including database connectivity.
        """
        try:
            db.session.execute(text("SELECT 1"))
        except SQLAlchemyError:
            db.session.rollback()
            return jsonify(
                {
                    "status": "unavailable",
                    "service": "AeroMind API",
                    "database": "unreachable",
                }
            ), 503

        return jsonify(
            {
                "status": "ok",
                "service": "AeroMind API",
                "database": "ok",
            }
        ), 200

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "resource not found"}), 404

    @app.errorhandler(BadRequest)
    def bad_request(error):
        return jsonify({"error": "bad request", "message": error.description}), 400

    @app.errorhandler(SQLAlchemyError)
    def database_error(error):
        db.session.rollback()
        return jsonify({"error": "database error"}), 500

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({"error": "internal server error"}), 500

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000)