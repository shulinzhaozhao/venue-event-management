from app import app
from app.db import *
from flask import render_template, request, redirect, url_for, session, flash
import re
import bcrypt
from datetime import datetime, date, time, timedelta
from collections import defaultdict

YEAR_END_GOAL = 100000.00


@app.route('/admin')
def home2():
    data = get_user_info()
    print(data)
    return 'admin views is all good .'

# display admin dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_authenticated():
        return redirect(url_for('home'))
    user_role = get_user_role()
    if user_role != 'admin':
        flash('Unauthorized', 'warning')
        return redirect(url_for('home'))
    # get a list of venues, including venue names, 
    # descriptions, first image_url, and event types
    venue_list = get_venue_list(None)

    # get event_type_list, location_list 
    event_type_list, location_list = get_filter_dropdown_options()

    return render_template('admin/admin_dashboard.html', full_name=f"{session['first_name']} {session['last_name']}",
        venue_list =  venue_list, event_type_list = event_type_list, location_list = location_list)


################### View and Manage Profile ###################

# Planner Display Profile 
@app.route('/admin/profile')
def admin_profile():

    if not is_authenticated():
        return redirect(url_for('home'))
    
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['customer', 'planner']:
        flash('Unauthorised. not admin', 'warning')
        return redirect(url_for('home'))
    
    user_id = session['user_id']
    connection = get_cursor()
    connection.execute('SELECT * FROM admins JOIN users \
                       ON admins.user_id = users.user_id \
                       WHERE admins.user_id =%s;', (user_id,))
    account = connection.fetchone()
    return render_template('admin/admin_profile.html', account=account)

# Update profile
@app.route('/admin/profile/update', methods=['GET', 'POST'])
def admin_profile_update():
    if not is_authenticated():
        return redirect(url_for('home'))
    
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['customer', 'planner']:
        flash('Unauthorised. not admin', 'warning')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        #print(request.form)
        if (
            request.form.get('first_name') and
            request.form.get('last_name') and
            request.form.get('email') and
            request.form.get('contact_number') and
            request.form.get('address')
        ):
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            contact_number = request.form['contact_number']
            address = request.form['address']

            if not re.match(r'^[A-Za-z\s]+$', first_name):
                flash('Invalid first name.', 'warning')
            elif not re.match(r'^[A-Za-z\s]+$', last_name):
                flash('Invalid last name.', 'warning')
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                flash('Invalid email address.', 'warning')
            elif not re.match(r'^[\d\s+\-().]+$', contact_number):
                flash('Invalid contact number.', 'warning')
            else:
                user_id = session['user_id']
                #print(user_id)
                connection = get_cursor()
                sql_admin = "UPDATE admins SET first_name = %s, last_name = %s, email = %s, contact_number = %s, address = %s WHERE user_id = %s;"
                # Update the planners table 
                connection.execute(sql_admin, (first_name, last_name, email, contact_number, address, user_id,))
                
                flash('You have successfully updated your profile!', 'success')
        else:
            flash('Please fill out the form.', 'warning')

    return redirect(url_for('admin_profile'))

########################### Change Password ###############################
# Display password change page
@app.route('/admin/password')
def admin_change_password():
    if "loggedin" in session:
        return render_template('admin/admin_change_password.html')
    
    return redirect(url_for('sign_in'))


# Define a route to handle the password change form
@app.route('/admin/password/change', methods=['GET', 'POST'])
def admin_change_password_update():
    if "loggedin" in session:

        if request.method == 'POST':
            if (
                request.form.get('old_password') and
                request.form.get('new_password') and
                request.form.get('confirm_password')
            ):
                # Get the form input values
                old_password = request.form.get('old_password')
                new_password = request.form.get('new_password')
                confirm_password = request.form.get('confirm_password')

                # Check if the new password matches the confirmation
                if new_password != confirm_password:
                    flash('New password and confirmation do not match.', 'warning')
                    return redirect(url_for('admin_change_password'))
        
                user_id = session['user_id']
                # Use "get_user_hashed_password" to get the hashed password
                hashed_password = get_user_hashed_password(user_id)
        
                #Verify the old password
                if not verify_password(old_password, hashed_password):
                    flash('Incorrect old password.', 'warning')
                    return redirect(url_for('admin_change_password'))
            
                # Hash the new password before updating the database
                hashed_new_password = generate_hashed_password(new_password)
        
                # Update the new password in db
                connection = get_cursor()
                sql = "UPDATE users SET password = %s WHERE user_id = %s;"
                connection.execute(sql, (hashed_new_password, user_id,))

                flash('Password updated successfully!', 'success')
                return redirect(url_for('admin_change_password'))
            else:
                flash('Please fill out the form.', 'warning')

    return redirect(url_for('sign_in'))
# note: when defining routes and functions, 
# please add the role prefix to avoid name clashing, 
# e.g., route('/admin/profile')
# def admin_profile()


@app.route('/view/manage/customers', methods=['GET'])
def view_manage_customers():
    if not is_authenticated():
        return redirect(url_for('home'))
    
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['customer', 'planner']:
        flash('Unauthorised. not admin', 'warning')
        return redirect(url_for('home'))

    connection = get_cursor()
    
    # Get the search query from the URL query parameters
    search_query = request.args.get('search_query', '')

    # Modify your SQL query to include the search filter
    query = 'SELECT * FROM customers WHERE first_name LIKE %s OR last_name LIKE %s'
    connection.execute(query, ('%' + search_query + '%', '%' + search_query + '%'))
    customers = connection.fetchall()
    
    return render_template('admin/manage_customers.html', customers=customers, search_query=search_query)


