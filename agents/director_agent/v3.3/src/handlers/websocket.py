"""
WebSocket handler for Director Agent.
"""
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from fastapi import WebSocket

from src.utils.logger import setup_logger
from src.agents.intent_router import IntentRouter
from src.agents.director import DirectorAgent
from src.utils.session_manager import SessionManager
from src.utils.message_packager import MessagePackager
from src.utils.streamlined_packager import StreamlinedMessagePackager
from src.storage.supabase import get_supabase_client
from src.models.agents import UserIntent, StateContext
from src.models.websocket_messages import StreamlinedMessage
from src.workflows.state_machine import WorkflowOrchestrator
from config.settings import get_settings

logger = setup_logger(__name__)


class WebSocketHandler:
    """Handles WebSocket connections and message routing."""

    def __init__(self):
        """Initialize handler components."""
        logger.info("Initializing WebSocketHandler...")

        # Get settings
        self.settings = get_settings()
        logger.info(f"Settings loaded: streamlined={self.settings.USE_STREAMLINED_PROTOCOL}, percentage={self.settings.STREAMLINED_PROTOCOL_PERCENTAGE}")

        # Initialize Supabase client
        try:
            self.supabase = get_supabase_client()
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}", exc_info=True)
            raise

        # Initialize components
        logger.info("Initializing handler components...")
        self.intent_router = IntentRouter()
        self.director = DirectorAgent()
        self.sessions = SessionManager(self.supabase)
        self.packager = MessagePackager()
        self.streamlined_packager = StreamlinedMessagePackager()
        self.workflow = WorkflowOrchestrator()

        logger.info("WebSocketHandler initialized successfully with streamlined protocol: %s",
                   self.settings.USE_STREAMLINED_PROTOCOL)

    def _should_use_streamlined(self, session_id: str) -> bool:
        """
        Determine if this session should use streamlined protocol.

        Args:
            session_id: Session identifier

        Returns:
            True if streamlined protocol should be used
        """
        # If feature is disabled globally, always use old protocol
        if not self.settings.USE_STREAMLINED_PROTOCOL:
            return False

        # If percentage is 100, always use streamlined
        if self.settings.STREAMLINED_PROTOCOL_PERCENTAGE >= 100:
            return True

        # If percentage is 0, never use streamlined
        if self.settings.STREAMLINED_PROTOCOL_PERCENTAGE <= 0:
            return False

        # Use session ID for consistent A/B testing
        # Hash the session ID to get a number between 0-99
        hash_value = hash(session_id) % 100
        return hash_value < self.settings.STREAMLINED_PROTOCOL_PERCENTAGE

    async def _send_messages(self, websocket: WebSocket, messages: List[StreamlinedMessage]):
        """
        Send multiple streamlined messages with small delays.

        Args:
            websocket: WebSocket connection
            messages: List of streamlined messages to send
        """
        for i, message in enumerate(messages):
            # Use model_dump with mode='json' for proper serialization
            message_data = message.model_dump(mode='json')
            logger.debug(f"Sending message {i+1}/{len(messages)}: {message_data.get('type')}")
            await websocket.send_json(message_data)

            # Add small delay between messages for better UX
            if i < len(messages) - 1:
                await asyncio.sleep(0.1)

    async def handle_connection(self, websocket: WebSocket, session_id: str, user_id: str):
        """
        Handle a WebSocket connection for a session.

        Args:
            websocket: The WebSocket connection
            session_id: The session ID from query parameter
            user_id: The user ID from query parameter
        """
        try:
            # Store user_id and websocket for use in other methods
            self.current_user_id = user_id
            self.current_websocket = websocket
            logger.info(f"Starting handle_connection for user: {user_id}, session: {session_id}")

            # Get or create session with user_id
            try:
                session = await self.sessions.get_or_create(session_id, user_id)
                logger.info(f"Session {session_id} initialized for user {user_id} with state: {session.current_state}")
            except Exception as session_error:
                logger.error(f"Failed to create/get session {session_id} for user {user_id}: {str(session_error)}", exc_info=True)
                raise

            # Send initial greeting if new session
            if session.current_state == "PROVIDE_GREETING":
                logger.info(f"Session {session_id} is new, sending greeting")
                try:
                    await self._send_greeting(websocket, session)
                    logger.info(f"Greeting sent successfully for session {session_id}")
                except Exception as greeting_error:
                    logger.error(f"Failed to send greeting for session {session_id}: {str(greeting_error)}", exc_info=True)
                    raise
            else:
                logger.info(f"Session {session_id} already in state: {session.current_state}, no greeting needed")

            # Main message loop
            logger.info(f"Entering message loop for session {session_id}")
            while True:
                # Receive message
                logger.debug(f"Waiting for message from session {session_id}")
                data = await websocket.receive_text()
                message = json.loads(data)
                logger.info(f"Received message for session {session_id}: type={message.get('type')}, data keys={list(message.get('data', {}).keys())}")

                # Process message
                await self._handle_message(websocket, session, message)

        except Exception as e:
            logger.error(f"Error in WebSocket handler for session {session_id}: {str(e)}", exc_info=True)
            # Don't try to close if already disconnected
            if websocket.client_state.value <= 2:  # CONNECTING=0, CONNECTED=1, DISCONNECTED=2
                try:
                    await websocket.close()
                except Exception:
                    pass  # Ignore errors when closing

    async def _send_greeting(self, websocket: WebSocket, session: Any):
        """Send initial greeting message."""
        logger.info(f"Starting _send_greeting for session {session.id}")
        try:
            use_streamlined = self._should_use_streamlined(session.id)
            logger.info(f"Session {session.id} using streamlined protocol: {use_streamlined}")

            if use_streamlined:
                # Use streamlined protocol
                messages = self.streamlined_packager.package_messages(
                    session_id=session.id,
                    state="PROVIDE_GREETING",
                    agent_output=None,  # Greeting doesn't need agent output
                    context=None
                )
                logger.info(f"Packaged {len(messages)} messages for greeting")
                await self._send_messages(websocket, messages)
            else:
                # Use legacy protocol
                state_context = StateContext(
                    current_state="PROVIDE_GREETING",
                    user_intent=None,  # No intent for greeting
                    conversation_history=[],
                    session_data={}
                )

                # Get greeting from director
                greeting = await self.director.process(state_context)

                # Package and send
                message = self.packager.package(
                    response=greeting,
                    session_id=session.id,
                    current_state="PROVIDE_GREETING"
                )

                await websocket.send_json(message)

            logger.info(f"Sent greeting for session {session.id}")

        except Exception as e:
            logger.error(f"Error sending greeting: {str(e)}", exc_info=True)
            raise

    async def _handle_message(self, websocket: WebSocket, session: Any, message: Dict[str, Any]):
        """
        Handle an incoming message.

        Args:
            websocket: The WebSocket connection
            session: The session object
            message: The incoming message
        """
        try:
            # Validate we have user_id
            if not hasattr(self, 'current_user_id') or not self.current_user_id:
                raise RuntimeError("User ID not set in handler - connection not properly initialized")

            # Extract user input
            user_input = message.get('data', {}).get('text', '')
            logger.info(f"Processing user input in state {session.current_state}")

            # STEP 1: Classify user intent
            intent = await self.intent_router.classify(
                user_message=user_input,
                context={
                    'current_state': session.current_state,
                    'recent_history': session.conversation_history[-3:] if session.conversation_history else []
                }
            )
            logger.info(f"Classified intent: {intent.intent_type} with confidence {intent.confidence}")

            # STEP 2: Handle intent-based actions
            if intent.intent_type == "Change_Topic":
                # Clear context and reset to questions
                await self.sessions.clear_context(session.id, self.current_user_id)
                session = await self.sessions.get_or_create(session.id, self.current_user_id)
                session.current_state = "ASK_CLARIFYING_QUESTIONS"
                session.user_initial_request = intent.extracted_info or user_input

            elif intent.intent_type == "Submit_Initial_Topic":
                # Save the initial topic
                await self.sessions.save_session_data(
                    session.id,
                    self.current_user_id,
                    'user_initial_request',
                    user_input
                )
                session = await self.sessions.get_or_create(session.id, self.current_user_id)

            elif intent.intent_type == "Submit_Clarification_Answers":
                # Save clarifying answers
                await self.sessions.save_session_data(
                    session.id,
                    self.current_user_id,
                    'clarifying_answers',
                    {
                        "raw_answers": user_input,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                session = await self.sessions.get_or_create(session.id, self.current_user_id)

            # STEP 3: Determine next state
            next_state = self._determine_next_state(
                session.current_state,
                intent,
                None,
                session
            )

            # Update state if it changed
            if next_state != session.current_state:
                logger.info(f"State transition: {session.current_state} -> {next_state}")
                await self.sessions.update_state(session.id, self.current_user_id, next_state)
                session.current_state = next_state

            # STEP 4: Build state context
            state_context = StateContext(
                current_state=session.current_state,
                user_intent=intent,
                conversation_history=session.conversation_history or [],
                session_data={
                    'user_initial_request': session.user_initial_request,
                    'clarifying_answers': session.clarifying_answers,
                    'confirmation_plan': session.confirmation_plan,
                    'presentation_strawman': session.presentation_strawman
                }
            )

            # STEP 4.5: Send pre-generation status for long-running states
            use_streamlined = self._should_use_streamlined(session.id)
            # v3.1: Added CONTENT_GENERATION as a long-running state (text generation takes 5-15s per slide)
            if use_streamlined and session.current_state in ["GENERATE_STRAWMAN", "REFINE_STRAWMAN", "CONTENT_GENERATION"]:
                pre_status = self.streamlined_packager.create_pre_generation_status(
                    session_id=session.id,
                    state=session.current_state
                )
                await websocket.send_json(pre_status.model_dump(mode='json'))
                await asyncio.sleep(0.1)

            # STEP 5: Process with Director
            response = await self.director.process(state_context)

            # Store in history
            await self.sessions.add_to_history(session.id, self.current_user_id, {
                'role': 'user',
                'content': user_input,
                'intent': intent.dict()
            })
            await self.sessions.add_to_history(session.id, self.current_user_id, {
                'role': 'assistant',
                'state': session.current_state,
                'content': response
            })

            # v3.1: Save strawman to session for REFINE_STRAWMAN and CONTENT_GENERATION
            if session.current_state in ["GENERATE_STRAWMAN", "REFINE_STRAWMAN"]:
                strawman_data = None
                presentation_url = None

                # Extract strawman from response (handles both v1.0 and v2.0/v3.1 formats)
                if response.__class__.__name__ == 'PresentationStrawman':
                    # v1.0: Direct strawman object (no deck-builder)
                    strawman_data = response.model_dump()
                    logger.debug("Extracted strawman from PresentationStrawman object")
                elif isinstance(response, dict):
                    if response.get("type") == "presentation_url" and "strawman" in response:
                        # v2.0/v3.1: Hybrid response with embedded strawman
                        strawman_obj = response["strawman"]
                        if hasattr(strawman_obj, 'model_dump'):
                            strawman_data = strawman_obj.model_dump()
                        elif isinstance(strawman_obj, dict):
                            strawman_data = strawman_obj
                        presentation_url = response.get("url")
                        logger.debug(f"Extracted strawman from hybrid response with URL: {presentation_url}")

                # Save strawman data to session
                if strawman_data:
                    await self.sessions.save_session_data(
                        session.id,
                        self.current_user_id,
                        'presentation_strawman',
                        strawman_data
                    )
                    logger.info(f"Saved strawman to session {session.id} ({len(strawman_data.get('slides', []))} slides)")

                    # Also save URL if available
                    if presentation_url:
                        await self.sessions.save_session_data(
                            session.id,
                            self.current_user_id,
                            'presentation_url',
                            presentation_url
                        )
                        logger.info(f"Saved presentation URL to session: {presentation_url}")

                    # Refresh session from DB to ensure cache consistency
                    session = await self.sessions.get_or_create(session.id, self.current_user_id)

            # Package and send response based on protocol
            if use_streamlined:
                # Use streamlined protocol
                messages = self.streamlined_packager.package_messages(
                    session_id=session.id,
                    state=session.current_state,
                    agent_output=response,
                    context=state_context
                )
                await self._send_messages(websocket, messages)
            else:
                # Use legacy protocol
                ws_message = self.packager.package(
                    response=response,
                    session_id=session.id,
                    current_state=session.current_state
                )
                await websocket.send_json(ws_message)

            logger.info(f"Sent response for session {session.id} in state {session.current_state}")

        except Exception as e:
            logger.error(f"Error handling message: {str(e)}", exc_info=True)
            # Send error message based on protocol
            use_streamlined = self._should_use_streamlined(session.id)

            if use_streamlined:
                error_messages = self.streamlined_packager.create_error_message(
                    session_id=session.id,
                    error_text=str(e)
                )
                await self._send_messages(websocket, error_messages)
            else:
                error_message = self.packager.package_error(
                    error=str(e),
                    session_id=session.id
                )
                await websocket.send_json(error_message)

    def _determine_next_state(self, current_state: str, intent: UserIntent,
                             response: Any, session: Any = None) -> str:
        """
        Determine next state based on directional intent.

        v3.1: Updated to support CONTENT_GENERATION state (Stage 6).

        Args:
            current_state: Current workflow state
            intent: Classified user intent
            response: Response from director (can be None for pre-processing)
            session: Session object to check state details

        Returns:
            Next state name
        """
        # Map directional intents to next states
        intent_to_next_state = {
            "Submit_Initial_Topic": "ASK_CLARIFYING_QUESTIONS",
            "Submit_Clarification_Answers": "CREATE_CONFIRMATION_PLAN",
            "Accept_Plan": "GENERATE_STRAWMAN",
            "Reject_Plan": "CREATE_CONFIRMATION_PLAN",  # Loop back
            "Accept_Strawman": "CONTENT_GENERATION",  # v3.1: Go to Stage 6 instead of END
            "Submit_Refinement_Request": "REFINE_STRAWMAN",
            "Change_Topic": "ASK_CLARIFYING_QUESTIONS",  # Reset
            "Change_Parameter": "CREATE_CONFIRMATION_PLAN",  # Regenerate
            "Ask_Help_Or_Question": current_state  # No state change
        }

        # Get next state from mapping
        next_state = intent_to_next_state.get(intent.intent_type, current_state)

        # v3.1: CONTENT_GENERATION is terminal - automatically transitions to END when complete
        # Director returns deck URL with generated content, no user input needed
        if current_state == "CONTENT_GENERATION":
            next_state = "END"

        # Log the transition
        if next_state != current_state:
            logger.info(f"State transition: {current_state} -> {next_state} (intent: {intent.intent_type})")
        else:
            logger.info(f"State remains: {current_state} (intent: {intent.intent_type})")

        return next_state