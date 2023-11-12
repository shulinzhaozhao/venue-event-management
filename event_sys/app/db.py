import mysql.connector
import connect
from flask import session, jsonify
import bcrypt
import datetime
from decimal import Decimal



dbconn = None
connection = None

def get_cursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn


USER_ROLES = ['customer', 'planner', 'admin']

######## test code ###########
def get_user_info():
    new_cursor = get_cursor()
    new_cursor.execute('Select * from users')
    data = new_cursor.fetchone()
    return data

def is_authenticated():
    return 'user_id' in session

def get_user_role():
    if is_authenticated:
        if session['user_role'] == 'admin':
            return 'admin'
        elif session['user_role'] == 'customer':
            return 'customer'
        elif session['user_role'] == 'planner':
            return 'planner'
    return None


# Update get_venue_list_with_duplicates
def get_venue_list_with_duplicates(venue_id_list):
    new_cursor = get_cursor()
    if venue_id_list:
        venue_list = []
        for venue_id in venue_id_list:
            sql = '''
            SELECT v.venue_name, v.description,
            SUBSTRING_INDEX(v.image_url, ', ', 1) AS image_url,
            (SELECT GROUP_CONCAT(et.event_name SEPARATOR ', ')
            FROM venue_spaces vs_sub
            JOIN space_events se_sub ON vs_sub.space_id = se_sub.space_id
            JOIN event_types et ON se_sub.event_id = et.event_id
            WHERE vs_sub.venue_id = v.venue_id) AS event_names,
            v.venue_id FROM venues v 
            WHERE v.venue_id = %s AND v.is_deleted = 0; '''
            new_cursor.execute(sql, (venue_id,))
            venue_list.append(new_cursor.fetchall()[0])
    else:
        sql = '''
        SELECT v.venue_name, v.description,
        SUBSTRING_INDEX(v.image_url, ', ', 1) AS image_url,
        (SELECT GROUP_CONCAT(et.event_name SEPARATOR ', ')
        FROM venue_spaces vs_sub
        JOIN space_events se_sub ON vs_sub.space_id = se_sub.space_id
        JOIN event_types et ON se_sub.event_id = et.event_id
        WHERE vs_sub.venue_id = v.venue_id) AS event_names,
        v.venue_id
        FROM venues v 
        WHERE v.is_deleted = 0; '''
        new_cursor.execute(sql)
        venue_list = new_cursor.fetchall()
    return venue_list

# Update get_venue_list
def get_venue_list(venue_id_list):
    if venue_id_list:
        venue_list = get_venue_list_with_duplicates(venue_id_list)
    else:
        venue_list = get_venue_list_with_duplicates(None)

    # Convert list of tuples to list of lists
    i = 0
    for venue in venue_list:
        venue = list(venue)
        venue_list[i] = venue
        i += 1

    # Delete duplicated event names
    i = 0
    for venue in venue_list:
        event_name_duplicated = venue[3].split(', ')
        event_names = []
        for name in event_name_duplicated:
            if name not in event_names:
                event_names.append(name)
        venue[3] = event_names
        venue_list[i] = venue
        i += 1
    return venue_list


# Update planner_get_venue_list_with_duplicates
def planner_get_venue_list_with_duplicates(planner_id):
    new_cursor = get_cursor()
    # Get venue names, descriptions, first image_url, and event types (duplicated) for a specific planner
    sql = '''
    SELECT v.venue_name, v.description,
    SUBSTRING_INDEX(v.image_url, ', ', 1) AS image_url,
    (SELECT GROUP_CONCAT(et.event_name SEPARATOR ', ')
    FROM venue_spaces vs_sub
    JOIN space_events se_sub ON vs_sub.space_id = se_sub.space_id
    JOIN event_types et ON se_sub.event_id = et.event_id
    WHERE vs_sub.venue_id = v.venue_id) AS event_names,
    v.venue_id
    FROM venues v
    WHERE v.planner_id = %s AND v.is_deleted = 0; '''
    
    new_cursor.execute(sql, (planner_id,))
    venue_list = new_cursor.fetchall()
    return venue_list