@app.route('/admin/add_customer', methods=['GET', 'POST'])
def add_customer():
    if not is_authenticated():
        return redirect(url_for('home'))
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['customer', 'planner']:
        flash('Unauthorised. not admin', 'warning')
        return redirect(url_for('home'))

    if request.method == 'POST':
        # Get customer details from the form
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        username = request.form['username']
        password = request.form.get('password')
        address = request.form.get('address')

        # Check if the email already exists
        connection = get_cursor()
        connection.execute('SELECT email FROM customers;')
        accounts1 = connection.fetchall()
        emails = [user[0] for user in accounts1]
        if email in emails:
            flash('Email already exists.', 'warning')

        # Perform validation on the form data
        elif not all([first_name, last_name, email, phone, username, password]):
            flash('Please fill out all the required fields.', 'warning')
        elif not re.match(r'^[a-zA-Z0-9]+$', username):
            flash('Invalid username. Usernames only contain letters and numbers.', 'warning')
        elif not re.match(r'^[A-Za-z\s]+$', first_name):
            flash('Invalid first name. Please use letters and spaces only.', 'warning')
        elif not re.match(r'^[A-Za-z\s]+$', last_name):
            flash('Invalid last name. Please use letters and spaces only.', 'warning')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address.', 'warning')
        elif not re.match(r'^[\d\s+\-().]+$', phone):
            flash('Invalid phone number. Please use digits, spaces, hyphens, and parentheses only.', 'warning')
        elif address and not re.match(r'^[A-Za-z0-9\s,.-]+$', address):
            flash('Invalid address.', 'warning')
        else:
            # Check if the username already exists
            connection = get_cursor()
            connection.execute('SELECT username FROM users;')
            accounts = connection.fetchall()
            usernames = [user[0] for user in accounts]
            
            if username in usernames:
                flash('Username already exists. Please choose another username.', 'warning')
            else:
                # Hash the password
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

                # Add the user to the database
                connection.execute('INSERT INTO users (password, username, role) VALUES (%s, %s, %s);', (hashed_password, username, 'customer'))

                # Get user_id
                connection.execute('SELECT user_id FROM users WHERE username = %s;', (username,))
                user_id = connection.fetchone()[0]

                # Add the customer to the database
                connection.execute('INSERT INTO customers (first_name, last_name, email, contact_number, address, user_id) VALUES (%s, %s, %s, %s, %s, %s)',
                                   (first_name, last_name, email, phone, address, user_id))

                flash('Customer added successfully', 'success')
                return redirect(url_for('view_manage_customers'))

    return render_template('admin/add_customer.html')


@app.route('/admin/delete_customer/<int:customer_id>')
def delete_customer(customer_id):
    if not is_authenticated():
        return redirect(url_for('home'))
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['customer', 'planner']:
        flash('Unauthorised. not admin', 'warning')
        return redirect(url_for('home'))
    # Get the user ID associated with the customer (assuming you have a users table)
    connection = get_cursor()
    connection.execute('SELECT * FROM users LEFT JOIN customers ON customers.user_id=users.user_id WHERE customers.customer_id = %s;', (customer_id,))
    user_id = connection.fetchone()[0]
    # Delete the customer from the database
    connection = get_cursor()
    connection.execute('DELETE FROM customers WHERE customer_id = %s;', (customer_id,))
    # Delete the user from the users table 
    connection = get_cursor()
    connection.execute('DELETE FROM users WHERE user_id = %s;', (user_id,))

    flash('Customer deleted successfully', 'success')
    return redirect(url_for('view_manage_customers'))

@app.route('/admin/update_customer/<int:customer_id>', methods=['GET', 'POST'])
def update_customer(customer_id):
    
    # Get the customer from the database based on the ID
    connection = get_cursor()
    connection.execute('SELECT * FROM users LEFT JOIN customers ON customers.user_id=users.user_id WHERE customers.customer_id = %s;', (customer_id,))
    customer = connection.fetchone()
    email=customer[7]
    user_id = customer[0]
    user_name=customer[2]

    if request.method == 'POST':
        # Get updated details from the form
        updated_first_name = request.form.get('first_name')
        updated_last_name = request.form.get('last_name')
        updated_email = request.form.get('email')
        updated_phone = request.form.get('phone')
        updated_address = request.form.get('address')
        updated_username = request.form.get('username')
        updated_password = request.form.get('password')
        # Check if the email already exists
        connection = get_cursor()
        connection.execute('SELECT email FROM customers;')
        accounts = connection.fetchall()
        emails = [user[0] for user in accounts]

        # Check if the username already exists
        connection = get_cursor()
        connection.execute('SELECT username FROM users;')
        accounts1 = connection.fetchall()
        usernames = [user[0] for user in accounts1]
    
        if updated_username in usernames and updated_username != user_name:
            flash('Username already exists. Please choose another username.', 'warning')
        elif updated_email in emails and updated_email!=email:
            flash('Email already exists.', 'warning')

        # Perform validation on the form data 
        elif not all([updated_first_name, updated_last_name, updated_email, updated_phone, updated_username]):
            flash('Please fill out all the required fields.', 'warning')
        elif not re.match(r'^[a-zA-Z0-9]+$', updated_username):
            flash('Invalid username. Usernames only contain letters and numbers.', 'warning')
        elif not re.match(r'^[A-Za-z\s]+$', updated_first_name):
            flash('Invalid first name. Please use letters and spaces only.', 'warning')
        elif not re.match(r'^[A-Za-z\s]+$', updated_last_name):
            flash('Invalid last name. Please use letters and spaces only.', 'warning')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', updated_email):
            flash('Invalid email address.', 'warning')
        elif not re.match(r'^[\d\s+\-().]+$', updated_phone):
            flash('Invalid phone number. Please use digits, spaces, hyphens, and parentheses only.', 'warning')
        elif updated_address and not re.match(r'^[A-Za-z0-9\s,.-]+$', updated_address):
            flash('Invalid address.', 'warning')
        else:
            
            # Update the variables based on the conditions
            if updated_password:
                hashed = bcrypt.hashpw(updated_password.encode('utf-8'), bcrypt.gensalt())
            else:
                connection = get_cursor()
                connection.execute('SELECT * FROM users WHERE user_id = %s;', (user_id,))
                hashed = connection.fetchone()[1]

            connection = get_cursor()
            connection.execute('UPDATE users SET password=%s, username=%s \
                                    WHERE user_id=%s;',(hashed, updated_username, user_id)) 

            connection.execute('UPDATE customers SET first_name=%s,last_name=%s, email=%s, contact_number=%s,address=%s WHERE user_id=%s;', (updated_first_name, updated_last_name, updated_email, updated_phone, updated_address, user_id))    
            flash('Customer updated successfully', 'success')
            return redirect(url_for('view_manage_customers'))

    return render_template('admin/update_customer.html', customer=customer)

