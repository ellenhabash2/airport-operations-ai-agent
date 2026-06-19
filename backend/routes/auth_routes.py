from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from sqlalchemy import or_

from database import db
from models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not username or not email or not password:
        return jsonify({"error": "username, email, and password are required"}), 400

    existing_user = User.query.filter(
        or_(User.username == username, User.email == email)
    ).first()
    if existing_user:
        return jsonify({"error": "username or email already exists"}), 409

    user = User(username=username, email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "user registered successfully", "user": user.to_dict()}), 201


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    identifier = (payload.get("username") or payload.get("email") or "").strip()
    password = payload.get("password") or ""

    if not identifier or not password:
        return jsonify({"error": "username/email and password are required"}), 400

    user = User.query.filter(
        or_(User.username == identifier, User.email == identifier.lower())
    ).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": access_token, "user": user.to_dict()}), 200
