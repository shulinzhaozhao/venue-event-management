from app import app
from app.db import *
from flask import render_template, request, redirect, url_for, session, flash, json
import re
import bcrypt
from datetime import datetime, date, time, timedelta
from decimal import Decimal
import math


@app.route('/customers')
def home4():
    data = get_user_info()
    print(data)
    return 'customers views is all good .'

# display customer dashboard
@app.route('/customer/dashboard')
def customer_dashboard():
    if not is_authenticated():
        return redirect(url_for('home'))
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['admin', 'planner']:
        flash('Unauthorised. not customer', 'warning')
        return redirect(url_for('home'))
    # get a list of venues, including venue names, 
    # descriptions, first image_url, and event types
    venue_list = get_venue_list(None)

    # get event_type_list, location_list 
    event_type_list, location_list = get_filter_dropdown_options()

    return render_template('customers/customer_dashboard.html', 
        full_name=f"{session['first_name']} {session['last_name']}",
        venue_list = venue_list, event_type_list = event_type_list,
        location_list = location_list)


################### View and Manage Profile ###################

# Planner Display Profile 
@app.route('/customers/profile')
def customer_profile():

    if not is_authenticated():
        return redirect(url_for('home'))
    
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['planner', 'admin']:
        flash('Unauthorised. not customer', 'warning')
        return redirect(url_for('home'))
    
    user_id = session['user_id']
    connection = get_cursor()
    connection.execute('SELECT * FROM customers JOIN users \
                       ON customers.user_id = users.user_id \
                       WHERE customers.user_id =%s;', (user_id,))
    account = connection.fetchone()
    return render_template('customers/customer_profile.html', account=account)

# Update profile
@app.route('/customers/profile/update', methods=['GET', 'POST'])
def customer_profile_update():
    
    if not is_authenticated():
        return redirect(url_for('home'))
    
    user_role = get_user_role()
    if user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
        return redirect(url_for('home'))
    elif user_role in ['planner', 'admin']:
        flash('Unauthorised. not customer', 'warning')
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
                sql_customer = "UPDATE customers SET first_name = %s, last_name = %s, email = %s, contact_number = %s, address = %s WHERE user_id = %s;"
                # Update the customer table 
                connection.execute(sql_customer, (first_name, last_name, email, contact_number, address, user_id,))
                
                flash('You have successfully updated your profile!', 'success')
        else:
            flash('Please fill out the form.', 'warning')

    return redirect(url_for('customer_profile'))

########################### Change Password ###############################
# Display password change page
@app.route('/customer/password')
def customer_change_password():
    if "loggedin" in session:
        return render_template('customers/customer_change_password.html')
    
    return redirect(url_for('sign_in'))


# Define a route to handle the password change form
@app.route('/customer/password/change', methods=['GET', 'POST'])
def customer_change_password_update():
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
                    return redirect(url_for('customer_change_password'))
        
                user_id = session['user_id']
                # Use "get_user_hashed_password" to get the hashed password
                hashed_password = get_user_hashed_password(user_id)
        
                #Verify the old password
                if not verify_password(old_password, hashed_password):
                    flash('Incorrect old password.', 'warning')
                    return redirect(url_for('customer_change_password'))
            
                # Hash the new password before updating the database
                hashed_new_password = generate_hashed_password(new_password)
        
                # Update the new password in db
                connection = get_cursor()
                sql = "UPDATE users SET password = %s WHERE user_id = %s;"
                connection.execute(sql, (hashed_new_password, user_id,))

                flash('Password updated successfully!', 'success')
                return redirect(url_for('customer_change_password'))
            else:
                flash('Please fill out the form.', 'warning')

    return redirect(url_for('sign_in'))

##################################### Customer View Venues ###################################
# View all venues from the customer's dashboard
@app.route('/customer/all_venues')
def customer_view_all_venues():

    # get a list of venues, including venue names, 
    # descriptions, first image_url, and event types
    venue_list = get_venue_list(None)

    # get event_type_list, location_list 
    event_type_list, location_list = get_filter_dropdown_options()

    return render_template('customers/customer_all_venues.html', 
        venue_list = venue_list, event_type_list = event_type_list,
        location_list = location_list)


