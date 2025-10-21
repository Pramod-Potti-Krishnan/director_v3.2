#!/usr/bin/env python3
"""
Simple interactive WebSocket test for Railway deployment.
Prints everything received and lets you respond manually.
"""
import asyncio
import json
import websockets
import ssl
import uuid

# Colors
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'


async def test_railway():
    """Simple interactive test."""
    base_url = "directorv20-production.up.railway.app"
    session_id = str(uuid.uuid4())
    user_id = f"test_user_{str(uuid.uuid4())[:8]}"
    ws_url = f"wss://{base_url}/ws?session_id={session_id}&user_id={user_id}"

    print(f"\n{Colors.BOLD}{Colors.CYAN}{'═' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Director v2.0 Railway Test - Interactive Mode{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 60}{Colors.ENDC}\n")
    print(f"Connecting to: {base_url}")
    print(f"Session ID: {session_id}")
    print(f"User ID: {user_id}\n")

    # SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        async with websockets.connect(ws_url, ssl=ssl_context, ping_interval=20) as websocket:
            print(f"{Colors.GREEN}✅ Connected!{Colors.ENDC}\n")
            print(f"{Colors.YELLOW}{'─' * 60}{Colors.ENDC}")
            print(f"{Colors.BOLD}Listening for messages... (Ctrl+C to exit){Colors.ENDC}")
            print(f"{Colors.YELLOW}{'─' * 60}{Colors.ENDC}\n")

            # Start two tasks: one for receiving, one for sending
            async def receive_messages():
                """Receive and display messages."""
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)

                        # Pretty print the message
                        msg_type = data.get("type", "unknown")
                        print(f"\n{Colors.CYAN}📨 Received: {msg_type}{Colors.ENDC}")

                        if msg_type == "agent_message":
                            print(f"{Colors.BOLD}🤖 Director:{Colors.ENDC}")
                            print(f"   {data.get('content', '')}")

                        elif msg_type == "chat_message":
                            payload = data.get("payload", {})
                            print(f"{Colors.BOLD}🤖 Director:{Colors.ENDC}")
                            print(f"   {payload.get('text', '')}")
                            if payload.get("list_items"):
                                for item in payload["list_items"]:
                                    print(f"   • {item}")

                        elif msg_type == "action_request":
                            payload = data.get("payload", {})
                            print(f"{Colors.YELLOW}❓ {payload.get('prompt_text', 'Action required')}{Colors.ENDC}")
                            for action in payload.get("actions", []):
                                print(f"   → {action.get('label', 'Action')}")

                        elif msg_type == "presentation_url":
                            print(f"\n{Colors.GREEN}{'═' * 60}{Colors.ENDC}")
                            print(f"{Colors.BOLD}{Colors.GREEN}🎉 PRESENTATION URL GENERATED!{Colors.ENDC}")
                            print(f"{Colors.GREEN}{'═' * 60}{Colors.ENDC}")
                            print(f"{Colors.BOLD}URL:{Colors.ENDC} {data.get('url', 'N/A')}")
                            print(f"Presentation ID: {data.get('presentation_id', 'N/A')}")
                            print(f"Slides: {data.get('slide_count', 'N/A')}")
                            print(f"{Colors.GREEN}{'═' * 60}{Colors.ENDC}\n")

                        elif msg_type == "state_change":
                            state = data.get("new_state", "unknown")
                            print(f"{Colors.BLUE}🔄 State: {state}{Colors.ENDC}")

                        elif msg_type == "status_update":
                            status = data.get("content", data.get("status", ""))
                            print(f"{Colors.CYAN}⏳ {status}{Colors.ENDC}")

                        else:
                            # Print full JSON for unknown types
                            print(f"{Colors.YELLOW}Full message:{Colors.ENDC}")
                            print(json.dumps(data, indent=2))

                        print(f"{Colors.YELLOW}{'─' * 60}{Colors.ENDC}")

                    except websockets.exceptions.ConnectionClosed:
                        print(f"\n{Colors.RED}Connection closed{Colors.ENDC}")
                        break
                    except Exception as e:
                        print(f"\n{Colors.RED}Error receiving: {e}{Colors.ENDC}")
                        break

            async def send_messages():
                """Send messages from user input."""
                await asyncio.sleep(1)  # Wait for initial greeting

                while True:
                    # Wait for user input
                    user_input = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: input(f"\n{Colors.BOLD}Your message (or 'quit'): {Colors.ENDC}")
                    )

                    if user_input.strip().lower() in ['quit', 'exit', 'q']:
                        print(f"{Colors.YELLOW}Exiting...{Colors.ENDC}")
                        break

                    if user_input.strip():
                        # Send message in correct format (data.text)
                        payload = {
                            "type": "user_message",
                            "data": {
                                "text": user_input
                            }
                        }

                        print(f"{Colors.GREEN}📤 Sending...{Colors.ENDC}")
                        await websocket.send(json.dumps(payload))

            # Run both tasks
            await asyncio.gather(
                receive_messages(),
                send_messages()
            )

    except Exception as e:
        print(f"\n{Colors.RED}❌ Connection failed: {e}{Colors.ENDC}")
        import traceback
        print(traceback.format_exc())


if __name__ == "__main__":
    try:
        asyncio.run(test_railway())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.ENDC}")
