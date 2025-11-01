# Director Agent v3.3 - Quick Start Guide

**🎯 5-Minute Setup for Local Development**

---

## Prerequisites

- Python 3.9+
- gcloud CLI installed (`brew install google-cloud-sdk` on macOS)
- Supabase account (existing project can be reused from v3.1)

---

## Setup Steps

### 1. Authenticate with Google Cloud (2 minutes)

```bash
# Authenticate with your Google account
gcloud auth application-default login

# Set the project
gcloud config set project deckster-xyz
```

**What this does**: Creates secure credentials in `~/.config/gcloud/` that the application will use automatically.

### 2. Configure Environment (1 minute)

Your `.env` file should already be set up with:
```bash
# v3.3: Google Cloud Platform (Vertex AI) - Secure ADC Authentication
GCP_ENABLED=true
GCP_PROJECT_ID=deckster-xyz
GCP_LOCATION=us-central1

# Old API key disabled (v3.3 doesn't need this!)
# GOOGLE_API_KEY=...

# Port
PORT=8503

# Supabase (reuse from v3.1)
SUPABASE_URL=https://eshvntffcestlfuofwhv.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_KEY=eyJhbGci...
```

### 3. Install Dependencies (1 minute)

```bash
cd /Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/director_agent/v3.3

# Activate virtual environment
source venv/bin/activate

# Dependencies already installed, but if needed:
# pip install -r requirements.txt
```

### 4. Start the Application (1 minute)

```bash
python main.py
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8503 (Press CTRL+C to quit)
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 5. Verify It's Working (30 seconds)

```bash
# In a new terminal, test the health endpoint
curl http://localhost:8503/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "service": "director-agent-api",
  "version": "1.0.0",
  "environment": "development"
}
```

---

## Test the Complete System

Run the comprehensive test suite:

```bash
python test_v33_deployment.py
```

**Expected Output**: All 7 tests should pass ✅

---

## Using the API

### WebSocket Connection

Connect to: `ws://localhost:8503/ws?session_id={session_id}&user_id={user_id}`

**Example**:
```javascript
const ws = new WebSocket('ws://localhost:8503/ws?session_id=test-123&user_id=user-456');

ws.onopen = () => {
  console.log('Connected - you will receive a greeting');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};

// Send a message
ws.send(JSON.stringify({
  type: 'user_message',
  data: { text: 'I need a presentation about cloud security' }
}));
```

---

## What's Different from v3.1?

| Feature | v3.1 | v3.3 |
|---------|------|------|
| **Authentication** | API key in .env | gcloud CLI credentials |
| **Security** | API key can leak | Secure, rotatable |
| **Setup** | Paste API key | Run gcloud command |
| **Library** | google-generativeai | google-cloud-aiplatform |
| **API** | Google AI | Vertex AI (GCP) |

**Everything else is the same**: Same API, same workflow, same features.

---

## Troubleshooting

### "Failed to initialize Vertex AI"

**Solution**: Run `gcloud auth application-default login` and authenticate.

### "Address already in use"

**Solution**: Change `PORT` in `.env` to a different port (e.g., 8504, 8505).

### "No AI service configured"

**Solution**: Ensure `GCP_ENABLED=true` in your `.env` file.

### Agent not responding

**Solution**: Check the application logs in the terminal where you ran `python main.py`.

---

## Next Steps

- ✅ Local development is ready to use
- 📖 Read `SECURITY.md` for comprehensive security information
- 🚀 Read `V3.3_MIGRATION_GUIDE.md` for Railway deployment instructions
- 📋 Review `V3.3_TEST_REPORT.md` for detailed test results

---

## Quick Reference

### Start Server
```bash
cd /Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/director_agent/v3.3
source venv/bin/activate
python main.py
```

### Run Tests
```bash
python test_v33_deployment.py
```

### Health Check
```bash
curl http://localhost:8503/health
```

### View Logs
Logs are shown in the terminal where you ran `python main.py`

---

**Status**: ✅ v3.3 is ready for local development
**Next**: Deploy to Railway (see V3.3_MIGRATION_GUIDE.md)