# get individual venue info and the related space list
@app.route('/customer/all_venues/<int:venue_id>')
def customer_venue_page_all_venues(venue_id):
    venue_info = get_venue_info(venue_id)
    space_list = get_space_list(venue_id)
    venue_id=venue_id

    return render_template('customers/customer_venue_page_all_venues.html', 
                           venue_info = venue_info, 
                           space_list = space_list,
                           venue_id=venue_id)



@app.route('/customer/book-venue/<int:venue_id>/<int:space_id>')
def customer_book_venue(venue_id, space_id):

    # print(f'venue id {venue_id}')
    # print(f'space id {space_id}')
    # print()

    venue_info = get_venue_info(venue_id)
    print(venue_info)
    print()

    space_list = get_space_list(venue_id)
    print(space_list)
    print()

    # Find which space in the venue to be booked
    space_info = []
    for space in space_list:
        if space[-1] == space_id:
            space_info = space
    print(space_info)

    # Format event_options as a list of stirng
    event_options = space_info[2].split(', ')
    print(event_options)

    # Get current date time info
    current_datetime = datetime.now()
    formatted_current_datetime = current_datetime.strftime("%Y-%m-%dT%H:%M")

    return render_template('customers/customer_book_venue.html', 
                           venue_id=venue_id,
                           space_id=space_id,
                           venue_info=venue_info,
                           space_info=space_info,
                           event_options=event_options,
                           current_datetime=formatted_current_datetime)


