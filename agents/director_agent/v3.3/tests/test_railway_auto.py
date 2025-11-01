#!/usr/bin/env python3
"""
Fully automated Railway test - no user input required.
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
    BOLD = '\033[1m'
    ENDC = '\033[0m'


async def automated_test():
    """Run fully automated test conversation."""
    base_url = "directorv20-production.up.railway.app"
    session_id = str(uuid.uuid4())
    user_id = f"test_user_{str(uuid.uuid4())[:8]}"
    ws_url = f"wss://{base_url}/ws?session_id={session_id}&user_id={user_id}"

    print(f"\n{Colors.BOLD}{Colors.CYAN}{'═' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Director v2.0 Automated Test{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 60}{Colors.ENDC}\n")

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    messages_to_send = [
        "I need a presentation about healthy eating for a nutrition conference",
        "The audience is healthcare professionals. Duration 20 minutes. Cover topics like balanced diet, meal planning, and nutrition myths. Professional tone. Yes, include statistics.",
        "Yes, that plan looks great",
        # After generation completes, we'll exit
    ]

    message_index = 0

    try:
        async with websockets.connect(ws_url, ssl=ssl_context, ping_interval=20, ping_timeout=10) as websocket:
            print(f"{Colors.GREEN}✅ Connected to Railway!{Colors.ENDC}")
            print(f"Session: {session_id}\n")
            print(f"{Colors.YELLOW}{'─' * 60}{Colors.ENDC}\n")

            while True:
                try:
                    # Receive message with timeout (180 seconds for generation phase)
                    message = await asyncio.wait_for(websocket.recv(), timeout=180.0)
                    data = json.loads(message)

                    msg_type = data.get("type", "unknown")
                    print(f"{Colors.CYAN}📨 {msg_type}{Colors.ENDC}")

                    # Display based on type
                    if msg_type == "chat_message":
                        payload = data.get("payload", {})
                        print(f"{Colors.BOLD}Director:{Colors.ENDC} {payload.get('text', '')[:200]}")
                        if payload.get("list_items"):
                            for item in payload.get("list_items", [])[:3]:
                                print(f"  • {item}")

                    elif msg_type == "presentation_url":
                        payload = data.get("payload", {})
                        print(f"\n{Colors.GREEN}{'═' * 60}{Colors.ENDC}")
                        print(f"{Colors.BOLD}{Colors.GREEN}🎉 SUCCESS! PRESENTATION URL:{Colors.ENDC}")
                        print(f"{Colors.GREEN}{'═' * 60}{Colors.ENDC}")
                        print(f"{Colors.GREEN}{payload.get('url', 'N/A')}{Colors.ENDC}")
                        print(f"Presentation ID: {payload.get('presentation_id', 'N/A')}")
                        print(f"Slides: {payload.get('slide_count', 'N/A')}")
                        print(f"Message: {payload.get('message', 'N/A')}")
                        print(f"{Colors.GREEN}{'═' * 60}{Colors.ENDC}\n")
                        print(f"{Colors.BOLD}{Colors.GREEN}✅ TEST PASSED!{Colors.ENDC}\n")
                        return True

                    elif msg_type == "action_request":
                        payload = data.get("payload", {})
                        print(f"{Colors.YELLOW}Action: {payload.get('prompt_text', '')[:100]}{Colors.ENDC}")

                    elif msg_type == "state_change":
                        state = data.get("new_state", "unknown")
                        print(f"{Colors.CYAN}State → {state}{Colors.ENDC}")

                    elif msg_type == "status_update":
                        print(f"{Colors.CYAN}Status: {data.get('content', '')[:100]}{Colors.ENDC}")

                    print(f"{Colors.YELLOW}{'─' * 60}{Colors.ENDC}\n")

                    # Auto-send next message after a brief delay
                    if message_index < len(messages_to_send):
                        await asyncio.sleep(1)  # Small delay before responding

                        user_message = messages_to_send[message_index]
                        message_index += 1

                        payload = {
                            "type": "user_message",
                            "data": {"text": user_message}
                        }

                        print(f"{Colors.GREEN}📤 Sending:{Colors.ENDC} {user_message[:100]}...\n")
                        await websocket.send(json.dumps(payload))

                except asyncio.TimeoutError:
                    print(f"{Colors.RED}⏱️  Timeout waiting for response{Colors.ENDC}")
                    return False
                except websockets.exceptions.ConnectionClosed:
                    print(f"{Colors.RED}Connection closed unexpectedly{Colors.ENDC}")
                    return False

    except Exception as e:
        print(f"{Colors.RED}❌ Test failed: {e}{Colors.ENDC}")
        import traceback
        print(traceback.format_exc())
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Starting automated Railway test...")
    print("This will test the complete conversation flow automatically.")
    print("=" * 60)

    success = asyncio.run(automated_test())

    print("\n" + "=" * 60)
    if success:
        print(f"{Colors.GREEN}✅ TEST PASSED - v2.0 deck-builder integration working!{Colors.ENDC}")
    else:
        print(f"{Colors.RED}❌ TEST FAILED{Colors.ENDC}")
    print("=" * 60 + "\n")
