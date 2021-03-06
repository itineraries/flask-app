from flask import Flask
from flask_mongoengine import MongoEngine
from flask_mail import Mail
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_pyfile('config.cfg')


db = MongoEngine(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
from ctip import routes, models


