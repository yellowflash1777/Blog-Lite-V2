from .database import db


class Follow(db.Model):
    __tablename__  = "follows"
    follow_id = db.Column(db.Integer, primary_key=True)
    follower_username = db.Column(
        db.String, db.ForeignKey("users.username"), nullable=False, index=True)
    followed_username = db.Column(
        db.String, db.ForeignKey("users.username"), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    __table_args__ = (db.UniqueConstraint(
        'follower_username', 'followed_username'), {'extend_existing': True})