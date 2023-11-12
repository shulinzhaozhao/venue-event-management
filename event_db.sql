CREATE DATABASE event_db;
use event_db;

CREATE TABLE users (
	user_id INT PRIMARY KEY AUTO_INCREMENT,
    password VARCHAR(255) NOT NULL,
	username VARCHAR(100) NOT NULL,
	role VARCHAR(50) NOT NULL
 );
 
INSERT INTO users (password, username, role)
VALUES
    ('$2b$12$5Tdfii6rFm7d2t.QF.9xAOnm8mKJFLaiNE3BJqPNOX71L2rhWbuae', 'customer1', 'customer'),
    ('$2b$12$Pw5qF8ruiO6xTq4.3QCpdOGh5D.Rx9p5VuwIUvsgVuJBu9yxEy7ZK', 'customer2', 'customer'),
    ('$2b$12$tkTTzwp70BP.X8eU16MvDOaFQdVH0kjOL67mCvrzHOM9rhSpwYE7i', 'customer3', 'customer'),
    ('$2b$12$wbxaj1T6/KG0QD0OJBtyCuUB12U0pL./MxHFLyMZHYGKiGyjp6Pwi', 'customer4','customer'),
    ('$2b$12$euuoBSdOawLEHl14cgQgQ.4HYJcjJTCxATTamocOB8lug913U4wP6', 'customer5','customer'),
    ('$2b$12$zbcQ8ZKy671xfEB53bgyReOWOhBylPJUMDxrCDjjWwagmoD2R7Vgi', 'customer6','customer'),
    ('$2b$12$8qrdlxr8Oj/BGMuYFjWJ1uY2ipdZye/Al/SjzKAvFPKeLeOWyml8m', 'customer7','customer'),
    ('$2b$12$w.8n4x45VSGgb.z4105jEeaPNVSu.SNzfGccYeh5.HgVMTo8YJ4/i', 'customer8','customer'),
    ('$2b$12$w.1355b3vAnIkSfYhcdtIO4QHYZwe0YU5z2Pce6qzYrnV3PP7LW4O', 'customer9','customer'),
    ('$2b$12$tMOz2SeDAi.tLIOs0dQzQ.PSZEyrRqdMyGdTRyWc/ct78kyHNKWzK', 'customer10','customer'),
    ('$2b$12$wYD5w9/bOwLeDSr/HwTr/OfpQ43r6oufv.SyEqymnKK9Vj.65wOzq', 'planner1', 'planner'),
    ('$2b$12$4gWdJFW7PVnBEFEkrMM.FO3C7RFcKi2Cg0ZX9ATlq5spJm5xTZgMm', 'planner2', 'planner'),
    ('$2b$12$DSaX5ZAJTO3TeB8jWfwSce5zg3SnoiJKeA7kd3iPnefvnriZmcvQG', 'planner3', 'planner'),
    ('$2b$12$B6Cmdin1hzE/K7/2XUpniejS3s4AW3w0jFliy3B18PqjH..eBsE0i', 'planner4','planner'),
    ('$2b$12$aP9Ofetn2.TeqLw6hINwDeImSwP45Hpeyp/D.XHg/YRo/5/8/NeQ2', 'planner5','planner'),
    ('$2b$12$0TDIZltMXdtg8sycxcA91.XBqC0oADZi17JZs/YJRlCrieiiRJ2uq', 'admin1', 'admin'),
    ('$2b$12$cFcLvKaAX56Z3Gf80HoYmeNQLrjCgYnevPZ7UuoWldmagB3yrkrEC', 'admin2', 'admin'),
    ('$2b$12$bhGShHsk8WskXXPx8hYfTeIQvoD/M0ZL2FLUZgPjGLY1n.rDUozze', 'admin3', 'admin');
    
CREATE TABLE customers (
	customer_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name TEXT (50),
    last_name TEXT (50),
    email VARCHAR(50),
    contact_number VARCHAR (20),
    address VARCHAR (50),
    user_id int,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
 );
 
INSERT INTO customers (first_name, last_name, email, contact_number, address, user_id)
VALUES
    ('John', 'Doe', 'john@example.com', '111-111-1111', '123 Elm St', 1),
    ('Alice', 'Johnson', 'alice@example.com', '222-222-2222', '566 Oak St', 2),
    ('Michael', 'Smith', 'michael@example.com', '333-333-3333', '789 Maple St', 3),
    ('Eva', 'Williams', 'eva@example.com', '444-444-4444', '987 Birch St', 4),
    ('James', 'Brown', 'james@example.com', '555-555-5555', '654 Cedar St', 5),
    ('Olivia', 'Lee', 'olivia@example.com', '666-666-6666', '231 Pine St', 6),
    ('David', 'Martinez', 'david@example.com', '777-777-7777', '765 Willow St', 7),
    ('Sophia', 'Anderson', 'sophia@example.com', '888-888-8888', '456 Oak St', 8),
    ('Lucas', 'Garcia', 'lucas@example.com', '999-999-9999', '321 Elm St', 9),
    ('Ava', 'Taylor', 'ava@example.com', '123-123-1234', '789 Oak St', 10);
    
