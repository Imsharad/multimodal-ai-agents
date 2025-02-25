"""
Database models for the customer support system.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .connection import execute_query, execute_update

@dataclass
class Customer:
    id: Optional[int]
    name: str
    email: str
    phone: Optional[str]
    registration_date: Optional[datetime]

    @staticmethod
    def create(name: str, email: str, phone: Optional[str] = None) -> 'Customer':
        """Create a new customer."""
        query = "INSERT INTO Customers (name, email, phone) VALUES (%s, %s, %s)"
        execute_update(query, (name, email, phone))
        return Customer.get_by_email(email)

    @staticmethod
    def get_by_email(email: str) -> Optional['Customer']:
        """Get customer by email."""
        query = "SELECT * FROM Customers WHERE email = %s"
        results = execute_query(query, (email,))
        return Customer(**results[0]) if results else None

@dataclass
class SupportAgent:
    id: Optional[int]
    name: str
    email: Optional[str]
    phone: Optional[str]
    available: Optional[bool] = True

    @staticmethod
    def get_available_agents() -> list['SupportAgent']:
        """Get list of available support agents."""
        query = "SELECT * FROM SupportAgents"
        results = execute_query(query)
        return [SupportAgent(**result) for result in results]

@dataclass
class Ticket:
    id: Optional[int]
    customer_id: int
    subject: str
    description: Optional[str]
    status: str
    created_date: Optional[datetime]
    closed_date: Optional[datetime]
    assigned_agent_id: Optional[int]

    @staticmethod
    def create_ticket(customer_id: int, subject: str, description: str) -> 'Ticket':
        """Create a new support ticket."""
        query = """
            INSERT INTO Tickets (customer_id, subject, description)
            VALUES (%s, %s, %s)
        """
        execute_update(query, (customer_id, subject, description))
        # Get the last inserted ticket
        query = "SELECT * FROM Tickets WHERE customer_id = %s ORDER BY id DESC LIMIT 1"
        results = execute_query(query, (customer_id,))
        return Ticket(**results[0]) if results else None

    def add_comment(self, comment: str, author: str) -> None:
        """Add a comment to the ticket."""
        query = "INSERT INTO TicketComments (ticket_id, comment, author) VALUES (%s, %s, %s)"
        execute_update(query, (self.id, comment, author))

    def get_comments(self) -> list[dict]:
        """Get all comments for this ticket."""
        query = "SELECT * FROM TicketComments WHERE ticket_id = %s ORDER BY created_at"
        return execute_query(query, (self.id,))

    def assign_agent(self, agent_id: int) -> None:
        """Assign an agent to the ticket."""
        query = "UPDATE Tickets SET assigned_agent_id = %s WHERE id = %s"
        execute_update(query, (agent_id, self.id))
        self.assigned_agent_id = agent_id

    def update_status(self, status: str) -> None:
        """Update ticket status."""
        query = "UPDATE Tickets SET status = %s WHERE id = %s"
        execute_update(query, (status, self.id))
        self.status = status

@dataclass
class Order:
    id: Optional[int]
    customer_id: int
    restaurant: str
    order_status: str
    order_timestamp: Optional[datetime]
    order_details: str

    @staticmethod
    def create_order(customer_id: int, restaurant: str, order_status: str, order_details: str) -> 'Order':
        query = "INSERT INTO Orders (customer_id, restaurant, order_status, order_timestamp, order_details) VALUES (%s, %s, %s, NOW(), %s)"
        execute_update(query, (customer_id, restaurant, order_status, order_details))
        query = "SELECT * FROM Orders WHERE customer_id = %s ORDER BY id DESC LIMIT 1"
        results = execute_query(query, (customer_id,))
        return Order(**results[0]) if results else None

    def update_status(self, new_status: str) -> None:
        query = "UPDATE Orders SET order_status = %s WHERE id = %s"
        execute_update(query, (new_status, self.id))
        self.order_status = new_status

@dataclass
class TicketComment:
    id: Optional[int]
    ticket_id: int
    comment: str
    author: str
    created_at: Optional[datetime]

    @staticmethod
    def create_comment(ticket_id: int, comment: str, author: str) -> 'TicketComment':
        query = "INSERT INTO TicketComments (ticket_id, comment, author) VALUES (%s, %s, %s)"
        execute_update(query, (ticket_id, comment, author))
        query = "SELECT * FROM TicketComments WHERE ticket_id = %s ORDER BY id DESC LIMIT 1"
        results = execute_query(query, (ticket_id,))
        return TicketComment(**results[0]) if results else None 