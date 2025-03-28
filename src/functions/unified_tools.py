from typing import Annotated, List, Optional
import asyncio
from livekit.agents import llm
from .gmail_tools import GmailMcpFunctions

class UnifiedFunctions(llm.FunctionContext):
    def __init__(self):
        super().__init__()
        self._gmail_functions = GmailMcpFunctions()

    # Utility methods
    async def cleanup(self):
        """Cleanup resources when closing the agent."""
        await self._gmail_functions.stop_mcp_server()

    # Gmail Functions - delegate to GmailMcpFunctions
    @llm.ai_callable()
    async def check_gmail_auth_status(self) -> str:
        """Checks if Gmail authentication is properly set up and provides instructions if not."""
        return await self._gmail_functions.check_gmail_auth_status()

    @llm.ai_callable()
    async def send_gmail(
        self,
        to: Annotated[List[str], llm.TypeInfo(description="List of recipient email addresses")],
        subject: Annotated[str, llm.TypeInfo(description="Email subject")],
        body: Annotated[str, llm.TypeInfo(description="Email body content")],
        cc: Annotated[List[str], llm.TypeInfo(description="List of CC recipients")] = [],
        bcc: Annotated[List[str], llm.TypeInfo(description="List of BCC recipients")] = [],
    ) -> str:
        """Sends an email using Gmail."""
        return await self._gmail_functions.send_gmail(to, subject, body, cc, bcc)

    @llm.ai_callable()
    async def draft_gmail(
        self,
        to: Annotated[List[str], llm.TypeInfo(description="List of recipient email addresses")],
        subject: Annotated[str, llm.TypeInfo(description="Email subject")],
        body: Annotated[str, llm.TypeInfo(description="Email body content")],
        cc: Annotated[List[str], llm.TypeInfo(description="List of CC recipients")] = [],
        bcc: Annotated[List[str], llm.TypeInfo(description="List of BCC recipients")] = [],
    ) -> str:
        """Creates an email draft in Gmail without sending it."""
        return await self._gmail_functions.draft_email(to, subject, body, cc, bcc)

    @llm.ai_callable()
    async def search_emails(
        self,
        query: Annotated[str, llm.TypeInfo(description="Gmail search query")],
        max_results: Annotated[int, llm.TypeInfo(description="Maximum number of results")] = 10
    ) -> str:
        """Searches for emails in Gmail."""
        return await self._gmail_functions.search_emails(query, max_results)

    @llm.ai_callable()
    async def read_email(
        self,
        message_id: Annotated[str, llm.TypeInfo(description="ID of the email message to read")]
    ) -> str:
        """Reads an email message from Gmail."""
        return await self._gmail_functions.read_email(message_id)
        
    @llm.ai_callable()
    async def modify_email_labels(
        self,
        message_id: Annotated[str, llm.TypeInfo(description="ID of the email message to modify")],
        add_labels: Annotated[List[str], llm.TypeInfo(description="List of label IDs to add to the message")] = None,
        remove_labels: Annotated[List[str], llm.TypeInfo(description="List of label IDs to remove from the message")] = None,
    ) -> str:
        """Modifies email labels (adds or removes labels from the email)."""
        return await self._gmail_functions.modify_email(message_id, add_labels, remove_labels)
        
    @llm.ai_callable()
    async def list_gmail_labels(self) -> str:
        """Lists all available Gmail labels."""
        return await self._gmail_functions.list_email_labels()

    # Common utility functions
    @llm.ai_callable()
    async def get_current_time(self) -> str:
        """Returns the current time."""
        from datetime import datetime
        now = datetime.now()
        return f"The current time is {now.strftime('%H:%M:%S')}."

    @llm.ai_callable()
    async def get_current_date(self) -> str:
        """Returns the current date."""
        from datetime import datetime
        now = datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}." 