CREATE TABLE planners (
	planner_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name TEXT (50),
    last_name TEXT (50),
    email VARCHAR(50),
    contact_number VARCHAR (20),
    address VARCHAR (50),
    user_id int,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
 );
 
INSERT INTO planners (first_name, last_name, email, contact_number, address, user_id)
VALUES
    ('Emily', 'Brown', 'emily@example.com', '444-444-4444', '111 Pine St', 11),
    ('Daniel', 'Wilson', 'daniel@example.com', '555-555-5555', '222 Cedar St', 12),
    ('Sophia', 'Lee', 'sophia@example.com', '666-666-6666', '333 Birch St', 13),
    ('Ethan', 'Garcia', 'ethan@example.com', '777-777-7777', '444 Willow St', 14),
    ('Olivia', 'Smith', 'olivia@example.com', '888-888-8888', '555 Oak St', 15);
 
 CREATE TABLE admins (
	admin_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name TEXT (50),
    last_name TEXT (50),
    email VARCHAR(50),
    contact_number VARCHAR (20),
    address VARCHAR (50),
    user_id int,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
 );

INSERT INTO admins (first_name, last_name, email, contact_number, address, user_id)
VALUES
    ('Oliver', 'Davis', 'oliver@example.com', '777-777-7777', '444 Spruce St', 16),
    ('Emma', 'Garcia', 'emma@example.com', '888-888-8888', '555 Redwood St', 17),
    ('Liam', 'Martinez', 'liam@example.com', '999-999-9999', '666 Sequoia St', 18);

-- Nay edits -------

CREATE TABLE venues (
	venue_id INT PRIMARY KEY AUTO_INCREMENT,
    venue_name VARCHAR(255),
    description TEXT(255),
    contact_phone VARCHAR (50),
    contact_email TEXT (50),
    city VARCHAR (50),
    address VARCHAR (50),
    facilities TEXT (255),
    image_url VARCHAR(255),
    planner_id int,
    is_deleted int,
    FOREIGN KEY (planner_id) REFERENCES planners(planner_id)
 );
 