# Update planner_get_venue_list
def planner_get_venue_list(planner_id):
    venue_list = planner_get_venue_list_with_duplicates(planner_id)

    # Convert list of tuples to list of lists 
    i = 0
    for venue in venue_list:
        venue = list(venue)
        venue_list[i] = venue
        i += 1

    # Delete duplicated event names 
    i = 0
    for venue in venue_list:
        event_name_duplicated = venue[3].split(', ')
        event_names = []
        for name in event_name_duplicated:
            if name not in event_names:
                event_names.append(name)
        venue[3] = event_names
        venue_list[i] = venue
        i += 1
    return venue_list


# get individual venue information
def get_venue_info(venue_id):
    new_cursor = get_cursor()
    sql = '''  
    SELECT 
    v.venue_name, 
    v.city,
    v.image_url,
    v.description, 
    v.facilities,
    GROUP_CONCAT(s.service_name) AS concatenated_services,
    v.contact_phone, 
    v.contact_email, 
    v.address
    FROM venues v JOIN venue_services vs ON v.venue_id = vs.venue_id
    JOIN services s ON vs.service_id = s.service_id 
    WHERE v.venue_id = %s
    GROUP BY v.venue_name, v.city, v.image_url,
    v.description, v.facilities, v.contact_phone,
    v.contact_email, v.address; '''
    new_cursor.execute(sql, (venue_id,))
    venue_info = new_cursor.fetchall()

    # turn image_url, facilities, services into lists 
    venue_info_list = list(venue_info[0]) 
    url_list = venue_info_list[2].split(', ')
    facility_list = venue_info_list[4].split(', ')
    service_list = venue_info_list[5].split(',') # !not an error without space after comma - don't change anything!

    venue_info_list[2] = url_list
    venue_info_list[4] = facility_list 
    venue_info_list[5] = service_list

    return venue_info_list

# get space list of an individual venue
def get_space_list(venue_id):
    new_cursor = get_cursor()
    sql = '''  SELECT vs.space_name, cp.max_capacity,
    GROUP_CONCAT(et.event_name) AS event_names,
    vs.equipment, c.price, c.pricing_model, vs.space_id  
    FROM venue_spaces vs
    JOIN space_events se ON vs.space_id = se.space_id
    JOIN capacity cp ON se.space_event_id = cp.space_event_id
    JOIN charges c ON se.space_event_id = c.space_event_id
    JOIN event_types et ON et.event_id = se.event_id
    WHERE vs.venue_id = %s
    GROUP BY vs.space_name, cp.max_capacity, vs.equipment,
    c.price, c.pricing_model, vs.space_id 
    ORDER BY cp.max_capacity DESC; '''
    new_cursor.execute(sql, (venue_id,))
    space_list = new_cursor.fetchall()

    # convert list of tuples to list of lists 
    i = 0
    for space in space_list:
        space_list[i] = list(space)
        i += 1

    # concact event name str with new format
    for space in space_list:
        space[2] = space[2].replace(',', ', ')

    # check if price is None 
    for space in space_list:
        if space[-2] is None:
            space[-2] = 'Free'
    
    # check if facilities is None
    for space in space_list:
        if space[-3] is None:
            space[-3] = 'N/A'

    return space_list


# Get hashed password from db for a specific user
def get_user_hashed_password(user_id):
    connection = get_cursor()
    sql = "SELECT password FROM users WHERE user_id = %s;"
    connection.execute(sql, (user_id,))
    result = connection.fetchone()
    
    if result is not None:
        hashed_password = result[0]  # Extract the hashed password from the tuple
        return hashed_password
    else:
        return None  # Handle the case where no password is found for the user


def generate_hashed_password(plain_txt_password: str) -> bytes:
    # Hash a password for the first time, using bcrypt (register)
    hashed_password = bcrypt.hashpw(plain_txt_password.encode("utf-8"), bcrypt.gensalt())
    return hashed_password

def verify_password(provided_password: str, hashed_pass_in_db: str) -> bool:
    # Check user provided password matches with the hased password stored in the database
    return bcrypt.checkpw(provided_password.encode('utf-8'), hashed_pass_in_db.encode('utf-8'))
  

