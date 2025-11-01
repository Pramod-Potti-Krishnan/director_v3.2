# Director Agent - AI Presentation Assistant

## Version 3.3 - Security Enhanced

**🔐 MAJOR SECURITY UPDATE**: v3.3 replaces static API keys with Application Default Credentials (ADC) for enhanced security.

**Key Changes:**
- ✅ No more API keys in environment variables
- ✅ Uses rotatable service accounts (production)
- ✅ Full GCP audit logging
- ✅ Fine-grained IAM permissions
- ⚠️ **Breaking change**: Requires new setup (see below)

**Documentation:**
- 📖 [SECURITY.md](./SECURITY.md) - Complete security guide and setup
- 📖 [V3.3_MIGRATION_GUIDE.md](./V3.3_MIGRATION_GUIDE.md) - Migration from v3.1
- 📖 [V3.3_CHANGELOG.md](./V3.3_CHANGELOG.md) - What's new in v3.3

---

## Overview

The Director Agent is a standalone implementation of the Phase 1 architecture for an AI-powered presentation assistant. It features a state-driven architecture with intent-based routing, providing a natural conversational flow for creating presentations.

## Architecture

This agent implements a clean Phase 1 architecture with:
- **State-Driven Workflow**: Clear progression through presentation creation states
- **Intent-Based Routing**: Natural language understanding for user interactions
- **WebSocket Communication**: Real-time bidirectional messaging
- **Modular Prompt System**: Maintainable and versioned prompts
- **v3.3 Security**: Application Default Credentials (ADC) for Google Cloud
- **Multi-Model Support**: Works with Google Gemini (via Vertex AI), OpenAI, and Anthropic

## Core Components

### 1. Director Agent (`src/agents/director.py`)
- Manages presentation creation workflow
- Handles state-specific processing
- Implements modular prompt loading

### 2. Intent Router (`src/agents/intent_router.py`)
- Classifies user messages into specific intents
- Maps intents to state transitions
- Enables natural conversation flow

### 3. WebSocket Handler (`src/handlers/websocket.py`)
- Manages WebSocket connections
- Routes messages based on intent
- Implements streamlined protocol

### 4. Session Manager (`src/utils/session_manager.py`)
- Manages session state and persistence
- Handles conversation history
- Integrates with Supabase storage

## States and Flow

The agent progresses through these states:

1. **PROVIDE_GREETING** → Initial welcome state
2. **ASK_CLARIFYING_QUESTIONS** → Gather presentation requirements
3. **CREATE_CONFIRMATION_PLAN** → Propose presentation structure
4. **GENERATE_STRAWMAN** → Create initial presentation outline
5. **REFINE_STRAWMAN** → Iteratively improve the presentation

## Setup Instructions

### Prerequisites

- Python 3.9+
- Supabase account and project
- **v3.3 NEW**: gcloud CLI (for local development) OR service account JSON (for production)

### v3.3 Authentication Setup

**⚠️ v3.3 uses Application Default Credentials instead of API keys**

#### Local Development
```bash
# Install gcloud CLI
brew install google-cloud-sdk  # macOS
# Or visit: https://cloud.google.com/sdk/docs/install

# Authenticate with Google Cloud
gcloud auth application-default login

# Set project
gcloud config set project deckster-xyz
```

#### Railway Production
1. Create service account in GCP Console
2. Download JSON key file
3. Add `GCP_SERVICE_ACCOUNT_JSON` to Railway environment variables
4. See [SECURITY.md](./SECURITY.md) for detailed instructions

### Installation

1. **Clone or copy this directory**:
```bash
cd agents/director_agent/v3.3
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
cp .env.example .env
# v3.3: No GOOGLE_API_KEY needed!
# Edit .env for Supabase and other services
```

5. **Set up Supabase**:
   - Create a new Supabase project at https://supabase.com
   - Create the sessions table using the SQL below
   - Copy your project URL and anon key to .env

### Supabase Setup

Run this SQL in your Supabase SQL editor:

```sql
CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  current_state TEXT NOT NULL DEFAULT 'PROVIDE_GREETING',
  conversation_history JSONB DEFAULT '[]'::jsonb,
  user_initial_request TEXT,
  clarifying_answers JSONB,
  confirmation_plan JSONB,
  presentation_strawman JSONB,
  refinement_feedback TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_created_at ON sessions(created_at);

-- Enable Row Level Security (optional but recommended)
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
```

