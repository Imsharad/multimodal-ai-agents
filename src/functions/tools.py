from typing import Annotated
import aiohttp
import asyncio
import json
from datetime import datetime
from livekit.agents import llm
from ..database.connection import execute_query, execute_update
from ..database.schema import init_schema
from ..utils.phone_utils import normalize_phone_number

class UnifiedFunctions(llm.FunctionContext):
    def __init__(self):
        super().__init__()
        self._mcp_process = None

    # Helper Functions
    async def find_customer_by_phone(self, phone: str):
        """
        Finds a customer by phone number.
        
        Args:
            phone (str): The normalized phone number to search for
            
        Returns:
            dict or None: Customer record if found, None otherwise
        """
        customer_query = "SELECT * FROM Customers WHERE phone = %s"
        customer_results = execute_query(customer_query, (phone,))
        
        if customer_results:
            return customer_results[0]
        
        return None

    # Assistant Functions
    @llm.ai_callable()
    async def get_weather(
        self,
        location: Annotated[str, llm.TypeInfo(description="The location to get the weather for")],
    ):
        """Returns weather details for the given location."""
        url = f"https://wttr.in/{location}?format=%C+%t"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    weather_data = await response.text()
                    return f"The weather in {location} is {weather_data}."
                else:
                    raise Exception(f"Failed to get weather data, status code: {response.status}")

    @llm.ai_callable()
    async def get_current_datetime(self):
        """Returns the current date and time as a formatted string."""
        now = datetime.now()
        return f"The current date and time is {now.strftime('%Y-%m-%d %H:%M:%S')}."

    # Zomato Support Functions
    async def start_mcp_server(self):
        """Starts the MCP MySQL server if not already running."""
        if self._mcp_process is None:
            config = {
                "mysqlHost": "localhost",
                "mysqlUser": "sharad",
                "mysqlDatabase": "zomato_support_db",
                "mysqlPassword": "password"
            }
            cmd = [
                "npx", "-y", "@smithery/cli@latest",
                "run", "@f4ww4z/mcp-mysql-server",
                "--config", json.dumps(config)
            ]
            self._mcp_process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            # Wait a short while for the server to start
            await asyncio.sleep(2)
            
            # Initialize the database schema
            await init_schema()

    @llm.ai_callable()
    async def create_zomato_ticket(
        self,
        customer_email: Annotated[str, llm.TypeInfo(description="Customer's email address")],
        subject: Annotated[str, llm.TypeInfo(description="Subject of the support ticket")],
        description: Annotated[str, llm.TypeInfo(description="Detailed description of the issue")],
        phone: Annotated[str, llm.TypeInfo(description="Customer phone number, optional")] = "",
        address: Annotated[str, llm.TypeInfo(description="Customer address, optional")] = "",
        order_id: Annotated[int, llm.TypeInfo(description="Related order ID, optional")] = None,
    ) -> str:
        """Creates a support ticket for a Zomato customer."""
        await self.start_mcp_server()

        # Check if customer exists
        query = "SELECT * FROM Customers WHERE email = %s"
        results = execute_query(query, (customer_email,))
        if results:
            customer = results[0]
        else:
            # Create new customer
            insert_customer = "INSERT INTO Customers (name, email, phone, address) VALUES (%s, %s, %s, %s)"
            name = customer_email.split('@')[0]
            execute_update(insert_customer, (name, customer_email, phone, address))
            customer = execute_query("SELECT * FROM Customers WHERE email = %s", (customer_email,))[0]

        # Create ticket
        insert_ticket = "INSERT INTO Tickets (customer_id, subject, description, status) VALUES (%s, %s, %s, %s)"
        ticket_status = "Open"
        execute_update(insert_ticket, (customer["id"], subject, description, ticket_status))
        ticket = execute_query("SELECT * FROM Tickets WHERE customer_id = %s ORDER BY id DESC LIMIT 1", (customer["id"],))[0]

        # Assign a support agent if available
        agent_query = "SELECT * FROM SupportAgents WHERE available = TRUE LIMIT 1"
        agents = execute_query(agent_query, ())
        assigned_agent = None
        if agents:
            assigned_agent = agents[0]
            execute_update("UPDATE Tickets SET assigned_agent_id = %s WHERE id = %s", (assigned_agent["id"], ticket["id"]))

        return f"Created ticket #{ticket['id']} for {customer_email}. Assigned to: {assigned_agent['name'] if assigned_agent else 'pending assignment'}. You will receive updates about this ticket over WhatsApp."

    @llm.ai_callable()
    async def get_zomato_ticket_status(
        self,
        ticket_id: Annotated[int, llm.TypeInfo(description="The ID of the ticket to check")],
    ) -> str:
        """Retrieves the status and details of a support ticket."""
        await self.start_mcp_server()

        query = """
         SELECT t.*, c.email as customer_email, c.name as customer_name, sa.name as agent_name
         FROM Tickets t
         JOIN Customers c ON t.customer_id = c.id
         LEFT JOIN SupportAgents sa ON t.assigned_agent_id = sa.id
         WHERE t.id = %s
         """
        results = execute_query(query, (ticket_id,))
        if not results:
            return f"No ticket found with ID {ticket_id}"
        ticket = results[0]

        comment_query = "SELECT * FROM TicketComments WHERE ticket_id = %s ORDER BY created_at DESC LIMIT 1"
        comments = execute_query(comment_query, (ticket_id,))
        status_msg = (
            f"Ticket #{ticket_id}\n"
            f"Status: {ticket['status']}\n"
            f"Customer: {ticket['customer_name']} ({ticket['customer_email']})\n"
            f"Subject: {ticket['subject']}\n"
            f"Priority: {ticket['priority']}\n"
            f"Category: {ticket['category']}\n"
            f"Created: {ticket['created_date'].strftime('%d %b %Y, %I:%M %p')}\n"
            f"Assigned to: {ticket['agent_name'] or 'Unassigned'}\n"
        )
        if comments:
            status_msg += f"Latest comment: {comments[0]['comment']}\n"
        return status_msg

    @llm.ai_callable()
    async def add_zomato_ticket_comment(
        self,
        ticket_id: Annotated[int, llm.TypeInfo(description="The ID of the ticket to comment on")],
        comment: Annotated[str, llm.TypeInfo(description="The comment to add")],
        author: Annotated[str, llm.TypeInfo(description="The name of the person adding the comment")],
    ) -> str:
        """Adds a comment to an existing support ticket."""
        await self.start_mcp_server()

        # Verify the ticket exists
        if not execute_query("SELECT id FROM Tickets WHERE id = %s", (ticket_id,)):
            return f"No ticket found with ID {ticket_id}"

        insert_comment = "INSERT INTO TicketComments (ticket_id, comment, author) VALUES (%s, %s, %s)"
        execute_update(insert_comment, (ticket_id, comment, author))
        return f"Comment added to ticket #{ticket_id}"

    @llm.ai_callable()
    async def get_order_status(
        self,
        order_id: Annotated[int, llm.TypeInfo(description="The ID of the order to check")],
    ) -> str:
        """Retrieves the status of a Zomato order."""
        await self.start_mcp_server()

        query = "SELECT * FROM Orders WHERE id = %s"
        results = execute_query(query, (order_id,))
        if not results:
            return f"No order found with ID {order_id}"
        order = results[0]
        return f"Order #{order_id} for restaurant {order['restaurant_name']} is currently {order['order_status']}."

    @llm.ai_callable()
    async def verify_mobile_number(
        self,
        mobile: Annotated[str, llm.TypeInfo(description="Customer's mobile number for verification")],
    ) -> str:
        """
        Verifies a customer's mobile number and returns basic information.
        Returns a greeting message if the customer is found, otherwise returns an error message.
        """
        await self.start_mcp_server()
        
        print(f"verify_mobile_number called with mobile: {mobile}")
        
        # Normalize the phone number
        standard_phone = normalize_phone_number(mobile)
        if not standard_phone:
            return f"Invalid phone number format: {mobile}"
            
        print(f"Standard phone number: {standard_phone}")
        
        # Find the customer
        customer = await self.find_customer_by_phone(standard_phone)
        if not customer:
            return f"No customer found with mobile {mobile}."
        
        # Return a greeting if customer is found
        return f"Hi {customer['name']}, we found your account details. How can I assist you today?"

    @llm.ai_callable()
    async def create_customer_support_ticket(
        self,
        mobile: Annotated[str, llm.TypeInfo(description="Customer's mobile number")],
        issue_description: Annotated[str, llm.TypeInfo(description="Description of the customer's issue")],
    ) -> str:
        """Creates a support ticket for a customer identified by mobile number."""
        await self.start_mcp_server()
        
        # Normalize the phone number
        standard_phone = normalize_phone_number(mobile)
        if not standard_phone:
            return f"Invalid phone number format: {mobile}"
            
        # Find the customer
        customer = await self.find_customer_by_phone(standard_phone)
        if not customer:
            return f"No customer found with mobile {mobile}."
        
        # Create a ticket
        insert_ticket = "INSERT INTO Tickets (customer_id, subject, description, status) VALUES (%s, %s, %s, %s)"
        ticket_status = "Open"
        execute_update(insert_ticket, (customer["id"], issue_description, "", ticket_status))
        ticket = execute_query("SELECT * FROM Tickets WHERE customer_id = %s ORDER BY id DESC LIMIT 1", (customer["id"],))[0]
        
        # Assign a support agent if available
        agent_query = "SELECT * FROM SupportAgents WHERE available = TRUE LIMIT 1"
        agents = execute_query(agent_query, ())
        assigned_agent = None
        if agents:
            assigned_agent = agents[0]
            execute_update("UPDATE Tickets SET assigned_agent_id = %s WHERE id = %s", (assigned_agent["id"], ticket["id"]))
        
        return f"Ticket #{ticket['id']} created for your issue: '{issue_description}'. Assigned to: {assigned_agent['name'] if assigned_agent else 'pending assignment'}. You will receive updates about this ticket over WhatsApp."

    @llm.ai_callable()
    async def get_customer_recent_orders(
        self,
        mobile: Annotated[str, llm.TypeInfo(description="Customer's mobile number")],
        limit: Annotated[int, llm.TypeInfo(description="Number of recent orders to return")] = 5
    ) -> str:
        """Retrieves recent orders for a customer identified by mobile number."""
        await self.start_mcp_server()
        
        print(f"get_customer_recent_orders called with mobile: {mobile}")

        # Normalize the phone number
        standard_phone = normalize_phone_number(mobile)
        if not standard_phone:
            return f"Invalid phone number format: {mobile}"
            
        print(f"Standard phone number: {standard_phone}")
        
        # Find the customer
        customer = await self.find_customer_by_phone(standard_phone)
        if not customer:
            return f"No customer found with mobile {mobile}."
        
        # Get recent orders for this customer
        orders_query = """
            SELECT o.id, o.restaurant_name, o.order_status, o.order_total, 
                   o.payment_method, o.order_timestamp, o.delivery_timestamp,
                   o.order_details
            FROM Orders o
            WHERE o.customer_id = %s
            ORDER BY o.order_timestamp DESC
            LIMIT %s
        """
        orders = execute_query(orders_query, (customer["id"], limit))
        
        if not orders:
            return f"Hi {customer['name']}, you don't have any recent orders."
        
        # Format order information
        orders_info = [
            f"Order #{order['id']} from {order['restaurant_name']}\n"
            f"Status: {order['order_status']}\n"
            f"Date: {order['order_timestamp'].strftime('%d %b %Y, %I:%M %p')}\n"
            f"Total: ₹{order['order_total']}"
            for order in orders
        ]
        
        response = f"Hi {customer['name']}, here are your {len(orders)} most recent orders:\n\n"
        response += "\n\n".join(orders_info)
        return response 