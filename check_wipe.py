from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    print("Initial User Count:", User.query.count())
    db.session.execute(db.text("DELETE FROM user"))
    db.session.commit()
    print("User Count after wipe:", User.query.count())
    
    # Check if there are ANY users left
    users = db.session.execute(db.text("SELECT * FROM user")).fetchall()
    print(f"Raw query users left: {len(users)}")
    
    try:
        levi = User(username="levi", email="levi@traveltales.com", password_hash="hash")
        db.session.add(levi)
        db.session.commit()
        print("Inserted levi successfully.")
    except Exception as e:
        print(f"Failed to insert levi: {e}")
