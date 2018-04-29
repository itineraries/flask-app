from flask import Flask, render_template, request, session, url_for, redirect,flash, send_from_directory
from ctip import app
from flask_login import current_user, login_user, login_required, logout_user
from ctip.models import User, Location
from ctip.forms import *
from ctip.email import send_password_reset_email
from ctip.itinerary_format import *

import cgi, datetime, dateutil.parser, os.path, pytz, sys


@app.route("/")
def root():
    # Read the parameters.
    try:
        origin = request.args["orig"].strip()
        destination = request.args["dest"].strip()
    except KeyError:
        origin = ""
        destination = ""
    depart = request.args.get("depart", None) != "0"
    datetime_trip = get_datetime_trip()
    walking_max_mode = request.args.get("walking-max", None)
    try:
        walking_max_custom = float(request.args["walking-max-custom"])
    except (KeyError, ValueError):
        walking_max_custom = 5.0
    weekdays_checked = get_weekdays_checked(datetime_trip)
    # Set the walking time limit.
    if walking_max_mode == "custom":
        agency_walking.set_max_seconds(walking_max_custom * 60.0)
    elif walking_max_mode == "zero":
        agency_walking.set_max_seconds(0.0)
    else:
        walking_max_mode = "unlimited"
        agency_walking.set_max_seconds_unlimited()
    # Check whether we should get an itinerary.
    document_title = "NYU CTIP"
    if origin and destination:
        document_title = origin + " to " + destination + " - " + document_title
        if origin == destination:
            output_escaped = \
                "<p>The origin and destination are the same.</p>\n\t\t\t"
        else:
            # Get the itinerary.
            markup_itineraries = "".join(
                (
                    # Start the list item.
                    "\t\t\t\t\t<li>\n"
                    # Add the travel time.
                    "\t\t\t\t\t\t" + cgi.escape(
                        days_hours_minutes_string(
                            itinerary[-1].datetime_arrive -
                            itinerary[0].datetime_depart
                        )
                    ) + "\n"
                    # Add the nested ordered list.
                    "\t\t\t\t\t\t<ol>\n" + "".join(
                        mark_weighted_edge_up(direction, "\t\t\t\t\t\t\t")
                        for direction in itinerary
                    ) +
                    "\t\t\t\t\t\t</ol>\n" +
                    # End the list item.
                    "\t\t\t\t\t</li>\n"
                )
                for itinerary in itinerary_finder.find_itineraries(
                    agencies_to_vary,
                    agencies,
                    origin,
                    destination,
                    datetime_trip,
                    depart,
                    max_count=3
                )
            )
            if markup_itineraries:
                output_escaped = "\n" \
                    "\t\t\t\t<p>Itineraries:</p>\n" \
                    "\t\t\t\t<ol>\n" + \
                    markup_itineraries + \
                    "\t\t\t\t</ol>\n" \
                    "\t\t\t"
            else:
                output_escaped = \
                    "\n\t\t\t\t<p>This itinerary is not possible either " \
                    "because there is no continuous path from the origin to " \
                    "the or because no agency recognized the origin or " \
                    "destination.</p>\n\t\t\t"
    else:
        output_escaped = ""
    # Reflect the parameters back to the user and send the itinerary.
    return render_template(
        "index.html",
        document_title=document_title,
        origin=origin,
        destination=destination,
        stops=stops.names_sorted,
        depart=depart,
        weekdays_checked=weekdays_checked,
        when=datetime_trip.strftime("%H:%M"),
        walking_max_mode=walking_max_mode,
        walking_max_custom=walking_max_custom,
        output_escaped=output_escaped
    )

@app.route("/departures")
def departures():
    # Read the parameters.
    origin = request.args.get("orig", "").strip()
    datetime_trip = get_datetime_trip()
    weekdays_checked = get_weekdays_checked(datetime_trip)
    # Check whether we should list departures.
    document_title = "Departures - NYU CTIP"
    if origin:
        document_title = origin + " - " + document_title
        # List the departures.
        markup_departures = "".join(
            mark_weighted_edge_up(direction, "\t\t\t\t\t")
            for direction in departure_lister.departure_list(
                agencies,
                origin,
                datetime_trip,
                20
            )
        )
        # Put the list to the output to the user.
        if markup_departures:
            output_escaped = \
                "\n\t\t\t\t<p>Departures from " + \
                "<span class=\"itinerary-node\">" + cgi.escape(origin) + \
                "</span>:</p>\n\t\t\t\t<ul>\n" + markup_departures + \
                "\t\t\t\t</ul>\n\t\t\t"
        else:
            output_escaped = \
                "\n\t\t\t\t<p>There are no departures from " \
                "<span class=\"itinerary-node\">" + cgi.escape(origin) + \
                "</span> after the specified time.</p>\n\t\t\t"
    else:
        output_escaped = ""
    # Reflect the parameters back to the user and list the departures.
    return render_template(
        "departures.html",
        document_title=document_title,
        origin=origin,
        stops=stops.names_sorted,
        weekdays_checked=weekdays_checked,
        when=datetime_trip.strftime("%H:%M"),
        output_escaped=output_escaped
    )

@app.route("/favicon.ico")
def favicon():
    # Taken straight from the Flask docs:
    # http://flask.pocoo.org/docs/0.12/patterns/favicon/
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon"
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('root'))
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        login_user(user, remember = form.remember_me.data)
        flash('You are now logged in')
        return redirect(url_for('root'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('root'))
    form = RegistrationForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User(email=form.email.data, first_name = form.first_name.data,\
                    last_name=form.last_name.data, confirmed = False) ##should I sanatize input? also does case matter
        #do we want a min password length
        user.set_password(form.password.data)
        user.save()
        token = user.get_confirmation_token()
        login_user(user)
        return redirect(url_for('root'))
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
    flash("Location Saved")
    return redirect(url_for('view_saved_locations'))

@login_required
@app.route('/view') 
def view_saved_locations():
        saved_places = Location.objects(email = current_user.email)
        return render_template('view_locations.html', locations = saved_places)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('root'))
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
        return redirect(url_for('root'))
    user = User.verify_reset_password_token(token)
    print(user.email)
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.save()
        flash('password changed successfully')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
        
##NOT DONE YET THIS WONT DO ANYTHING
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
    return redirect(url_for('root'))        
    

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You are now logged out")
    return redirect(url_for('root'))