INSERT INTO venues (venue_id, venue_name, description, contact_phone, contact_email, city, address, facilities, image_url, planner_id, is_deleted)
VALUES
    (1, 'WILD & CO', 
    'A beautiful blank canvas in the heart of Morningside. These simple spaces, thoughtfully created to celebrate the big and small moments in your life. From weddings, to photo shoots, corporate events, and private dinners, create your dream event in our space made to be shared.', 
    '021-675-099','info@wildandco.com', 'Auckland', 
    '28 Ethel Street, Morningside, Auckland',
    'Kitchen, Bathrooms, Bar, Air Conditioner, WIFI, Sound System, Catering, On-site Parking, BYO', 
    'images/venues/1-1.jpg, images/venues/1-2.jpg, images/venues/1-3.jpg',
    1,
    0),
    
    (2, 'Wow Factor', 
    "Wow your guests with a venue that is spacious, full of character, and easily adapted to cater for your event's requirements. From ball room to classroom style conference, The Great Hall at Chateau on the Park, a DoubleTree by Hilton can accommodate up to 340 guests and offers an array of possibilities.",
    '027-888-67300', 'info@wowfactor.com', 'Christchurch', 
    '189 Deans Ave, Riccarton, Christchurch', 
    'Bathrooms, Bar, Air Conditioner, WIFI, Sound System, Projector, Catering, On-site Parking', 
    'images/venues/2-1.jpg, images/venues/2-2.jpg, images/venues/2-3.jpg', 
    2,
    0),
    
    (3, 'Generator Waring Taylor Street', 
    'An award-winning building with major character and style. Located at 30 Waring Taylor Street, where the Lambton Quay shopping district meets the parliamentary precinct, Generator offers a full range of engaging event spaces and cutting edge meeting facilities. Host your next meeting or event at Generator and make the right impression effortlessly.', 
    '022-321-6641', 'inquiry@generator.com', 'Wellington', 
    '30 Waring Taylor Street, Te Aro, Wellington', 
    'Bathrooms, Bar, Air Conditioner, WIFI, Sound System, Projector, Whiteboard, TV, Catering', 
    'images/venues/3-1.jpg, images/venues/3-2.jpg, images/venues/3-3.jpg', 
    3,
    0),

    (4, 'Kingi Private',
    "Meet and eat in high style at Auckland's newest dining and meeting space. Bringing together the relaxed warmth and the refined elegance at The Hotel Britomart, it is a sophisticated dining and meeting space in the heart of the waterfront. It’s the ideal place for a celebratory private lunch or dinner, but this space has been designed for function as much as for fun.",
    '022-221-55466', 'info@kingi.com', 'Auckland',
    '29 Galway Street, Auckland City, Auckland',
    'Bathrooms, Bar, Air Conditioner, WIFI, TV, Catering', 
    'images/venues/4-1.jpg, images/venues/4-2.jpg, images/venues/4-3.jpg',
    1,
    0),
    
    (5, 'Heathcote Valley',
    "This award winning architectural home is discreetly located in the Heathcote Valley in Christchurch. Completely hidden from the road, the expansive open plan living and outdoor spaces with spectacular mountain views is a unique setting to host incredible event experiences.",
    '021-111-333', 'inquiry@heathcote.com', 'Christchurch',
    'Bridle Path Road, Heathcote Valley, Christchurch',
    'Bathrooms, Kitchen, Air Conditioner, WIFI, TV, Swimming Pool',
    'images/venues/5-1.jpg, images/venues/5-2.jpg, images/venues/5-3.jpg',
    1,
    0),
    
    (6, 'SHED 10',
    "A 100 year old cargo shed, full of character and historical significance. This well-appointed blank canvas is for you to create your event exactly as you choose. You can see views of Auckland city at one end, and the Waitematā Harbour at the other, while the wide sliding doors on both sides of the building let in plenty of natural light.",
    '023-666-444', 'info@shed10.com', 'Auckland',
    '89 Quay Street, Auckland CBD, Auckland',
    'Air Conditioner, Whiteboards, Projector, WIFI, Catering, Bar, TV, Sound System, Lighting System, Bathrooms',
    'images/venues/6-1.jpg, images/venues/6-2.jpg, images/venues/6-3.jpg',
    2,
    0),
    
    (7, 'The Garden Pavilion', 
    "Nestled within a lush garden, The Garden Pavilion offers a serene and picturesque setting for weddings, private gatherings, and special events. With its beautiful floral surroundings and elegant architecture, it's the perfect venue for those seeking a touch of natural beauty for their celebrations.", 
    '028-555-7890', 'info@gardenpavilion.com', 'Wellington', 
    '12 Botanical Gardens, Wellington', 
    'Gardens, Outdoor Seating, Pavilion, Restrooms, Parking, Catering', 
    'images/venues/7-1.jpg, images/venues/7-2.jpg, images/venues/7-3.jpg', 
    4,
    0),
    
	(8, 'Harborview Convention Center', 
    "The Harborview Convention Center boasts stunning panoramic views of Auckland Harbor and the city skyline. This state-of-the-art facility is equipped to host large conferences, trade shows, and corporate events. Its modern design and technology make it a top choice for business gatherings.", 
    '025-123-4567', 'info@harborviewcenter.com', 'Auckland', 
    '18 Waterfront Drive, Auckland', 
    'Conference Halls, Meeting Rooms, Exhibition Space, Sound System, Projectors, Wi-Fi, Catering', 
    'images/venues/8-1.jpg, images/venues/8-2.jpg, images/venues/8-3.jpg', 
    4,
    0);

CREATE TABLE venue_spaces (
    space_id INT AUTO_INCREMENT PRIMARY KEY,
    space_name VARCHAR(255),
    venue_id INT,
    equipment VARCHAR(255),
    FOREIGN KEY (venue_id) REFERENCES venues(venue_id)
);

INSERT INTO venue_spaces (space_id, space_name, venue_id, equipment) VALUES 
-- venue 1 -- 
(1, 'Main Hall', 1, Null),
-- venue 2 --
(2, 'Great Hall', 2, Null),
(3, 'Ballantyne Room', 2, Null),
(4, 'Camelot Room', 2, Null),
-- venue 3 --
(5, 'Dunbar', 3, Null),
(6, 'Sloane', 3, Null),
(7, 'Meeting Room 1', 3, Null),
(8, 'Meeting Room 2', 3, Null),
-- venue 4 --
(9, 'Main Room', 4, Null),
-- venue 5 --
(10, 'Main Room', 5, Null),
-- venue 6 --
(11, 'Level 1', 6, Null),
(12, 'Ground Floor', 6, Null),
-- venue 7 --
(13, 'Garden', 7, Null),
(14, 'Inside Hall', 7, Null),
-- venue 8 --
(15, 'Harbour View Room', 8, Null)
;

CREATE TABLE event_types (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    event_name VARCHAR(255)
);

