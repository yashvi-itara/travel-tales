
# Fixed overhaul script with more recs
def get_new_seed_func():
    return """
@main_bp.route('/seed-data')
def seed_data():
    '''Full seed: wipes old test data and creates rich realistic data.'''
    try:
        db.session.rollback()
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
        
        levi = User(username="levi", email="levi@traveltales.com", password_hash=generate_password_hash("levi123"),
                    bio="Professional wanderer and mountain enthusiast. Always searching for the next altitude high.",
                    avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop&q=80")
        alice = User(username="alice_wanders", email="alice@traveltales.com", password_hash=generate_password_hash("alice123"),
                     bio="City guide and coffee shop connoisseur. Finding the heartbeat of every metropolis.",
                     avatar_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&fit=crop&q=80")
        kai = User(username="kai_explores", email="kai@traveltales.com", password_hash=generate_password_hash("kai123"),
                   bio="Filmmaker and adventure seeker. Documenting the world's most remote trails.",
                   avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&q=80")
        mia = User(username="mia_travels", email="mia@traveltales.com", password_hash=generate_password_hash("mia123"),
                   bio="Solo traveler and landscape photographer. Capturing silence and light.",
                   avatar_url="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop&q=80")
        db.session.add_all([levi, alice, kai, mia])
        db.session.commit()

        tale_imgs = [
            "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&q=80",
            "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&q=80",
            "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=800&q=80",
            "https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=800&q=80",
            "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80",
            "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&q=80",
            "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=800&q=80",
            "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=800&q=80",
        ]
        
        import random, uuid
        all_tales = []
        dests = ["Paris, France", "Tokyo, Japan", "Rome, Italy", "London, UK", "New York, USA", "Sydney, Australia", "Cape Town, SA", "Cairo, Egypt", "Bali, Indonesia", "Kyoto, Japan"]
        cats = ["Adventure", "City", "Cultural", "Foodie", "Beach", "Mountain", "Solo", "Road Trip"]
        users = [levi, alice, kai, mia]
        
        for i in range(40):
            u = random.choice(users)
            d = random.choice(dests)
            c = random.choice(cats)
            title = f"Secret {c} in {d} #{i+1}"
            slug = title.lower().replace(' ', '-').replace(',', '').replace('#', '') + '-' + str(uuid.uuid4())[:6]
            content = f"An incredible {c} exploration of {d}. Truly a magical experience."
            img = random.choice(tale_imgs)
            tale = Tale(title=title, slug=slug, destination=d, category=c, content=content, is_public=True, views=random.randint(50, 2500), user_id=u.id)
            tale.image_file = img
            db.session.add(tale)
            all_tales.append(tale)
        
        db.session.commit()

        rec_data = [
            ("The Louvre Pyramid", "Iconic spot for history and architecture.", "Famous Spots", "Paris", "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&q=80"),
            ("Shinjuku Gyoen", "Peaceful oasis in the heart of Tokyo.", "Hidden Gems", "Tokyo", "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&q=80"),
            ("Seminyak Beach", "Perfect waves and stunning sunsets.", "Beach", "Bali", "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800&q=80"),
            ("Table Mountain", "Unbeatable views of the Cape Coast.", "Famous Spots", "Cape Town", "https://images.unsplash.com/photo-1580060839134-75a5edca2e99?w=800&q=80"),
            ("Trastevere Eats", "Best pasta in all of Rome.", "Food", "Rome", "https://images.unsplash.com/photo-1515669097368-22e68427d265?w=800&q=80"),
            ("Harajuku Shopping", "A wild journey into street fashion.", "Shopping", "Tokyo", "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=800&q=80"),
            ("Chelsea Market", "Foodie heaven in NYC.", "Food", "New York", "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&q=80"),
            ("London Eye", "Best view of the Thames.", "Famous Spots", "London", "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=800&q=80"),
            ("Kyoto Bamboo Forest", "A walk through nature's cathedral.", "Hidden Gems", "Kyoto", "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80"),
            ("Bondi Icebergs", "Most photographed pool in the world.", "Famous Spots", "Sydney", "https://images.unsplash.com/photo-1506929113675-8964f7727ec4?w=800&q=80"),
            ("Ubud Art Market", "Handmade treasures and local crafts.", "Shopping", "Bali", "https://images.unsplash.com/photo-1533900298318-6b8da08a523e?w=800&q=80"),
            ("Colosseum Dawn", "Witness history before the crowds arrive.", "Famous Spots", "Rome", "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=800&q=80"),
        ]
        
        for name, desc, cat, dest, img in rec_data:
            slug = str(uuid.uuid4())[:8] + "-" + name.lower().replace(" ", "-")
            rec = Recommendation(name=name, slug=slug, description=desc, category=cat, destination=dest, photo_url=img, views=random.randint(100, 5000), user_id=random.choice(users).id)
            db.session.add(rec)
        
        db.session.commit()

        # Meetups
        for i in range(8):
            d = random.choice(dests)
            meetup = MeetupRequest(
                title=f"Exploring {d.split(',')[0]} Group",
                destination=d,
                description=f"Let's explore {d} together!",
                category=random.choice(cats),
                photo_url=random.choice(tale_imgs),
                user_id=random.choice(users).id
            )
            db.session.add(meetup)
        db.session.commit()

        for tale in all_tales:
            for user in users:
                if user.id != tale.user_id:
                    if random.random() < 0.6: db.session.add(Like(user_id=user.id, tale_id=tale.id))
                    if random.random() < 0.3: user.saved.append(tale)
        
        for u1 in users:
            for u2 in users:
                if u1.id != u2.id and random.random() < 0.7: u1.follow(u2)
        
        db.session.commit()

        return jsonify({"message": "✅ App restored with full social vibe!", "tales": Tale.query.count(), "recs": Recommendation.query.count()})
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
    f.write(get_new_seed_func())
    f.write("\n")
