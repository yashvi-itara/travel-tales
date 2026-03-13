from flask import Blueprint

meetups_bp = Blueprint('meetups', __name__, url_prefix='/meetups')

from app.blueprints.meetups import routes
