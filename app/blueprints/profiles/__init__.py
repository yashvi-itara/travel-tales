from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.models import User, Tale, Follow, Like, Recommendation, db

profiles_bp = Blueprint('profiles', __name__, url_prefix='/user')

from app.blueprints.profiles import routes