INSERT INTO event_types (event_id, event_name) VALUES 
(1, 'Wedding'),
(2, 'Private Event'),
(3, 'Corporate Event'),
(4, 'Corporate Meeting'),
(5, 'Workshop'),
(6, 'Conference'),
(7, 'Exhibition');

CREATE TABLE space_events (
    space_event_id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT,
    space_id INT,
    additional_details TEXT,
    FOREIGN KEY (event_id) REFERENCES event_types(event_id),
    FOREIGN KEY (space_id) REFERENCES venue_spaces(space_id)
);

INSERT INTO space_events (space_event_id, event_id, space_id, additional_details) VALUES 
-- venue 1 --
(1, 1, 1, Null),
(2, 2, 1, Null),
(3, 3, 1, Null),
-- venue 2 --
(4, 7, 2, Null),
(5, 5, 2, Null),
(6, 3, 2, Null),
(7, 5, 2, Null),
(8, 6, 2, Null),

(9, 1, 3, Null),   
(10, 2, 3, Null),
(11, 3, 3, Null),
(12, 5, 3, Null),

(13, 1, 4, Null),   
(14, 2, 4, Null),
(15, 3, 4, Null),
(16, 5, 4, Null),
-- venue 3 -- 
(17, 6, 5, Null),
(18, 3, 5, Null),
(19, 5, 5, Null),

(20, 4, 6, Null),
(21, 5, 6, Null),

(22, 4, 7, Null),
(23, 5, 7, Null),

(24, 4, 8, Null),
(25, 5, 8, Null),
-- venue 4 -- 
(26, 2, 9, Null),
(27, 3, 9, Null),
-- venue 5 -- 
(28, 1, 10, Null),
(29, 2, 10, Null),
(30, 3, 10, Null),
-- venue 6 -- 
(31, 3, 11, Null),
(32, 4, 11, Null),
(33, 5, 11, Null),
(34, 6, 11, Null),
(35, 7, 11, Null),

(36, 3, 12, Null),
(37, 4, 12, Null),
(38, 5, 12, Null),
(39, 6, 12, Null),
(40, 7, 12, Null),
-- venue 7 -- 
(41, 1, 13, Null),
(42, 2, 13, Null),
(43, 7, 13, Null),

(44, 2, 14, Null),
(45, 4, 14, Null),
(46, 5, 14, Null),
-- venue 8 -- 
(47, 4, 15, Null),
(48, 6, 15, Null)
;


CREATE TABLE capacity (
    capacity_id INT AUTO_INCREMENT PRIMARY KEY,
    space_event_id INT,
    max_capacity INT,
    FOREIGN KEY (space_event_id) REFERENCES space_events(space_event_id)
);

INSERT INTO capacity (space_event_id, max_capacity) VALUES 
-- venue 1 --
(1, 200),
(2, 200),
(3, 200),
-- venue 2 --
(4, 340),
(5, 340),
(6, 340),
(7, 340),
(8, 340), 

(9, 180),
(10, 180),
(11, 180),
(12, 180),

(13, 180),
(14, 180), 
(15, 180),
(16, 180),
-- venue 3 --
(17, 105),
(18, 105),
(19, 105),

(20, 60),
(21, 60),

(22, 14),
(23, 14),

(24, 10),
(25, 10),
-- venue 4 --
(26, 14),
(27, 14),
-- venue 5 --
(28, 25),
(29, 25),
(30, 25),
-- venue 6 -- 
(31, 500),
(32, 500),
(33, 500),
(34, 500),
(35, 500),

(36, 500),
(37, 500),
(38, 500),
(39, 500),
(40, 500),
-- venue 7 --
(41, 100),
(42, 100),
(43, 100),

(44, 30),
(45, 30),
(46, 30),
-- venue 8 --
(47, 300),
(48, 300)
;


CREATE TABLE charges (
    charge_id INT AUTO_INCREMENT PRIMARY KEY,
    space_event_id INT,
    price DECIMAL(10, 2),
    pricing_model VARCHAR(255),
    FOREIGN KEY (space_event_id) REFERENCES space_events(space_event_id)
);

INSERT INTO charges (space_event_id, price, pricing_model) VALUES 
-- venue 1 --
(1, 40.00, 'PerHour'),
(2, 40.00, 'PerHour'),
(3, 40.00, 'PerHour'),
-- venue 2 --
(4, 38.00, 'PerHour'),
(5, 38.00, 'PerHour'),
(6, 38.00, 'PerHour'),
(7, 38.00, 'PerHour'),
(8, 38.00, 'PerHour'),

(9, 35.00, 'PerHour'),
(10, 35.00, 'PerHour'),
(11, 35.00, 'PerHour'),
(12, 35.00, 'PerHour'),

(13, 35.00, 'PerHour'),
(14, 35.00, 'PerHour'),
(15, 35.00, 'PerHour'),
(16, 35.00, 'PerHour'),
-- venue 3 -- 
(17, 25.00, 'PerHour'),
(18, 25.00, 'PerHour'),
(19, 25.00, 'PerHour'),

