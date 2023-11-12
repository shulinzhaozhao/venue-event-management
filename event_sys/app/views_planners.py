from app import app
from app.db import *
from flask import render_template, request, redirect, url_for, session, flash, jsonify
import re
import bcrypt
from datetime import datetime, date, time, timedelta


@app.route('/planners')
def home3():
    data = get_user_info()
    print(data)
    return 'planners views is all good .'

# display planner dashboard
@app.route('/planner/dashboard')
def planner_dashboard():
    if not is_authenticated():
        return redirect(url_for('home'))
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['customer', 'admin']:
        flash('Unauthorised. not planner', 'warning')
        return redirect(url_for('home'))
    # get a list of venues, including venue names, 
    # descriptions, first image_url, and event types
    venue_list = get_venue_list(None)

    # get event_type_list, location_list 
    event_type_list, location_list = get_filter_dropdown_options()

    return render_template('planners/planner_dashboard.html', 
        full_name=f"{session['first_name']} {session['last_name']}", 
        venue_list =  venue_list,
        event_type_list = event_type_list, location_list = location_list)


################### View and Manage Profile ###################

# Planner Display Profile 
@app.route('/planner/profile')
def planner_profile():

    if not is_authenticated():
        return redirect(url_for('home'))
    
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['customer', 'admin']:
        flash('Unauthorised. not planner', 'warning')
        return redirect(url_for('home'))
    
    user_id = session['user_id']
    connection = get_cursor()
    connection.execute('SELECT * FROM planners JOIN users \
                       ON planners.user_id = users.user_id \
                       WHERE planners.user_id =%s;', (user_id,))
    account = connection.fetchone()
    return render_template('planners/planner_profile.html', account=account)

# Update profile
@app.route('/planner/profile/update', methods=['GET', 'POST'])
def planner_profile_update():
    
    if not is_authenticated():
        return redirect(url_for('home'))
    
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['customer', 'admin']:
        flash('Unauthorised. not planner', 'warning')
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
                sql_planners = "UPDATE planners SET first_name = %s, last_name = %s, email = %s, contact_number = %s, address = %s WHERE user_id = %s;"
                # Update the planners table 
                connection.execute(sql_planners, (first_name, last_name, email, contact_number, address, user_id,))
                
                flash('You have successfully updated your profile!', 'success')
        else:
            flash('Please fill out the form.', 'warning')

    return redirect(url_for('planner_profile'))

########################### Change Password ###############################
# Display password change page
@app.route('/planner/password')
def planner_change_password():
    if "loggedin" in session:
        return render_template('planners/planner_change_password.html')
    
    return redirect(url_for('sign_in'))


# Define a route to handle the password change form
@app.route('/planner/password/change', methods=['GET', 'POST'])
def planner_change_password_update():
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
                    return redirect(url_for('planner_change_password'))
        
                user_id = session['user_id']
                # Use "get_user_hashed_password" to get the hashed password
                hashed_password = get_user_hashed_password(user_id)
        
                #Verify the old password
                if not verify_password(old_password, hashed_password):
                    flash('Incorrect old password.', 'warning')
                    return redirect(url_for('planner_change_password'))
            
                # Hash the new password before updating the database
                hashed_new_password = generate_hashed_password(new_password)
        
                # Update the new password in db
                connection = get_cursor()
                sql = "UPDATE users SET password = %s WHERE user_id = %s;"
                connection.execute(sql, (hashed_new_password, user_id,))

                flash('Password updated successfully!', 'success')
                return redirect(url_for('planner_change_password'))
            else:
                flash('Please fill out the form.', 'warning')

    return redirect(url_for('sign_in'))

######################## Planner View and Edit Venues ###############################
@app.route('/planner/my_venues')
def planner_view_my_venues():
    user_id = session['user_id']
    # Use user_id to get planner id 
    connection = get_cursor()
    sql_plannerID = "SELECT planner_id FROM planners JOIN users \
                    ON planners.user_id = users.user_id WHERE planners.user_id = %s;"
    connection.execute(sql_plannerID, (user_id,))
    planner_id = connection.fetchone()[0]
    venue_list = planner_get_venue_list(planner_id)
    
    return render_template('planners/planner_venue_list.html', venue_list=venue_list)



# Get individual venue info and the related space list
@app.route('/planner/my_venues/<int:venue_id>')
def planner_venue_page(venue_id):

    if not is_authenticated():
        return redirect(url_for('home'))
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['admin', 'customer']:
        flash('Unauthorised. not planner', 'warning')
        return redirect(url_for('home'))
    
    venue_info = get_venue_info(venue_id)
    space_list = get_space_list(venue_id)

    return render_template('planners/planner_venue_page.html', venue_info = venue_info, space_list = space_list)