@app.route('/view/manage/planners', methods=['GET'])
def view_manage_planners():
    if not is_authenticated():
        return redirect(url_for('home'))
    
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['customer', 'planner']:
        flash('Unauthorised. not admin', 'warning')
        return redirect(url_for('home'))

    connection = get_cursor()
    
    # Get the search query from the URL query parameters
    search_query = request.args.get('search_query', '')

    # Modify your SQL query to include the search filter
    query = 'SELECT * FROM planners WHERE first_name LIKE %s OR last_name LIKE %s'
    connection.execute(query, ('%' + search_query + '%', '%' + search_query + '%'))
    planners = connection.fetchall()
    
    return render_template('admin/manage_planners.html', planners=planners, search_query=search_query)


@app.route('/admin/add_planner', methods=['GET', 'POST'])
def add_planner():
    if not is_authenticated():
        return redirect(url_for('home'))
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['customer', 'planner']:
        flash('Unauthorised. not admin', 'warning')
        return redirect(url_for('home'))

    if request.method == 'POST':
        # Get planner details from the form
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        username = request.form['username']
        password = request.form.get('password')
        address = request.form.get('address')

        # Check if the email already exists
        connection = get_cursor()
        connection.execute('SELECT email FROM planners;')
        accounts1 = connection.fetchall()
        emails = [user[0] for user in accounts1]
        if email in emails:
            flash('Email already exists.', 'warning')

        # Perform validation on the form data
        elif not all([first_name, last_name, email, phone, username, password]):
            flash('Please fill out all the required fields.', 'warning')
        elif not re.match(r'^[a-zA-Z0-9]+$', username):
            flash('Invalid username. Usernames only contain letters and numbers.', 'warning')
        elif not re.match(r'^[A-Za-z\s]+$', first_name):
            flash('Invalid first name. Please use letters and spaces only.', 'warning')
        elif not re.match(r'^[A-Za-z\s]+$', last_name):
            flash('Invalid last name. Please use letters and spaces only.', 'warning')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address.', 'warning')
        elif not re.match(r'^[\d\s+\-().]+$', phone):
            flash('Invalid phone number. Please use digits, spaces, hyphens, and parentheses only.', 'warning')
        elif address and not re.match(r'^[A-Za-z0-9\s,.-]+$', address):
            flash('Invalid address.', 'warning')
        else:
            # Check if the username already exists
            connection = get_cursor()
            connection.execute('SELECT username FROM users;')
            accounts = connection.fetchall()
            usernames = [user[0] for user in accounts]
            
            if username in usernames:
                flash('Username already exists. Please choose another username.', 'warning')
            else:
                # Hash the password
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

                # Add the user to the database
                connection.execute('INSERT INTO users (password, username, role) VALUES (%s, %s, %s);', (hashed_password, username, 'customer'))

                # Get user_id
                connection.execute('SELECT user_id FROM users WHERE username = %s;', (username,))
                user_id = connection.fetchone()[0]

                # Add the planner to the database
                connection.execute('INSERT INTO planners (first_name, last_name, email, contact_number, address, user_id) VALUES (%s, %s, %s, %s, %s, %s)',
                                   (first_name, last_name, email, phone, address, user_id))

                flash('Planner added successfully', 'success')
                return redirect(url_for('view_manage_planners'))

    return render_template('admin/add_planner.html')

@app.route('/admin/delete_planner/<int:planner_id>')
def delete_planner(planner_id):
    if not is_authenticated():
        return redirect(url_for('home'))
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['customer', 'planner']:
        flash('Unauthorised. not admin', 'warning')
        return redirect(url_for('home'))
    # Get the user ID associated with the planner (assuming you have a users table)
    connection = get_cursor()
    connection.execute('SELECT * FROM users LEFT JOIN planners ON planners.user_id=users.user_id WHERE planners.planner_id = %s;', (planner_id,))
    user_id = connection.fetchone()[0]
    # Delete the planner from the database
    connection = get_cursor()
    connection.execute('DELETE FROM planners WHERE planner_id = %s;', (planner_id,))
    # Delete the user from the users table 
    connection = get_cursor()
    connection.execute('DELETE FROM users WHERE user_id = %s;', (user_id,))

    flash('Planner deleted successfully', 'success')
    return redirect(url_for('view_manage_planners'))

@app.route('/admin/update_planner/<int:planner_id>', methods=['GET', 'POST'])
def update_planner(planner_id):
    
    # Get the planner from the database based on the ID
    connection = get_cursor()
    connection.execute('SELECT * FROM users LEFT JOIN planners ON planners.user_id=users.user_id WHERE planners.planner_id = %s;', (planner_id,))
    planner = connection.fetchone()
    email=planner[7]
    user_id = planner[0]
    user_name=planner[2]

    if request.method == 'POST':
        # Get updated details from the form
        updated_first_name = request.form.get('first_name')
        updated_last_name = request.form.get('last_name')
        updated_email = request.form.get('email')
        updated_phone = request.form.get('phone')
        updated_address = request.form.get('address')
        updated_username = request.form.get('username')
        updated_password = request.form.get('password')
        # Check if the email already exists
        connection = get_cursor()
        connection.execute('SELECT email FROM planners;')
        accounts = connection.fetchall()
        emails = [user[0] for user in accounts]

        # Check if the username already exists
        connection = get_cursor()
        connection.execute('SELECT username FROM users;')
        accounts1 = connection.fetchall()
        usernames = [user[0] for user in accounts1]
    
        if updated_username in usernames and updated_username != user_name:
            flash('Username already exists. Please choose another username.', 'warning')
        elif updated_email in emails and updated_email!=email:
            flash('Email already exists.', 'warning')

        # Perform validation on the form data 
        elif not all([updated_first_name, updated_last_name, updated_email, updated_phone, updated_username]):
            flash('Please fill out all the required fields.', 'warning')
        elif not re.match(r'^[a-zA-Z0-9]+$', updated_username):
            flash('Invalid username. Usernames only contain letters and numbers.', 'warning')
        elif not re.match(r'^[A-Za-z\s]+$', updated_first_name):
            flash('Invalid first name. Please use letters and spaces only.', 'warning')
        elif not re.match(r'^[A-Za-z\s]+$', updated_last_name):
            flash('Invalid last name. Please use letters and spaces only.', 'warning')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', updated_email):
            flash('Invalid email address.', 'warning')
        elif not re.match(r'^[\d\s+\-().]+$', updated_phone):
            flash('Invalid phone number. Please use digits, spaces, hyphens, and parentheses only.', 'warning')
        elif updated_address and not re.match(r'^[A-Za-z0-9\s,.-]+$', updated_address):
            flash('Invalid address.', 'warning')
        else:
            
            # Update the variables based on the conditions
            if updated_password:
                hashed = bcrypt.hashpw(updated_password.encode('utf-8'), bcrypt.gensalt())
            else:
                connection = get_cursor()
                connection.execute('SELECT * FROM users WHERE user_id = %s;', (user_id,))
                hashed = connection.fetchone()[1]

            connection = get_cursor()
            connection.execute('UPDATE users SET password=%s, username=%s \
                                    WHERE user_id=%s;',(hashed, updated_username, user_id)) 

            connection.execute('UPDATE planners SET first_name=%s,last_name=%s, email=%s, contact_number=%s,address=%s WHERE user_id=%s;', (updated_first_name, updated_last_name, updated_email, updated_phone, updated_address, user_id))    
            flash('Planner updated successfully', 'success')
            return redirect(url_for('view_manage_planners'))

    return render_template('admin/update_planner.html', planner=planner)


