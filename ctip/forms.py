from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_wtf import FlaskForm
from ctip.models import User, db

class RegistrationForm(FlaskForm):
    first_name = StringField('first_name', validators=[DataRequired()])
    last_name = StringField('last_name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        ##can also have a min password length
        try:
            user = User.objects.get(email = email.data) ##TODO can also use get()
            self.email.errors.append('User already exists with this username')
        except db.DoesNotExist:
            return email
            
            

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    
    def validate_email(self, email):
        user = User.objects(email= self.email.data).first()
        if not user or not user.check_password(password = self.password.data):
            self.email.errors.append('User email or password is incorrect')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')
    def validate_email(self, email):
        user = User.objects(email= self.email.data).first()
        if not user:
            self.email.errors.append('Email does not exist')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
    
 
