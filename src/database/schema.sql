-- Customer Support Database Schema for Zomato
-- Drop database if exists (optional, comment out if not needed)
DROP DATABASE IF EXISTS `customer-support-db`;

-- Create and use the database
CREATE DATABASE IF NOT EXISTS `customer-support-db`
    DEFAULT CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE `customer-support-db`;

-- Drop tables if they exist (in correct order due to foreign key constraints)
DROP TABLE IF EXISTS TicketComments;
DROP TABLE IF EXISTS Tickets;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Customers;

-- Create Customers table
CREATE TABLE Customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    city VARCHAR(100),
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE INDEX idx_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create Orders table
CREATE TABLE Orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    restaurant_name VARCHAR(255) NOT NULL,
    order_status ENUM('PLACED', 'CONFIRMED', 'PREPARING', 'OUT_FOR_DELIVERY', 'DELIVERED', 'CANCELLED') DEFAULT 'PLACED',
    order_total DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50),
    delivery_address TEXT,
    order_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    delivery_timestamp DATETIME,
    order_details JSON,
    FOREIGN KEY (customer_id) REFERENCES Customers(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create Tickets table
CREATE TABLE Tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_id INT,
    subject VARCHAR(255) NOT NULL,
    description TEXT,
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    status ENUM('open', 'in_progress', 'resolved', 'closed') DEFAULT 'open',
    category ENUM('delivery_delay', 'quality_issue', 'wrong_items', 'missing_items', 'refund', 'other') DEFAULT 'other',
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_date DATETIME,
    FOREIGN KEY (customer_id) REFERENCES Customers(id),
    FOREIGN KEY (order_id) REFERENCES Orders(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create Ticket Comments table
CREATE TABLE TicketComments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    comment TEXT NOT NULL,
    author_type ENUM('customer', 'agent', 'system') DEFAULT 'agent',
    author_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES Tickets(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add performance optimization indexes
ALTER TABLE Customers ADD INDEX idx_city (city);
ALTER TABLE Orders ADD INDEX idx_order_status (order_status);
ALTER TABLE Orders ADD INDEX idx_order_timestamp (order_timestamp);
ALTER TABLE Tickets ADD INDEX idx_status (status);
ALTER TABLE Tickets ADD INDEX idx_priority (priority);
ALTER TABLE Tickets ADD INDEX idx_category (category);

-- Insert sample data for Zomato customer support
-- Insert 11 customers from different Indian cities
INSERT INTO Customers (name, email, phone, city, registration_date) VALUES 
    ('Rahul Sharma', 'rahul.s@gmail.com', '+91-9876543210', 'Mumbai', '2024-01-15 10:30:00'),
    ('Priya Patel', 'priya.p@gmail.com', '+91-9876543211', 'Delhi', '2024-02-01 11:45:00'),
    ('Amit Kumar', 'amit.k@yahoo.com', '+91-9876543212', 'Bangalore', '2024-02-15 09:15:00'),
    ('Deepa Verma', 'deepa.v@gmail.com', '+91-9876543213', 'Pune', '2024-02-20 14:20:00'),
    ('Suresh Reddy', 'suresh.r@hotmail.com', '+91-9876543214', 'Hyderabad', '2024-02-25 16:30:00'),
    ('Anita Singh', 'anita.s@gmail.com', '+91-9876543215', 'Chennai', '2024-03-01 12:15:00'),
    ('Mohammed Khan', 'mk@gmail.com', '+91-9876543216', 'Mumbai', '2024-03-05 10:45:00'),
    ('Kavita Menon', 'kavita.m@yahoo.com', '+91-9876543217', 'Bangalore', '2024-03-07 09:30:00'),
    ('Rajesh Gupta', 'rajesh.g@gmail.com', '+91-9876543218', 'Delhi', '2024-03-08 15:20:00'),
    ('Lakshmi Krishnan', 'lakshmi.k@gmail.com', '+91-9876543219', 'Chennai', '2024-03-09 11:10:00'),
    ('Test Customer', 'test.customer@zomato.com', '+91-1234567890', 'TestCity', '2024-03-10 12:00:00');

-- Insert 11 orders with realistic Indian restaurant data
INSERT INTO Orders (customer_id, restaurant_name, order_status, order_total, payment_method, delivery_address, order_timestamp, delivery_timestamp, order_details) VALUES
    (1, 'Paradise Biryani', 'DELIVERED', 845.00, 'UPI', 'A-101, Harmony Apartments, Andheri West, Mumbai', '2024-03-10 19:30:00', '2024-03-10 20:15:00', 
        '{"items": [{"name": "Hyderabadi Chicken Biryani", "quantity": 2, "price": 349}, {"name": "Raita", "quantity": 1, "price": 49}, {"name": "Gulab Jamun", "quantity": 2, "price": 49}], "special_instructions": "Extra raita please"}'),
    (2, 'Punjab Grill', 'OUT_FOR_DELIVERY', 1250.00, 'Credit Card', 'C-42, Vasant Kunj, New Delhi', '2024-03-10 19:45:00', NULL,
        '{"items": [{"name": "Butter Chicken", "quantity": 1, "price": 450}, {"name": "Garlic Naan", "quantity": 3, "price": 60}, {"name": "Dal Makhani", "quantity": 1, "price": 299}], "special_instructions": "Less spicy"}'),
    (3, 'MTR Restaurant', 'PREPARING', 450.00, 'UPI', '205, Richmond Road, Bangalore', '2024-03-10 20:00:00', NULL,
        '{"items": [{"name": "Masala Dosa", "quantity": 2, "price": 150}, {"name": "Filter Coffee", "quantity": 2, "price": 75}], "special_instructions": "Crispy dosa"}'),
    (4, 'Behrouz Biryani', 'CANCELLED', 699.00, 'Wallet', 'D-303, Magarpatta City, Pune', '2024-03-10 18:30:00', NULL,
        '{"items": [{"name": "Royal Chicken Biryani", "quantity": 1, "price": 499}, {"name": "Kebab Platter", "quantity": 1, "price": 200}], "special_instructions": "No onions"}'),
    (5, 'Shah Ghouse', 'DELIVERED', 1100.00, 'COD', '12-2-459/A, Banjara Hills, Hyderabad', '2024-03-10 20:15:00', '2024-03-10 21:00:00',
        '{"items": [{"name": "Family Pack Biryani", "quantity": 1, "price": 899}, {"name": "Chicken 65", "quantity": 1, "price": 201}], "special_instructions": "Extra spicy"}'),
    (6, 'Saravana Bhavan', 'DELIVERED', 550.00, 'UPI', '24, Anna Salai, Chennai', '2024-03-10 19:00:00', '2024-03-10 19:45:00',
        '{"items": [{"name": "South Indian Thali", "quantity": 2, "price": 275}], "special_instructions": "No garlic"}'),
    (7, 'Bademiya', 'CONFIRMED', 800.00, 'Credit Card', 'Colaba Causeway, Mumbai', '2024-03-10 20:30:00', NULL,
        '{"items": [{"name": "Seekh Kebab Roll", "quantity": 4, "price": 200}], "special_instructions": "Extra mint chutney"}'),
    (8, 'Empire Restaurant', 'PLACED', 675.00, 'UPI', 'Koramangala 5th Block, Bangalore', '2024-03-10 20:45:00', NULL,
        '{"items": [{"name": "Chicken Wings", "quantity": 2, "price": 250}, {"name": "Mutton Keema Dosa", "quantity": 1, "price": 175}], "special_instructions": "Extra tissues"}'),
    (9, 'Karim''s', 'DELIVERED', 1450.00, 'Credit Card', 'Chandni Chowk, Delhi', '2024-03-10 19:15:00', '2024-03-10 20:00:00',
        '{"items": [{"name": "Mutton Korma", "quantity": 1, "price": 550}, {"name": "Butter Naan", "quantity": 4, "price": 60}, {"name": "Chicken Jahangiri", "quantity": 1, "price": 600}], "special_instructions": "Pack gravy separately"}'),
    (10, 'Murugan Idli Shop', 'OUT_FOR_DELIVERY', 480.00, 'UPI', 'T Nagar, Chennai', '2024-03-10 20:00:00', NULL,
        '{"items": [{"name": "Idli Plate", "quantity": 3, "price": 100}, {"name": "Pongal", "quantity": 1, "price": 120}], "special_instructions": "Extra sambar"}'),
    (11, 'Test Restaurant', 'DELIVERED', 650.00, 'COD', 'Test Address, Bangalore', '2024-03-10 19:00:00', '2024-03-10 19:45:00',
        '{"items": [{"name": "Test Meal", "quantity": 2, "price": 300}, {"name": "Test Dessert", "quantity": 1, "price": 50}], "special_instructions": "Test instructions"}');

-- Insert 11 support tickets
INSERT INTO Tickets (customer_id, order_id, subject, description, priority, status, category, created_date, resolved_date) VALUES
    (2, 2, 'Order Delayed', 'My order is taking longer than estimated delivery time', 'high', 'in_progress', 'delivery_delay', '2024-03-10 20:30:00', NULL),
    (4, 4, 'Wrong Items', 'Received veg biryani instead of chicken biryani', 'high', 'resolved', 'wrong_items', '2024-03-10 19:00:00', '2024-03-10 19:30:00'),
    (1, 1, 'Spice Level Issue', 'Food is much spicier than requested', 'medium', 'open', 'quality_issue', '2024-03-10 20:45:00', NULL),
    (3, 3, 'Missing Items', 'Didn''t receive the filter coffee in my order', 'medium', 'in_progress', 'missing_items', '2024-03-10 20:30:00', NULL),
    (5, 5, 'Refund Request', 'Order delivered late and cold', 'high', 'resolved', 'refund', '2024-03-10 21:15:00', '2024-03-10 21:45:00'),
    (6, 6, 'Quality Complaint', 'Food not fresh', 'high', 'in_progress', 'quality_issue', '2024-03-10 20:00:00', NULL),
    (7, 7, 'Payment Issue', 'Charged twice for the same order', 'urgent', 'open', 'refund', '2024-03-10 20:45:00', NULL),
    (8, 8, 'Order Confirmation', 'Haven''t received order confirmation', 'low', 'resolved', 'other', '2024-03-10 21:00:00', '2024-03-10 21:15:00'),
    (9, 9, 'Packaging Issue', 'Gravy spilled in delivery bag', 'medium', 'closed', 'quality_issue', '2024-03-10 20:30:00', '2024-03-10 21:00:00'),
    (10, 10, 'Delivery Location', 'Delivery partner unable to locate address', 'high', 'in_progress', 'delivery_delay', '2024-03-10 20:30:00', NULL),
    (11, 11, 'Test Ticket', 'Test ticket description', 'medium', 'open', 'other', '2024-03-10 21:00:00', NULL);

-- Insert 10 ticket comments
INSERT INTO TicketComments (ticket_id, comment, author_type, author_id, created_at) VALUES
    (1, 'I have contacted the delivery partner. Your order will be delivered in 10 minutes.', 'agent', 1, '2024-03-10 20:35:00'),
    (2, 'We sincerely apologize for the mix-up. We have initiated a refund and will send a complimentary dish.', 'agent', 2, '2024-03-10 19:05:00'),
    (3, 'We have noted your feedback about the spice level. Would you like us to arrange a replacement?', 'agent', 3, '2024-03-10 20:50:00'),
    (4, 'The missing coffee will be delivered in 15 minutes by a separate delivery partner.', 'agent', 4, '2024-03-10 20:35:00'),
    (5, 'Full refund processed. Added ₹200 worth Zomato credits as a goodwill gesture.', 'agent', 5, '2024-03-10 21:20:00'),
    (6, 'We are speaking with the restaurant about the quality. Would you like a refund?', 'agent', 6, '2024-03-10 20:05:00'),
    (7, 'I can see the duplicate charge. Initiating refund for the extra payment immediately.', 'agent', 7, '2024-03-10 20:50:00'),
    (8, 'Order confirmed and accepted by restaurant. You will receive updates shortly.', 'agent', 8, '2024-03-10 21:05:00'),
    (9, 'Refund processed for the damaged items. Next order delivery will be free.', 'agent', 9, '2024-03-10 20:35:00'),
    (10, 'Shared your exact location with the delivery partner. They are en route.', 'agent', 10, '2024-03-10 20:35:00');
