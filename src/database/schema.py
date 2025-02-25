"""
Database schema management module.
Provides functions to initialize and maintain the database schema.
"""
import asyncio
from .connection import execute_update

async def init_schema():
    """
    Initializes the database schema for Zomato support.
    Creates tables if they don't exist.
    """
    schema_queries = [
        """CREATE TABLE IF NOT EXISTS Customers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            phone VARCHAR(50) NOT NULL,
            city VARCHAR(100),
            registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE INDEX idx_phone (phone)
        )""",
        """CREATE TABLE IF NOT EXISTS Orders (
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
        )""",
        """CREATE TABLE IF NOT EXISTS SupportAgents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            available BOOLEAN DEFAULT TRUE
        )""",
        """CREATE TABLE IF NOT EXISTS Tickets (
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
            assigned_agent_id INT,
            FOREIGN KEY (customer_id) REFERENCES Customers(id),
            FOREIGN KEY (order_id) REFERENCES Orders(id),
            FOREIGN KEY (assigned_agent_id) REFERENCES SupportAgents(id)
        )""",
        """CREATE TABLE IF NOT EXISTS TicketComments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ticket_id INT NOT NULL,
            comment TEXT NOT NULL,
            author_type ENUM('customer', 'agent', 'system') DEFAULT 'agent',
            author_id INT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ticket_id) REFERENCES Tickets(id)
        )"""
    ]
    for query in schema_queries:
        execute_update(query, ()) 