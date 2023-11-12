from app import app
from app.db import *
from flask import render_template, request, redirect, url_for, session, flash
import re
import bcrypt
from datetime import datetime, date, time, timedelta
from typing import *


###############  Routes  ###############


@app.route('/')
def home():
    return render_template('index/index.html')


#-------------------------------------------------#
#--------------------Register---------------------#
#-------------------------------------------------#

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Get form data from the request
        username = request.form["username"]
        password = request.form["password"]
        role = "customer"
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        contact_number = request.form["contact_number"]
        email = request.form["email"]
        address = request.form["address"]

        # Create a cursor for the database connection
        db_cursor = get_cursor()

        # Check if the username already exists in the database
        db_cursor.execute("SELECT COUNT(*) FROM users WHERE UserName = %s", (username,))
        user_count = db_cursor.fetchone()[0]
        if user_count > 0:
            flash("Username already exists. Please choose a different username.", "warning")
            return redirect(url_for("register"))

        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # Insert the new user data into the 'users' table
        db_cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                          (username, hashed_password, role))

        # Get the new user_id to be ready to insert into the three role table 
        db_cursor.execute("SELECT user_id FROM Users WHERE username = %s", (username,))
        user_id = db_cursor.fetchone()[0]

        # Insert into the Customer table
        db_cursor.execute("INSERT INTO customers (first_name, last_name, contact_number, email, address, user_id) VALUES (%s, %s, %s, %s, %s, %s)",
                  (first_name, last_name, contact_number, email, address, user_id))

                
        flash("You have successfully registered!", "success")
        return redirect(url_for("home"))

    # If the request method is 'GET', render the registration form
    return render_template('index/register.html')

#-------------------------------------------------#
#-------------------  Sign in --------------------#
#-------------------------------------------------#

@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        provided_username = request.form.get("username")
        provided_password = request.form.get("password")

        cursor = get_cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (provided_username,))
        user_info = cursor.fetchone()

        if user_info is None:
            flash("User not found", 'warning')
            return redirect(request.url)
        else:
            hashed_pass_in_db = user_info[1]

            if verify_password(provided_password, hashed_pass_in_db) is True:
                session['user_id'] = user_info[0]
                session["username"] = user_info[2]
                session['user_role'] = user_info[3]
                session['loggedin'] = True

                if session['user_role'] == "admin":
                    # Fetch additional user data (first_name, last_name) from the admins table
                    cursor.execute('SELECT first_name, last_name FROM admins WHERE user_id = %s', (user_info[0],))
                    admin_info = cursor.fetchone()

                    if admin_info:
                        # If the user is an admin, add first_name and last_name to the session
                        session['first_name'] = admin_info[0]
                        session['last_name'] = admin_info[1]

                    return redirect(url_for("admin_dashboard"))
                elif session['user_role'] == "customer":
                    # Fetch additional user data (first_name, last_name) from the customers table
                    cursor.execute('SELECT first_name, last_name FROM customers WHERE user_id = %s', (user_info[0],))
                    customer_info = cursor.fetchone()

                    if customer_info:
                        # If the user is a customer, add first_name and last_name to the session
                        session['first_name'] = customer_info[0]
                        session['last_name'] = customer_info[1]

                    return redirect(url_for("customer_dashboard"))
                elif session['user_role'] == "planner":
                    # Fetch additional user data (first_name, last_name) from the planners table
                    cursor.execute('SELECT first_name, last_name FROM planners WHERE user_id = %s', (user_info[0],))
                    planner_info = cursor.fetchone()

                    if planner_info:
                        # If the user is a planner, add first_name and last_name to the session
                        session['first_name'] = planner_info[0]
                        session['last_name'] = planner_info[1]

                    return redirect(url_for("planner_dashboard"))
            else:
                flash("Password incorrect", "warning")
                return redirect(request.url)

    return render_template('index/sign-in.html')



@app.route("/sign-out")
def sign_out():
    session.pop('username', None)
    session.pop('user_id', None)
    # session.pop('username', None)
    session.pop('user_role', None)  
    session['loggedin'] = False
 

    return redirect(url_for('home'))


@app.route('/list_venues')
def list_venues():
    # get a list of venues, including venue names, 
    # descriptions, first image_url, and event types
    venue_list = get_venue_list(None)

    # get event_type_list, location_list 
    event_type_list, location_list = get_filter_dropdown_options()


    return render_template('public/venue_list.html', 
            venue_list = venue_list, event_type_list = event_type_list, location_list = location_list)

