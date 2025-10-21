#!/usr/bin/env python3
"""
WebSocket client test for Railway deployed Director v2.0.
Tests end-to-end conversation flow via WebSocket connection.
"""
import asyncio
import json
import websockets
import ssl
from typing import Dict, Any, List
from datetime import datetime

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class RailwayDirectorTester:
    """WebSocket client tester for Railway deployed Director v2.0."""

    def __init__(self, base_url: str = "directorv20-production.up.railway.app"):
        """Initialize tester with Railway URL."""
        # Generate session and user IDs for WebSocket connection
        import uuid
        self.session_id = str(uuid.uuid4())
        self.user_id = "test_user_" + str(uuid.uuid4())[:8]

        # Construct WebSocket URL with required parameters
        self.ws_url = f"wss://{base_url}/ws?session_id={self.session_id}&user_id={self.user_id}"
        self.conversation_history = []

    async def connect(self):
        """Connect to Railway WebSocket server."""
        print(f"{Colors.CYAN}Connecting to Railway deployment...{Colors.ENDC}")
        print(f"URL: {self.ws_url}")
        print(f"Session ID: {self.session_id}")
        print(f"User ID: {self.user_id}")
        print(f"{Colors.YELLOW}Note: SSL verification disabled for testing{Colors.ENDC}")

        try:
            # Create SSL context that doesn't verify certificates (for testing)
            # This is safe for testing Railway deployments
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            self.websocket = await websockets.connect(
                self.ws_url,
                ping_interval=20,
                ping_timeout=10,
                ssl=ssl_context
            )
            print(f"{Colors.GREEN}✅ Connected successfully!{Colors.ENDC}\n")
            return True
        except Exception as e:
            print(f"{Colors.RED}❌ Connection failed: {e}{Colors.ENDC}")
            print(f"{Colors.YELLOW}Tip: Check if Railway deployment is running{Colors.ENDC}")
            return False

    async def send_message(self, message: str):
        """Send user message to server."""
        payload = {
            "type": "user_message",
            "content": message,
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat()
        }

        print(f"\n{Colors.BOLD}👤 User:{Colors.ENDC} {message}")
        await self.websocket.send(json.dumps(payload))
        self.conversation_history.append({"role": "user", "content": message})

    async def receive_messages(self):
        """Receive and process messages from server."""
        messages = []

        try:
            while True:
                # Set a timeout for receiving messages
                response = await asyncio.wait_for(
                    self.websocket.recv(),
                    timeout=60.0  # 60 second timeout for AI response
                )

                data = json.loads(response)
                messages.append(data)

                # Display message based on type
                self._display_message(data)

                # Check if this is the final message
                if self._is_final_message(data):
                    break

        except asyncio.TimeoutError:
            print(f"{Colors.YELLOW}⏱️  No more messages (timeout){Colors.ENDC}")
        except websockets.exceptions.ConnectionClosed:
            print(f"{Colors.RED}Connection closed by server{Colors.ENDC}")

        return messages

    def _display_message(self, data: Dict[str, Any]):
        """Display server message based on type."""
        msg_type = data.get("type", "unknown")

        if msg_type == "session_start":
            print(f"\n{Colors.GREEN}🎬 Session Started{Colors.ENDC}")
            print(f"   Session ID: {data.get('session_id', 'N/A')}")

        elif msg_type == "state_change":
            state = data.get("new_state", "unknown")
            print(f"\n{Colors.CYAN}🔄 State: {state}{Colors.ENDC}")

        elif msg_type == "agent_message":
            content = data.get("content", "")
            print(f"\n{Colors.BOLD}🤖 Director:{Colors.ENDC}")
            print(f"{content}")

        elif msg_type == "chat_message":
            # Streamlined protocol
            payload = data.get("payload", {})
            text = payload.get("text", "")
            print(f"\n{Colors.BOLD}🤖 Director:{Colors.ENDC}")
            print(f"{text}")

            # Display list items if present
            if payload.get("list_items"):
                for item in payload["list_items"]:
                    print(f"  • {item}")

        elif msg_type == "action_request":
            # Streamlined protocol - actions
            payload = data.get("payload", {})
            print(f"\n{Colors.YELLOW}{payload.get('prompt_text', 'Choose an action:')}{Colors.ENDC}")
            for action in payload.get("actions", []):
                marker = "►" if action.get("primary") else "▷"
                print(f"  {marker} {action.get('label', 'Action')}")

        elif msg_type == "slide_update":
            # Presentation data
            payload = data.get("payload", {})
            metadata = payload.get("metadata", {})
            slides = payload.get("slides", [])

            print(f"\n{Colors.GREEN}📊 Presentation Generated!{Colors.ENDC}")
            print(f"   Title: {metadata.get('main_title', 'N/A')}")
            print(f"   Theme: {metadata.get('overall_theme', 'N/A')}")
            print(f"   Slides: {len(slides)}")
            print(f"   Audience: {metadata.get('target_audience', 'N/A')}")
            print(f"   Duration: {metadata.get('presentation_duration', 'N/A')} minutes")

        elif msg_type == "presentation_url":
            # v2.0 deck-builder URL response
            url = data.get("url", "")
            presentation_id = data.get("presentation_id", "N/A")
            slide_count = data.get("slide_count", "N/A")
            message = data.get("message", "")

            print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 Presentation URL Generated! (v2.0){Colors.ENDC}")
            print(f"\n{Colors.CYAN}{'═' * 60}{Colors.ENDC}")
            print(f"{Colors.BOLD}📊 Presentation URL:{Colors.ENDC}")
            print(f"{Colors.GREEN}{url}{Colors.ENDC}")
            print(f"\n{Colors.BOLD}Details:{Colors.ENDC}")
            print(f"  • Presentation ID: {presentation_id}")
            print(f"  • Number of Slides: {slide_count}")
            print(f"  • Message: {message}")
            print(f"{Colors.CYAN}{'═' * 60}{Colors.ENDC}")
            print(f"\n{Colors.YELLOW}💡 Open the URL in your browser to view the presentation!{Colors.ENDC}")

        elif msg_type == "status_update":
            status = data.get("content", data.get("status", "Processing..."))
            print(f"{Colors.CYAN}⏳ {status}{Colors.ENDC}")

        elif msg_type == "error":
            error = data.get("content", data.get("error", "Unknown error"))
            print(f"{Colors.RED}❌ Error: {error}{Colors.ENDC}")

        elif msg_type == "system":
            message = data.get("message", "")
            print(f"{Colors.YELLOW}ℹ️  {message}{Colors.ENDC}")

    def _is_final_message(self, data: Dict[str, Any]) -> bool:
        """Check if this is the final message in a conversation turn."""
        msg_type = data.get("type", "")

        # These message types indicate completion of a turn
        final_types = [
            "slide_update",
            "presentation_url",
            "action_request"
        ]

        return msg_type in final_types

    async def run_test_conversation(self):
        """Run a complete test conversation."""
        print(f"\n{Colors.BOLD}{Colors.HEADER}{'═' * 60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}   Director v2.0 Railway Deployment Test   {Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'═' * 60}{Colors.ENDC}\n")

        # Connect to server
        if not await self.connect():
            return False

        try:
            # Stage 1: Receive greeting
            print(f"{Colors.CYAN}Stage 1: Receiving greeting...{Colors.ENDC}")
            await self.receive_messages()

            # Stage 2: Send topic and receive questions
            print(f"\n{Colors.CYAN}Stage 2: Sending topic...{Colors.ENDC}")
            await self.send_message(
                "I need to create a presentation about AI in healthcare for a medical conference."
            )
            await self.receive_messages()

            # Stage 3: Answer questions
            print(f"\n{Colors.CYAN}Stage 3: Answering clarifying questions...{Colors.ENDC}")
            await self.send_message(
                """Here are my answers:
                1. The target audience is healthcare professionals and doctors attending a medical conference
                2. The presentation should be about 15 minutes long
                3. I'd like to cover diagnostic AI, treatment planning, and patient monitoring
                4. The tone should be professional and evidence-based
                5. Yes, please include data and statistics about AI adoption in healthcare"""
            )
            await self.receive_messages()

            # Stage 4: Confirm plan
            print(f"\n{Colors.CYAN}Stage 4: Confirming plan...{Colors.ENDC}")
            await self.send_message("Yes, that plan looks great! Please proceed.")
            await self.receive_messages()

            # Stage 5: Generate presentation
            print(f"\n{Colors.CYAN}Stage 5: Waiting for presentation generation...{Colors.ENDC}")
            await self.receive_messages()

            # Stage 6: Request refinement (optional)
            print(f"\n{Colors.CYAN}Stage 6: Testing refinement...{Colors.ENDC}")
            await self.send_message(
                "Please add more specific examples of AI diagnostic tools to slide 3."
            )
            await self.receive_messages()

            print(f"\n{Colors.BOLD}{Colors.GREEN}✅ Test Completed Successfully!{Colors.ENDC}")
            print(f"{Colors.BOLD}{Colors.GREEN}{'═' * 60}{Colors.ENDC}\n")

            return True

        except Exception as e:
            print(f"\n{Colors.RED}❌ Test failed: {e}{Colors.ENDC}")
            import traceback
            print(traceback.format_exc())
            return False

        finally:
            # Close connection
            if self.websocket:
                await self.websocket.close()
                print(f"\n{Colors.CYAN}Connection closed.{Colors.ENDC}")

    async def run_interactive_test(self):
        """Run interactive test mode - user controls conversation."""
        print(f"\n{Colors.BOLD}{Colors.HEADER}{'═' * 60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}   Director v2.0 Interactive Test Mode   {Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'═' * 60}{Colors.ENDC}\n")

        # Connect to server
        if not await self.connect():
            return False

        try:
            # Receive initial greeting
            print(f"{Colors.CYAN}Receiving initial greeting...{Colors.ENDC}")
            await self.receive_messages()

            print(f"\n{Colors.YELLOW}You can now chat with the Director. Type 'quit' to exit.{Colors.ENDC}")

            while True:
                # Get user input
                user_input = input(f"\n{Colors.BOLD}Your message: {Colors.ENDC}").strip()

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print(f"{Colors.YELLOW}Exiting...{Colors.ENDC}")
                    break

                if not user_input:
                    continue

                # Send message
                await self.send_message(user_input)

                # Receive response
                await self.receive_messages()

            return True

        except Exception as e:
            print(f"\n{Colors.RED}❌ Test failed: {e}{Colors.ENDC}")
            import traceback
            print(traceback.format_exc())
            return False

        finally:
            # Close connection
            if self.websocket:
                await self.websocket.close()
                print(f"\n{Colors.CYAN}Connection closed.{Colors.ENDC}")


async def main():
    """Main entry point."""
    import sys

    # Default Railway URL
    railway_url = "directorv20-production.up.railway.app"

    # Check for custom URL
    if len(sys.argv) > 1:
        railway_url = sys.argv[1]

    # Initialize tester
    tester = RailwayDirectorTester(base_url=railway_url)

    # Choose test mode
    print(f"\n{Colors.BOLD}Select test mode:{Colors.ENDC}")
    print("1. Automated test (full conversation)")
    print("2. Interactive test (manual control)")
    print("\nChoice (1-2): ", end="")

    choice = input().strip()

    if choice == "1":
        await tester.run_test_conversation()
    elif choice == "2":
        await tester.run_interactive_test()
    else:
        print(f"{Colors.RED}Invalid choice{Colors.ENDC}")


if __name__ == "__main__":
    asyncio.run(main())