# ##################################### Admin View Venues ###################################

# View all venues from the customer's dashboard
@app.route('/admin/all_venues')
def admin_view_all_venues():
    # get a list of venues, including venue names, 
    # descriptions, first image_url, and event types
    venue_list = get_venue_list(None)

    # get event_type_list, location_list 
    event_type_list, location_list = get_filter_dropdown_options()

    return render_template('admin/admin_all_venues.html', venue_list =  venue_list,
        event_type_list = event_type_list, location_list = location_list)

# get individual venue info and the related space list
@app.route('/admin/all_venues/<int:venue_id>')
def admin_venue_page_all_venues(venue_id):
    venue_info = get_venue_info(venue_id)
    space_list = get_space_list(venue_id)

    return render_template('admin/admin_venue_page_all_venues.html', venue_info = venue_info, space_list = space_list)


# ######################## Admin View and Edit Venues ###############################
@app.route('/admin/manage_venues')
def admin_manage_venues():
    venue_list = get_venue_list(None)
    
    return render_template('admin/admin_manage_venues.html', venue_list=venue_list)


# @app.route('/admin/manage_venues/add', methods=['GET', 'POST'])
# def admin_venue_add():

#     if not is_authenticated():
#         return redirect(url_for('home'))
#     user_role = get_user_role()
#     if user_role not in USER_ROLES:
#         flash('Unauthorised. not in roles', 'warning')
#         return redirect(url_for('home'))
#     elif user_role in ['planner', 'customer']:
#         flash('Unauthorised. not admin', 'warning')
#         return redirect(url_for('home'))
#     service_list = get_service_list()

#     if request.method == 'POST':
#         venue_name = request.form.get('venue_name')
#         city = request.form.get('city')
#         description = request.form.get('description')

#         contact_phone = request.form['contact_phone']
#         contact_email = request.form['contact_email']
#         address = request.form['address']

#         facilities = request.form.getlist('facilities[]')
#         # Convert the list of facilities to a string
#         facilities_str = ', '.join(facilities)

#         selected_service_ids = request.form.getlist('service_option[]')
#         price_list = request.form.getlist('service_price[]')

#         connection = get_cursor()

#         # Perform validation on the form data
#         if not all([venue_name, city, description,description, contact_phone,contact_email, address, facilities,selected_service_ids]):
#             flash('Please fill out all the required fields.', 'warning')
    
#         elif not re.match(r'[^@]+@[^@]+\.[^@]+', contact_email):
#             flash('Invalid email address.', 'warning')
#         elif not re.match(r'^[\d\s+\-().]+$', contact_phone):
#             flash('Invalid phone number. Please use digits, spaces, hyphens, and parentheses only.', 'warning')
#         elif address and not re.match(r'^[A-Za-z0-9\s,.-]+$', address):
#             flash('Invalid address.', 'warning')
#         else:
            
#             # INSERT into table venues 
#             sql_venues = "INSERT INTO venues (venue_name, description, contact_phone, contact_email, city, address, facilities, is_deleted)\
#                 VALUES (%s,%s,%s,%s,%s,%s,%s,0);"
#             connection.execute(sql_venues,(venue_name,description,contact_phone,contact_email,city,address,facilities_str,))
            
#             # Now get the new venue id 
#             connection.execute("SELECT venue_id FROM venues WHERE venue_name = %s;", (venue_name,))
#             venue_id = connection.fetchone()[0]

#             # INSERT into table venue_services
#             for selected_service_id, price in zip(selected_service_ids, price_list):
#                 sql_venue_services = "INSERT into venue_services (venue_id,service_id, price) VALUES (%s, %s);"
#                 connection.execute(sql_venue_services, (venue_id, selected_service_id, price))


#     return render_template('admin/admin_add_venue.html', service_list = service_list)

# @app.route('/admin/manage_venues/add')
# def admin_venue_add():

#     if not is_authenticated():
#         return redirect(url_for('home'))
#     user_role = get_user_role()
#     if user_role not in USER_ROLES:
#         flash('Unauthorised. not in roles', 'warning')
#         return redirect(url_for('home'))
#     elif user_role in ['planner', 'customer']:
#         flash('Unauthorised. not admin', 'warning')
#         return redirect(url_for('home'))
#     service_list = get_service_list()


@app.route('/admin/manage_venues/add', methods=['GET', 'POST'])
def admin_venue_add():

    if not is_authenticated():
        return redirect(url_for('home'))
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['planner', 'customer']:
        flash('Unauthorised. not admin', 'warning')
        return redirect(url_for('home'))
    
    service_list = get_service_list()

    if request.method == 'POST':
        venue_name = request.form.get('venue_name')
        city = request.form.get('city')
        description = request.form.get('description')


        contact_phone = request.form['contact_phone']
        contact_email = request.form['contact_email']
        address = request.form['address']

        facilities = request.form.getlist('facilities[]')
        # Convert the list of facilities to a string
        facilities_str = ', '.join(facilities)

        selected_service_ids = request.form.getlist('service_option[]')
        price_list = request.form.getlist('service_price[]')

        connection = get_cursor()

