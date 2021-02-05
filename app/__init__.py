from flask import Flask
from flask_login import LoginManager
from flask import Blueprint




    # blueprint for auth routes in our app

app = Flask(__name__)
app.config.from_object('app.config')
app.config['MONGODB_SETTINGS'] = {
    'db': 'textbase',
    'host': 'localhost',
    'port': 27017,
    'connect': False
}
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'


from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

# blueprint for non-auth parts of app
from .views import main as main_blueprint
app.register_blueprint(main_blueprint)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

from app.models import User
import requests
import json

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))
from app import apirequests
from app import monitor
from app import lntranslator