@app.route('/customer/review-booking', methods=['GET','POST'])
def review_booking():

    booking_data = None # Initialize booking_data as None
    venue_info = None 

    if request.method == 'POST':
        # Constance
        current_date_time = datetime.now()
        status = 'booked'
        refund = 0
        user_id = session['user_id']

        # Retrieve data from form
        venue_id = request.form.get('venue_id')
        space_id = request.form.get('space_id')
        venue_name = request.form.get('venue')
        space_name = request.form.get('space')
        event_type = request.form.get('event_type')
        number_of_guests = request.form.get('number_of_guests')
        start = request.form.get('start') # datetime-local input get iso8601 str
        end = request.form.get('end') # iso str
        selected_services = request.form.getlist('services[]')

        # validate space availability
        # Convert ISO 8601 string to datetime object
        wanted_start_datetime = datetime.strptime(start, '%Y-%m-%dT%H:%M')
        wanted_end_datetime = datetime.strptime(end, '%Y-%m-%dT%H:%M')
        
        if not is_booking_available(space_id,wanted_start_datetime,wanted_end_datetime):
            flash('The time has been booked. Please choose another time', 'warning')
            return redirect(url_for('customer_book_venue', space_id=space_id, venue_id=venue_id))

        # Get event id for populating database
        event_id = get_event_id_by_name(event_type)

        # Get venue info
        venue_info = get_venue_info(venue_id)

        # Find space_event_id
        space_event_id = find_space_event_id_by_space_id_and_event_id(space_id, event_id)

        # Find venue hourly rate
        venue_hourly_rate = find_venue_price_by_space_event_id(space_event_id)

        # Format booking date time into string
        booking_date_time = current_date_time.strftime('%Y-%m-%d %H:%M:%S')

        # Convert start and end time str to datatime object then format them into readable strings
        start_datetime = datetime.strptime(start, '%Y-%m-%dT%H:%M')
        end_datetime = datetime.strptime(end, '%Y-%m-%dT%H:%M')
        start_str = start_datetime.strftime('%Y-%m-%d %H:%M %p')
        end_str = end_datetime.strftime('%Y-%m-%d %H:%M %p')


        ####### calculate event total hours #############
        total_hours = 0 # Initialize total_hours

        # situation 1:  3 and more days event
        if (end_datetime.date() - start_datetime.date()).days + 1 >= 3:
            num_of_days_between_start_and_end_dates = (end_datetime.date() - start_datetime.date()).days + 1 - 2
            interval_hours = num_of_days_between_start_and_end_dates * 6
            total_hours += interval_hours
            print(f"number of days between start and end dats is {num_of_days_between_start_and_end_dates} days, and the total hours for that is {interval_hours}")
        
            # Calculate how many hours in start date
            next_midnight = datetime(start_datetime.year, start_datetime.month, start_datetime.day) + timedelta(days=1)
            print(f"next_midnight is {next_midnight}")
            duration_to_midnight_in_hours = math.ceil((next_midnight - start_datetime).seconds / 3600)
            print(f"duration_to_midnight_in_hours is {duration_to_midnight_in_hours} hours")
            
            if duration_to_midnight_in_hours >= 6:
                total_hours += 6
            else:
                total_hours += duration_to_midnight_in_hours

            # Calculate how many hours in end date
            midnight = datetime(end_datetime.year, end_datetime.month, end_datetime.day)
            print(f"midnight is {midnight}")
            midnight_to_end_in_hours = math.ceil((end_datetime - midnight).seconds/3600)
            print(f"midnight_to_end_in_hours is {duration_to_midnight_in_hours} hours")

            if midnight_to_end_in_hours >= 6:
                total_hours += 6
            else:
                total_hours += midnight_to_end_in_hours
        
        # situation 2: 2days event
        elif (end_datetime.date() - start_datetime.date()).days + 1 == 2:
            # Calculate how many hours in start date
            next_midnight = datetime(start_datetime.year, start_datetime.month, start_datetime.day) + timedelta(days=1)
            print(f"next_midnight is {next_midnight}")
            duration_to_midnight_in_hours = math.ceil((next_midnight - start_datetime).seconds / 3600)
            print(f"duration_to_midnight_in_hours is {duration_to_midnight_in_hours} hours")
            
            if duration_to_midnight_in_hours >= 6:
                total_hours += 6
            else:
                total_hours += duration_to_midnight_in_hours

            # Calculate how many hours in end date
            midnight = datetime(end_datetime.year, end_datetime.month, end_datetime.day)
            print(f"midnight is {midnight}")
            midnight_to_end_in_hours = math.ceil((end_datetime - midnight).seconds/3600)
            print(f"midnight_to_end_in_hours is {duration_to_midnight_in_hours} hours")

            if midnight_to_end_in_hours >= 6:
                total_hours += 6
            else:
                total_hours += midnight_to_end_in_hours       

        # situation 3: event within one day
        elif (start_datetime.date() - end_datetime.date()).days == 0:
           hours = math.ceil((end_datetime - start_datetime).seconds / 3600)
           print(f"hours is {hours}")
           if hours >= 6:
               total_hours += 6
           else:
               total_hours += hours
               print(f"total hours is {total_hours}")
        
        else: 
            flash("Please choose another date and time", 'warning')

        # Format selected_services
        add_on_services = []
        for option in selected_services:
            service_id = get_service_id_by_name(option)
            service_price_and_pricing_model = find_service_price_and_pricing_model_by_venue_id_and_service_id(venue_id, service_id)
            add_on = (service_id, option, service_price_and_pricing_model[0],service_price_and_pricing_model[1])
            add_on_services.append(add_on)

        # Pack and send booking_data to review-booking page
        booking_data = [
            user_id,#0
            booking_date_time, #1
            status, #2
            refund, #3
            (venue_id, venue_name), #4
            (space_id, space_name), #5
            (event_id, event_type), #6
            number_of_guests, #7
            (start_str, end_str, total_hours, venue_hourly_rate), #8
            add_on_services, #9
            space_event_id #10
        ]
        
    return render_template('customers/customer_review_booking.html',
                           booking_data=booking_data,
                           venue_info=venue_info)



