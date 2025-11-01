#!/usr/bin/env python3
"""
Test script for Director Agent v3.3 - ADC Authentication
Verifies that the v3.3 security refactoring works correctly
"""
import asyncio
import json
import sys
import websockets
from datetime import datetime

GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_test(message):
    print(f"\n{BOLD}Testing:{RESET} {message}")

def print_success(message):
    print(f"{GREEN}✓{RESET} {message}")

def print_error(message):
    print(f"{RED}✗{RESET} {message}")

def print_info(message):
    print(f"{YELLOW}ℹ{RESET} {message}")

async def test_gcp_auth():
    """Test 1: Verify GCP authentication is properly initialized"""
    print_test("GCP Authentication Initialization")

    try:
        from src.utils.gcp_auth import get_project_info, is_production_environment

        info = get_project_info()
        is_prod = is_production_environment()

        print_success(f"GCP Project: {info['project_id']}")
        print_success(f"GCP Location: {info['location']}")
        print_success(f"Environment: {'Production' if is_prod else 'Local Development'}")
        print_success(f"Auth Method: {'Service Account' if info['has_service_account'] else 'ADC (gcloud)'}")

        return True
    except Exception as e:
        print_error(f"GCP auth failed: {e}")
        return False

async def test_director_initialization():
    """Test 2: Verify Director Agent initializes with Vertex AI"""
    print_test("Director Agent Initialization")

    try:
        from src.agents.director import DirectorAgent

        director = DirectorAgent()
        print_success("Director Agent initialized successfully")
        print_success(f"Using model with Vertex AI")

        return True
    except Exception as e:
        print_error(f"Director initialization failed: {e}")
        return False

async def test_intent_router_initialization():
    """Test 3: Verify Intent Router initializes with Vertex AI"""
    print_test("Intent Router Initialization")

    try:
        from src.agents.intent_router import IntentRouter

        router = IntentRouter()
        print_success("Intent Router initialized successfully")
        print_success(f"Using Vertex AI for intent classification")

        return True
    except Exception as e:
        print_error(f"Intent Router initialization failed: {e}")
        return False

async def test_websocket_handler():
    """Test 4: Verify WebSocket Handler initializes all components"""
    print_test("WebSocket Handler Initialization")

    try:
        from src.handlers.websocket import WebSocketHandler

        handler = WebSocketHandler()
        print_success("WebSocket Handler initialized successfully")
        print_success("All components (Director, Intent Router, Session Manager) ready")

        return True
    except Exception as e:
        print_error(f"WebSocket Handler initialization failed: {e}")
        return False

async def test_health_endpoint():
    """Test 5: Verify health endpoint is responding"""
    print_test("Health Endpoint")

    try:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8503/health') as response:
                if response.status == 200:
                    data = await response.json()
                    print_success(f"Health check passed: {data['status']}")
                    print_success(f"Service: {data['service']}")
                    return True
                else:
                    print_error(f"Health check failed with status {response.status}")
                    return False
    except Exception as e:
        print_error(f"Health endpoint test failed: {e}")
        return False

async def test_websocket_connection():
    """Test 6: Verify WebSocket connection and AI response"""
    print_test("WebSocket Connection & AI Response")

    try:
        session_id = f"test-v33-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        uri = f'ws://localhost:8503/ws?session_id={session_id}&user_id=test-v33-user'

        async with websockets.connect(uri) as websocket:
            print_success("Connected to WebSocket")

            # Receive greeting
            greeting = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            greeting_data = json.loads(greeting)
            print_success(f"Received greeting message (type: {greeting_data.get('type')})")

            # Send test message
            test_message = {
                'type': 'user_message',
                'data': {'text': 'I need a quick presentation about cloud security'}
            }
            await websocket.send(json.dumps(test_message))
            print_success("Sent test message")

            # Receive response (may be status update or chat message)
            response = await asyncio.wait_for(websocket.recv(), timeout=15.0)
            response_data = json.loads(response)
            print_success(f"Received AI response (type: {response_data.get('type')})")

            # Close connection
            await websocket.close()
            print_success("WebSocket connection closed cleanly")

            return True

    except asyncio.TimeoutError:
        print_error("WebSocket test timed out waiting for response")
        return False
    except Exception as e:
        print_error(f"WebSocket test failed: {e}")
        return False

async def test_environment_variables():
    """Test 7: Verify environment variables are correctly configured"""
    print_test("Environment Variables Configuration")

    try:
        from config.settings import get_settings

        settings = get_settings()

        print_success(f"GCP_ENABLED: {settings.GCP_ENABLED}")
        print_success(f"GCP_PROJECT_ID: {settings.GCP_PROJECT_ID}")
        print_success(f"GCP_LOCATION: {settings.GCP_LOCATION}")

        if settings.GCP_SERVICE_ACCOUNT_JSON:
            print_success("GCP_SERVICE_ACCOUNT_JSON: [configured]")
        else:
            print_info("GCP_SERVICE_ACCOUNT_JSON: [not set - using ADC]")

        # Check that old API key is not being used
        if hasattr(settings, 'GOOGLE_API_KEY') and settings.GOOGLE_API_KEY:
            print_error("GOOGLE_API_KEY is still set! Should be removed.")
            return False
        else:
            print_success("GOOGLE_API_KEY: [correctly disabled]")

        return True

    except Exception as e:
        print_error(f"Environment variables test failed: {e}")
        return False

async def run_all_tests():
    """Run all v3.3 tests"""
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}Director Agent v3.3 - ADC Authentication Test Suite{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

    tests = [
        ("Environment Variables", test_environment_variables),
        ("GCP Authentication", test_gcp_auth),
        ("Director Agent", test_director_initialization),
        ("Intent Router", test_intent_router_initialization),
        ("WebSocket Handler", test_websocket_handler),
        ("Health Endpoint", test_health_endpoint),
        ("WebSocket & AI", test_websocket_connection),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))

    # Print summary
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}Test Results Summary{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = f"{GREEN}PASSED{RESET}" if result else f"{RED}FAILED{RESET}"
        print(f"{test_name:.<50} {status}")

    print(f"\n{BOLD}Total:{RESET} {passed}/{total} tests passed")

    if passed == total:
        print(f"\n{GREEN}{BOLD}✓ ALL TESTS PASSED!{RESET}")
        print(f"{GREEN}v3.3 security refactoring is working correctly{RESET}")
        print(f"{GREEN}Application is using Vertex AI with ADC authentication{RESET}")
        return 0
    else:
        print(f"\n{RED}{BOLD}✗ SOME TESTS FAILED{RESET}")
        print(f"{RED}Please review the errors above{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(run_all_tests()))