## Running the Agent

### Development Mode

```bash
python main.py
```

The server will start on `http://localhost:8000`

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t director-agent .
docker run -p 8000:8000 --env-file .env director-agent
```

## API Endpoints

### WebSocket Connection
```
ws://localhost:8000/ws?session_id={session_id}&user_id={user_id}
```

### REST Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /test-handler` - Test handler initialization

## WebSocket Message Protocol

### Client → Server
```json
{
  "type": "user_message",
  "data": {
    "text": "I need a presentation about AI"
  }
}
```

### Server → Client (Streamlined Protocol)

#### Chat Message
```json
{
  "type": "chat_message",
  "data": {
    "text": "What's the target audience for your presentation?",
    "format": "markdown"
  }
}
```

#### Action Request
```json
{
  "type": "action_request",
  "data": {
    "prompt_text": "Should I proceed with this plan?",
    "actions": [
      {
        "label": "Accept",
        "value": "accept",
        "primary": true
      },
      {
        "label": "Revise",
        "value": "revise",
        "primary": false
      }
    ]
  }
}
```

#### Slide Update
```json
{
  "type": "slide_update",
  "data": {
    "operation": "full_update",
    "metadata": {
      "title": "AI Presentation",
      "total_slides": 10
    },
    "slides": [...]
  }
}
```

## Configuration Options

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SUPABASE_URL` | Supabase project URL | Yes | - |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | Yes | - |
| `GOOGLE_API_KEY` | Google Gemini API key | One of AI keys required | - |
| `OPENAI_API_KEY` | OpenAI API key | One of AI keys required | - |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | One of AI keys required | - |
| `PORT` | Server port | No | 8000 |
| `DEBUG` | Debug mode | No | false |
| `USE_STREAMLINED_PROTOCOL` | Use streamlined WebSocket protocol | No | true |
| `STREAMLINED_PROTOCOL_PERCENTAGE` | A/B testing percentage | No | 100 |

## Testing

### Manual Testing

1. Connect to WebSocket:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws?session_id=test-123&user_id=user-456');

ws.onopen = () => {
  console.log('Connected');
};

ws.onmessage = (event) => {
  console.log('Received:', JSON.parse(event.data));
};

// Send a message
ws.send(JSON.stringify({
  type: 'user_message',
  data: { text: 'I need a presentation about quantum computing' }
}));
```

2. Use the test endpoint:
```bash
curl http://localhost:8000/test-handler
```

### Health Check
```bash
curl http://localhost:8000/health
```

## Troubleshooting

### Common Issues

1. **"No AI API key configured"**
   - Ensure at least one AI service API key is set in `.env`
   - Google Gemini is recommended for best performance

2. **"Supabase configuration missing"**
   - Add your Supabase project URL and anon key to `.env`
   - Ensure the sessions table is created in your database

3. **WebSocket connection fails**
   - Check that both `session_id` and `user_id` are provided
   - Verify the server is running on the correct port

4. **Import errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version is 3.9 or higher

## Development

### Project Structure
```
director_agent/
├── main.py                 # FastAPI application entry
├── config/
│   ├── settings.py        # Configuration management
│   └── prompts/
│       └── modular/       # State-specific prompts
├── src/
│   ├── agents/           # Core agents
│   ├── handlers/         # WebSocket handler
│   ├── models/          # Pydantic models
│   ├── storage/         # Database integration
│   ├── utils/           # Utility functions
│   └── workflows/       # State machine
├── requirements.txt      # Dependencies
├── .env.example         # Environment template
└── README.md           # This file
```

### Adding New States

1. Add the state to the workflow in `src/workflows/state_machine.py`
2. Create a new prompt in `config/prompts/modular/`
3. Update the Director Agent to handle the new state
4. Add intent mappings in the Intent Router

### Customizing Prompts

Prompts are stored in `config/prompts/modular/`:
- `base_prompt.md` - Shared base instructions
- State-specific prompts for each workflow state

## License

This implementation is based on the Phase 1 Architecture design and is intended for educational and development purposes.

## Support

For issues or questions about this implementation:
1. Check the troubleshooting section above
2. Review the architecture documentation
3. Ensure all dependencies are correctly installed
4. Verify your API keys and Supabase configuration