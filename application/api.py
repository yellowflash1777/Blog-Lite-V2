from flask_restful import Resource, Api
from flask_restful import marshal_with,fields,reqparse
from application.database import db
from application.models import Post, User
from flask_cors import cross_origin

from application.validation import BadError, NotFoundError

#feilds
user_fields = {
    'user_id': fields.Integer,
    'username': fields.String,
    'password': fields.String,
    'number_of_posts': fields.Integer,
    'number_of_followers': fields.Integer,
    'number_of_following': fields.Integer,
}

post_fields = {
    'post_id': fields.Integer,
    'username': fields.String,
    'title': fields.String,
    'content': fields.String,
    'timestamp': fields.DateTime,
    'image_url': fields.String,
    'number_of_likes': fields.Integer,
    'number_of_comments': fields.Integer,
}

create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument('username')
create_user_parser.add_argument('password')
create_user_parser.add_argument('number_of_posts')
create_user_parser.add_argument('number_of_followers')
create_user_parser.add_argument('number_of_following')


create_post_parser = reqparse.RequestParser()
create_post_parser.add_argument('username')
create_post_parser.add_argument('title')
create_post_parser.add_argument('content')
create_post_parser.add_argument('timestamp')
create_post_parser.add_argument('image_url')
create_post_parser.add_argument('number_of_likes')
create_post_parser.add_argument('number_of_comments')



class UserAPI(Resource):
    
    @cross_origin(supports_credentials=True)
    @marshal_with(user_fields)
    def get(self,user_id):
        user=User.query.filter_by(user_id=user_id).first()
        if user:
            return user
        else:
            raise NotFoundError(status_code=404)
    
    @cross_origin(supports_credentials=True)
    @marshal_with(user_fields)
    def put(self,user_id):
        args=create_user_parser.parse_args()
        user=User.query.filter_by(user_id=user_id).first()
        if user:
            user.password=args['password']
            db.session.commit()
            return user
        else:
            raise NotFoundError(status_code=404)
      
    @cross_origin(supports_credentials=True)
    def delete(self,user_id):
        user=User.query.filter_by(user_id=user_id).first()
        if user:
            post=Post.query.filter_by(username=user.username).all()
            for p in post:
                db.session.delete(p)
            db.session.delete(user)
            db.session.commit()
            return 'Succefully Deleted',200
        else:
            raise NotFoundError(status_code=404)
    
    @cross_origin(supports_credentials=True)
    @marshal_with(user_fields)
    def post(self):
        args=create_user_parser.parse_args()
        username=args['username']
        password=args['password']
        user=User.query.filter_by(username=username).first()
        if user:
            raise BadError(status_code=409, message='username already exist')
        else:
            user=User(username=username,password=password)
            db.session.add(user)
            db.session.commit()
            return user

class PostAPI(Resource):

    @cross_origin(supports_credentials=True)
    @marshal_with(post_fields)
    def get(self,post_id):
        post=Post.query.filter_by(post_id=post_id).first()
        if post:
            return post
        else:
            raise NotFoundError(status_code=404)

    @cross_origin(supports_credentials=True)
    @marshal_with(post_fields)
    def put(self,post_id):
        args=create_post_parser.parse_args()
        post=Post.query.filter_by(post_id=post_id).first()
        if post:
            post.image_url=args['image_url']
            post.title=args['title']
            post.content=args['content']
            db.session.commit()
            return post
        else:
            raise NotFoundError(status_code=404)

    @cross_origin(supports_credentials=True)
    def delete(self,post_id):
        post=Post.query.filter_by(post_id=post_id).first()
        if post:
            db.session.delete(post)
            db.session.commit()
            return 'Succefully Deleted',200
        else:
            raise NotFoundError(status_code=404)
    
    @cross_origin(supports_credentials=True)
    @marshal_with(post_fields)
    def post(self):
        args=create_post_parser.parse_args()
        username=args['username']
        title=args['title']
        content=args['content']
        image_url=args['image_url']
        post=Post(username=username,title=title,content=content,image_url=image_url)
        db.session.add(post)
        db.session.commit()
        return post





class FeedAPI(Resource):

    @cross_origin(supports_credentials=True)
    @marshal_with(post_fields)
    def get(self,username):
        posts=Post.query.filter_by(username=username).all()
        if posts:
            return posts
        else:
            raise NotFoundError(status_code=404)
        