@app.route('/customer/process-booking', methods=['POST'])
def process_booking():
    if request.method == 'POST':
        total_fee = request.form.get('total_fee')
        user_id = request.form.get('user_id')
        booking_date_time = request.form.get('booking_date_time')
        status = request.form.get('status')
        refund = request.form.get('refund')
        venue_id = request.form.get('venue_id')
        space_id = request.form.get('space_id')
        event_id = request.form.get('event_id')
        number_of_guests = request.form.get('number_of_guests')
        start_str = request.form.get('start_str')
        end_str = request.form.get('end_str')
        service_ids = request.form.get('all_service_ids')
        
        space_event_id = find_space_event_id_by_space_id_and_event_id(space_id,event_id)

        ### update tables:1.bookings, 2.availability,  3.payment
        # update 1. booking table
        insert_new_booking(booking_date_time,status,refund,user_id,space_event_id,number_of_guests,service_ids)
        booking_id = get_booking_id_by_booking_date_time_and_space_event_id(booking_date_time, space_event_id)
        # Convert tuple to a int value
        
        # update 2. availability table
        # convert start and end date time format into datetime object
        format = "%Y-%m-%d %H:%M %p"
        start_date_time= datetime.strptime(start_str, format)
        end_date_time= datetime.strptime(end_str, format)
        
        insert_new_availability(start_date_time, end_date_time, space_id, booking_id)

        # update 3. payment
        payment_date_time = datetime.now()
        insert_new_payment(booking_id,payment_date_time, total_fee, payment_status="successful")

        # Insert the "Booking Made" message into the customer_messages table
        message_body = "New booking Made"

        message_date = datetime.now().date()

        subject = "Booking"
        
        db_cursor = get_cursor()
        insert_query = "INSERT INTO customer_messages (user_id, message_date, subject, message_body) VALUES (%s, %s, %s, %s)"
        db_cursor.execute(insert_query, (user_id, message_date, subject, message_body))


        flash("Payment successful", "success")
        return redirect("/customer/booking_list")
    
# def create_customer_message(user_id, message_body):
#     db_cursor = get_cursor()
#     insert_query = "INSERT INTO customer_messages (user_id, message_date_time, subject, message_body) VALUES (%s, NOW(), %s, %s)"
#     subject = "Booking Confirmation"  # Assuming a static subject
#     db_cursor.execute(insert_query, (user_id, subject, message_body))

##############################################################
######################## manage booking ######################
##############################################################

# get hold of customer's booking list, containing both past and upcoming events 
@app.route('/customer/booking_list')
def customer_booking_list():
     
    user_role = get_user_role()

    if not is_authenticated():
        flash('Unauthorised. Please sign in first.', 'warning')  
    elif user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
    elif user_role in ['planner', 'admin']:
        flash('Unauthorised. not customer', 'warning')
    else:

        user_id = session['user_id']
        upcoming_event_list, past_event_list = get_booking_list(user_id)

        if upcoming_event_list:
            for index,event in enumerate(upcoming_event_list):
                event = list(event)
                booking_datetime = event[1].strftime('%Y-%m-%d %H:%M') 
                start_datetime = event[-2].strftime('%Y-%m-%d %H:%M')
                end_datetime = event[-1].strftime('%Y-%m-%d %H:%M')  
                event[1] = booking_datetime
                event[-2] = start_datetime
                event[-1] = end_datetime
                upcoming_event_list[index] = event

        # print(f'upcoming: \n {upcoming_event_list} \n')


        if past_event_list:
            for index,event in enumerate(past_event_list):
                event = list(event)
                booking_datetime = event[1].strftime('%Y-%m-%d %H:%M') 
                start_datetime = event[-2].strftime('%Y-%m-%d %H:%M')
                end_datetime = event[-1].strftime('%Y-%m-%d %H:%M')  
                event[1] = booking_datetime
                event[-2] = start_datetime
                event[-1] = end_datetime
                past_event_list[index] = event
        # print(f'past: \n {past_event_list}')

        return render_template('customers/customer_booking_list.html', 
            upcoming_event_list = upcoming_event_list, 
            past_event_list = past_event_list)
    
    return redirect(url_for('home'))


