from .database import db


class Follow(db.Model):
    __tablename__  = "follows"
    id = db.Column(db.Integer, primary_key=True)
    follower_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    followed_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    __table_args__ = (db.UniqueConstraint(
        'follower_user_id', 'followed_user_id'), {'extend_existing': True})