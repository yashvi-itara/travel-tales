from flask import render_template, request, current_app, jsonify, redirect, url_for, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required, current_user
import os
import uuid
import random
from app.blueprints.main import main_bp
from app.models import Tale, User, Like, Comment, Recommendation, RecommendationLike, Follow, MeetupRequest, db

@main_bp.route('/')
def index():
    return redirect(url_for('main.explore'))

@main_bp.route('/explore')
def explore():
    return render_template('main/explore.html')

@main_bp.route('/explore/tales')
def get_tales():
    sort_by = request.args.get('sort', 'views')
    category = request.args.get('category', 'all').lower()
    
    query = Tale.query.filter_by(is_public=True)
    
    if category != 'all':
        query = query.filter(Tale.category.ilike(category))
        
    if sort_by == 'newest':
        query = query.order_by(Tale.created_at.desc())
    else:
        query = query.order_by(Tale.views.desc())
        
    tales = query.all()
    
    if not tales:
        # Dummy fallback if DB empty
        all_dummies = [
            {"id": 1, "title": "Kyoto Dreams", "destination": "Kyoto, Japan", "category": "Cultural", "views": 1500, "image_url": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80", "author_name": "Yashvi", "slug": "#"},
            {"id": 2, "title": "Alpine Escapade", "destination": "Swiss Alps", "category": "Mountain", "views": 3210, "image_url": "https://images.unsplash.com/photo-1544645224-fa76840dcf91?w=800&q=80", "author_name": "Wanderer", "slug": "#"},
            {"id": 3, "title": "Bali Bliss", "destination": "Bali, Indonesia", "category": "Beach", "views": 890, "image_url": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800&q=80", "author_name": "Traveler", "slug": "#"},
            {"id": 4, "title": "Midnight in Paris", "destination": "Paris, France", "category": "City", "views": 4320, "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&q=80", "author_name": "Explorer", "slug": "#"},
            {"id": 5, "title": "Route 66 Classic", "destination": "USA", "category": "Road Trip", "views": 560, "image_url": "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800&q=80", "author_name": "Yashvi", "slug": "#"},
            {"id": 6, "title": "Patagonia Trails", "destination": "Patagonia, Chile", "category": "Adventure", "views": 2100, "image_url": "https://images.unsplash.com/photo-1551608779-d3dd6e5667dc?w=800&q=80", "author_name": "Hiker", "slug": "#"},
        ]
        if category != 'all':
            dummy_tales = [d for d in all_dummies if d['category'].lower() == category]
        else:
            dummy_tales = all_dummies
        return render_template('main/partials/_tale_cards.html', dummy_tales=dummy_tales)

    return render_template('main/partials/_tale_cards.html', tales=tales)


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if 'HX-Request' in request.headers:
                response = jsonify({'status': 'success'})
                response.headers['HX-Redirect'] = url_for('main.index')
                return response
            return redirect(url_for('main.index'))
            
        error = 'Invalid email or password'
        if 'HX-Request' in request.headers:
            return render_template('main/partials/_login_form.html', error=error, email=email)
            
    return render_template('main/login.html')


@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            error = 'Email or username already taken!'
            if 'HX-Request' in request.headers:
                return render_template('main/partials/_register_form.html', error=error, email=email, username=username)
            return render_template('main/register.html', error=error)
            
        user = User(username=username, email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        if 'HX-Request' in request.headers:
            response = jsonify({'status': 'success'})
            response.headers['HX-Redirect'] = url_for('main.index')
            return response
        return redirect(url_for('main.index'))
        
    return render_template('main/register.html')


@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}


@main_bp.route('/tale/create', methods=['GET', 'POST'])
@login_required
def create_tale():
    if request.method == 'POST':
        title = request.form.get('title')
        destination = request.form.get('destination')
        category = request.form.get('category', 'Adventure')
        content = request.form.get('content')
        is_public = request.form.get('is_public') == 'on'
        
        if not title:
            title = "Untitled Journey"
            
        slug = title.lower().replace(' ', '-') + '-' + str(uuid.uuid4())[:8]
        
        image_file = request.files.get('image')
        filename = None
        
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            filename = f"{uuid.uuid4().hex}_{filename}"
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            
        tale = Tale(
            title=title, slug=slug, destination=destination,
            category=category, content=content, is_public=is_public,
            image_file=filename, author=current_user
        )
        
        db.session.add(tale)
        db.session.commit()
        
        if 'HX-Request' in request.headers:
            response = jsonify({'status': 'success'})
            response.headers['HX-Redirect'] = url_for('main.view_tale', slug=tale.slug)
            return response
            
        return redirect(url_for('main.view_tale', slug=tale.slug))
        
    return render_template('main/create_tale.html')


@main_bp.route('/tale/<slug>')
def view_tale(slug):
    tale = Tale.query.filter_by(slug=slug).first_or_404()
    
    if not tale.is_public and (not current_user.is_authenticated or current_user.id != tale.user_id):
        flash('This tale is private.', 'error')
        return redirect(url_for('main.index'))
        
    return render_template('main/view_tale.html', tale=tale)


@main_bp.route('/tale/<slug>/view', methods=['POST'])
def record_view(slug):
    tale = Tale.query.filter_by(slug=slug).first_or_404()
    tale.views += 1
    db.session.commit()
    return str(tale.views)


@main_bp.route('/profile')
@login_required
def profile():
    return render_template('main/profile.html')


@main_bp.route('/profile/tales')
@login_required
def profile_tales():
    tab = request.args.get('tab', 'public')
    
    if tab == 'saved':
        tales = current_user.saved.order_by(Tale.created_at.desc()).all()
    else:
        is_public = (tab == 'public')
        tales = Tale.query.filter_by(user_id=current_user.id, is_public=is_public).order_by(Tale.created_at.desc()).all()
    
    return render_template('main/partials/_tale_cards.html', tales=tales)


@main_bp.route('/tale/<int:tale_id>/like', methods=['POST'])
@login_required
def toggle_like(tale_id):
    tale = Tale.query.get_or_404(tale_id)
    like = Like.query.filter_by(user_id=current_user.id, tale_id=tale_id).first()
    
    if like:
        db.session.delete(like)
        is_liked = False
    else:
        new_like = Like(user_id=current_user.id, tale_id=tale_id)
        db.session.add(new_like)
        is_liked = True
        
    db.session.commit()
    
    response = render_template('main/partials/_like_button.html', tale=tale, is_liked=is_liked)
    if is_liked:
        # Trigger a toast notification with HTMX
        import json
        trigger_data = {
            "show-toast": {
                "message": f"Liked! ✨ View {tale.author.username}'s Profile",
                "link": url_for('profiles.public_profile', username=tale.author.username)
            }
        }
        # Flask response objects handle headers easily
        from flask import make_response
        resp = make_response(response)
        resp.headers['HX-Trigger'] = json.dumps(trigger_data)
        return resp
        
    return response


@main_bp.route('/tale/<int:tale_id>/save', methods=['POST'])
@login_required
def toggle_save(tale_id):
    tale = Tale.query.get_or_404(tale_id)
    
    if tale in current_user.saved:
        current_user.saved.remove(tale)
        is_saved = False
    else:
        current_user.saved.append(tale)
        is_saved = True
        
    db.session.commit()
    return render_template('main/partials/_save_button.html', tale=tale, is_saved=is_saved)


@main_bp.route('/tale/<slug>/modal')
def tale_modal(slug):
    tale = Tale.query.filter_by(slug=slug).first_or_404()
    
    if not tale.is_public and (not current_user.is_authenticated or current_user.id != tale.user_id):
        abort(403)
        
    return render_template('main/partials/_tale_modal.html', tale=tale)


@main_bp.route('/tale/<int:tale_id>/comment', methods=['POST'])
@login_required
def post_comment(tale_id):
    tale = Tale.query.get_or_404(tale_id)
    text = request.form.get('text', '').strip()
    
    if not text or len(text) > 500:
        return '<p class="text-red-500 text-sm p-2">Comment must be 1-500 characters.</p>', 400
    
    comment = Comment(text=text, user_id=current_user.id, tale_id=tale.id)
    db.session.add(comment)
    db.session.commit()
    
    return render_template('main/partials/_comment_item.html', comment=comment)


@main_bp.route('/recommendations')
def recommendations():
    return render_template('main/recommendations.html')


@main_bp.route('/recommendations/items')
def get_recommendations():
    sort_by = request.args.get('sort', 'popular')
    category = request.args.get('category', 'all').lower()
    
    query = Recommendation.query
    
    if category != 'all':
        query = query.filter(Recommendation.category.ilike(category))
        
    if sort_by == 'newest':
        query = query.order_by(Recommendation.created_at.desc())
    else:
        query = query.order_by(Recommendation.views.desc())
        
    items = query.all()
    return render_template('main/partials/_recommendation_cards.html', recommendations=items)


@main_bp.route('/recommendations/seed')
def seed_recommendations():
    if Recommendation.query.count() > 0:
        return jsonify({"message": "Already seeded!"})
        
    samples = [
        ("Le Relais de l'Entrecôte", "Legendary steak frites in a classically Parisian bustling atmosphere.", "Food", "Paris", "https://images.unsplash.com/photo-1544148103-0773bf10d330?w=800&q=80"),
        ("Shinjuku Gyoen", "One of Tokyo's largest and most popular parks, stunning during cherry blossom season.", "Hidden Gems", "Tokyo", "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&q=80"),
        ("Ubud Art Market", "Vibrant market filled with silk scarves, lightweight shirts, handmade woven bags.", "Shopping", "Bali", "https://images.unsplash.com/photo-1533900298318-6b8da08a523e?w=800&q=80"),
        ("Table Mountain Cableway", "Iconic flat-topped mountain providing breathtaking views of the city.", "Famous Spots", "Cape Town", "https://images.unsplash.com/photo-1580060839134-75a5edca2e99?w=800&q=80"),
        ("Oia Sunset Viewpoint", "World-renowned spot to watch the sun dip below the Aegean Sea.", "Famous Spots", "Santorini", "https://images.unsplash.com/photo-1469796466635-455ede028aca?w=800&q=80"),
        ("Fushimi Inari-taisha", "Famous shrine with thousands of vermilion torii gates.", "Hidden Gems", "Kyoto", "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80"),
        ("Chelsea Market", "Enclosed food hall with incredible variety.", "Shopping", "New York", "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&q=80"),
        ("Trastevere Trattoria", "Authentic Roman pasta in a charming neighborhood.", "Food", "Rome", "https://images.unsplash.com/photo-1515669097368-22e68427d265?w=800&q=80"),
        ("Seminyak Beach Club", "Luxurious beachfront venue for cocktails and sunsets.", "Food", "Bali", "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800&q=80"),
        ("Louvre Pyramid", "The iconic glass pyramid entrance to the world's largest art museum.", "Famous Spots", "Paris", "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&q=80"),
        ("Nishiki Market", "Kyoto's pantry — a narrow street of more than 100 food shops.", "Food", "Kyoto", "https://images.unsplash.com/photo-1580880916362-e192ff6d8ae1?w=800&q=80"),
        ("Tsukiji Outer Market", "Bustling retail fish market with incredible street food.", "Shopping", "Tokyo", "https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=800&q=80"),
    ]
    
    for name, desc, cat, dest, photo in samples:
        slug = str(uuid.uuid4())[:8] + "-" + name.lower().replace(" ", "-")
        rec = Recommendation(name=name, slug=slug, description=desc, category=cat, destination=dest, photo_url=photo, views=random.randint(50, 5000))
        db.session.add(rec)
        
    db.session.commit()
    return jsonify({"message": f"Seeded {len(samples)} recommendations."})


@main_bp.route('/recommendation/<int:rec_id>/like', methods=['POST'])
@login_required
def like_recommendation(rec_id):
    rec = Recommendation.query.get_or_404(rec_id)
    like = RecommendationLike.query.filter_by(user_id=current_user.id, recommendation_id=rec.id).first()
    
    if like:
        db.session.delete(like)
        is_liked = False
    else:
        new_like = RecommendationLike(user_id=current_user.id, recommendation_id=rec.id)
        db.session.add(new_like)
        is_liked = True
        
    db.session.commit()
    return render_template('main/partials/_rec_like_button.html', rec=rec, is_liked=is_liked)


@main_bp.route('/recommendation/<int:rec_id>/save', methods=['POST'])
@login_required
def save_recommendation(rec_id):
    rec = Recommendation.query.get_or_404(rec_id)
    
    if rec in current_user.saved_recommendations:
        current_user.saved_recommendations.remove(rec)
        is_saved = False
    else:
        current_user.saved_recommendations.append(rec)
        is_saved = True
        
    db.session.commit()
    return render_template('main/partials/_rec_save_button.html', rec=rec, is_saved=is_saved)


# =============================================================
# SEED DATA ROUTE — creates levi user + 40 tales + comments etc.
# =============================================================




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