(20, 35.00, 'PerHour'),
(21, 35.00, 'PerHour'),

(22, 28.00, 'PerHour'),
(23, 28.00, 'PerHour'),

(24, 24.00, 'PerHour'),
(25, 24.00, 'PerHour'),
-- venue 4 -- 
(26, 50.00, 'PerHour'),
(27, 50.00, 'PerHour'),
-- venue 5 -- 
(28, 40.00, 'PerHour'),
(29, 40.00, 'PerHour'),
(30, 40.00, 'PerHour'),
-- venue 6 -- 
(31, 56.00, 'PerHour'),
(32, 56.00, 'PerHour'),
(33, 56.00, 'PerHour'),
(34, 56.00, 'PerHour'),
(35, 56.00, 'PerHour'),

(36, 45.00, 'PerHour'),
(37, 45.00, 'PerHour'),
(38, 45.00, 'PerHour'),
(39, 45.00, 'PerHour'),
(40, 45.00, 'PerHour'),
-- venue 7 --
(41, 35.00, 'PerHour'),
(42, 35.00, 'PerHour'),
(43, 35.00, 'PerHour'),

(44, 20.00, 'PerHour'),
(45, 20.00, 'PerHour'),
(46, 20.00, 'PerHour'),
-- venue 8 --
(47, 50.00, 'PerHour'),
(48, 50.00, 'PerHour')
;

CREATE TABLE services (
    service_id INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(255)
);

INSERT INTO services (service_id, service_name) VALUES 
(1, 'Catering'),
(2, 'Catering Staffing'),
(3, 'Security'),
(4, 'Styling'),
(5, 'Cleaning'),
(6, 'Photography'),
(7, 'Live Streaming'),
(8, 'DJ'),
(9, 'Live Band'),
(10, 'MC');

CREATE TABLE venue_services (
    venue_service_id INT AUTO_INCREMENT PRIMARY KEY,
    venue_id INT,
    service_id INT,
    price DECIMAL(10, 2),
    pricing_model VARCHAR(255),
    note VARCHAR(255),
    FOREIGN KEY (venue_id) REFERENCES venues(venue_id),
    FOREIGN KEY (service_id) REFERENCES services(service_id)
);

INSERT INTO venue_services (venue_id, service_id, price, pricing_model, note) VALUES 
(1, 1, 50.00, 'PerHead', Null),
(1, 2, 120.00, 'Fixed', Null),
(1, 3, 150.00, 'Fixed', Null),
(1, 4, 200.00, 'Fixed', Null),
(1, 5, 150.00, 'Fixed', Null),

(2, 1, 56.00, 'PerHead', Null),
(2, 2, 120.00, 'Fixed', Null),
(2, 3, 150.00, 'Fixed', Null),
(2, 4, 200.00, 'Fixed', Null),
(2, 5, 150.00, 'Fixed', Null),
(2, 10, 150.00, 'Fixed', Null),

(3, 1, 56.00, 'PerHead', Null),
(3, 4, 200.00, 'Fixed', Null),
(3, 5, 150.00, 'Fixed', Null),
(3, 6, 200.00, 'Fixed', Null),
(3, 7, 200.00, 'Fixed', Null),

(4, 1, 85.00, 'PerHead', 'Custom menu set'),
(4, 4, 200.00, 'Fixed', Null),
(4, 9, 180.00, 'Fixed', Null),

(5, 1, 40.00, 'PerHead', Null),
(5, 2, 160.00, 'Fixed', Null),
(5, 4, 150.00, 'Fixed', Null),
(5, 5, 120.00, 'Fixed', Null),
(5, 6, 180.00, 'Fixed', Null),

(6, 1, 30.00, 'PerHead', Null),
(6, 2, 130.00, 'Fixed', Null),
(6, 3, 130.00, 'Fixed', Null),
(6, 4, 250.00, 'Fixed', Null),
(6, 5, 150.00, 'Fixed', Null),
(6, 6, 200.00, 'Fixed', Null),
(6, 7, 200.00, 'Fixed', Null),
(6, 8, 250.00, 'Fixed', Null),
(6, 9, 260.00, 'Fixed', Null),

(7, 1, 35.00, 'PerHead', Null),
(7, 2, 130.00, 'Fixed', Null),
(7, 4, 200.00, 'Fixed', Null),
(7, 5, 130.00, 'Fixed', Null),
(7, 6, 200.00, 'Fixed', Null),
(7, 7, 200.00, 'Fixed', Null),

(8, 3, 120.00, 'Fixed', Null),
(8, 5, 150.00, 'Fixed', Null),
(8, 10, 200.00, 'Fixed', Null)