######################## Edit Venues ###############################
######################## Edit Venues ###############################
######################## Edit Venues ###############################
######################## Edit Venues ###############################


# Route for updating venue information
@app.route('/planner/my_venues/<int:venue_id>/edit-venue', methods=['GET', 'POST'])
def planner_venue_edit(venue_id):
    # Your authentication and role checking code here
    if not is_authenticated():
        return redirect(url_for('home'))
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['admin', 'customer']:
        flash('Unauthorised. not planner', 'warning')
        return redirect(url_for('home'))

    venue_info = get_venue_info(venue_id)
    space_list = get_space_list(venue_id)
    event_type_list = get_event_type_list()
    #venue_service_price_list = get_venue_service_price(venue_id)

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
        return redirect(url_for('planner_venue_edit', venue_id=venue_id))

    return render_template('planners/planner_venue_page_update.html', 
                           venue_info=venue_info, service_list = service_list, 
                           space_list=space_list, venue_id=venue_id,
                           selected_service_list = selected_service_list,
                           complete_service_list = complete_service_list,
                           event_type_list = event_type_list, 
                        )

# Route for updating venue contact information
@app.route('/planner/my_venues/<int:venue_id>/edit-contact', methods=['GET', 'POST'])
def planner_venue_contact_edit(venue_id):
    # Your authentication and role checking code here
    if not is_authenticated():
        return redirect(url_for('home'))
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['admin', 'customer']:
        flash('Unauthorised. not planner', 'warning')
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
        return redirect(url_for('planner_venue_edit', venue_id=venue_id))

    return render_template('planners/planner_venue_page_update.html', venue_info=venue_info, venue_id=venue_id)

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
@app.route('/planner/my_venues/<int:venue_id>/edit-facilities', methods=['GET', 'POST'])
def planner_facilities_edit(venue_id):
    # Your authentication and role checking code here
    if not is_authenticated():
        return redirect(url_for('home'))
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['admin', 'customer']:
        flash('Unauthorised. not planner', 'warning')
        return redirect(url_for('home'))

    venue_info = get_venue_info(venue_id)

    if request.method == 'POST':
        # Get the list of facilities from the form
        facilities = request.form.getlist('facilities[]')

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
        return redirect(url_for('planner_venue_edit', venue_id=venue_id))


# Route for saving service options
@app.route('/planner/my_venues/<int:venue_id>/edit-services', methods=['POST'])
def planner_service_options_edit(venue_id):
    # Your authentication and role checking code here
    if not is_authenticated():
        return redirect(url_for('home'))
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['admin', 'customer']:
        flash('Unauthorised. not planner', 'warning')
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
                            return redirect(url_for('planner_venue_edit', venue_id=venue_id))

        return redirect(url_for('planner_venue_edit', venue_id=venue_id))


######################## Edit space ###############################
######################## Edit space ###############################
######################## Edit space ###############################
######################## Edit space ###############################


# Route for saving space information
@app.route('/planner/my_venues/<int:venue_id>/edit-spaces', methods=['POST'])
def planner_space_information_edit(venue_id):

    # Your authentication and role checking code here
    if not is_authenticated():
        return redirect(url_for('home'))
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['admin', 'customer']:
        flash('Unauthorised. not planner', 'warning')
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
    return redirect(url_for('planner_venue_edit', venue_id=venue_id))

    # return 'some info missing'


@app.route('/planner/my_venues/<int:venue_id>/delete')
def planner_venue_delete(venue_id):

    if not is_authenticated():
        return redirect(url_for('home'))
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['admin', 'customer']:
        flash('Unauthorised. not planner', 'warning')
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
    if len(result) != 0:
        flash('This venue has bookings. Delete venue not allowed.','warning')
        return redirect(url_for('planner_view_my_venues'))
    else:
        sql_update = 'UPDATE venues SET is_deleted = 1 WHERE venue_id = %s;'
        connection.execute(sql_update, (venue_id,))

    flash('Venue deleted successfully', 'success')
    return redirect(url_for('planner_view_my_venues'))
  
# View all venues from the planner's dashboard
@app.route('/planner/all_venues')
def planner_view_all_venues():
    # get a list of venues, including venue names, 
    # descriptions, first image_url, and event types
    venue_list = get_venue_list(None)

    # get event_type_list, location_list 
    event_type_list, location_list = get_filter_dropdown_options()

    return render_template('planners/planner_all_venues.html', venue_list =  venue_list,
        event_type_list = event_type_list, location_list = location_list)