# get individual venue info and the related space list
@app.route('/venue_page/<int:venue_id>')
def venue_page(venue_id):
    venue_info = get_venue_info(venue_id)
    space_list = get_space_list(venue_id)
    venue_planner = get_venue_planner(venue_id)

    return render_template('public/venue_page.html', venue_info = venue_info, space_list = space_list, venue_id = venue_id, venue_planner=venue_planner)

# search venues by events, num of guests, and location 
@app.route('/search_venues', methods=["GET", "POST"])
def search_venues():
    # validate method and if all required data is present
    if (request.method == "POST" 
        and request.form.get('event-type')
        and request.form.get('guests')
        and request.form.get('location')):

        # fetch data
        event_type = request.form['event-type']
        guests = request.form['guests']
        location = request.form['location']

        # debug code:
        # print(f'{event_type} {guests} {location}')

        #validate input 
        event_input_pattern = r'^[a-zA-Z]+(?:\s+[a-zA-Z]+)?(?:\s+[a-zA-Z]+)?$'
        guest_input_pattern = r'^(?:[5-9]|[1-9][0-9]|[1-4][0-9]{2}|500)$'
        location_input_pattern = r'^[a-zA-Z -]+$'

        if not re.match(event_input_pattern, event_type):
            flash('Invalid event type. Event type only contain letters and space.', 'warning')
        elif not re.match(guest_input_pattern, guests):
            flash('Invalid guest number. Guest number only contain whole numbers from 5 to 500.', 'warning')
        elif not re.match(location_input_pattern, location):
            flash('Invalid location. Location only contain letters, space, and hyphen', 'warning')
        else:
            # perform search function
            if not search_venues_db(event_type, guests, location):
                flash('Sorry - no matching venues available.', 'warning') 
            else:
                venue_id_list = search_venues_db(event_type, guests, location)
                venue_list = get_venue_list(venue_id_list)
                event_type_list, location_list = get_filter_dropdown_options()


                if 'user_role' not in session: # not logged in
                    return render_template('public/venue_list.html', venue_list = venue_list, 
                    event_type_list = event_type_list, location_list = location_list)
                elif session['user_role'] == 'admin':
                    print('logged in: admin')
                    return render_template('admin/admin_all_venues.html', venue_list = venue_list, 
                    event_type_list = event_type_list, location_list = location_list)
                elif session['user_role'] == 'customer':
                    print('logged in: customer')
                    return render_template('customers/customer_all_venues.html', venue_list = venue_list, 
                    event_type_list = event_type_list, location_list = location_list)
                elif session['user_role'] == 'planner':
                    print('logged in: planner')
                    return render_template('planners/planner_all_venues.html', venue_list = venue_list, 
                    event_type_list = event_type_list, location_list = location_list)

    return redirect(url_for('home')) 


#-------------------------------------------------#
#-----------------Message Venue-------------------#
#-------------------------------------------------#

@app.route('/message_venue', methods=['GET', 'POST'])
def message_venue():
    current_date = date.today().isoformat()  # Define current_date here
    planner_id = request.args.get('planner_id')
    print (planner_id)

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        event_date = request.form.get('event_date')
        message = request.form.get('message')
        planner_id = request.form.get('planner_id')

        # Create a cursor for the database connection
        db_cursor = get_cursor()

        # Insert into the database with the associated planner_id
        db_cursor.execute(
            "INSERT INTO venue_inquiries (name, email, phone, inquiry_date, message, planner_id) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, email, phone, event_date, message, planner_id))

        # Flash a message to indicate success
        flash('Venue inquiry sent', 'success')

        # You can redirect to a thank you page or any other appropriate action
        return redirect(url_for('list_venues'))

    return render_template('public/message_venue.html', current_date=current_date, planner_id=planner_id)


#-------------------------------------------------#
#-------------------Venue Planner-----------------#
#-------------------------------------------------#

def get_venue_planner(venue_id):
    db_cursor = get_cursor()

    # Assuming you have a SQL query to fetch venue information with planner_id
    query = """
        SELECT venue_id, venue_name, description, contact_phone, contact_email,
               city, address, facilities, image_url, planner_id
        FROM venues
        WHERE venue_id = %s
    """

    db_cursor.execute(query, (venue_id,))
    venue_planner = db_cursor.fetchone()

    return venue_planner



# fixing facility str after changing/editing, see edit facility route and func
# ', Bathrooms, Bar, , WIFI, Sound System, , On-site Parking, BYO, , , , '