;


CREATE TABLE notifications (
	notification_id INT PRIMARY KEY AUTO_INCREMENT,
	notification_date_time DATETIME,
    message TEXT(255),
    read_status TEXT (20),
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
 );
 
  INSERT INTO notifications (notification_date_time, message, read_status, user_id)
VALUES
    (curdate(), 'test', 'test', 1);
    
CREATE TABLE customer_communication (
	communication_id INT PRIMARY KEY AUTO_INCREMENT,
	subject VARCHAR (50),
    message_body TEXT(255),
    send_status TEXT (20),
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
 );
 
   INSERT INTO customer_communication (subject, message_body, send_status, user_id)
VALUES
    ('test', 'test', 'test', 1);
    

CREATE TABLE system_settings (
	setting_id INT PRIMARY KEY AUTO_INCREMENT,
    setting_name VARCHAR (50),
    setting_value VARCHAR (50),
    description VARCHAR (255)
 );
 
    INSERT INTO system_settings (setting_name, setting_value, description)
VALUES
    ('test', 'test', 'test');
    
    



    
-- Nay edits end-------

CREATE TABLE bookings (
	booking_id INT PRIMARY KEY AUTO_INCREMENT,
	booking_date_time DATETIME,
    order_status TEXT(20),
    refund_amount FLOAT,
    additional_details VARCHAR (255),
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    space_event_id INT,
	FOREIGN KEY (space_event_id) REFERENCES space_events(space_event_id),
    guest_number INT,
    service_booked TEXT
);
 

INSERT INTO bookings (booking_id, booking_date_time, order_status, refund_amount, additional_details, user_id, space_event_id, guest_number, service_booked)
VALUES
    (1, '2023-09-04 10:00:00', 'cancelled', 0.00, 'Test Booking 1', 1, 1, 100, '1,2,3,4,5'),
    (2, '2023-09-05 15:30:00', 'booked', 0.00, 'Test Booking 2', 2, 2, 30, '1,4'),
    (3, '2023-09-06 12:56:00', 'booked', 0.00, 'Test Booking 3', 3, 3, 80, '1,2,3'),
    (4, '2023-09-06 12:50:00', 'booked', 0.00, 'Test Booking 4: a long event', 1, 4, 250, '1,2,3,4,5,10'),
    (5, '2023-09-06 12:50:00', 'booked', 0.00, 'Test Booking 5: all day event', 2, 5, 50, '3,4,5'),
    (6, '2023-09-06 12:50:09', 'booked', 0.00, 'Test Booking 6: short event', 3, 17, 80, '1,4,6,7'),
    (7, '2023-09-06 12:50:09', 'booked', 0.00, 'Test Booking 7: more events', 1, 11, 35, '4,5'),
    (8, '2023-09-06 12:50:09', 'booked', 0.00, 'Test Booking 8: planner1', 1, 26, 10, '1,9'),
    (9, '2023-08-20 12:00:00', 'booked', 0.00, Null, 4, 2, 100,'1,2,3'),
    (10,'2023-10-01 08:00:00', 'booked', 0.00, Null, 5, 7, 12, '1,4'),
    (11,'2023-10-05 19:05:20', 'booked', 0.00, Null, 6, 36, 10, '3,4,5'),
    (12,'2023-10-06 21:00:50', 'booked', 0.00, Null, 7, 16, 20, '4'),
    (13,'2023-06-06 11:00:50', 'booked', 0.00, Null, 1, 27, 10, '1,4'),
    (14,'2023-06-26 10:00:00', 'booked', 0.00, Null, 1, 1, 11, '1,3,4'),
    (15,'2023-06-26 11:00:00', 'booked', 0.00, Null, 1, 1, 15, '3,4'),
    (16,'2023-05-26 11:00:00', 'booked', 0.00, Null, 5, 26, 65, '1,4,9'),
    (17,'2023-04-26 12:00:00', 'booked', 0.00, Null, 2, 27, 45, '4,9'),
    (18,'2023-03-06 12:00:00', 'booked', 0.00, Null, 3, 26, 54, '9'),
    (19,'2023-02-06 12:00:00', 'booked', 0.00, Null, 5, 1, 9, '1,2,3,4,5'),
    (20,'2023-02-03 13:00:00', 'booked', 0.00, Null, 1, 26, 29, '1,4,9'),
    (21,'2023-01-03 13:00:00', 'booked', 0.00, Null, 2, 27, 9, '4'),
    (22,'2022-12-03 13:00:00', 'booked', 0.00, Null, 2, 1, 9, '2,3,4'),
    (23,'2022-11-03 13:00:00', 'booked', 0.00, Null, 1, 1, 89, '3,4'),
    (24,'2023-02-03 13:00:00', 'booked', 0.00, Null, 6, 41, 70, '4,5'),
    (25,'2023-01-03 13:00:00', 'booked', 0.00, Null, 2, 48, 35, '5,6,7'),
    (26,'2023-09-09 09:00:00', 'booked', 0.00, Null, 9, 3, 20, '4'),
    (27,'2023-11-09 09:00:00', 'booked', 0.00, Null, 1, 1, 20, '2,3,4'),
    (28,'2023-11-04 09:00:00', 'booked', 0.00, Null, 1, 1, 10, '5'),
	(29,'2023-11-01 09:00:00', 'booked', 0.00, Null, 1, 1, 70, '1'),
    (30,'2023-10-01 09:00:00', 'booked', 0.00, Null, 4, 27, 45, '1,4,9'),
    (31,'2023-10-20 09:00:00', 'booked', 0.00, Null, 4, 26, 15, '4,9'),
    (32,'2023-10-30 09:00:00', 'booked', 0.00, Null, 4, 26, 5, '1')
    
    
    ;

