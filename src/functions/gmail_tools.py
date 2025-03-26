from typing import Annotated, List, Optional
import asyncio
import subprocess
import json
import os
import tempfile
from pathlib import Path
from livekit.agents import llm

class GmailMcpFunctions(llm.FunctionContext):
    def __init__(self):
        super().__init__()
        self._mcp_process = None

    async def start_mcp_server(self):
        """Starts the Gmail MCP server if not already running."""
        if self._mcp_process is None:
            # Path to the Gmail MCP Server directory
            gmail_mcp_dir = str(Path(__file__).parent.parent.parent / "Gmail-MCP-Server")
            
            print(f"Starting Gmail MCP server from {gmail_mcp_dir}")
            
            # Check if the server has been authenticated
            credentials_path = os.path.expanduser("~/.gmail-mcp/credentials.json")
            oauth_keys_path = os.path.expanduser("~/.gmail-mcp/gcp-oauth.keys.json")
            
            if not os.path.exists(credentials_path) or not os.path.exists(oauth_keys_path):
                print("Gmail MCP server needs authentication. Please run authentication steps manually.")
                print("1. Create a Google Cloud Project and enable the Gmail API")
                print("2. Create an OAuth 2.0 Client ID (choose 'Desktop app' type)")
                print("3. Download the JSON file and place it at ~/.gmail-mcp/gcp-oauth.keys.json")
                print("4. Run 'cd Gmail-MCP-Server && node dist/index.js auth'")
                return "Authentication required for Gmail MCP server. Follow the printed instructions."
            
            cmd = ["node", "dist/index.js"]
            self._mcp_process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=gmail_mcp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            # Wait for the server to start
            await asyncio.sleep(2)
            print("Gmail MCP server started")
            return "Gmail MCP server started successfully"
        return "Gmail MCP server already running"

    async def stop_mcp_server(self):
        """Stops the MCP server."""
        if self._mcp_process:
            print("Stopping Gmail MCP server")
            self._mcp_process.terminate()
            await self._mcp_process.wait()
            self._mcp_process = None
            print("Gmail MCP server stopped")

    @llm.ai_callable()
    async def send_gmail(
        self,
        to: Annotated[List[str], llm.TypeInfo(description="List of recipient email addresses")],
        subject: Annotated[str, llm.TypeInfo(description="Email subject")],
        body: Annotated[str, llm.TypeInfo(description="Email body content")],
        cc: Annotated[List[str], llm.TypeInfo(description="List of CC recipients")] = [],
        bcc: Annotated[List[str], llm.TypeInfo(description="List of BCC recipients")] = [],
    ) -> str:
        """Sends an email using the Gmail MCP server."""
        server_status = await self.start_mcp_server()
        
        # Check if server startup failed due to authentication
        if "Authentication required" in server_status:
            return server_status
        
        # Since we're using stdio transport for now, we'll directly call the Gmail MCP server
        gmail_mcp_dir = str(Path(__file__).parent.parent.parent / "Gmail-MCP-Server")
        
        params = {
            "to": to,
            "subject": subject,
            "body": body,
            "cc": cc,
            "bcc": bcc
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp:
            json.dump(params, temp)
            temp_path = temp.name
        
        try:
            cmd = ["node", "dist/index.js", "send_email", "--params", temp_path]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=gmail_mcp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                try:
                    result = json.loads(stdout.decode('utf-8'))
                    if result.get("success"):
                        recipients = ", ".join(to)
                        return f"Email successfully sent to {recipients} with subject: '{subject}'"
                    else:
                        return f"Error: {result.get('content', [{'text': 'Unknown error'}])[0]['text']}"
                except json.JSONDecodeError:
                    return f"Email sent successfully to {', '.join(to)}"
            else:
                error_msg = stderr.decode('utf-8')
                return f"Error sending email: {error_msg}"
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)

    @llm.ai_callable()
    async def search_emails(
        self,
        query: Annotated[str, llm.TypeInfo(description="Gmail search query")],
        max_results: Annotated[int, llm.TypeInfo(description="Maximum number of results")] = 10
    ) -> str:
        """
        Searches for emails using the Gmail MCP server.
        
        You can use Gmail search operators, such as:
        - from: (e.g., from:john@example.com)
        - to: (e.g., to:mary@example.com)
        - subject: (e.g., subject:meeting)
        - after: or before: (e.g., after:2023/12/25)
        - has:attachment
        - is:unread, is:read, is:starred
        """
        server_status = await self.start_mcp_server()
        
        # Check if server startup failed due to authentication
        if "Authentication required" in server_status:
            return server_status
        
        gmail_mcp_dir = str(Path(__file__).parent.parent.parent / "Gmail-MCP-Server")
        
        params = {
            "query": query,
            "maxResults": max_results
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp:
            json.dump(params, temp)
            temp_path = temp.name
        
        try:
            cmd = ["node", "dist/index.js", "search_emails", "--params", temp_path]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=gmail_mcp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                try:
                    result = json.loads(stdout.decode('utf-8'))
                    if result.get("success"):
                        if "content" in result and result["content"]:
                            return result["content"][0]["text"]
                        else:
                            return f"No email results found for query: {query}"
                    else:
                        return f"Error: {result.get('content', [{'text': 'Unknown error'}])[0]['text']}"
                except json.JSONDecodeError:
                    return stdout.decode('utf-8')
            else:
                error_msg = stderr.decode('utf-8')
                return f"Error searching emails: {error_msg}"
        finally:
            os.unlink(temp_path)

    @llm.ai_callable()
    async def read_email(
        self,
        message_id: Annotated[str, llm.TypeInfo(description="ID of the email message to read")]
    ) -> str:
        """Reads an email message content using the Gmail MCP server."""
        server_status = await self.start_mcp_server()
        
        # Check if server startup failed due to authentication
        if "Authentication required" in server_status:
            return server_status
        
        gmail_mcp_dir = str(Path(__file__).parent.parent.parent / "Gmail-MCP-Server")
        
        params = {
            "messageId": message_id
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp:
            json.dump(params, temp)
            temp_path = temp.name
        
        try:
            cmd = ["node", "dist/index.js", "read_email", "--params", temp_path]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=gmail_mcp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                try:
                    result = json.loads(stdout.decode('utf-8'))
                    if result.get("success"):
                        if "content" in result and result["content"]:
                            return result["content"][0]["text"]
                        else:
                            return f"Email content could not be retrieved for message ID: {message_id}"
                    else:
                        return f"Error: {result.get('content', [{'text': 'Unknown error'}])[0]['text']}"
                except json.JSONDecodeError:
                    return stdout.decode('utf-8')
            else:
                error_msg = stderr.decode('utf-8')
                return f"Error reading email: {error_msg}"
        finally:
            os.unlink(temp_path)

    @llm.ai_callable()
    async def draft_email(
        self,
        to: Annotated[List[str], llm.TypeInfo(description="List of recipient email addresses")],
        subject: Annotated[str, llm.TypeInfo(description="Email subject")],
        body: Annotated[str, llm.TypeInfo(description="Email body content")],
        cc: Annotated[List[str], llm.TypeInfo(description="List of CC recipients")] = [],
        bcc: Annotated[List[str], llm.TypeInfo(description="List of BCC recipients")] = [],
    ) -> str:
        """Creates a draft email in Gmail without sending it."""
        server_status = await self.start_mcp_server()
        
        # Check if server startup failed due to authentication
        if "Authentication required" in server_status:
            return server_status
        
        gmail_mcp_dir = str(Path(__file__).parent.parent.parent / "Gmail-MCP-Server")
        
        params = {
            "to": to,
            "subject": subject,
            "body": body,
            "cc": cc,
            "bcc": bcc
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp:
            json.dump(params, temp)
            temp_path = temp.name
        
        try:
            cmd = ["node", "dist/index.js", "draft_email", "--params", temp_path]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=gmail_mcp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                try:
                    result = json.loads(stdout.decode('utf-8'))
                    if result.get("success"):
                        recipients = ", ".join(to)
                        return f"Email draft created for {recipients} with subject: '{subject}'"
                    else:
                        return f"Error: {result.get('content', [{'text': 'Unknown error'}])[0]['text']}"
                except json.JSONDecodeError:
                    return f"Email draft created for {', '.join(to)}"
            else:
                error_msg = stderr.decode('utf-8')
                return f"Error creating email draft: {error_msg}"
        finally:
            os.unlink(temp_path)
            
    @llm.ai_callable()
    async def modify_email(
        self,
        message_id: Annotated[str, llm.TypeInfo(description="ID of the email message to modify")],
        add_labels: Annotated[List[str], llm.TypeInfo(description="List of label IDs to add to the message")] = None,
        remove_labels: Annotated[List[str], llm.TypeInfo(description="List of label IDs to remove from the message")] = None,
    ) -> str:
        """Modifies email labels (adds or removes labels from the email)."""
        server_status = await self.start_mcp_server()
        
        # Check if server startup failed due to authentication
        if "Authentication required" in server_status:
            return server_status
        
        gmail_mcp_dir = str(Path(__file__).parent.parent.parent / "Gmail-MCP-Server")
        
        params = {
            "messageId": message_id,
            "addLabelIds": add_labels if add_labels else [],
            "removeLabelIds": remove_labels if remove_labels else []
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp:
            json.dump(params, temp)
            temp_path = temp.name
        
        try:
            cmd = ["node", "dist/index.js", "modify_email", "--params", temp_path]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=gmail_mcp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                try:
                    result = json.loads(stdout.decode('utf-8'))
                    if result.get("success"):
                        return f"Email labels updated successfully for message ID: {message_id}"
                    else:
                        return f"Error: {result.get('content', [{'text': 'Unknown error'}])[0]['text']}"
                except json.JSONDecodeError:
                    return f"Email labels updated for message ID: {message_id}"
            else:
                error_msg = stderr.decode('utf-8')
                return f"Error modifying email labels: {error_msg}"
        finally:
            os.unlink(temp_path)
            
    @llm.ai_callable()
    async def list_email_labels(self) -> str:
        """Lists all available Gmail labels."""
        server_status = await self.start_mcp_server()
        
        # Check if server startup failed due to authentication
        if "Authentication required" in server_status:
            return server_status
        
        gmail_mcp_dir = str(Path(__file__).parent.parent.parent / "Gmail-MCP-Server")
        
        try:
            cmd = ["node", "dist/index.js", "list_email_labels"]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=gmail_mcp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                try:
                    result = json.loads(stdout.decode('utf-8'))
                    if result.get("success"):
                        if "content" in result and result["content"]:
                            return result["content"][0]["text"]
                        else:
                            return "No labels found in your Gmail account."
                    else:
                        return f"Error: {result.get('content', [{'text': 'Unknown error'}])[0]['text']}"
                except json.JSONDecodeError:
                    return stdout.decode('utf-8')
            else:
                error_msg = stderr.decode('utf-8')
                return f"Error listing email labels: {error_msg}"
        except Exception as e:
            return f"Error listing email labels: {str(e)}" 