def get_planer_id_by_user_id(user_id):
    cur = get_cursor()
    cur.execute('SELECT * FROM planners WHERE user_id = %s', (user_id,))
    planner_info = cur.fetchone()
    if planner_info:
        planner_id = planner_info[0]
        return planner_id
    else:
        return None

  
def get_booked_venue_spaces(selected_venue_id):
    """
    Fetches booked venues/spaces/events that the planner manages for FullCalendar.
    """
    user_id = session['user_id']   
    planner_id = get_planer_id_by_user_id(user_id)

    cursor = get_cursor()
    query = """
        SELECT
            bookings.order_status,
            bookings.guest_number,
            payment.payment_amount,
            customers.first_name,
            customers.last_name,
            venues.venue_name,
            venue_spaces.space_name,
            event_types.event_name,
            availability.start_date_time,
            availability.end_date_time
        FROM
            bookings
		JOIN payment on bookings.booking_id = payment.booking_id
        JOIN customers ON bookings.user_id = customers.user_id
        JOIN space_events ON bookings.space_event_id = space_events.space_event_id
        JOIN venue_spaces ON space_events.space_id = venue_spaces.space_id
        JOIN venues ON venue_spaces.venue_id = venues.venue_id
        JOIN event_types ON space_events.event_id = event_types.event_id
        JOIN availability ON bookings.booking_id = availability.booking_id
        WHERE order_status = "booked"
        AND venues.planner_id = %s
        AND venues.venue_id = %s;
        """
    cursor.execute(query, (planner_id, selected_venue_id))

    events = [] # A list to store event as dict

    while True:
        event_info = cursor.fetchone()

        if not event_info:
            break  

        # Extract relevant information from the tuple/row
        order_status = event_info[0]
        guest_number = event_info[1]
        payment_amount = event_info[2]
        customer_first_name = event_info[3]
        customer_last_name = event_info[4]
        venue_name = event_info[5]
        space_name = event_info[6]
        event_name = event_info[7]
        start_date_time = event_info[8]
        end_date_time = event_info[9]

        # Format dates and times as ISO8601 strings for FullCalendar
        iso_str_start_date_time = start_date_time.isoformat()
        iso_str_end_date_time = end_date_time.isoformat()

        # Format dates and times as strings for display
        start_date_str = start_date_time.date().strftime('%d/%m/%Y')
        start_time_str = start_date_time.time().strftime('%H:%M %p')
        end_date_str = end_date_time.date().strftime('%d/%m/%Y')
        end_time_str = end_date_time.time().strftime('%H:%M %p')

        # Construct a dictionary with the required fields for FullCalendar
        event = {
            'title': f"{event_name}",
            'start': iso_str_start_date_time,
            'end': iso_str_end_date_time,
            'venue': venue_name,
            'space': space_name,
            'description': f"{space_name}@{venue_name} - {customer_first_name} {customer_last_name} - FROM {start_time_str}, {start_date_str} TO {end_time_str}, {end_date_str} - {guest_number} Guests - ${payment_amount}."
        }

        # Event as dictionary in list
        events.append(event)

    # Convert the list of dicts
    return events


# search if venues match search terms
# return false, or a list of venue_id  
def search_venues_db(event_type: str, guests: int, location: str):
    
    liketerm_event = f"%{event_type}%"
    liketerm_location = f"%{location}%" 

    new_cursor = get_cursor()
    sql = ''' SELECT v.venue_id FROM venues v 
        JOIN venue_spaces vs ON v.venue_id = vs.venue_id
        JOIN space_events se ON vs.space_id = se.space_id 
        JOIN event_types et ON se.event_id = et.event_id
        JOIN capacity c ON se.space_event_id = c.space_event_id
        WHERE et.event_name LIKE %s
	    AND v.city LIKE %s
        AND c.max_capacity >= %s; '''
    new_cursor.execute(sql, (liketerm_event, liketerm_location, guests))
    venue_id_list_duplicated = new_cursor.fetchall()

    # delete duplicated id 
    venue_id_list = []
    if venue_id_list_duplicated:
        for entry in venue_id_list_duplicated:
            if entry[0] not in venue_id_list:
                venue_id_list.append(entry[0])
        return venue_id_list 
    return False 