# get hold of customer's booking detail
@app.route('/customer/booking_detail/<booking_id>')
def customer_booking_detail(booking_id):
    user_role = get_user_role()

    if not is_authenticated():
        flash('Unauthorised. Please sign in first.', 'warning')  
    elif user_role not in USER_ROLES:
        flash('Unauthorised. not in roles', 'warning')
    elif user_role in ['planner', 'admin']:
        flash('Unauthorised. not customer', 'warning')
    else:
        # print(f' \n booking id {booking_id} \n')

        booking_info = get_booking_detail(booking_id)


        venue_id = booking_info[-2]
        venue_info = get_venue_info(venue_id)

        space_list = get_space_list(venue_id)


        # Find which space in the venue has been booked
        space_id = booking_info[-1]
        space_info = []
        for space in space_list:
            if space[-1] == space_id:
                space_info = space

        # Format event_options as a list of stirng
        event_options = space_info[2].split(', ')

        # Get current date time info
        current_datetime = datetime.now()
        formatted_current_datetime = current_datetime.strftime("%Y-%m-%dT%H:%M")


        return render_template('customers/customer_booking_detail.html',
            booking_info = booking_info,
            current_datetime=formatted_current_datetime,
            venue_info = venue_info,
            event_options = event_options,
            booking_id = booking_id)
    
    return redirect(url_for('home'))


@app.route('/customer/review_edited_booking', methods=['GET','POST'])
def customer_review_edited_booking():

    booking_data = None # Initialize booking_data as None
    venue_info = None 

    if request.method == 'POST':
        # Constance
        current_date_time = datetime.now()
        status = 'booked'
        refund = 0
        user_id = session['user_id']

        # Retrieve data from form
        booking_id = request.form.get('booking_id')
        venue_id = request.form.get('venue_id')
        space_id = request.form.get('space_id')
        venue_name = request.form.get('venue')
        space_name = request.form.get('space')
        event_type = request.form.get('event_type')
        number_of_guests = request.form.get('number_of_guests')
        start = request.form.get('start') # str
        end = request.form.get('end') # str
        selected_services = request.form.getlist('services[]')

        # validate space availability
        # Convert ISO 8601 string to datetime object
        wanted_start_datetime = datetime.strptime(start, '%Y-%m-%dT%H:%M')
        wanted_end_datetime = datetime.strptime(end, '%Y-%m-%dT%H:%M')
        
        if not is_booking_available(space_id,wanted_start_datetime,wanted_end_datetime):
            flash('The time has been booked. Please choose another time', 'warning')

            return redirect(url_for('customer_booking_detail', booking_id = booking_id))


        # Get event id for populating database
        event_id = get_event_id_by_name(event_type)

        # Get venue info
        venue_info = get_venue_info(venue_id)

        # Find space_event_id
        space_event_id = find_space_event_id_by_space_id_and_event_id(space_id, event_id)

        # Find venue hourly rate
        venue_hourly_rate = find_venue_price_by_space_event_id(space_event_id)

        # Format booking date time into string
        booking_date_time = current_date_time.strftime('%Y-%m-%d %H:%M:%S')

        # Convert start and end time str to datatime object then format them into readable strings
        start_datetime = datetime.strptime(start, '%Y-%m-%dT%H:%M')
        end_datetime = datetime.strptime(end, '%Y-%m-%dT%H:%M')
        start_str = start_datetime.strftime('%Y-%m-%d %H:%M %p')
        end_str = end_datetime.strftime('%Y-%m-%d %H:%M %p')


        ####### calculate event total hours #############
        total_hours = 0 # Initialize total_hours

        # situation 1:  3 and more days event
        if (end_datetime.date() - start_datetime.date()).days + 1 >= 3:
            num_of_days_between_start_and_end_dates = (end_datetime.date() - start_datetime.date()).days + 1 - 2
            interval_hours = num_of_days_between_start_and_end_dates * 6
            total_hours += interval_hours
            print(f"number of days between start and end dats is {num_of_days_between_start_and_end_dates} days, and the total hours for that is {interval_hours}")
        
            # Calculate how many hours in start date
            next_midnight = datetime(start_datetime.year, start_datetime.month, start_datetime.day) + timedelta(days=1)
            print(f"next_midnight is {next_midnight}")
            duration_to_midnight_in_hours = math.ceil((next_midnight - start_datetime).seconds / 3600)
            print(f"duration_to_midnight_in_hours is {duration_to_midnight_in_hours} hours")
            
            if duration_to_midnight_in_hours >= 6:
                total_hours += 6
            else:
                total_hours += duration_to_midnight_in_hours

            # Calculate how many hours in end date
            midnight = datetime(end_datetime.year, end_datetime.month, end_datetime.day)
            print(f"midnight is {midnight}")
            midnight_to_end_in_hours = math.ceil((end_datetime - midnight).seconds/3600)
            print(f"midnight_to_end_in_hours is {duration_to_midnight_in_hours} hours")

            if midnight_to_end_in_hours >= 6:
                total_hours += 6
            else:
                total_hours += midnight_to_end_in_hours
        
        # situation 2: 2days event
        elif (end_datetime.date() - start_datetime.date()).days + 1 == 2:
            # Calculate how many hours in start date
            next_midnight = datetime(start_datetime.year, start_datetime.month, start_datetime.day) + timedelta(days=1)
            print(f"next_midnight is {next_midnight}")
            duration_to_midnight_in_hours = math.ceil((next_midnight - start_datetime).seconds / 3600)
            print(f"duration_to_midnight_in_hours is {duration_to_midnight_in_hours} hours")
            
            if duration_to_midnight_in_hours >= 6:
                total_hours += 6
            else:
                total_hours += duration_to_midnight_in_hours

            # Calculate how many hours in end date
            midnight = datetime(end_datetime.year, end_datetime.month, end_datetime.day)
            print(f"midnight is {midnight}")
            midnight_to_end_in_hours = math.ceil((end_datetime - midnight).seconds/3600)
            print(f"midnight_to_end_in_hours is {duration_to_midnight_in_hours} hours")

            if midnight_to_end_in_hours >= 6:
                total_hours += 6
            else:
                total_hours += midnight_to_end_in_hours       

        # situation 3: event within one day
        elif (start_datetime.date() - end_datetime.date()).days == 0:
           hours = math.ceil((end_datetime - start_datetime).seconds / 3600)
           print(f"hours is {hours}")
           if hours >= 6:
               total_hours += 6
           else:
               total_hours += hours
               print(f"total hours is {total_hours}")
        
        else: 
            flash("Please choose another date and time", 'warning')

        # Format selected_services
        add_on_services = []
        for option in selected_services:
            service_id = get_service_id_by_name(option)
            service_price_and_pricing_model = find_service_price_and_pricing_model_by_venue_id_and_service_id(venue_id, service_id)
            add_on = (service_id, option, service_price_and_pricing_model[0],service_price_and_pricing_model[1])
            add_on_services.append(add_on)

        # Pack and send booking_data to review-booking page
        booking_data = [
            user_id,#0
            booking_date_time, #1
            status, #2
            refund, #3
            (venue_id, venue_name), #4
            (space_id, space_name), #5
            (event_id, event_type), #6
            number_of_guests, #7
            (start_str, end_str, total_hours, venue_hourly_rate), #8
            add_on_services, #9
            space_event_id #10
        ]
        
    return render_template('customers/customer_review_edited_booking.html',
                           booking_data=booking_data,
                           venue_info=venue_info,
                           booking_id = booking_id)



