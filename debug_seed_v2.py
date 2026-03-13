from app import create_app, db
from app.models import User, Tale, Like, Comment, Follow, Recommendation, RecommendationLike, MeetupRequest
from werkzeug.security import generate_password_hash
import sqlalchemy

app = create_app()

with app.app_context():
    print("Doing fresh wipe...")
    tables = [
        'comment', 'like', 'follow', 'recommendation_like', 
        'meetup_joins', 'saved_tales', 'saved_recommendations',
        'meetup_request', 'tale', 'recommendation', 'user'
    ]
    for table in tables:
        try:
            db.session.execute(db.text(f"DELETE FROM {table}"))
        except Exception as e:
            print(f"Delete failed for {table}: {e}")
            
    db.session.commit()
    print("Wipe committed.")
    
    print("Attempting to insert 'levi'...")
    try:
        levi = User(username="levi", email="levi@traveltales.com", password_hash=generate_password_hash("levi123"),
                    bio="Professional wanderer.",
                    avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop&q=80")
        db.session.add(levi)
        db.session.commit()
        print("Success: Levi created.")
    except sqlalchemy.exc.IntegrityError as e:
        db.session.rollback()
        print(f"INTEGRITY ERROR: {e}")
    except Exception as e:
        db.session.rollback()
        print(f"OTHER ERROR: {e}")
