import os
from flask import Flask
from flask_restful import Api
from application import config
from application.config import LocalDevelopmentConfig
from application.database import db
from flask_cors import CORS
from application.models import User, Post, Comment, Like
from application.follow import Follow

app = None
api = None


basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'db_directory/database.db')

UPLOAD_FOLDER = 'uploads\posts'



def create_app():  
    app = Flask(__name__, template_folder="templates")
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    if os.getenv('ENV', "development") == "production":
      raise Exception("Currently no production config is setup.")
    else:
      print("Staring Local Development")
      app.config.from_object(LocalDevelopmentConfig)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app) 
    with app.app_context():
      db.metadata.clear()
      db.create_all()
    api=Api(app)
    app.app_context().push()
    return app,api

app ,api= create_app()
CORS(app, support_credentials=True)

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