# Get the planner id from the logged in user id 
def get_planner_id(user_id):
    connection = get_cursor()
    sql = "SELECT planner_id FROM planners WHERE planners.user_id = %s;"
    connection.execute(sql,(user_id,))
    result = connection.fetchone()
    planner_id = result[0] if result else None
    
    return planner_id

# Get the customer_id from the booking
def get_customer_id_from_booking(planner_id):
    connection = get_cursor()
    sql = "SELECT DISTINCT c.customer_id FROM customers c \
       JOIN users u ON c.user_id = u.user_id \
       JOIN bookings b ON b.user_id = u.user_id \
       JOIN space_events se ON b.space_event_id = se.space_event_id \
       JOIN venue_spaces vs ON se.space_id = vs.space_id \
       JOIN venues v ON v.venue_id = vs.venue_id \
       WHERE v.planner_id = %s ;"
    connection.execute(sql,(planner_id,))
    customer_id_list_of_tuples = connection.fetchall()
    customer_id_list = []
    for tuple in customer_id_list_of_tuples:
        customer_id = tuple[0]
        customer_id_list.append(customer_id)
    
    return customer_id_list


def get_booking_list(user_id):
    cursor = get_cursor()
    query = """    
            SELECT
            bookings.booking_id,
            bookings.booking_date_time,
            bookings.guest_number, 
            bookings.service_booked,
            payment.payment_amount,
            customers.first_name,
            customers.last_name,   
            users.username,       
            venues.venue_name,
            venue_spaces.space_name,
            event_types.event_name,        
            availability.start_date_time,
            availability.end_date_time
        FROM
            bookings
        JOIN payment ON bookings.booking_id = payment.booking_id
        JOIN customers ON bookings.user_id = customers.user_id
        JOIN users ON customers.user_id = users.user_id
        JOIN space_events ON bookings.space_event_id = space_events.space_event_id
        JOIN venue_spaces ON space_events.space_id = venue_spaces.space_id
        JOIN venues ON venue_spaces.venue_id = venues.venue_id
        JOIN event_types ON space_events.event_id = event_types.event_id
        JOIN availability ON bookings.booking_id = availability.booking_id
        WHERE order_status = "booked"
        AND customers.user_id = %s
        ORDER BY bookings.booking_date_time DESC;
        """
       
    cursor.execute(query, (user_id,))
    event_info = cursor.fetchone()

    past_event_list = [] 
    upcoming_event_list = []
 
    while event_info:

        current_datetime = datetime.datetime.now()
        end_datetime = event_info[-1]
        if end_datetime >=  current_datetime:
            upcoming_event_list.append(event_info)
        else:
            past_event_list.append(event_info)
        
        event_info = cursor.fetchone()
                
    return upcoming_event_list, past_event_list