# get individual venue info and the related space list
@app.route('/planner/all_venues/<int:venue_id>')
def planner_venue_page_all_venues(venue_id):
    venue_info = get_venue_info(venue_id)
    space_list = get_space_list(venue_id)

    return render_template('planners/planner_venue_page_all_venues.html', venue_info = venue_info, space_list = space_list)

############################# Planner View Event Calendar ###############################
@app.route('/planner/select-venue')
def select_venue():
    # find the planner's venues and make a drop down menue, so it can be selected
    user_id = session['user_id']
    planner_id = get_planer_id_by_user_id(user_id)
    planner_s_venue_info = get_planner_s_venue_info_by_planner_id(planner_id)
    print(f"planner_s_venue_info is {planner_s_venue_info}")

    return render_template("planners/planner_select_venue.html", planner_s_venue_info=planner_s_venue_info )

@app.route('/planner/handle_venue_selection', methods=['POST'])
def handle_venue_selection():
    if request.method == 'POST':
        selected_venue_id = request.form.get('selected_venue_id')
        print(f"selected venue id is {selected_venue_id}")

        # find all the space the planner manages
        space_id_list = get_space_id_list_by_venue_id(selected_venue_id)
        print(f"space_id_list is {space_id_list}")
        
        # get all space with events booked
        all_space_event_id_list = []

        if space_id_list is not None:    
            for space_id in space_id_list:
                space_event_id_data = get_all_space_event_ids_by_space_id(space_id)
                for data in space_event_id_data:
                    all_space_event_id_list.append(data[0])
            print(f"allllll space event id list is {all_space_event_id_list}")

            # Store the data in the session
            session['selected_venue_id'] = selected_venue_id
            return redirect(url_for("event_calendar"))
        
        else:
            flash("No events have been found in this space", "warning")
            return redirect(url_for("select_venue"))
        
    return redirect(url_for('event_calendar'))


@app.route('/planner/event-calendar', methods=['POST', 'GET'])
def event_calendar():
    try:
        selected_venue_id = session['selected_venue_id']
        events = get_booked_venue_spaces(selected_venue_id)
        print(f"alllllllllll events are {events}")   

    except KeyError:
        events = get_booked_venue_spaces(selected_venue_id)
        flash("Selected Venue ID not found in the session", 'warning')
        return redirect(url_for('select_venue'))
    
    return render_template('planners/planner_event_calendar.html', events=events)

############################## Planner View Customers ###################################
@app.route('/planner/my_customer')
def planner_my_customer():
    if "loggedin" in session:
        # Get the planner_id of the planner logged in
        user_id = session['user_id']
        planner_id = get_planner_id(user_id)
        #print(planner_id)
        
        # Get the customer_id list from bookings that match the logged in planner
        customer_id_list = get_customer_id_from_booking(planner_id)
        #print(customer_id_list)
        
        customers = []
        for customer_id in customer_id_list:

            connection = get_cursor()
            sql = "SELECT * FROM customers WHERE customer_id = %s;"
            connection.execute(sql, (customer_id,))
            customer = connection.fetchone()
            customers.append(customer)
        
        #print(customers)
        return render_template('planners/planner_view_customer.html', customers = customers)
    
    return redirect(url_for('sign_in'))

@app.route('/planner/my_customer/view', methods=['GET'])
def planner_my_customer_search():
    if "loggedin" in session:

        connection = get_cursor()
    
        # Get the search query from the URL query parameters
        search_query = request.args.get('search_query', '')

        # Modify your SQL query to include the search filter
        query = 'SELECT * FROM customers WHERE first_name LIKE %s OR last_name LIKE %s'
        connection.execute(query, ('%' + search_query + '%', '%' + search_query + '%'))
        customers = connection.fetchall()
    
        return render_template('planners/planner_view_customer.html', customers=customers, search_query=search_query)
    return redirect(url_for('sign_in'))
# note: when defining routes and functions, 
# please add the role prefix to avoid name clashing, 
# e.g., route('/admin/profile')
# def admin_profile()

#-------------------------------------------------------------------
#----------------------Planner Messages-----------------------------
#-------------------------------------------------------------------

