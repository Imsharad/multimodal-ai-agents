from typing import Annotated
import aiohttp
from livekit.agents import llm
import asyncio
import subprocess
import json
from ..database.models import Customer, Ticket, SupportAgent
from ..database.connection import execute_query, execute_update

class AssistantFunctions(llm.FunctionContext):
    def __init__(self):
        super().__init__()
        self._mcp_process = None
        
    async def start_mcp_server(self):
        """Start the MCP MySQL server if not already running."""
        if self._mcp_process is None:
            config = {
                "mysqlHost": "localhost",
                "mysqlUser": "sharad",
                "mysqlDatabase": "customer-support-db",
                "mysqlPassword": "password"
            }
            cmd = ["npx", "-y", "@smithery/cli@latest", "run", "@f4ww4z/mcp-mysql-server", 
                   "--config", json.dumps(config)]
            self._mcp_process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            # Wait a bit for the server to start
            await asyncio.sleep(2)

    async def stop_mcp_server(self):
        """Stop the MCP MySQL server if running."""
        if self._mcp_process:
            self._mcp_process.terminate()
            await self._mcp_process.wait()
            self._mcp_process = None

    @llm.ai_callable()
    async def get_weather(
        self,
        location: Annotated[
            str, llm.TypeInfo(description="The location to get the weather for")
        ],
    ):
        """Called when the user asks about the weather. This function will return the weather for the given location."""
        url = f"https://wttr.in/{location}?format=%C+%t"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    weather_data = await response.text()
                    return f"The weather in {location} is {weather_data}."
                else:
                    raise Exception(
                        f"Failed to get weather data, status code: {response.status}"
                    )

    @llm.ai_callable()
    async def get_current_datetime(
        self,
    ):
        """Returns the current date and time as a formatted string."""
        from datetime import datetime
        now = datetime.now()
        return f"The current date and time is {now.strftime('%Y-%m-%d %H:%M:%S')}."

    @llm.ai_callable()
    async def create_support_ticket(
        self,
        customer_email: Annotated[
            str, llm.TypeInfo(description="The email of the customer who needs support")
        ],
        subject: Annotated[
            str, llm.TypeInfo(description="The subject or title of the support ticket")
        ],
        description: Annotated[
            str, llm.TypeInfo(description="The detailed description of the issue")
        ],
    ) -> str:
        """Creates a support ticket in the database for the specified customer."""
        try:
            # Ensure MCP server is running
            await self.start_mcp_server()
            
            # Get or create customer
            customer = Customer.get_by_email(customer_email)
            if not customer:
                # If customer doesn't exist, create new one
                customer = Customer.create(
                    name=customer_email.split('@')[0],  # Use email prefix as name
                    email=customer_email
                )
            
            # Create ticket
            ticket = Ticket.create_ticket(
                customer_id=customer.id,
                subject=subject,
                description=description
            )
            
            # Get available agents and assign to first available
            agents = SupportAgent.get_available_agents()
            if agents:
                ticket.assign_agent(agents[0].id)
                agent_name = agents[0].name
            else:
                agent_name = "pending assignment"
            
            return f"Created ticket #{ticket.id} for {customer.email}. Assigned to: {agent_name}"
            
        except Exception as e:
            return f"Failed to create ticket: {str(e)}"

    @llm.ai_callable()
    async def get_ticket_status(
        self,
        ticket_id: Annotated[
            int, llm.TypeInfo(description="The ID of the ticket to check")
        ],
    ) -> str:
        """Get the current status and details of a support ticket."""
        try:
            await self.start_mcp_server()
            
            # Query ticket details
            query = """
                SELECT t.*, c.email as customer_email, sa.name as agent_name
                FROM Tickets t
                JOIN Customers c ON t.customer_id = c.id
                LEFT JOIN SupportAgents sa ON t.assigned_agent_id = sa.id
                WHERE t.id = %s
            """
            results = execute_query(query, (ticket_id,))
            
            if not results:
                return f"No ticket found with ID {ticket_id}"
                
            ticket = results[0]
            comments = execute_query(
                "SELECT * FROM TicketComments WHERE ticket_id = %s ORDER BY commented_at DESC LIMIT 1",
                (ticket_id,)
            )
            
            status_msg = (
                f"Ticket #{ticket_id}\n"
                f"Status: {ticket['status']}\n"
                f"Customer: {ticket['customer_email']}\n"
                f"Subject: {ticket['subject']}\n"
                f"Assigned to: {ticket['agent_name'] or 'Unassigned'}\n"
            )
            
            if comments:
                status_msg += f"Latest comment: {comments[0]['comment']}"
                
            return status_msg
            
        except Exception as e:
            return f"Failed to get ticket status: {str(e)}"

    @llm.ai_callable()
    async def add_ticket_comment(
        self,
        ticket_id: Annotated[
            int, llm.TypeInfo(description="The ID of the ticket to comment on")
        ],
        comment: Annotated[
            str, llm.TypeInfo(description="The comment to add")
        ],
        author: Annotated[
            str, llm.TypeInfo(description="The name of the person adding the comment")
        ],
    ) -> str:
        """Add a comment to an existing support ticket."""
        try:
            await self.start_mcp_server()
            
            # First check if ticket exists
            query = "SELECT id FROM Tickets WHERE id = %s"
            if not execute_query(query, (ticket_id,)):
                return f"No ticket found with ID {ticket_id}"
            
            # Add the comment
            execute_update(
                "INSERT INTO TicketComments (ticket_id, comment, author) VALUES (%s, %s, %s)",
                (ticket_id, comment, author)
            )
            
            return f"Comment added to ticket #{ticket_id}"
            
        except Exception as e:
            return f"Failed to add comment: {str(e)}" 