def get_service_id_by_name(service_name):
    cursor = get_cursor()
    query = "SELECT service_id FROM services WHERE service_name = %s"
    cursor.execute(query, (service_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None
    
def get_event_id_by_name(event_name):
    cur = get_cursor()
    cur.execute('select event_id from event_types where event_name = %s', (event_name,))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        return None

  

def find_space_event_id_by_space_id_and_event_id(space_id, event_id):
    cur = get_cursor()
    cur.execute('select space_event_id from space_events where space_id=%s and event_id=%s', (space_id, event_id))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        return None
    
def find_venue_price_by_space_event_id(space_event_id):
    cur = get_cursor()
    cur.execute('select price from charges where space_event_id=%s', (space_event_id,))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        return None    

# get hold of filter dropdown options, 
# return event_type_list, location_list  
def get_filter_dropdown_options():
    cur = get_cursor()
    cur.execute("SELECT event_name FROM event_types")
    event_type_list = cur.fetchall()

    cur = get_cursor()
    cur.execute("SELECT city FROM venues")
    location_result = cur.fetchall()

    # delete duplicated locations 
    location_list = []
    for entry in location_result:
        if entry not in location_list:
            location_list.append(entry)
    
    return event_type_list, location_list


# Get all the services in a list 
def get_service_list():
    connection = get_cursor()
    sql = "SELECT * FROM services;"
    connection.execute(sql)
    services_list = connection.fetchall()
    return services_list


# Get all the event types in a list 
def get_event_type_list():
    connection = get_cursor()
    sql = "SELECT * FROM event_types;"
    connection.execute(sql)
    event_type_list = connection.fetchall()
    return event_type_list

def find_service_price_and_pricing_model_by_venue_id_and_service_id(venue_id, service_id):
    cur = get_cursor()
    query = 'select price, pricing_model from venue_services where venue_id=%s and service_id=%s'
    cur.execute(query, (venue_id, service_id))
    result = cur.fetchone()
    if result:
        return result
    else:
        return None    

# passing in a string of booked services of id 
# and return a service list of tuples with service id and name 
def get_service_name_by_id(service_id_str):

    service_id_list = [int(num) for num in service_id_str.split(',')]
    cur = get_cursor()
    service_list = []
    for id in service_id_list:
        cur.execute('SELECT * FROM services WHERE service_id = %s', (id,))
        service_info = cur.fetchone()
        service_list.append(service_info)
    return service_list


def get_booking_detail(booking_id):

# booking info to display:
    # cus name, username
    # venue name, space name 
    # event type, num of guest
    # start time, end time 
    # service booked 
    # total charge, additional requirements 

    sql = '''
        SELECT
        bookings.guest_number, 
        bookings.service_booked,
        bookings.additional_details,
        payment.payment_amount,
        customers.first_name,
        customers.last_name, 
        users.username, 

        capacity.max_capacity,

        event_types.event_name,
        venue_spaces.space_name,
        availability.start_date_time,
        availability.end_date_time,
        venues.venue_name,

        venues.venue_id,
        venue_spaces.space_id

        FROM bookings 
        JOIN payment ON payment.booking_id = bookings.booking_id
        JOIN customers ON bookings.user_id = customers.user_id
        JOIN users ON customers.user_id = users.user_id
        JOIN space_events ON bookings.space_event_id = space_events.space_event_id

        JOIN capacity ON capacity.space_event_id = space_events.space_event_id 

        JOIN event_types ON space_events.event_id = event_types.event_id
        JOIN venue_spaces ON venue_spaces.space_id = space_events.space_id 
        JOIN availability ON bookings.booking_id = availability.booking_id
        JOIN venues ON venues.venue_id = venue_spaces.venue_id
        WHERE bookings.order_status = "booked"
        AND bookings.booking_id = %s;'''
    cur = get_cursor()
    cur.execute(sql, (booking_id,))
    booking_info = cur.fetchone()

# format data for display 
    # 1. convert booked services (a string of service id, separated by ',') into a string of services
    service_list = get_service_name_by_id(booking_info[1]) # list of tuples of (service id, service name)

    # 2. replace it with the new service_list in booking_info
    booking_info = list(booking_info)
    booking_info[1] = service_list

    # 3. format start and end datetime for display as pre-selected value (YYYY-MM-DDTHH:MM)   
    start_datetime = booking_info[-5].strftime('%Y-%m-%dT%H:%M')
    end_datetime = booking_info[-4].strftime('%Y-%m-%dT%H:%M')  

    booking_info[-5] = start_datetime
    booking_info[-4] = end_datetime

    # 4. convert event_name into a tuple of (event_id, event_name)
    event_id = get_event_id_by_name(booking_info[8])
    chosen_event = (event_id, booking_info[8])
    booking_info[8] = chosen_event
   
    return booking_info  # [250, [(1, 'Catering'), (2, 'Catering Staffing'), (3, 'Security'), (4, 'Styling'), (5, 'Cleaning'), (10, 'MC')], 'Test Booking 4: a long event', Decimal('17278.00'), 'John', 'Doe', 'customer1', MAX_CAP, (7, 'Exhibition'), 'Great Hall', '2023-10-08T09:00', '2023-10-18T21:00', 'Wow Factor']

# extra data to display for user to choose:
    # all other event types 
    # all other venue services 


  
def insert_new_booking(booking_date_time, status, refund, user_id, space_event_id, number_of_guests, services_booked_str):
    cur = get_cursor()
    sql = "INSERT INTO bookings (booking_date_time, order_status, refund_amount, user_id, space_event_id, guest_number, service_booked) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cur.execute(sql, (booking_date_time, status, refund, user_id, space_event_id, number_of_guests, services_booked_str))

def get_booking_id_by_booking_date_time_and_space_event_id(booking_date_time, space_event_id):
    cur = get_cursor()
    sql = 'select booking_id from bookings where booking_date_time=%s and space_event_id=%s'
    cur.execute(sql,(booking_date_time, space_event_id))
    result = cur.fetchone() # This gets a tuple
    if result:
        # Get the int value in this tuple 
        booking_id = result[0]
        return booking_id
    else:
        return None    


def update_availability_table(start_date_time, end_date_time, space_id, booking_id):
    # delete old entry 
    cur = get_cursor()
    sql = "DELETE FROM availability WHERE booking_id = %s;"
    cur.execute(sql,(booking_id,))

    # insert new entry
    cur = get_cursor()
    sql = "INSERT INTO availability (start_date_time, end_date_time, space_id, booking_id) VALUES (%s, %s, %s, %s)"
    cur.execute(sql, (start_date_time, end_date_time, space_id, booking_id))


def insert_new_availability(start_date_time, end_date_time, space_id, booking_id):
    # insert new entry
    cur = get_cursor()
    sql = "INSERT INTO availability (start_date_time, end_date_time, space_id, booking_id) VALUES (%s, %s, %s, %s)"
    cur.execute(sql, (start_date_time, end_date_time, space_id, booking_id))


def insert_new_payment(booking_id, payment_date_time, payment_amount, payment_status):
    cur = get_cursor()
    sql = "INSERT INTO payment (booking_id, payment_date_time, payment_amount, payment_status) VALUES (%s, %s, %s, %s)"
    cur.execute(sql,(booking_id, payment_date_time, payment_amount, payment_status))



def get_venue_service_price(venue_id):
    connection = get_cursor()
    sql = "SELECT price FROM venue_services WHERE venue_id = %s;"
    connection.execute(sql,(venue_id,))
    result = connection.fetchall()
    if result:
        venue_service_price_list = result
        return venue_service_price_list
    else:
        return None
    

def get_planner_s_venue_info_by_planner_id(planner_id):
    cur = get_cursor()
    sql = "select venue_id, venue_name, planner_id from venues where planner_id = %s;"
    cur.execute(sql, (planner_id,))
    result = cur.fetchall()
    if result:
        return result # list of tuple
    else:
        return None



def get_planner_id_by_user_id(user_id):
    cur = get_cursor()
    sql = "select planner_id, user_id from planners where user_id = %s;"
    cur.execute(sql, (user_id,))
    result = cur.fetchone()
    if result:
        return result
    else:
        return None
    
def get_space_id_list_by_venue_id(venue_id):
    cur = get_cursor()
    sql = "SELECT * FROM event_db.venue_spaces where venue_id = %s;"
    cur.execute(sql, (venue_id,))
    result = cur.fetchall()
    space_id_list = []
    if result:
        for row in result:
            space_id_list.append(row[0])
        return space_id_list
    else:
        return None


def get_all_space_event_ids_by_space_id(space_id):
    cur = get_cursor()
    sql = "select space_event_id from space_events where space_id = %s;"
    cur.execute(sql, (space_id,))
    result = cur.fetchall()
    if result:
        return result
    else:
        return None





def update_bookings_table(booking_id, booking_date_time, status, refund, user_id, space_event_id, number_of_guests, services_booked_str):
    # 1. update previous booking, set order_status and refund_amount 


    # calculate refund
    # fetch and format event start date time 
    cur = get_cursor()
    cur.execute("SELECT start_date_time FROM availability WHERE booking_id = %s", (booking_id,))
    booking_date = cur.fetchone()[0]
    booking_date_str=str(booking_date)
    booking_datetime = datetime.datetime.strptime(booking_date_str, '%Y-%m-%d %H:%M:%S')

    # calculate refund by comparing event start and cancelation date 
    cancellation_date = datetime.datetime.now()
    refund_percentage = calculate_refund_amount(booking_datetime, cancellation_date)
    cur = get_cursor()
    cur.execute("SELECT payment_amount FROM payment WHERE booking_id = %s", (booking_id,))
    payment_amount=cur.fetchone()[0]
    print(payment_amount)
    refund_amount = payment_amount * refund_percentage
    print(refund_amount)

    # update bookings table 
    cur = get_cursor()
    sql = '''UPDATE bookings 
    SET order_status = 'cancelled', refund_amount = %s
    WHERE booking_id = %s;'''
    cur.execute(sql, (refund_amount,booking_id))


    # 3. insert new booking 
    cur = get_cursor()
    sql = "INSERT INTO bookings (booking_date_time, order_status, refund_amount, user_id, space_event_id, guest_number, service_booked) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cur.execute(sql, (booking_date_time, status, refund, user_id, space_event_id, number_of_guests, services_booked_str))

    return refund_amount

def insert_new_space_event_id(space_id, event_id):
    cur = get_cursor()
    sql = "INSERT INTO space_events (space_id, event_id) VALUES (%s, %s)"
    cur.execute(sql,(space_id, event_id))

def update_payment_table(refund_amount, new_booking_id, booking_id, payment_date_time, payment_amount, payment_status):
    # 1. update last payment with booking_id: set payment_description as 'refunded'

    # 3. update payment table
    if refund_amount != 0:
        cur = get_cursor()
        sql = "UPDATE payment SET payment_description = 'refund pending' WHERE booking_id = %s;"
        cur.execute(sql,(booking_id,))
    else:
        cur = get_cursor()
        sql = "UPDATE payment SET payment_description = NULL WHERE booking_id = %s;"
        cur.execute(sql,(booking_id,))

    # 2. insert new payment
    cur = get_cursor()
    sql = "INSERT INTO payment (booking_id, payment_date_time, payment_amount, payment_status) VALUES (%s, %s, %s, %s)"
    cur.execute(sql,(new_booking_id, payment_date_time, payment_amount, payment_status))






def is_booking_available(wanted_space_id, wanted_start_datetime, wanted_end_datetime):
    cur = get_cursor()
    sql = "select * from availability where space_id = %s"
    cur.execute(sql, (wanted_space_id,))
    availability_records = cur.fetchall()

    for row in availability_records:
        existing_start_datetime = row[1]
        existing_end_datetime = row[2]

        # check for overlap
        if existing_start_datetime <= wanted_start_datetime <= existing_end_datetime or existing_start_datetime <= wanted_end_datetime <= existing_end_datetime:
            return False
    
    return True





def get_service_id_by_venue_id(venue_id):
    cur = get_cursor()
    sql = "SELECT * FROM venue_services WHERE venue_id = %s;"
    cur.execute(sql, (venue_id,))
    data = cur.fetchall()
    return data


def get_venue_service_price_list(venue_id):
    connection = get_cursor()
    sql = "SELECT service_id, price FROM venue_services WHERE venue_id = %s;"
    connection.execute(sql,(venue_id,))
    result = connection.fetchall()
    if result:
        venue_service_price_list = result
        return venue_service_price_list
    else:
        return None
    
def update_existing_venue_services(venue_id, new_selected_service_list):
    # get hold of related service_id 
    service_id_list_by_venue_id = get_service_id_by_venue_id(venue_id) # list of tuples, service id at [2] 
    for service in service_id_list_by_venue_id:
        service_id = service[2]
        for selected_service in new_selected_service_list:
            if str(service_id) == selected_service[0]:  # check if ids match
                service_price = float(selected_service[1]) 
                if service_id == 1:
                    pricing_model = 'PerHead'
                else:
                    pricing_model = 'Fixed'
                # update db 
                cur = get_cursor()
                sql = "UPDATE venue_services SET price = %s, pricing_model = %s WHERE venue_id = %s AND service_id = %s;"
                cur.execute(sql, (service_price, pricing_model, venue_id, service_id))



def get_all_payment_data():
    cur = get_cursor()
    sql = 'select payment_date_time, payment_amount from payment where payment_status = "successful"'
    cur.execute(sql)
    result = cur.fetchall()
    if result:
        return result
    else:
        return None
    

def get_venue_id_and_name():
    cur = get_cursor()
    cur.execute('select venue_id, venue_name from venues')
    result = cur.fetchall()
    if result:
        return result
    else:
        return None
    
def get_all_venue_names_list():
    venue_id_and_name = get_venue_id_and_name()
    if venue_id_and_name:
        all_venue_names_list = []
        for info in venue_id_and_name:
            all_venue_names_list.append(info[1])
        return all_venue_names_list
    else:
        return None
    
def get_venue_revenue_data():
    cur = get_cursor()
    sql = """select venues.venue_name,
    payment.payment_date_time,
    payment.payment_amount
    from payment
    join bookings on payment.booking_id = bookings.booking_id
    join space_events on bookings.space_event_id = space_events.space_event_id
    join venue_spaces on space_events.space_id = venue_spaces.space_id
    join venues on venues.venue_id = venue_spaces.venue_id
    where bookings.order_status = 'booked' and payment.payment_status='successful'
    """
    cur.execute(sql)
    result = cur.fetchall()
    if result:
        return result
    else:
        return None
    


def get_popular_venues_data():
    cur = get_cursor()
    sql = """select
    venue_spaces.venue_id,
    venues.venue_name,
    availability.space_id,
    venue_spaces.space_name
    from availability
    join venue_spaces on venue_spaces.space_id = availability.space_id
    join venues on venues.venue_id = venue_spaces.venue_id;
    """
    cur.execute(sql)
    result = cur.fetchall()
    return result if result else None


def calculate_refund_amount(booking_date, cancellation_date):

    # calculate gap between event start and cancelation date 
    days_before_event = (booking_date - cancellation_date).days
    print(booking_date)
    print(cancellation_date)
    print(days_before_event)

    # determine refund rate 
    if days_before_event >= 30:
        return Decimal('1.0')  # 100% refund
    elif 15 <= days_before_event <= 29:
        return Decimal('0.5')  # 50% refund
    else:
        return Decimal('0.0')  # No refund

# update bookings and payment 
def delete_booking_update_db(booking_id, cancellation_date):


    print(f'booking_id: {booking_id}')

    # 1. update bookings table, set order_status as 'cancelled', and refund_amount

    # fetch and format event start date time 
    cur = get_cursor()
    cur.execute("SELECT start_date_time FROM availability WHERE booking_id = %s", (booking_id,))
    booking_date = cur.fetchone()[0]
    booking_date_str=str(booking_date)
    booking_datetime = datetime.datetime.strptime(booking_date_str, '%Y-%m-%d %H:%M:%S')

    # calculate refund by comparing event start and cancelation date 
    refund_percentage = calculate_refund_amount(booking_datetime, cancellation_date)
    cur = get_cursor()
    cur.execute("SELECT payment_amount FROM payment WHERE booking_id = %s", (booking_id,))
    payment_amount=cur.fetchone()[0]
    print(payment_amount)
    refund_amount = payment_amount * refund_percentage
    print(refund_amount)

    # update bookings table 
    cur = get_cursor()
    sql = '''UPDATE bookings 
    SET order_status = 'cancelled', refund_amount = %s
    WHERE booking_id = %s;'''
    cur.execute(sql, (refund_amount,booking_id))

    # 2. delete entry from availability table 
    cur = get_cursor()
    sql = "DELETE FROM availability WHERE booking_id = %s;"
    cur.execute(sql,(booking_id,))

    
    # update payment as 'refund pending' if there's any refund
    # after processing, as  'refunded' 

    # 3. update payment table

    if refund_amount != 0:
        cur = get_cursor()
        sql = "UPDATE payment SET payment_description = 'refund pending' WHERE booking_id = %s;"
        cur.execute(sql,(booking_id,))
    else:
        cur = get_cursor()
        sql = "UPDATE payment SET payment_description = NULL WHERE booking_id = %s;"
        cur.execute(sql,(booking_id,))

    return refund_amount

