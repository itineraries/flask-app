from ctip import db, login_manager, app
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from flask_login import UserMixin
from passlib.hash import sha256_crypt
from time import time
import jwt

class User(UserMixin, db.Document):
    email = db.EmailField(primary_key=True)
    first_name = db.StringField(max_length=50, required = True)
    last_name = db.StringField(max_length=50, required = True)
    passwordh = db.StringField(max_length=128, required = True)
    confirmed = db.BooleanField(default = False)
        
    def set_password(self, password):
        self.passwordh = sha256_crypt.encrypt(password)
        
    def check_password(self, password):
        return sha256_crypt.verify(password, self.passwordh)

    def get_confirmation_token(self, expires_in=3600):
        return jwt.encode(
            {'confirm_email': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')


    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_confirmation_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['confirm_email']
        except:
            return
        return User.objects.get(email = id)

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.objects.get(email = id)

##used by flask-login to load a user object
@login_manager.user_loader
def load_user(email):
    user = User.objects(email=email).first()
    if user:
        return user
    return None


class Location(db.Document):
    email = db.ReferenceField(User)
    address = db.StringField(max_length=100, required = True)
