
# Finalized seed_data route
def get_new_func():
    return """
@main_bp.route('/seed-data')
def seed_data():
    \"\"\"Full seed: wipes old test data and creates rich realistic data.\"\"\"
    try:
        # Clear session to avoid stale objects
        db.session.rollback()
        # --- Wipe ALL relevant data via raw SQL ---
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
        
        # --- Create Users ---
        levi = User(username="levi", email="levi@traveltales.com", password_hash=generate_password_hash("levi123"),
                    bio="Professional wanderer and mountain enthusiast.",
                    avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop&q=80")
        alice = User(username="alice_wanders", email="alice@traveltales.com", password_hash=generate_password_hash("alice123"),
                     bio="City guide and coffee shop connoisseur.",
                     avatar_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&fit=crop&q=80")
        kai = User(username="kai_explores", email="kai@traveltales.com", password_hash=generate_password_hash("kai123"),
                   bio="Filmmaker and adventure seeker.",
                   avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&q=80")
        mia = User(username="mia_travels", email="mia@traveltales.com", password_hash=generate_password_hash("mia123"),
                   bio="Solo traveler and landscape photographer.",
                   avatar_url="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop&q=80")
        db.session.add_all([levi, alice, kai, mia])
        db.session.commit()

        import random, uuid
        all_tales = []
        dests = ["Paris, France", "Tokyo, Japan", "Rome, Italy", "London, UK", "New York, USA", "Sydney, Australia", "Cape Town, SA", "Cairo, Egypt"]
        cats = ["Adventure", "City", "Cultural", "Foodie", "Beach", "Mountain"]
        users = [levi, alice, kai, mia]
        
        for i in range(40):
            u = random.choice(users)
            d = random.choice(dests)
            c = random.choice(cats)
            title = f"Magic in {d} #{i+1}"
            slug = title.lower().replace(' ', '-').replace(',', '').replace('#', '') + '-' + str(uuid.uuid4())[:6]
            tale = Tale(title=title, slug=slug, destination=d, category=c, content=f"An amazing {c} journey in {d}.", is_public=True, views=random.randint(50, 500), user_id=u.id)
            tale.image_file = f"__ext__https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&q=80"
            db.session.add(tale)
            all_tales.append(tale)
        
        db.session.commit()

        # --- Social ---
        for tale in all_tales:
            for user in users:
                if user.id != tale.user_id and random.random() < 0.6:
                    db.session.add(Like(user_id=user.id, tale_id=tale.id))
                if user.id != tale.user_id and random.random() < 0.3:
                    user.saved.append(tale)
        
        for u1 in users:
            for u2 in users:
                if u1.id != u2.id and random.random() < 0.7: u1.follow(u2)
        
        db.session.commit()
        return jsonify({"message": "✅ Seeded successfully!", "tales": Tale.query.count()})
    except Exception as e:
        import traceback
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e), "traceback": traceback.format_exc()}), 500
"""

with open(r'app/blueprints/main/routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

marker = "@main_bp.route('/seed-data')"
header = content.split(marker)[0]

with open(r'app/blueprints/main/routes.py', 'w', encoding='utf-8') as f:
    f.write(header)
    f.write(get_new_func())
