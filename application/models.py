from datetime import datetime
from .database import db
from .follow import Follow
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin,db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    posts = db.relationship('Post', backref='user', cascade='all,delete')
    comments = db.relationship('Comment', backref='user', cascade='all,delete')
    likes = db.relationship('Like', backref='user', cascade='all,delete')
    followers = db.relationship('Follow', foreign_keys=[
                                Follow.followed_username], backref='followed_user')
    following = db.relationship('Follow', foreign_keys=[
                                Follow.follower_username], backref='follower_user')
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def change_password(self, old_password, new_password):
        if self.check_password(old_password):
            self.password_hash = generate_password_hash(new_password)
            return True
        else:
            return False

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follower_username=self.username,
                            followed_username=user.username,
                            timestamp=datetime.utcnow())
            db.session.add(follow)
            db.session.commit()

    def unfollow(self, user):
        follow = Follow.query.filter_by(follower_username=self.username,
                                         followed_username=user.username).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()

    def is_following(self, user):
         return self.following and any(f.followed_username == user.username for f in self.following)

    def is_followed_by(self, user):
        return any(follower.follower_username == user.username for follower in self.followers)
    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.get(id)


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, db.ForeignKey(
        "users.username"), nullable=False, index=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    image_url = db.Column(db.String)
    comments = db.relationship('Comment', backref='post', cascade='all,delete')
    likes = db.relationship('Like', backref='post', cascade='all,delete')


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey(
        "posts.id"), nullable=False, index=True)
    username = db.Column(db.String, db.ForeignKey(
        "users.username"), nullable=False, index=True)
    comment = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)


class Like(db.Model):
    __tablename__ = "likes"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey(
        "posts.id"), nullable=False, index=True)
    username = db.Column(db.String, db.ForeignKey(
        "users.username"), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)




# User.__table__.create(db.engine, extend_existing=True)