CREATE TABLE refunds (
    refund_id INT PRIMARY KEY AUTO_INCREMENT,
    booking_id INT,
    refund_amount DECIMAL(10, 2),
    refund_date DATETIME,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
);

CREATE TABLE availability (
    availability_id INT AUTO_INCREMENT PRIMARY KEY,
    start_date_time DATETIMe,
    end_date_time DATETIME,
    space_id INT,
    booking_id INT,
    FOREIGN KEY (space_id) REFERENCES venue_spaces(space_id),
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
);

INSERT INTO availability (start_date_time, end_date_time, space_id, booking_id) VALUES 
-- venue 1 --
('2023-10-04 12:00:00', '2023-10-04 15:00:00', 1, 1),
('2023-10-04 10:00:00', '2023-10-05 12:00:00', 1, 2),
('2023-10-05 17:00:00', '2023-10-05 21:00:00', 1, 3),
('2023-11-03 13:00:00', '2023-11-03 20:00:00', 1, 9),
('2023-07-03 13:00:00', '2023-07-13 20:00:00', 1, 14),
('2023-09-13 23:00:00', '2023-09-20 23:00:00', 1, 15),
('2023-09-13 23:00:00', '2023-09-20 23:00:00', 1, 15),
('2023-03-13 23:00:00', '2023-03-20 23:00:00', 1, 19),
('2022-12-15 13:00:00', '2022-12-17 13:00:00', 1, 22),
('2022-11-05 13:00:00', '2022-11-17 13:00:00', 1, 23),
('2023-10-15 20:00:00', '2023-10-18 20:00:00', 1, 26),
('2023-11-15 20:00:00', '2023-11-18 20:00:00', 1, 27),
('2023-11-05 20:00:00', '2023-11-06 20:00:00', 1, 28),
('2023-11-28 20:00:00', '2023-11-30 20:00:00', 1, 29),
-- venue 2 --
('2023-10-08 09:00:00', '2023-10-18 21:00:00', 2, 4),
('2023-10-20 16:00:00', '2023-10-20 19:00:00', 2, 10),
('2023-10-10 15:00:00', '2023-10-12 15:00:00', 4, 12),
-- ('2023-10-07', '10:00:00', '12:00:00', 2),
-- ('2023-10-08', '12:00:00', '14:00:00', 3),
-- ('2023-10-08', '17:00:00', '20:00:00', 4),
-- -- venue 3 --
('2023-10-30 08:00:00', '2023-10-31 13:00:00', 2, 5),
('2023-11-15 06:00:00', '2023-11-18 18:30:00', 5, 6),
('2023-11-16 06:00:00', '2023-11-19 18:30:00', 3, 7),
-- ('2023-10-08', '17:00:00', '20:00:00', 7);
-- -- venue 4 --
('2023-11-12 06:00:00', '2023-11-12 18:30:00', 9, 8),
('2023-08-12 06:00:00', '2023-08-15 18:30:00', 9, 13),
('2023-06-12 09:00:00', '2023-06-15 09:00:00', 9, 16),
('2023-05-02 19:00:00', '2023-05-15 19:00:00', 9, 17),
('2023-04-02 19:00:00', '2023-04-05 19:00:00', 9, 18),
('2023-02-05 13:00:00', '2023-02-10 13:00:00', 9, 20),
('2023-01-15 13:00:00', '2023-01-17 13:00:00', 9, 21),
('2023-11-15 13:00:00', '2023-11-17 13:00:00', 9, 30),
('2023-11-01 13:00:00', '2023-11-02 13:00:00', 9, 31),
('2023-11-21 13:00:00', '2023-11-24 13:00:00', 9, 32),
-- -- venue 5 --

