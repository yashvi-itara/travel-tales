from flask import Flask
from app.models import db
from flask_login import LoginManager
import os

login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'wanderlust-secret-vibe')
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    default_db_url = 'sqlite:///' + os.path.join(basedir, '..', 'travel_tales.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', default_db_url)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'uploads')

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from app.blueprints.main import main_bp
    app.register_blueprint(main_bp)

    from app.blueprints.meetups import meetups_bp
    app.register_blueprint(meetups_bp)

    from app.blueprints.profiles import profiles_bp
    app.register_blueprint(profiles_bp)

    with app.app_context():
        # In a real app we'd use Flask-Migrate, but for vibes we'll just create the missing table if it doesn't exist.
        db.create_all()

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