@app.route('/planner_messages', methods=['GET', 'POST'])
def planner_messages():
    if not is_authenticated():
        return redirect(url_for('home'))

    if request.method == 'POST':
        # Handle actions like deleting or updating messages here
        message_id_to_delete = request.form.get('delete_message_id')

        if message_id_to_delete:
            # Assuming you have a database connection, delete the message by its ID
            db_cursor = get_cursor()  # Replace get_cursor with your database connection logic
            query = "DELETE FROM venue_inquiries WHERE venue_inquiry_id = %s"
            db_cursor.execute(query, (message_id_to_delete,))

            # Optionally, you can add a flash message to indicate that the message was deleted
            flash('Message deleted successfully', 'success')

    # Fetch messages for the logged-in planner from the database
    if 'user_id' in session:
        user_id = session['user_id']
        # Get the planner_id based on the user_id
        db_cursor = get_cursor()  # Replace with your database connection logic
        query = "SELECT planner_id FROM planners WHERE user_id = %s"
        db_cursor.execute(query, (user_id,))
        result = db_cursor.fetchone()

        if result:
            planner_id = result[0]
            # Retrieve messages associated with the planner_id
            query = "SELECT * FROM venue_inquiries WHERE planner_id = %s"
            db_cursor.execute(query, (planner_id,))
            messages = db_cursor.fetchall()

            return render_template('planners/planner_messages.html', messages=messages)

    flash('Please log in to view your messages.', 'warning')
    return redirect(url_for('sign_in'))

#-------------------------------------------------------------------
#------------------Planner Messages Details-------------------------
#-------------------------------------------------------------------

@app.route('/planner_message/<int:message_id>')
def planner_message(message_id):
    # Retrieve the message details from the database based on the message_id
    db_cursor = get_cursor()  # Replace with your database connection logic
    query = "SELECT * FROM venue_inquiries WHERE venue_inquiry_id = %s"
    db_cursor.execute(query, (message_id,))
    message = db_cursor.fetchone()

    return render_template('planners/planner_message_details.html', message=message)

#-------------------------------------------------------------------
#----------------------Planner Send Messages------------------------
#-------------------------------------------------------------------

@app.route('/planner_send_message', methods=['GET', 'POST'])
def planner_send_message():
    if request.method == 'POST':
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Get the current date and time
        current_date = datetime.now()

        db_cursor = get_cursor()

        query = "INSERT INTO planner_message (subject, message_body, message_date) VALUES (%s, %s, %s)"
        values = (subject, message, current_date)
        db_cursor.execute(query,values)

        # Redirect to a confirmation page or another page as needed
        return redirect(url_for('planner_messages'))

    return render_template('planners/planner_send_message.html')

@app.route('/refund_process')
def refund_process():
    if not is_authenticated():
        return redirect(url_for('home'))
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['customer', 'admin']:
        flash('Unauthorised. not planner', 'warning')
        return redirect(url_for('home'))
    cur = get_cursor()
    # cur.execute(
    #     '''SELECT * FROM payment
    #         JOIN bookings ON payment.booking_id = bookings.booking_id
    #         WHERE bookings.order_status = 'cancelled'
    #         AND bookings.refund_amount != 0.00
    #         AND payment.payment_description = 'refund pending';'''
    #         )


    sql = '''
        SELECT
        payment.booking_id, 
        payment.payment_amount,
        bookings.refund_amount,

        customers.first_name,
        customers.last_name, 
        users.username, 

        event_types.event_name,
        venue_spaces.space_name,
        venues.venue_name

        FROM payment
        JOIN bookings ON payment.booking_id = bookings.booking_id
        JOIN customers ON bookings.user_id = customers.user_id
        JOIN users ON customers.user_id = users.user_id
        JOIN space_events ON bookings.space_event_id = space_events.space_event_id
        JOIN event_types ON space_events.event_id = event_types.event_id
        JOIN venue_spaces ON venue_spaces.space_id = space_events.space_id 
        JOIN venues ON venues.venue_id = venue_spaces.venue_id
        WHERE bookings.order_status = 'cancelled'
        AND bookings.refund_amount != 0.00
        AND payment.payment_description = 'refund pending';'''
    cur.execute(sql)

    bookings = cur.fetchall()
    print(bookings)

    return render_template('planners/refund_process.html',bookings=bookings )

@app.route('/process_refund/<booking_id>/<refund_amount>', methods=['POST'])
def process_refund(booking_id,refund_amount):
    # cur = get_cursor()
    # cur.execute("UPDATE bookings SET refund_amount = 0.0 WHERE booking_id = %s", (booking_id,))

    cur = get_cursor()
    sql = "UPDATE payment SET payment_description = 'refunded' WHERE booking_id = %s;"
    cur.execute(sql,(booking_id,))

    # Insert data into the refunds table
    cur.execute(
        "INSERT INTO refunds (booking_id, refund_amount, refund_date) VALUES (%s, %s, %s)",
        (booking_id, refund_amount, datetime.now())
    )
    flash(f'Refund has been processed successfully.', 'success')
    return redirect(url_for('refund_process'))






 