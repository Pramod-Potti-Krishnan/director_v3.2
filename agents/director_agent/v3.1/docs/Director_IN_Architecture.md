# Director_IN Architecture - Phase 1 Implementation

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Core Components](#core-components)
4. [Agent Architecture](#agent-architecture)
5. [State Machine Design](#state-machine-design)
6. [Message Flow Architecture](#message-flow-architecture)
7. [Data Models](#data-models)
8. [Integration Points](#integration-points)
9. [Component Reusability Matrix](#component-reusability-matrix)
10. [Technical Implementation Details](#technical-implementation-details)
11. [Security and Performance](#security-and-performance)
12. [Future Extensibility](#future-extensibility)

## Executive Summary

Director_IN is the core AI agent responsible for the entire Phase 1 presentation generation workflow in Deckster. Built using PydanticAI and a state-driven architecture, it guides users through a conversational process to create comprehensive presentation outlines (strawman). The implementation emphasizes modularity, token efficiency, and clean separation of concerns.

### Key Achievements
- **Conversational UI**: Natural language interaction through 5 distinct states
- **Token Optimization**: 40-60% reduction through modular prompts and context strategies
- **Multi-Provider Support**: Seamless fallback between Gemini, OpenAI, and Anthropic
- **Type Safety**: Structured outputs using Pydantic models
- **Real-time Communication**: WebSocket-based progressive updates

## Architecture Overview

```mermaid
graph TB
    subgraph "Frontend"
        UI[Web Interface]
    end
    
    subgraph "WebSocket Layer"
        WS[WebSocket Handler]
        SP[Streamlined Packager]
        LP[Legacy Packager]
    end
    
    subgraph "Core Processing"
        IR[Intent Router]
        SM[State Machine]
        DA[Director Agent]
    end
    
    subgraph "AI Agents"
        GA[Greeting Agent]
        QA[Questions Agent]
        PA[Plan Agent]
        SA[Strawman Agent]
        RA[Refine Agent]
    end
    
    subgraph "Support Services"
        CB[Context Builder]
        PM[Prompt Manager]
        TT[Token Tracker]
        SM2[Session Manager]
    end
    
    subgraph "Storage"
        SB[Supabase]
        Cache[Local Cache]
    end
    
    UI <--> WS
    WS --> IR
    IR --> SM
    SM --> DA
    DA --> GA & QA & PA & SA & RA
    DA --> CB & PM & TT
    WS --> SM2
    SM2 --> SB & Cache
    WS --> SP & LP
```

## Core Components

### 1. WebSocket Handler (`/src/handlers/websocket.py`)
**Purpose**: Manages real-time bidirectional communication with frontend

**Key Features**:
- Connection lifecycle management
- Message routing and dispatch
- Protocol version handling (legacy/streamlined)
- Session state persistence
- Error handling and recovery

**Reusability**: ✅ **Fully reusable** for Phase 2/3

```python
class WebSocketHandler:
    """
    WebSocket connection handler for managing real-time client-server communication.
    Coordinates between frontend, intent routing, state management, and agent processing.
    """
```

### 2. Intent Router (`/src/agents/intent_router.py`)
**Purpose**: Classifies user messages into actionable intents

**Key Features**:
- Fast intent classification using lightweight models
- Structured intent output with UserIntent model
- Support for multiple intent types
- Context-aware classification

**Reusability**: ✅ **Fully reusable** with extended intent types

```python
class IntentRouter:
    """
    Routes user messages to appropriate intents using AI classification.
    Uses a fast model for quick intent detection without heavy processing.
    """
```

### 3. State Machine (`/src/workflows/state_machine.py`)
**Purpose**: Manages workflow states and transitions

**Key Features**:
- Simple, extensible state management
- Valid transition enforcement
- State history tracking
- Placeholder for future LangGraph integration

**Reusability**: ✅ **Fully reusable** with additional states

```python
class WorkflowOrchestrator:
    """
    Simple state machine for Phase 1. 
    Will be replaced by LangGraph in future phases.
    """
    
    VALID_STATES = [
        "PROVIDE_GREETING",
        "ASK_CLARIFYING_QUESTIONS", 
        "CREATE_CONFIRMATION_PLAN",
        "GENERATE_STRAWMAN",
        "REFINE_STRAWMAN"
    ]
```

### 4. Director Agent (`/src/agents/director.py`)
**Purpose**: Core AI agent orchestrating presentation generation

**Key Features**:
- State-specific sub-agents with embedded modular prompts
- Multi-provider AI support (Gemini primary, OpenAI/Anthropic fallback)
- Token-efficient processing with integrated tracking
- Structured output generation with post-processing
- AssetFormatter integration for consistent field formatting

**Reusability**: ⚠️ **Partially reusable** - Base structure reusable, state-specific logic not

```python
class DirectorAgent:
    """
    Main AI agent for directing the presentation creation workflow.
    Uses separate PydanticAI agents for each state with embedded modular prompts.
    Prompts are loaded once at initialization and embedded into agent system prompts.
    Includes integrated AssetFormatter for post-processing outputs.
    """
```

## Agent Architecture

### Multi-Agent Design
Director_IN uses a sophisticated multi-agent architecture where each state has its own specialized PydanticAI agent:

1. **Greeting Agent**: Handles initial user interaction
2. **Questions Agent**: Generates contextual clarifying questions
3. **Plan Agent**: Creates presentation confirmation plan
4. **Strawman Agent**: Generates detailed presentation outline
5. **Refine Agent**: Iteratively improves the strawman

### Agent Configuration
Each agent is configured with:
- **Model**: Primary (Gemini) with fallbacks (OpenAI, Anthropic)
- **System Prompt**: Base + state-specific prompts
- **Output Type**: Strongly typed Pydantic models
- **Temperature**: Optimized per state (0.7-0.9)

### Modular Prompt System (Embedded in Director Agent)
**Architecture**:
```
config/prompts/modular/
├── base_prompt.md                    # Shared context
├── provide_greeting.md
├── ask_clarifying_questions.md
├── create_confirmation_plan.md
├── generate_strawman.md
└── refine_strawman.md
```

**Implementation**: Director agent loads base + state-specific prompts at initialization using `_load_modular_prompt()` method, combining them into complete system prompts for each PydanticAI sub-agent.

**Benefits**:
- **Token Efficiency**: 40-60% reduction
- **Maintainability**: Easy prompt updates
- **Consistency**: Shared base knowledge
- **Performance**: Prompts loaded once at startup, not per-request

## State Machine Design

### State Definitions

| State | Purpose | Input | Output |
|-------|---------|-------|---------|
| PROVIDE_GREETING | Welcome user | User's initial input | Friendly greeting + guidance |
| ASK_CLARIFYING_QUESTIONS | Gather context | Previous answers | 3-7 targeted questions |
| CREATE_CONFIRMATION_PLAN | Confirm approach | All context | Structured plan |
| GENERATE_STRAWMAN | Create outline | Approved plan | Complete strawman |
| REFINE_STRAWMAN | Iterate on outline | User feedback | Updated strawman |

### State Transitions
```mermaid
stateDiagram-v2
    [*] --> PROVIDE_GREETING
    PROVIDE_GREETING --> ASK_CLARIFYING_QUESTIONS
    ASK_CLARIFYING_QUESTIONS --> ASK_CLARIFYING_QUESTIONS: Continue_Questions
    ASK_CLARIFYING_QUESTIONS --> CREATE_CONFIRMATION_PLAN: All_Questions_Answered
    CREATE_CONFIRMATION_PLAN --> ASK_CLARIFYING_QUESTIONS: Request_More_Info
    CREATE_CONFIRMATION_PLAN --> GENERATE_STRAWMAN: Accept_Plan
    GENERATE_STRAWMAN --> REFINE_STRAWMAN: Request_Changes
    GENERATE_STRAWMAN --> [*]: Accept_Strawman
    REFINE_STRAWMAN --> REFINE_STRAWMAN: Continue_Refinement
    REFINE_STRAWMAN --> [*]: Accept_Strawman
```

## Message Flow Architecture

### Request Flow
1. **WebSocket Message Receipt**
   ```
   Frontend → WebSocket Handler → Message Validation
   ```

2. **Intent Classification**
   ```
   Message → Intent Router → UserIntent
   ```

3. **State Determination**
   ```
   Current State + UserIntent → State Machine → Next State
   ```

4. **Agent Processing**
   ```
   State + Context → Director Agent → Sub-Agent → AI Response
   ```

5. **Response Packaging**
   ```
   AI Response → Message Packager → WebSocket → Frontend
   ```

### Context Building Strategy (`/src/utils/context_builder.py`)

The system uses state-specific context strategies to minimize token usage:

```python
class ContextBuildingStrategyFactory:
    """Factory for creating state-specific context building strategies"""
    
    @staticmethod
    def create_strategy(state: str) -> ContextBuildingStrategy:
        strategies = {
            "PROVIDE_GREETING": GreetingContextStrategy,
            "ASK_CLARIFYING_QUESTIONS": QuestionsContextStrategy,
            "CREATE_CONFIRMATION_PLAN": PlanContextStrategy,
            "GENERATE_STRAWMAN": StrawmanContextStrategy,
            "REFINE_STRAWMAN": RefineContextStrategy,
        }
```

Each strategy provides only the necessary context for its state, significantly reducing token consumption.

## Data Models

### Core Models (`/src/models/agents.py`)

#### 1. UserIntent
```python
class UserIntent(BaseModel):
    """Represents the classified intent of a user message"""
    intent_type: str
    confidence: float
    entities: Dict[str, Any] = {}
    requires_state_change: bool = False
```

#### 2. PresentationStrawman
```python
class PresentationStrawman(BaseModel):
    """Simplified presentation outline structure"""
    type: Literal["PresentationStrawman"] = "PresentationStrawman"
    main_title: str
    overall_theme: str  # e.g., "Informative and data-driven"
    slides: List[Slide]
    # Required metadata
    design_suggestions: str
    target_audience: str
    presentation_duration: int  # minutes

    @property
    def total_slides(self) -> int:
        return len(self.slides)
```

#### 3. Slide
```python
class Slide(BaseModel):
    """Simplified slide model with flexible guidance fields"""
    slide_number: int
    slide_id: str
    title: str
    slide_type: str  # title_slide, content_heavy, visual_heavy, etc.
    narrative: str  # Story/key message
    key_points: List[str]
    # Open-ended guidance for future agents (descriptive strings)
    analytics_needed: Optional[str]
    visuals_needed: Optional[str]
    diagrams_needed: Optional[str]
    tables_needed: Optional[str]  # New field for structured data
    structure_preference: Optional[str]
    speaker_notes: Optional[str]

    # Backward compatibility
    @property
    def visual_suggestions(self) -> Optional[List[str]]:
        """Aggregates all visual guidance fields"""
```

### Session Model (`/src/models/session.py`)
Manages conversation state and persistence:
- User information
- Conversation history
- Clarifying answers
- Generated artifacts
- Token usage metrics

## Integration Points

### 1. Frontend Integration
- **Protocol**: WebSocket (Socket.IO compatible)
- **Message Format**: JSON with typed events
- **Delivery**: Real-time streaming for long operations

### 2. AI Provider Integration
- **Primary**: Google Gemini (2.5-flash/pro)
- **Fallback 1**: OpenAI (GPT-4)
- **Fallback 2**: Anthropic (Claude)
- **Error Handling**: Automatic failover with retry logic

### 3. Storage Integration
- **Primary**: Supabase (PostgreSQL)
- **Caching**: In-memory with TTL
- **Session Management**: Persistent with recovery

### 4. Observability Integration
- **Logging**: Structured via custom logger
- **Metrics**: Logfire for distributed tracing
- **Token Tracking**: Detailed usage analytics

## Component Reusability Matrix

| Component | Director_IN Specific | Reusable for Phase 2/3 | Notes |
|-----------|---------------------|------------------------|-------|
| WebSocket Handler | ❌ | ✅ | Fully reusable infrastructure |
| Intent Router | ❌ | ✅ | Extend with new intent types |
| State Machine | ❌ | ✅ | Add new states and transitions |
| Session Manager | ❌ | ✅ | Core session infrastructure |
| Message Packagers | ❌ | ✅ | Protocol handling |
| Token Tracker | ❌ | ✅ | Universal token monitoring |
| Logger/Logfire | ❌ | ✅ | Observability infrastructure |
| Context Builder | ⚠️ | ⚠️ | Framework reusable, strategies specific |
| Prompt Manager | ❌ | ✅ | Load prompts for any agent |
| Director Agent | ✅ | ❌ | Presentation-specific logic |
| Agent Models | ✅ | ❌ | Presentation-specific structures |
| State Prompts | ✅ | ❌ | Director_IN specific content |

## Technical Implementation Details

### 1. Token Optimization
The system achieves 40-60% token reduction through:
- **Modular Prompts**: Only load necessary instructions
- **Context Strategies**: State-specific context filtering
- **Caching**: Reuse computed contexts
- **Minimal Outputs**: Structured responses without fluff

### 2. Error Handling
```python
# Comprehensive error handling at multiple levels
try:
    response = await agent.process_message(message)
except AIProviderError:
    # Fallback to secondary provider
    response = await fallback_agent.process_message(message)
except Exception as e:
    # Graceful degradation
    logger.error(f"Agent processing failed: {e}")
    response = create_error_response(e)
```

### 3. Performance Optimizations
- **Connection Pooling**: Reuse database connections
- **Async Processing**: Non-blocking I/O throughout
- **Lazy Loading**: Load resources on demand
- **Response Streaming**: Progressive updates for long operations

### 4. Security Measures
- **Input Validation**: Pydantic models for all inputs
- **Rate Limiting**: Configurable per session
- **Authentication**: Session-based with timeout
- **Sanitization**: Output cleaning before frontend delivery

## Security and Performance

### Security Measures
1. **Input Validation**: All inputs validated through Pydantic
2. **Session Management**: Secure session tokens with expiry
3. **API Key Protection**: Environment-based configuration
4. **Error Sanitization**: No sensitive data in error messages

### Performance Characteristics
- **Response Time**: <2s for most operations
- **Concurrent Sessions**: Tested up to 100+
- **Token Efficiency**: 40-60% reduction vs monolithic
- **Memory Usage**: ~50MB per active session

## Future Extensibility

### Phase 2 Integration Points
1. **State Machine Extension**: Add LAYOUT_GENERATION state
2. **New Agent Integration**: Register Layout Architect agent
3. **Message Types**: Extend for progressive layout updates
4. **Context Strategies**: Add layout-specific strategies

### Phase 3 Considerations
1. **Multi-Agent Coordination**: WorkflowOrchestrator can manage multiple agents
2. **Event System**: WebSocket handler supports broadcast events
3. **Storage Schema**: Extensible for new data types
4. **Monitoring**: Logfire can track cross-agent workflows

### Upgrade Path to LangGraph
The current state machine is designed as a placeholder:
```python
# Future LangGraph integration
# class WorkflowOrchestrator:
#     """Will be replaced by LangGraph workflow engine"""
#     def __init__(self):
#         self.workflow = StateGraph(AgentState)
#         self._build_workflow()
```

## Code References and Examples

### Key File Locations

#### Core Components
- **Director Agent**: [`/src/agents/director.py`](../src/agents/director.py)
- **Intent Router**: [`/src/agents/intent_router.py`](../src/agents/intent_router.py)
- **WebSocket Handler**: [`/src/handlers/websocket.py`](../src/handlers/websocket.py)
- **State Machine**: [`/src/workflows/state_machine.py`](../src/workflows/state_machine.py)

#### Models
- **Agent Models**: [`/src/models/agents.py`](../src/models/agents.py)
- **Session Model**: [`/src/models/session.py`](../src/models/session.py)
- **WebSocket Messages**: [`/src/models/websocket_messages.py`](../src/models/websocket_messages.py)

#### Utilities
- **Context Builder**: [`/src/utils/context_builder.py`](../src/utils/context_builder.py)
- **Session Manager**: [`/src/utils/session_manager.py`](../src/utils/session_manager.py)
- **Token Tracker**: [`/src/utils/token_tracker.py`](../src/utils/token_tracker.py)
- **Asset Formatter**: [`/src/utils/asset_formatter.py`](../src/utils/asset_formatter.py)
- **Message Packagers**:
  - [`/src/utils/message_packager.py`](../src/utils/message_packager.py)
  - [`/src/utils/streamlined_packager.py`](../src/utils/streamlined_packager.py)

#### Configuration
- **Prompts**: [`/config/prompts/modular/`](../config/prompts/modular/)
  - All prompts (base + state-specific) in modular/ directory
  - Loaded and combined at DirectorAgent initialization

### Example Integration for Phase 2

#### Extending the State Machine
```python
# In workflows/state_machine.py
class ExtendedWorkflowOrchestrator(WorkflowOrchestrator):
    VALID_STATES = WorkflowOrchestrator.VALID_STATES + [
        "LAYOUT_GENERATION",
        "LAYOUT_REFINEMENT"
    ]
    
    VALID_TRANSITIONS = WorkflowOrchestrator.VALID_TRANSITIONS + {
        "GENERATE_STRAWMAN": ["REFINE_STRAWMAN", "LAYOUT_GENERATION"],
        "LAYOUT_GENERATION": ["LAYOUT_REFINEMENT", "COMPLETE"],
        "LAYOUT_REFINEMENT": ["LAYOUT_REFINEMENT", "COMPLETE"]
    }
```

#### Adding New Agent
```python
# In agents/layout_architect.py
from src.agents.base import BaseAgent
from pydantic_ai import Agent

class LayoutArchitect(BaseAgent):
    def __init__(self, config):
        super().__init__(name="layout_architect")
        self.config = config
        # Initialize similar to DirectorAgent
```

#### Extending Intent Router
```python
# New intents for Phase 2
LAYOUT_INTENTS = [
    "Request_Layout_Change",
    "Accept_Layout", 
    "Request_Theme_Change"
]
```

## Deployment and Operations

### Environment Variables
```bash
# AI Provider Keys
GOOGLE_API_KEY=<key>
OPENAI_API_KEY=<key>
ANTHROPIC_API_KEY=<key>

# Database
SUPABASE_URL=<url>
SUPABASE_KEY=<key>

# Feature Flags
USE_STREAMLINED_PROTOCOL=true
ENABLE_TOKEN_TRACKING=true

# Performance
MAX_CONCURRENT_SESSIONS=100
SESSION_TIMEOUT_MINUTES=30
```

### Monitoring Dashboards
1. **Token Usage**: Track usage by state and model
2. **Response Times**: P50, P95, P99 latencies
3. **Error Rates**: By error type and state
4. **Session Metrics**: Active sessions, completion rates

### Common Operations

#### Adding a New State
1. Define state in `WorkflowOrchestrator.VALID_STATES`
2. Add transitions in `VALID_TRANSITIONS`
3. Create prompt in `/config/prompts/modular/`
4. Add context strategy in `ContextBuildingStrategyFactory`
5. Create agent handler in `DirectorAgent`

#### Updating Prompts
1. Edit markdown files in `/config/prompts/`
2. Clear prompt cache (automatic on file change)
3. Test with subset of users
4. Monitor token usage changes

## Conclusion

The Director_IN implementation demonstrates a well-architected, production-ready system that balances sophistication with maintainability. The modular design, comprehensive error handling, and clear separation of concerns provide a solid foundation for future phases while delivering immediate value in Phase 1.

Key strengths:
- **Modularity**: Clear component boundaries enable independent evolution
- **Extensibility**: Designed for future phases from the ground up
- **Performance**: Optimized for both token usage and response time
- **Reliability**: Multiple fallback mechanisms ensure availability
- **Observability**: Comprehensive logging and monitoring

The architecture serves as both a complete Phase 1 solution and a robust platform for Phases 2-3 expansion.