#         selected_service_ids = request.form.getlist('service_option[]')


        # Perform validation on the form data
        if not all([venue_name, city, description,description, contact_phone,contact_email, address]):
            flash('Please fill out all the required fields.', 'warning')
    

        elif not re.match(r'[^@]+@[^@]+\.[^@]+', contact_email):
            flash('Invalid email address.', 'warning')
        elif not re.match(r'^[\d\s+\-().]+$', contact_phone):
            flash('Invalid phone number. Please use digits, spaces, hyphens, and parentheses only.', 'warning')
        elif address and not re.match(r'^[A-Za-z0-9\s,.-]+$', address):
            flash('Invalid address.', 'warning')
        else:
            
            # INSERT into table venues 
            sql_venues = "INSERT INTO venues (venue_name, description, contact_phone, contact_email, city, address, facilities, is_deleted)\
                VALUES (%s,%s,%s,%s,%s,%s,%s,0);"
            connection.execute(sql_venues,(venue_name,description,contact_phone,contact_email,city,address,facilities_str,))
            
            # Now get the new venue id 
            connection.execute("SELECT venue_id FROM venues WHERE venue_name = %s;", (venue_name,))
            venue_id = connection.fetchone()[0]

            
            # for selected_service_id, price in zip(selected_service_ids, price_list):
            #     sql_venue_services = "INSERT into venue_services (venue_id, service_id, price) VALUES (%s, %s, %s);"
            #     connection.execute(sql_venue_services, (venue_id, selected_service_id, price))

            # nay edits 
            # INSERT into table venue_services
            combined_service_id_and_price = zip(selected_service_ids, price_list) # a list of arrays 
            combined_service_id_and_price = tuple( combined_service_id_and_price)
            # print(combined_service_id_and_price)

            for service in combined_service_id_and_price:
                connection = get_cursor()
                id, price = service 
                print('going in')
                if id == '1':
                    pricing_model = 'PerHead'
                else:
                    pricing_model = 'Fixed'
                sql = "INSERT into venue_services (venue_id, service_id, price, pricing_model) VALUES (%s, %s, %s, %s);"
                connection.execute(sql, (venue_id, id, price, pricing_model))
            
            return redirect(url_for('admin_manage_venues'))

    return render_template('admin/admin_add_venue.html', service_list = service_list)

#         elif not re.match(r'[^@]+@[^@]+\.[^@]+', contact_email):
#             flash('Invalid email address.', 'warning')
#         elif not re.match(r'^[\d\s+\-().]+$', contact_phone):
#             flash('Invalid phone number. Please use digits, spaces, hyphens, and parentheses only.', 'warning')
#         elif address and not re.match(r'^[A-Za-z0-9\s,.-]+$', address):
#             flash('Invalid address.', 'warning')
#         else:
#             connection = get_cursor()
#             sql_venue_info = ""
#             sql_
#     return render_template('admin/admin_add_venue.html', service_list = service_list)


@app.route('/admin/manage_venues/<int:venue_id>/delete')
def admin_venue_delete(venue_id):

    if not is_authenticated():
        return redirect(url_for('home'))
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['planner', 'customer']:
        flash('Unauthorised. not admin', 'warning')
        return redirect(url_for('home'))
    
    connection = get_cursor()
    # Check if this venue has bookings, if yes, cant delete 
    sql_check_booking = '''SELECT booking_id FROM bookings JOIN space_events 
                        ON bookings.space_event_id = space_events.space_event_id 
                        JOIN venue_spaces 
                        ON space_events.space_id = venue_spaces.space_id 
                        WHERE venue_spaces.venue_id = %s;'''
    connection.execute(sql_check_booking,(venue_id,))
    result = connection.fetchall()
    print(result)
    if len(result) != 0:
        flash('This venue has bookings. Delete venue not allowed.','warning')
        return redirect(url_for('admin_manage_venues'))
    else:
        sql_update = 'UPDATE venues SET is_deleted = 1 WHERE venue_id = %s;'
        connection.execute(sql_update, (venue_id,))

    flash('Venue deleted successfully', 'success')
    return redirect(url_for('admin_manage_venues'))








# Route for updating venue information
@app.route('/admin/manage_venues/<int:venue_id>/edit-venue', methods=['GET', 'POST'])
def admin_venue_edit(venue_id):
    # Your authentication and role checking code here
    if not is_authenticated():
        return redirect(url_for('home'))
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['planner', 'customer']:
        flash('Unauthorised. not admin', 'warning')
        return redirect(url_for('home'))

    venue_info = get_venue_info(venue_id)
    space_list = get_space_list(venue_id)
    event_type_list = get_event_type_list()
    
    # complete service list with id and name 
    service_list = get_service_list() # list of tuples with id and name 

    # selected service list with id and price 
    selected_service_list = get_venue_service_price_list(venue_id) # list of tuples with id and price 

    # construct complete_service_list, with id, name, and existing price
    complete_service_list = []
    for service in service_list:
        service_id = service[0]
        service_name = service[1]
        for selected_service in selected_service_list:
            if service_id == selected_service[0]:  # if id match, price exists in db          
                service_price = selected_service[1]
                break  # immediately break out of for loop and lock the price once there is a match 
            else: # id not matched, price is none
                service_price = None
        entry = [service_id, service_name, service_price] 
        complete_service_list.append(entry)

    # print(complete_service_list)


    if request.method == 'POST':
        # Retrieve and update venue information
        venue_name = request.form['venue_name']
        city = request.form['city']
        description = request.form['description']

        # Update the venue information in the database
        connection = get_cursor()
        sql = '''
            UPDATE venues
            SET venue_name = %s, 
            description = %s,
            city = %s
        WHERE venue_id = %s;
        '''
        connection.execute(sql, (venue_name, description, city, venue_id))

        flash('Venue information updated successfully', 'success')
        return redirect(url_for('admin_venue_edit', venue_id=venue_id))

    return render_template('admin/admin_venue_page_update.html', 
        venue_info=venue_info, service_list = service_list, 
        space_list=space_list, venue_id=venue_id,
        selected_service_list = selected_service_list,
        complete_service_list = complete_service_list,
        event_type_list = event_type_list)