@app.route('/customer/update_booking', methods=['POST'])
def customer_update_booking():
    
    if request.method == 'POST':
        total_fee = request.form.get('total_fee')
        user_id = request.form.get('user_id')
        booking_date_time = request.form.get('booking_date_time')
        status = request.form.get('status')
        refund = request.form.get('refund')
        venue_id = request.form.get('venue_id')
        space_id = request.form.get('space_id')
        event_id = request.form.get('event_id')
        number_of_guests = request.form.get('number_of_guests')
        start_str = request.form.get('start_str')
        end_str = request.form.get('end_str')
        service_ids = request.form.get('all_service_ids')
        booking_id = request.form.get('booking_id')
        
        space_event_id = find_space_event_id_by_space_id_and_event_id(space_id,event_id)
        print(f"Cheeeeeeck:{total_fee}//{start_str}//{end_str}//{service_ids}//{space_event_id}")

        ### update tables:1.bookings, 2.availability,  3.payment, (4.space_events)
        # update 1. booking table

        refund_amount = update_bookings_table(booking_id, booking_date_time,status,refund,user_id,space_event_id,number_of_guests,service_ids)

        new_booking_id = get_booking_id_by_booking_date_time_and_space_event_id(booking_date_time, space_event_id)
      
        # update 2. availability table
        # convert start and end date time format into datetime object
        format = "%Y-%m-%d %H:%M %p"
        start_date_time= datetime.strptime(start_str, format)
        end_date_time= datetime.strptime(end_str, format)
        
        update_availability_table(start_date_time, end_date_time, space_id, new_booking_id)

        # update 3. payment
        payment_date_time = datetime.now()


        update_payment_table(refund_amount, new_booking_id, booking_id, payment_date_time, total_fee, payment_status="successful")

        if refund_amount==0:
            flash(f"Your previous booking has been cancelled with no refund. \nYour new booking has been placed successfully.","success")
            return redirect("/customer/booking_list")
        else:
            flash(f"Your new booking has been placed successfully. \nYour previous booking has been cancelled with a rufund of ${refund_amount}. Please wait for the planner to process it within 14 days.", "success")
            return redirect("/customer/booking_list")
       

    
