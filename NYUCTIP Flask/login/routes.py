from flask import Flask, render_template, request, session, url_for, redirect,flash
from login import app
from flask_login import current_user, login_user, login_required, logout_user
from login.models import User, Location
from login.forms import *
from login.email import send_password_reset_email

@app.route('/')
def index():
    return render_template('index.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        login_user(user, remember = form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User(email=form.email.data, first_name = form.first_name.data,\
                    last_name=form.last_name.data, confirmed = False) ##should I sanatize input? also does case matter
        #do we want a min password length
        user.set_password(form.password.data)
        user.save()
        token = user.get_confirmation_token()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)

@app.route('/location')
@login_required
def save_start():
    return render_template('save_locations.html')
@app.route('/save')
@login_required
def save():
    location = request.args.get('location')
    loc_obj = Location(email = current_user.email, address = location).save()
    return "Location: " + location + " saved."

@login_required
@app.route('/view') 
def view_saved_locations():
        saved_places = Location.objects(email = current_user.email)
        return render_template('view_locations.html', locations = saved_places)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        print(user.email)
        if user:
            send_password_reset_email(user)
            flash('Check your email for the instructions to reset your password')
            return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    print(user.email)
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.save()
        flash('password changed successfully')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
        
@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        user = User.verify_confirmation_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.confirmed = True
        user.save()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('main.home'))        
    

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return "You are now logged out"