# Route for updating venue contact information
@app.route('/admin/manage_venues/<int:venue_id>/edit-contact', methods=['GET', 'POST'])
def admin_venue_contact_edit(venue_id):
    # Your authentication and role checking code here
    if not is_authenticated():
        return redirect(url_for('home'))
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['planner', 'customer']:
        flash('Unauthorised. not admin', 'warning')
        return redirect(url_for('home'))

    venue_info = get_venue_info(venue_id)

    if request.method == 'POST':
        # Retrieve and update contact information
        contact_phone = request.form['contact_phone']
        contact_email = request.form['contact_email']
        address = request.form['address']

        # Update the contact information in the database
        connection = get_cursor()
        sql = '''
            UPDATE venues
            SET contact_phone = %s,
            contact_email = %s,
            address = %s
        WHERE venue_id = %s;
        '''
        connection.execute(sql, (contact_phone, contact_email, address, venue_id))

        flash('Contact information updated successfully', 'success')
        return redirect(url_for('admin_venue_edit', venue_id=venue_id))

    return render_template('admin/admin_venue_page_update.html', venue_info=venue_info, venue_id=venue_id)

# Route to handle the form submission
# @app.route('/planner/my_venues/<int:venue_id>/edit-photos', methods=['GET', 'POST'])
# def planner_venue_photos_edit(venue_id):
#     # Your authentication and role checking code here


#     if request.method == 'POST':
#         # Retrieve and update photos
#         new_image = request.files.get('new_image')

#         # Handle photo upload and save to storage or database
#         # Update the venue's photo URLs list
    

#         flash('Photos updated successfully', 'success')
#         return redirect(url_for('planner_venue_edit', venue_id=venue_id))



# Route for updating facilities
@app.route('/admin/manage_venues/<int:venue_id>/edit-facilities', methods=['GET', 'POST'])
def admin_facilities_edit(venue_id):
    # Your authentication and role checking code here
    if not is_authenticated():
        return redirect(url_for('home'))
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['planner', 'customer']:
        flash('Unauthorised. not admin', 'warning')
        return redirect(url_for('home'))

    venue_info = get_venue_info(venue_id)

    if request.method == 'POST':
        # Get the list of facilities from the form
        facilities = request.form.getlist('facilities[]')
        # Convert the list of facilities to a string

        # remove emtry strs
        non_empty_facilities = []
        for entry in facilities:
            if entry != '':
                non_empty_facilities.append(entry)


        # Convert the list of facilities to a string
        facilities_str = ', '.join(non_empty_facilities)

        # Update the facilities information in the database
        connection = get_cursor()
        sql = '''
            UPDATE venues
            SET facilities = %s
        WHERE venue_id = %s;
        '''
        connection.execute(sql, (facilities_str, venue_id))

        flash('Facilities information updated successfully', 'success')
        return redirect(url_for('admin_venue_edit', venue_id=venue_id))




# Route for saving service options
@app.route('/admin/manage_venues/<int:venue_id>/edit-services', methods=['POST'])
def admin_service_options_edit(venue_id):
    # Your authentication and role checking code here
    if not is_authenticated():
        return redirect(url_for('home'))
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['planner', 'customer']:
        flash('Unauthorised. not admin', 'warning')
        return redirect(url_for('home'))

    if request.method == 'POST':
        # Retrieve and update service options
        new_service_ids = request.form.getlist('new_service_option[]')
        selected_service_list = request.form.getlist('selected_service_list[]') # a single list of str, with id and price, needing to be separated into sets of 2  

        # print(new_service_ids)
        # print(selected_service_list)

        # divide selected_service_list into sublists, with a set of 2 in each sublist 
        current_sublist = []
        new_selected_service_list = []

        for item in selected_service_list:
            current_sublist.append(item)
            if len(current_sublist) == 2:
                new_selected_service_list.append(current_sublist)
                current_sublist = []
        
        # print(new_selected_service_list)


        # situation 1: if new_service_ids does not exist, meaning an empty list, 
        # only existing services need to be updated in db 
        if not new_service_ids:
            update_existing_venue_services(venue_id, new_selected_service_list)
            flash('Service options updated successfully', 'success')

        # situation 2: if new_service_ids exist, 
        # update existing services and insert new services
        else:
            for id in new_service_ids:
                for selected_service in new_selected_service_list:
                    # if (id == selected_service[0] and selected_service[1] == '') or (id != selected_service[0] and selected_service[1] != ''):
                    #     flash('Please match service option with price','warning') 
                    # else:
                        update_existing_venue_services(venue_id, new_selected_service_list)
                        # insert new services
                        if id == selected_service[0]:
                            service_id = int(id)
                            service_price = float(selected_service[1])
                            if service_id == 1:
                                pricing_model = 'PerHead'
                            else:
                                pricing_model = 'Fixed'
                            cur = get_cursor()
                            sql = "INSERT INTO venue_services (venue_id, service_id, price, pricing_model) VALUES (%s, %s, %s, %s);"
                            cur.execute(sql, (venue_id, service_id, service_price, pricing_model))
                            
                            flash('Service options updated successfully', 'success')
                            return redirect(url_for('admin_venue_edit', venue_id=venue_id))

        return redirect(url_for('admin_venue_edit', venue_id=venue_id))