@app.route('/customer/delete_booking/<booking_id>')
def customer_delete_booking(booking_id):
    
    # Get the cancelation date time
    cancellation_date = datetime.now()
    print(cancellation_date)

    # Call the delete_booking function with the booking_id and cancellation_date
    refund_amount = delete_booking_update_db(booking_id, cancellation_date)
    if refund_amount==0:
        flash(f"Your booking has been cancelled successfully with no refund.","success")
        return redirect("/customer/booking_list")
    else:
        flash(f"Your booking has been cancelled successfully, and an amount of {refund_amount} will be refunded. Please wait for the planner to process it within 14 days.", "success")
        return redirect("/customer/booking_list")




@app.route('/customer/show_reminder', methods=['GET', 'POST'])
def show_reminder():
    return render_template('customers/reminder_page.html')


#-------------------------------------------------------------------#
#----------------------Customer View Messages-----------------------#
#-------------------------------------------------------------------#

# Assuming you have already imported necessary libraries and established a database connection

@app.route('/customer_messages', methods=['GET', 'POST'])
def customer_messages():
    if request.method == 'POST':
        message_id_to_delete = request.form.get('delete_message_id')

        if message_id_to_delete:
            db_cursor = get_cursor()
            delete_query = "DELETE FROM planner_message WHERE planner_message_id = %s"
            db_cursor.execute(delete_query, (message_id_to_delete,))
            flash('Message deleted successfully', 'success')
    
    # Fetch the messages after deletion
    db_cursor = get_cursor()
    query = "SELECT planner_message_id, message_date, subject, message_body FROM planner_message"
    db_cursor.execute(query)
    messages = db_cursor.fetchall()

    # Get the user_id of the currently logged-in customer from the session
    current_user_id = session.get('user_id')

    # Fetch and display customer messages only for the currently logged-in customer
    db_cursor = get_cursor()
    customer_query = "SELECT message_id, message_date, subject, message_body FROM customer_messages WHERE user_id = %s"
    db_cursor.execute(customer_query, (current_user_id,))
    customer_messages = db_cursor.fetchall()

    return render_template('customers/customer_messages.html', messages=messages, customer_messages=customer_messages, current_user_id=current_user_id)


#-------------------------------------------------------------------#
#----------------------Customer Message Details---------------------#
#-------------------------------------------------------------------#

@app.route('/customer_message_details/<int:message_id>', methods=['GET'])
def customer_message_details(message_id):
    # Fetch the message details using the message_id
    db_cursor = get_cursor()
    query = "SELECT message_date, subject, message_body FROM planner_message WHERE planner_message_id = %s"
    db_cursor.execute(query, (message_id,))
    message_details = db_cursor.fetchone()

    return render_template('customers/customer_message_details.html', message_details=message_details)







# note: when defining routes and functions, 
# please add the role prefix to avoid name clashing, 
# e.g., route('/admin/profile')
# def admin_profile()



