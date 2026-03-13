from flask import render_template, request, jsonify, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from datetime import date, datetime
import uuid, random
from app.blueprints.meetups import meetups_bp
from app.models import MeetupRequest, db


@meetups_bp.route('/')
def index():
    return render_template('meetups/index.html')


@meetups_bp.route('/items')
def get_meetups():
    sort_by = request.args.get('sort', 'newest')
    category = request.args.get('category', 'all').lower()
    destination = request.args.get('destination', '').strip()

    query = MeetupRequest.query.filter_by(status='open')

    if category != 'all':
        query = query.filter(MeetupRequest.category.ilike(category))
    if destination:
        query = query.filter(MeetupRequest.destination.ilike(f'%{destination}%'))

    if sort_by == 'soonest':
        query = query.order_by(MeetupRequest.start_date.asc())
    elif sort_by == 'responses':
        # Sort by number of attendees
        query = query.order_by(MeetupRequest.created_at.desc())  # fallback
    else:  # newest
        query = query.order_by(MeetupRequest.created_at.desc())

    meetups = query.all()
    return render_template('meetups/partials/_meetup_cards.html', meetups=meetups)


@meetups_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_meetup():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        destination = request.form.get('destination', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'Adventure')
        photo_url = request.form.get('photo_url', '').strip() or None

        start_str = request.form.get('start_date', '')
        end_str = request.form.get('end_date', '')

        try:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date() if start_str else None
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date() if end_str else None
        except ValueError:
            start_date = end_date = None

        if not title or not destination or not description:
            if 'HX-Request' in request.headers:
                return '<p class="text-red-500 text-sm mt-2">Please fill in all required fields.</p>', 400
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('meetups.index'))

        meetup = MeetupRequest(
            title=title,
            destination=destination,
            description=description,
            category=category,
            photo_url=photo_url,
            start_date=start_date,
            end_date=end_date,
            user_id=current_user.id
        )
        db.session.add(meetup)
        db.session.commit()

        if 'HX-Request' in request.headers:
            response = jsonify({'status': 'ok'})
            response.headers['HX-Redirect'] = url_for('meetups.index')
            return response

        flash('Your meetup is live! 🎉', 'success')
        return redirect(url_for('meetups.index'))

    return render_template('meetups/create.html')


@meetups_bp.route('/<int:meetup_id>/join', methods=['POST'])
@login_required
def join_meetup(meetup_id):
    meetup = MeetupRequest.query.get_or_404(meetup_id)

    if meetup.user_id == current_user.id:
        return render_template('meetups/partials/_join_button.html',
                               meetup=meetup, status='own'), 200

    already_joined = current_user in meetup.attendees
    if already_joined:
        meetup.attendees.remove(current_user)
        joined = False
    else:
        meetup.attendees.append(current_user)
        joined = True

    db.session.commit()
    return render_template('meetups/partials/_join_button.html',
                           meetup=meetup, status='joined' if joined else 'open')


@meetups_bp.route('/seed')
def seed_meetups():
    if MeetupRequest.query.count() > 0:
        return jsonify({'message': 'Already seeded!'})

    # We need at least one user to be organizer
    from app.models import User
    admin = User.query.first()
    if not admin:
        return jsonify({'message': 'Create a user first!'}), 400

    samples = [
        ("Sunrise Hike in the Atlas Mountains", "Morocco", "2026-04-10", "2026-04-17",
         "Join me for an epic 7-day trek through the Atlas Mountains. All fitness levels welcome. Let's watch sunrise together from 4000m!", "Hiking",
         "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800&q=80"),
        ("Bali Foodie Week 🍜", "Bali, Indonesia", "2026-05-01", "2026-05-07",
         "A curated food tour across Bali's best warungs, cooking classes, and night markets. Meet fellow foodies!", "Food Tour",
         "https://images.unsplash.com/photo-1580880916362-e192ff6d8ae1?w=800&q=80"),
        ("Tokyo Cherry Blossom Squad 🌸", "Tokyo, Japan", "2026-03-25", "2026-04-05",
         "Experience Japanese Hanami (flower viewing parties) in Shinjuku Gyoen and Ueno Park with a group of travel lovers.", "Cultural",
         "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&q=80"),
        ("Santorini Sunset Photos 📸", "Santorini, Greece", "2026-06-15", "2026-06-22",
         "Photography enthusiasts and sunset chasers wanted! We'll visit Oia, Fira, and all the hidden white-washed alleyways.", "Photography",
         "https://images.unsplash.com/photo-1469796466635-455ede028aca?w=800&q=80"),
        ("Cape Town Adventure Week 🏄", "Cape Town, South Africa", "2026-07-01", "2026-07-08",
         "Surfing, hiking Table Mountain, wine tasting in Stellenbosch and penguin spotting at Boulders Beach!", "Adventure",
         "https://images.unsplash.com/photo-1580060839134-75a5edca2e99?w=800&q=80"),
        ("Kyoto Cultural Immersion 🏯", "Kyoto, Japan", "2026-04-20", "2026-04-27",
         "Tea ceremonies, traditional ryokan stays, samurai sword lessons and exploring ancient temples with a small intimate group.", "Cultural",
         "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80"),
        ("Patagonia Backpacking 🏔️", "Patagonia, Chile", "2026-11-01", "2026-11-14",
         "14 days across Torres del Paine. Looking for experienced hikers who are comfortable camping in the wild.", "Hiking",
         "https://images.unsplash.com/photo-1551608779-d3dd6e5667dc?w=800&q=80"),
        ("New York Food Crawl 🥐", "New York, USA", "2026-04-01", "2026-04-03",
         "Weekend trip through NYC's boroughs for the best hot dogs, pizza, bagels, dim sum, and everything in between.", "Food Tour",
         "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&q=80"),
    ]

    for title, dest, start_str, end_str, desc, cat, photo in samples:
        meetup = MeetupRequest(
            title=title,
            destination=dest,
            start_date=datetime.strptime(start_str, '%Y-%m-%d').date(),
            end_date=datetime.strptime(end_str, '%Y-%m-%d').date(),
            description=desc,
            category=cat,
            photo_url=photo,
            user_id=admin.id
        )
        db.session.add(meetup)

    db.session.commit()
    return jsonify({'message': f'Seeded {len(samples)} meetups!'})
