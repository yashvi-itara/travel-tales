from flask import render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.models import User, Tale, Follow, Recommendation, db
from app.blueprints.profiles import profiles_bp


@profiles_bp.route('/<username>')
def public_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    is_own = current_user.is_authenticated and current_user.id == user.id
    is_following = current_user.is_authenticated and current_user.is_following(user)
    return render_template('profiles/public_profile.html',
                           profile_user=user,
                           is_own=is_own,
                           is_following=is_following)


@profiles_bp.route('/<username>/tales')
def profile_tales(username):
    user = User.query.filter_by(username=username).first_or_404()
    is_own = current_user.is_authenticated and current_user.id == user.id

    if is_own:
        tales = Tale.query.filter_by(user_id=user.id).order_by(Tale.created_at.desc()).all()
    else:
        tales = Tale.query.filter_by(user_id=user.id, is_public=True).order_by(Tale.created_at.desc()).all()

    return render_template('main/partials/_tale_cards.html', tales=tales)


@profiles_bp.route('/<username>/recs')
def profile_recs(username):
    user = User.query.filter_by(username=username).first_or_404()
    recs = Recommendation.query.filter_by(user_id=user.id).order_by(Recommendation.created_at.desc()).all()
    return render_template('main/partials/_recommendation_cards.html', recommendations=recs)


@profiles_bp.route('/<username>/follow', methods=['POST'])
@login_required
def toggle_follow(username):
    user = User.query.filter_by(username=username).first_or_404()

    if user.id == current_user.id:
        return render_template('profiles/partials/_follow_button.html',
                               profile_user=user, is_following=False, error=True)

    if current_user.is_following(user):
        current_user.unfollow(user)
        is_following = False
    else:
        current_user.follow(user)
        is_following = True

    db.session.commit()
    return render_template('profiles/partials/_follow_button.html',
                           profile_user=user, is_following=is_following)