# Route for saving space information
@app.route('/admin/manage_venues/<int:venue_id>/edit-spaces', methods=['POST'])
def admin_space_information_edit(venue_id):

    # Your authentication and role checking code here
    if not is_authenticated():
        return redirect(url_for('home'))
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['planner', 'customer']:
        flash('Unauthorised. not admin', 'warning')
        return redirect(url_for('home'))
    
    ###### nay edits #####
    if (request.method == 'POST'
        and request.form.get("space_name")
        and request.form.get("space_id")
        and request.form.get("max_capacity")
        # and request.form.getlist("space_event_options[]")
        and request.form.get("equipment")
        and request.form.get("price")):


        venue_id = venue_id
        space_name = request.form.get("space_name")
        space_id = request.form.get("space_id")
        max_capacity = request.form.get("max_capacity")
        new_event_options = request.form.getlist("space_event_options[]")
        equipment = request.form.get("equipment")
        price = request.form.get("price")

        print(venue_id)
        print(space_name)
        print(space_id)
        print(max_capacity)
        print(new_event_options) # might be None (empty list), or ['4', '5']
        print(equipment)
        print(price)

        # input validation here with if-elif statements 
        # if all passed, the following would be in an else block
        
        ##### update 4 related tables ######
        # 1. update venue_spaces 
        connection = get_cursor()
        sql = 'UPDATE venue_spaces SET space_name = %s, equipment = %s WHERE space_id = %s;'
        connection.execute(sql, (space_name, equipment, space_id))

        # 2. update space_events, and get hold of a lift of space_event_id 
        new_space_event_id_list = [] 
        if new_event_options: # if not an empty list, e.g., ['4', '5']
            for event_id in new_event_options:
                connection = get_cursor()
                sql = 'INSERT INTO space_events (event_id, space_id) VALUES (%s, %s);'
                connection.execute(sql, (event_id, space_id))

                # get hold of newly auto-generated space_event_id from db
                connection = get_cursor()
                sql = 'SELECT space_event_id FROM space_events WHERE event_id = %s AND space_id = %s;'
                connection.execute(sql, (event_id, space_id))
                new_space_event_id = connection.fetchone() # a signle tuple
                new_space_event_id_list.append(new_space_event_id[0]) # a list of new space_event_id
        else: # if empty list, meaning no new event selected 
            pass

        # 3. update capacity
        # if new_event_options exist, change previous entries with new value, with old space_event_id,
        # at the same time create new entries with new value, with new space_event_id
        # else change previous entries only 
        if new_event_options: # if not an empty list, e.g., ['4', '5']
            # create new entries 
            for se_id in new_space_event_id_list:
                connection = get_cursor()
                sql = 'INSERT INTO capacity (space_event_id, max_capacity) VALUES (%s, %s);'
                connection.execute(sql, (se_id, max_capacity))
            
            # update previous entries 
            # step 1. get hold of a list of old space_event_id
            existing_se_id_list = get_all_space_event_ids_by_space_id(space_id) # list of tuples
            if existing_se_id_list:
                for data in existing_se_id_list:
                    existing_se_id = data[0]
                    # step 2. update previous entries 
                    connection = get_cursor()
                    sql = 'UPDATE capacity SET max_capacity = %s WHERE space_event_id = %s;'
                    connection.execute(sql, (max_capacity, existing_se_id))
        else: # no new event selected 
            # update previous entries 
            # step 1. get hold of a list of old space_event_id
            existing_se_id_list = get_all_space_event_ids_by_space_id(space_id) # list of tuples
            if existing_se_id_list:
                for data in existing_se_id_list:
                    existing_se_id = data[0]
                    # step 2. update previous entries 
                    connection = get_cursor()
                    sql = 'UPDATE capacity SET max_capacity = %s WHERE space_event_id = %s;'
                    connection.execute(sql, (max_capacity, existing_se_id))

        # 4. update charges 
        # if new_event_options exist, change previous entries with new value, with old space_event_id,
        # at the same time create new entries with new value, with new space_event_id
        # else change previous entries only 
        if new_event_options: # if not an empty list, e.g., ['4', '5']
            # create new entries 
            for se_id in new_space_event_id_list:
                connection = get_cursor()
                sql = 'INSERT INTO charges (space_event_id, price, pricing_model) VALUES (%s, %s, %s);'
                connection.execute(sql, (se_id, price, 'PerHour'))

            # update previous entries 
            if existing_se_id_list:
                for data in existing_se_id_list:
                    existing_se_id = data[0]
                    connection = get_cursor()
                    sql = 'UPDATE charges SET price = %s WHERE space_event_id = %s;'
                    connection.execute(sql, (price, existing_se_id))
        else: # no new event selected 
            # update previous entries only
            if existing_se_id_list:
                for data in existing_se_id_list:
                    existing_se_id = data[0]
                    connection = get_cursor()
                    sql = 'UPDATE charges SET price = %s WHERE space_event_id = %s;'
                    connection.execute(sql, (price, existing_se_id))


        # return 'all good!'
    
    flash('Space information updated successfully', 'success')
    return redirect(url_for('admin_venue_edit', venue_id=venue_id))


########### Financial Report ###########
@app.route('/admin/financial-report')
def generate_financial_report():
    # Get current date
    current_date = datetime.now()
    print(f"current date is {current_date}")

    # Get all payment data
    all_payment_data = get_all_payment_data()
    if all_payment_data is not None:

        ############## Total Revenue Jan to current month ##########
        this_jan = current_date.strftime('%Y-01')
        print(f'this jan is {this_jan}')
        this_month = current_date.strftime('%Y-%m')
        print(f'this month is {this_month}')

        year_end_goal = YEAR_END_GOAL
        year_to_date_total = 0.0

        for payment in all_payment_data:
            if datetime.strptime(this_jan, '%Y-%m') <= payment[0] <= current_date:
                year_to_date_total += float(payment[1]) 
        formatted_year_to_date_total = '{:,.2f}'.format(year_to_date_total)  # for display
        
        year_to_date_vs_year_end_labels = ['Year-to-Date Total', 'Year End Goal'] # list of str
        year_to_date_vs_year_end_values = [year_to_date_total, year_end_goal] # a list of val
        print(f"year_to_date_vs_year_end_values = {year_to_date_vs_year_end_values}")


        #################### monthly total revenue ########################
        this_month_total = 0.0
        for payment in all_payment_data:
            if this_month == payment[0].strftime('%Y-%m'):
                this_month_total += float(payment[1]) 
        formatted_this_month_total = '{:,.2f}'.format(this_month_total)  # for display
        
    ############# Past 12 months Performance ##################
        
        # Get the start date in the past 12 months
        twelve_months_ago = current_date - timedelta(days=365)
        print(f"12 months ago is {twelve_months_ago}")

        # Generate a list of the past 12 months
        months_list = [twelve_months_ago + timedelta(days=30 * i) for i in range(12)]
        print(f"months_list is {months_list}")

        # Create a dict where contains 12 months and default payment amount as 0.0
        monthly_totals_dict = {}
        for month in months_list:
            month_key = month.strftime('%Y-%m')
            monthly_totals_dict[month_key] = 0.0
        print(f"montly_totals_dict before accumulating : {monthly_totals_dict}")
        print()
  
        for payment_date_time, payment_amount in all_payment_data:
            month = payment_date_time.strftime('%Y-%m')
            for key in monthly_totals_dict.keys():
                if month == key:
                    monthly_totals_dict[key] += float(payment_amount)      
        print(f"montly total dict after accumulating is {monthly_totals_dict}")
        print()

        # seperate table into two data: labels - xcor and values- ycor
        labels = list(monthly_totals_dict.keys())
        print(f"labels = {labels}") 

        values = list(monthly_totals_dict.values())
        print(f" values = {values}")
        print()

        ################## YTD Total Revenue by Venues ###############
        all_venue_names_list = get_all_venue_names_list()
        print(f"all_venue_names_list = {all_venue_names_list}")

        venue_ytd_revenue_data = {}
        for venue_name in all_venue_names_list:
            venue_ytd_revenue_data[venue_name] = 0.0
        print(f"Initial venue_ytd_revenue_data = {venue_ytd_revenue_data}")
        print()

        venue_revenue_data_in_db = get_venue_revenue_data()

        for row in venue_revenue_data_in_db:
            venue_name = row[0]
            revenue = row[2]
            # print(type(revenue))

            # Check if the venue_name is in the dict
            for key in venue_ytd_revenue_data.keys():
                if key.strip().lower() == venue_name.strip().lower():
                    venue_ytd_revenue_data[key] += float(revenue)
        print(f"venue_ytd_revenue_data = {venue_ytd_revenue_data}")

        # seperate data into two dataset: labels - xcor and values- ycor
        venue_name_labels = list(venue_ytd_revenue_data.keys())
        print(f"venue_name_labels = {venue_name_labels}") 
        print("~~~~")

        venue_total_revenue = list(venue_ytd_revenue_data.values())
        print(f"venue_total_revenue = {venue_total_revenue }") 
        print("~~~~")

