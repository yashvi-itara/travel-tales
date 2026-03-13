from app import create_app, db
from app.models import User, Tale, Like, Comment, Follow, Recommendation, RecommendationLike, MeetupRequest
from werkzeug.security import generate_password_hash
import random
import uuid

app = create_app()

with app.app_context():
    print("Wiping data...")
    try:
        Comment.query.delete()
        Like.query.delete()
        Follow.query.delete()
        RecommendationLike.query.delete()
        MeetupRequest.query.delete()
        db.session.execute(db.text("DELETE FROM meetup_joins"))
        db.session.execute(db.text("DELETE FROM saved_tales"))
        db.session.execute(db.text("DELETE FROM saved_recommendations"))
        Tale.query.delete()
        
        # Delete users one by one to see where it fails
        target_emails = ['levi@traveltales.com', 'alice@traveltales.com', 'kai@traveltales.com', 'mia@traveltales.com']
        users = User.query.filter(User.email.in_(target_emails)).all()
        for u in users:
            print(f"Deleting user {u.username}...")
            db.session.delete(u)
            
        db.session.commit()
        print("Data wiped successfully.")
        
        # Now seed... (Wait, I'll just run the actual route logic here or similar)
        print("Starting seed...")
        # ... (I'll skip full tales for diagnostic, just users)
        levi = User(username="levi", email="levi@traveltales.com", password_hash=generate_password_hash("levi123"),
                    bio="Professional wanderer.",
                    avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop&q=80")
        db.session.add(levi)
        db.session.commit()
        print("Seed user created successfully.")
        
    except Exception as e:
        db.session.rollback()
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
