from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# --- Association Tables ---

saved_tales = db.Table('saved_tales',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('tale_id', db.Integer, db.ForeignKey('tale.id'), primary_key=True)
)

saved_recommendations = db.Table('saved_recommendations',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('recommendation_id', db.Integer, db.ForeignKey('recommendation.id'), primary_key=True)
)

meetup_joins = db.Table('meetup_joins',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('meetup_id', db.Integer, db.ForeignKey('meetup_request.id'), primary_key=True)
)


# --- Main Models ---

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    bio = db.Column(db.String(300), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)  # Optional external avatar

    # Tale relationships
    tales = db.relationship('Tale', backref='author', lazy='dynamic')
    likes = db.relationship('Like', backref='user', lazy='dynamic', foreign_keys='Like.user_id')
    saved = db.relationship('Tale', secondary=saved_tales, lazy='dynamic', backref=db.backref('saved_by', lazy='dynamic'))
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    # Recommendation relationships
    recommendation_likes = db.relationship('RecommendationLike', backref='user', lazy='dynamic')
    saved_recommendations = db.relationship('Recommendation', secondary=saved_recommendations, lazy='dynamic', backref=db.backref('saved_by', lazy='dynamic'))

    # Meetup relationships
    meetups_created = db.relationship('MeetupRequest', backref='organizer', lazy='dynamic', foreign_keys='MeetupRequest.user_id')
    meetups_joined = db.relationship('MeetupRequest', secondary=meetup_joins, lazy='dynamic', backref=db.backref('attendees', lazy='dynamic'))

    # Follow relationships
    following = db.relationship(
        'Follow', foreign_keys='Follow.follower_id',
        backref=db.backref('follower', lazy='joined'),
        lazy='dynamic', cascade='all, delete-orphan'
    )
    followers = db.relationship(
        'Follow', foreign_keys='Follow.followed_id',
        backref=db.backref('followed', lazy='joined'),
        lazy='dynamic', cascade='all, delete-orphan'
    )

    def is_following(self, user):
        return self.following.filter_by(followed_id=user.id).first() is not None

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower_id=self.id, followed_id=user.id)
            db.session.add(f)

    def unfollow(self, user):
        f = self.following.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def total_likes_received(self):
        return Like.query.join(Tale).filter(Tale.user_id == self.id).count()

    def places_visited(self):
        return self.tales.with_entities(Tale.destination).distinct().count()

    def __repr__(self):
        return f'<User {self.username}>'


class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('follower_id', 'followed_id', name='unique_follow'),)


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tale_id = db.Column(db.Integer, db.ForeignKey('tale.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'tale_id', name='unique_user_tale_like'),)


class Tale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    slug = db.Column(db.String(140), unique=True)
    destination = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), default='Adventure')
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(500), nullable=True)
    is_public = db.Column(db.Boolean, default=True)
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    likes = db.relationship('Like', backref='tale', lazy='dynamic', foreign_keys='Like.tale_id')
    comments = db.relationship('Comment', backref='tale', lazy='dynamic', order_by='Comment.created_at.asc()')

    def image_url(self):
        if self.image_file:
            if self.image_file.startswith('http'):
                return self.image_file
            if self.image_file.startswith('__ext__'):
                return self.image_file[7:]
            from flask import url_for
            try:
                return url_for('static', filename='uploads/' + self.image_file)
            except:
                pass
        return 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&q=80'

    def __repr__(self):
        return f'<Tale {self.title}>'


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tale_id = db.Column(db.Integer, db.ForeignKey('tale.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MeetupRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='Adventure')
    photo_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default='open')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def display_image(self):
        if self.photo_url:
            return self.photo_url
        return 'https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=800&q=80'


class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(140), unique=True, nullable=False)
    name = db.Column(db.String(140), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    photo_url = db.Column(db.String(500), nullable=True)
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    likes = db.relationship('RecommendationLike', backref='recommendation', lazy='dynamic')

    @property
    def display_image(self):
        if self.photo_url:
            return self.photo_url
        return 'https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?w=800&q=80'


class RecommendationLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recommendation_id = db.Column(db.Integer, db.ForeignKey('recommendation.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