##################### Year-to-Date Monthly Total Revenue #####################
        this_jan_datetime = datetime.strptime(this_jan, '%Y-%m')
        this_month_datetime = datetime.strptime(this_month, '%Y-%m')
        
        year_to_date_months_list = [] 
        next_month = this_jan_datetime

        while next_month <= this_month_datetime:
            year_to_date_months_list.append(next_month.strftime('%Y-%m'))

            # Move to the first day of the next month
            next_month = next_month.replace(day=1)
            # Add one month
            next_month += timedelta(days=32)
            if year_to_date_months_list[-1] > this_month:
                year_to_date_months_list.pop()
        if this_month not in year_to_date_months_list:
            year_to_date_months_list.append(this_month)  

        print(f"year_to_date_months_list = {year_to_date_months_list}")
        year_to_date_monthly_revenue_data = {}
        for month in year_to_date_months_list:
            year_to_date_monthly_revenue_data[month] = 0.0
        print(f"Before - year_to_date_monthly_revenue_data = {year_to_date_monthly_revenue_data}")
        
        for payment in all_payment_data:
            payment_month_str = payment[0].strftime("%Y-%m")
            for month in year_to_date_months_list:
                if payment_month_str == month:
                    year_to_date_monthly_revenue_data[month] += float(payment[1]) 
        print(f"After - year_to_date_monthly_revenue_data = {year_to_date_monthly_revenue_data}")
        
        bar_chart_labels = year_to_date_months_list
        bar_chart_values = list(year_to_date_monthly_revenue_data.values())
        
        return render_template('admin/financial_report.html',
                                this_jan=this_jan, this_month=this_month,
                                formatted_year_to_date_total=formatted_year_to_date_total,
                                formatted_this_month_total=formatted_this_month_total,
                                year_to_date_vs_year_end_labels=year_to_date_vs_year_end_labels,
                                year_to_date_vs_year_end_values=year_to_date_vs_year_end_values,
                                labels=labels, values=values,
                                venue_name_labels=venue_name_labels,
                                bar_chart_labels=bar_chart_labels,
                                bar_chart_values=bar_chart_values,
                                venue_total_revenue=venue_total_revenue)
    else:
        flash('Data not found', 'warning')
        return redirect(url_for('home2'))
    

@app.route('/admin/popularity-report')
def popularity(): 
    ################### Most popular venue space ###################
    all_venue_names = get_all_venue_names_list()
    data_in_db = get_popular_venues_data()

    popularity_data = {}
    for venue_name in all_venue_names:
        popularity_data[venue_name] = 0
    print(f"before - popularity data is {popularity_data}")
    print()

    for row in data_in_db:
        for venue_name in popularity_data.keys():
            if row[1] == venue_name:
                popularity_data[venue_name] += 1
    print(f"after-popularity data = {popularity_data}")
    print()

    most_popular_venue_count = 0
    for venue, count in popularity_data.items():
        if count > most_popular_venue_count:
            most_popular_venue_count = count
    print(f"most_popular_venue_count is {most_popular_venue_count}")

    most_popular_venue = []
    for venue in popularity_data.keys():
        if popularity_data[venue] == most_popular_venue_count:
            most_popular_venue.append(venue)
    formatted_most_popular_venue = (" ,").join(most_popular_venue)
    print(f"most popular venues are {formatted_most_popular_venue}")

    labels = list(popularity_data.keys())
    values = list(popularity_data.values())

    ################### Most popular venue space ###################
    # get all spaces name
    all_space_names_list = []
    for row in data_in_db:
        space_name = row[3] + " @ " + row[1]
        all_space_names_list.append(space_name)
    print(f"all_space_names_list = {all_space_names_list}")
    print("----")

    space_popularity_data = {}
    for space_name in all_space_names_list:
        space_popularity_data[space_name] = 0
    print(f"before-space_popularity_data={space_popularity_data}")
    print("----")

    for space_name in all_space_names_list:
        for key in space_popularity_data.keys():
            if key == space_name:
                space_popularity_data[key] += 1
    print(f"after-space_popularity_data={space_popularity_data}")
    print("----")

    space_labels = list(space_popularity_data.keys())
    space_values = list(space_popularity_data.values())

    most_popular_space_count = 0
    for space, count in space_popularity_data.items():
        if count > most_popular_space_count:
            most_popular_space_count = count
    print(f"most_popular_space_count is {most_popular_space_count}")

    most_popular_space = []
    for space in space_popularity_data.keys():
        if space_popularity_data[space] == most_popular_space_count:
            most_popular_space.append(space)
    formatted_most_popular_space = (" ,").join(most_popular_space)
    print(f"most popular space are {formatted_most_popular_space}")



    return render_template("admin/popularity.html",
                           labels=labels,
                           values=values,
                           most_popular_venue=formatted_most_popular_venue,
                           space_labels=space_labels,
                           space_values=space_values,
                           most_popular_space=formatted_most_popular_space)
    