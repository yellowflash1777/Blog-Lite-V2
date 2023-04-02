import os
from flask import Flask
from flask_login import LoginManager
from flask_restful import Api
from application import config
from application.config import LocalDevelopmentConfig
from application.database import db
from flask_cors import CORS
from application.flask_upload import UploadSet, IMAGES, configure_uploads


from application.models import User, Post, Comment, Like
from application.follow import Follow


app = None
api = None


basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'db_directory/database.db')




def create_app():  
    app = Flask(__name__, template_folder="templates")
    
    app.config['UPLOADED_PHOTOS_DEST'] = 'static/img/uploads'
    
    if os.getenv('ENV', "development") == "production":
      raise Exception("Currently no production config is setup.")
    else:
      print("Staring Local Development")
      app.config.from_object(LocalDevelopmentConfig)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    # app.config['LOGIN_URL'] = '/login'
    
    db.init_app(app) 
    with app.app_context():
      #db.metadata.clear()
      db.create_all()
    api=Api(app)
    app.app_context().push()
    return app,api

app ,api= create_app()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
CORS(app, support_credentials=True)
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# Import all the controllers so they are loaded
from application.controllers import *

#Import restful controllers
from application.api import FeedAPI, UserAPI,PostAPI
# Add the resources to the api
api.add_resource(UserAPI,'/api/user', '/api/user/<int:user_id>')
api.add_resource(PostAPI,'/api/post', '/api/post/<int:post_id>')
api.add_resource(FeedAPI,'/api/feed/<string:username>')

if __name__ == '__main__':
  # Run the Flask app
  app.run(host='0.0.0.0',port=5000)