#!/usr/bin/env python3
"""
Quick health check for Railway deployment.
"""
import asyncio
import httpx
import ssl

# Color codes
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'


async def check_railway_deployment():
    """Check if Railway deployment is accessible."""
    base_url = "directorv20-production.up.railway.app"

    print(f"\n{Colors.BOLD}Railway Deployment Health Check{Colors.ENDC}")
    print("=" * 60)
    print(f"Testing: {base_url}\n")

    # Create SSL context that doesn't verify certificates
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
        # Test 1: HTTPS root
        print(f"{Colors.CYAN}1. Testing HTTPS root...{Colors.ENDC}")
        try:
            response = await client.get(f"https://{base_url}/")
            print(f"   Status: {response.status_code}")
            print(f"   {Colors.GREEN}✅ HTTPS accessible{Colors.ENDC}")
            if response.text:
                print(f"   Response preview: {response.text[:200]}")
        except Exception as e:
            print(f"   {Colors.RED}❌ Failed: {e}{Colors.ENDC}")

        # Test 2: Health endpoint
        print(f"\n{Colors.CYAN}2. Testing /health endpoint...{Colors.ENDC}")
        try:
            response = await client.get(f"https://{base_url}/health")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   {Colors.GREEN}✅ Health check passed{Colors.ENDC}")
                print(f"   Response: {response.text}")
            else:
                print(f"   {Colors.YELLOW}⚠️  Non-200 status{Colors.ENDC}")
        except Exception as e:
            print(f"   {Colors.RED}❌ Failed: {e}{Colors.ENDC}")

        # Test 3: Check for docs/API endpoints
        print(f"\n{Colors.CYAN}3. Testing /docs endpoint...{Colors.ENDC}")
        try:
            response = await client.get(f"https://{base_url}/docs")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   {Colors.GREEN}✅ Docs accessible{Colors.ENDC}")
            else:
                print(f"   {Colors.YELLOW}⚠️  Docs not available (status: {response.status_code}){Colors.ENDC}")
        except Exception as e:
            print(f"   {Colors.YELLOW}⚠️  Docs not accessible{Colors.ENDC}")

        # Test 4: Check WebSocket endpoint availability
        print(f"\n{Colors.CYAN}4. Checking WebSocket endpoint info...{Colors.ENDC}")
        print(f"   Expected WebSocket URL: wss://{base_url}/ws")
        print(f"   {Colors.YELLOW}Note: WebSocket cannot be tested via HTTP{Colors.ENDC}")

    print(f"\n{Colors.BOLD}Summary:{Colors.ENDC}")
    print("If all tests above passed, the deployment is running.")
    print("If WebSocket connection still fails, check:")
    print("  • Railway deployment logs")
    print("  • WebSocket endpoint configuration in main.py")
    print("  • Environment variables on Railway")
    print("=" * 60)


async def test_websocket_connection():
    """Try to connect to WebSocket with detailed error info."""
    import websockets

    base_url = "directorv20-production.up.railway.app"
    ws_url = f"wss://{base_url}/ws"

    print(f"\n{Colors.BOLD}WebSocket Connection Test{Colors.ENDC}")
    print("=" * 60)
    print(f"URL: {ws_url}\n")

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        print(f"{Colors.CYAN}Attempting WebSocket connection...{Colors.ENDC}")
        async with websockets.connect(
            ws_url,
            ssl=ssl_context,
            ping_interval=20,
            ping_timeout=10
        ) as websocket:
            print(f"{Colors.GREEN}✅ WebSocket connected successfully!{Colors.ENDC}")
            print(f"Connection state: {websocket.state.name}")

            # Try to receive initial message
            print(f"\n{Colors.CYAN}Waiting for initial message...{Colors.ENDC}")
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"{Colors.GREEN}✅ Received message:{Colors.ENDC}")
                print(f"   {message[:200]}")
            except asyncio.TimeoutError:
                print(f"{Colors.YELLOW}⚠️  No initial message received (timeout){Colors.ENDC}")

    except Exception as e:
        print(f"{Colors.RED}❌ WebSocket connection failed:{Colors.ENDC}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")

        if "502" in str(e):
            print(f"\n{Colors.YELLOW}Diagnosis: HTTP 502 Bad Gateway{Colors.ENDC}")
            print("Possible causes:")
            print("  • Railway service is not running")
            print("  • WebSocket endpoint /ws is not configured")
            print("  • Application crashed or failed to start")
            print("\nNext steps:")
            print("  1. Check Railway deployment logs")
            print("  2. Verify main.py has WebSocket endpoint configured")
            print("  3. Check if service needs to be restarted")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print(f"{Colors.BOLD}Director v2.0 Railway Diagnostics{Colors.ENDC}")
    print("=" * 60)

    asyncio.run(check_railway_deployment())
    print("\n")
    asyncio.run(test_websocket_connection())

    print("\n" + "=" * 60)
    print(f"{Colors.BOLD}Diagnostic Complete{Colors.ENDC}")
    print("=" * 60 + "\n")