-- -- venue 6 --
('2023-10-16 12:00:00', '2023-10-16 15:00:00', 12, 11),

-- -- venue 7 --
('2023-03-01 23:00:00', '2023-03-04 23:00:00', 13, 24),
-- -- venue 8 --
('2023-07-19 23:00:00', '2023-07-27 23:00:00', 15, 25)

;
CREATE TABLE payment (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    booking_id INT,
    payment_date_time DATETIME,
    payment_amount DECIMAL(10, 2),
    payment_status TEXT(20),
    payment_description TEXT(255),
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
);
    
INSERT INTO payment (booking_id, payment_date_time, payment_amount, payment_status, payment_description) VALUES 
(1, '2023-09-04 10:00:00', 5740, 'successful', Null), 
(2, '2023-09-05 15:30:00', 670, 'successful', Null),
(3, '2023-09-06 12:56:00', 830, 'successful', Null),
(4, '2023-09-06 12:50:00', 17278, 'successful', Null), 
(5, '2023-09-06 12:50:00', 918, 'successful', Null),
(6, '2023-09-06 12:50:09', 5680, 'successful', Null),
(7, '2023-09-06 12:50:09', 1190, 'successful', Null),
(8, '2023-09-06 12:50:09', 1330, 'successful', Null),
(9, '2023-08-20 12:05:00', 2550, 'successful', Null),
(10, '2023-10-01 09:10:00', 3012, 'successful', Null),
(11, '2023-10-05 20:09:20', 8756, 'successful', Null),
(12, '2023-10-06 22:00:00', 9800, 'successful', Null),
(13, '2023-06-06 11:10:50', 1800, 'successful', Null),
(14, '2023-06-26 10:00:00', 5800, 'successful', Null),
(15, '2023-06-26 11:00:00', 3890, 'successful', Null),
(16, '2023-05-26 11:00:00', 890, 'successful', Null),
(17, '2023-04-26 12:00:00', 2890, 'successful', Null),
(18, '2023-03-06 12:00:00', 990, 'successful', Null),
(19, '2023-02-06 12:00:00', 9990, 'successful', Null),
(20, '2023-02-03 13:00:00', 5670, 'successful', Null),
(21, '2023-01-03 13:00:00', 670, 'successful', Null),
(22,'2022-12-03 13:00:00', 2670, 'successful', Null),
(23,'2022-11-03 13:00:00', 6670, 'successful', Null),
(24,'2023-02-03 13:00:00', 4670, 'successful', Null),
(25,'2023-01-03 13:00:00', 7670, 'successful', Null),
(26,'2023-09-09 10:00:00', 5910, 'successful', Null),
(27,'2023-11-09 09:00:00', 4910, 'successful', Null),
(28,'2023-11-04 09:00:00', 910, 'successful', Null),
(29,'2023-11-01 09:00:00', 1110, 'successful', Null),
(30,'2023-10-01 09:00:00', 2510, 'successful', Null),
(31,'2023-10-20 09:00:00', 1510, 'successful', Null),
(32,'2023-10-30 09:00:00', 880, 'successful', Null)


;
    
CREATE TABLE venue_inquiries(
	venue_inquiry_id INT PRIMARY KEY auto_increment,
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20),
    inquiry_date DATE,
    message TEXT,
    planner_id int,
    FOREIGN KEY (planner_id) REFERENCES planners(planner_id)
    );

INSERT INTO venue_inquiries (name, email, phone, inquiry_date, message, planner_id)
VALUES ('John Doe', 'john@example.com', '123-456-7890', '2023-10-29', 'I am interested in your venue.', 1),
       ('Alice Smith', 'alice@example.com', '987-654-3210', '2023-10-30', 'Can you provide pricing details?', 2);

CREATE TABLE planner_message(
	planner_message_id INT PRIMARY KEY auto_increment,
    subject VARCHAR (255),
    message_date DATE,
    message_body TEXT,
    customer_id int,
    planner_id INT,
    FOREIGN KEY (customer_id) references customers(customer_id),
    FOREIGN KEY (planner_id) REFERENCES planners(planner_id)
    );

INSERT INTO planner_message (subject, message_date, message_body, customer_id, planner_id)
VALUES ('Discount on weddings in January', '2023-10-18', 'Hi Everyone, there is a 10% discount for all weddings booked for January.', 1, 1),
       ('Venue Closing', '2023-10-20', 'Hi Everyone, sadly I have to announce that Wild and Co will be closing their doors mid 2024.', 1, 1);

CREATE TABLE customer_messages (
    message_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    message_date DATE,
    subject TEXT,
    message_body TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

INSERT INTO customer_messages (user_id, message_date, subject, message_body)
VALUES (1, '2023-10-29', 'Booking', 'New booking made'),
       (2, '2023-10-30', 'Booking', 'New booking made');
