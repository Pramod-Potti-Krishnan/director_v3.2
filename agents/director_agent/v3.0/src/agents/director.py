"""
Director Agent for managing presentation creation workflow.
"""
import os
import json
from typing import Union, Dict, Any
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings
from pydantic_ai.exceptions import ModelHTTPError
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.providers.google import GoogleProvider
from src.models.agents import (
    StateContext, ClarifyingQuestions, ConfirmationPlan,
    PresentationStrawman, Slide
)
from src.utils.logger import setup_logger
from src.utils.logfire_config import instrument_agents
from src.utils.context_builder import ContextBuilder
from src.utils.token_tracker import TokenTracker
from src.utils.asset_formatter import AssetFormatter
# v2.0: Deck-builder integration
from src.utils.layout_mapper import LayoutMapper
from src.utils.content_transformer import ContentTransformer
from src.utils.deck_builder_client import DeckBuilderClient
# v3.0: Content Orchestrator integration (internal module)
from orchestration import ContentOrchestrator
from orchestration.clients.real_text_client import RealTextClient
from orchestration.clients.real_chart_client import RealChartClient
from orchestration.clients.real_image_client import RealImageClient
from orchestration.clients.real_diagram_client import RealDiagramClient
from src.utils.orchestrator_transformer import (
    OrchestratorTransformer, EnrichedPresentationResponse
)

logger = setup_logger(__name__)


class DirectorAgent:
    """Main agent for handling presentation creation states."""

    def __init__(self):
        """Initialize state-specific agents with embedded modular prompts."""
        # Instrument agents for token tracking
        instrument_agents()

        # Get settings to check which AI service is available
        from config.settings import get_settings
        settings = get_settings()

        # Determine which model to use
        if settings.GOOGLE_API_KEY:
            provider = GoogleProvider(api_key=settings.GOOGLE_API_KEY)
            # Use GoogleModel with explicit settings for better control
            model = GoogleModel('gemini-2.5-flash', provider=provider)
            model_turbo = GoogleModel('gemini-2.5-pro', provider=provider)
        elif settings.OPENAI_API_KEY:
            model = 'openai:gpt-4'
            model_turbo = 'openai:gpt-4-turbo'
        elif settings.ANTHROPIC_API_KEY:
            model = 'anthropic:claude-3-sonnet-20240229'
            model_turbo = 'anthropic:claude-3-opus-20240229'
        else:
            raise ValueError(
                "No AI API key configured. Please set GOOGLE_API_KEY, OPENAI_API_KEY, or "
                "ANTHROPIC_API_KEY in your .env file."
            )

        # Initialize agents with embedded modular prompts
        logger.info("DirectorAgent initializing with embedded modular prompts")
        self._init_agents_with_embedded_prompts(model, model_turbo)

        # Initialize context builder and token tracker
        self.context_builder = ContextBuilder()
        self.token_tracker = TokenTracker()

        # v2.0: Initialize deck-builder components
        self.deck_builder_enabled = getattr(settings, 'DECK_BUILDER_ENABLED', True)
        if self.deck_builder_enabled:
            try:
                self.layout_mapper = LayoutMapper()
                self.content_transformer = ContentTransformer(self.layout_mapper)
                deck_builder_url = getattr(settings, 'DECK_BUILDER_API_URL', 'http://localhost:8000')
                self.deck_builder_client = DeckBuilderClient(deck_builder_url)
                logger.info(f"Deck-builder integration enabled: {deck_builder_url}")
            except Exception as e:
                logger.warning(f"Failed to initialize deck-builder components: {e}")
                logger.warning("Deck-builder integration disabled, will return JSON only")
                self.deck_builder_enabled = False
        else:
            logger.info("Deck-builder integration disabled in settings")

        # v3.0: Initialize Content Orchestrator components (internal module)
        self.content_orchestrator_enabled = getattr(settings, 'CONTENT_ORCHESTRATOR_ENABLED', True)
        if self.content_orchestrator_enabled:
            try:
                # Initialize service clients
                text_client = RealTextClient()
                chart_client = RealChartClient()
                image_client = RealImageClient()
                diagram_client = RealDiagramClient()

                # Initialize internal orchestrator
                self.content_orchestrator = ContentOrchestrator(
                    text_client=text_client,
                    chart_client=chart_client,
                    image_client=image_client,
                    diagram_client=diagram_client
                )
                self.orchestrator_transformer = OrchestratorTransformer()
                logger.info("Content Orchestrator integration enabled (internal module)")
            except Exception as e:
                logger.warning(f"Failed to initialize Content Orchestrator components: {e}")
                logger.warning("Content Orchestrator integration disabled, will use placeholder content")
                self.content_orchestrator_enabled = False
        else:
            logger.info("Content Orchestrator integration disabled in settings")

        logger.info(f"DirectorAgent initialized with {type(model).__name__ if hasattr(model, '__class__') else model} model")

    def _load_modular_prompt(self, state: str) -> str:
        """Load and combine base prompt with state-specific prompt."""
        # Get the base path - this now points to the agent's config directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        prompt_dir = os.path.join(base_dir, 'config', 'prompts', 'modular')

        # Load base prompt
        base_path = os.path.join(prompt_dir, 'base_prompt.md')
        with open(base_path, 'r') as f:
            base_prompt = f.read()

        # Load state-specific prompt
        state_prompt_map = {
            'PROVIDE_GREETING': 'provide_greeting.md',
            'ASK_CLARIFYING_QUESTIONS': 'ask_clarifying_questions.md',
            'CREATE_CONFIRMATION_PLAN': 'create_confirmation_plan.md',
            'GENERATE_STRAWMAN': 'generate_strawman.md',
            'REFINE_STRAWMAN': 'refine_strawman.md',
            'CONTENT_GENERATION': 'generate_content.md'
        }

        state_file = state_prompt_map.get(state)
        if not state_file:
            raise ValueError(f"Unknown state for prompt loading: {state}")

        state_path = os.path.join(prompt_dir, state_file)
        with open(state_path, 'r') as f:
            state_prompt = f.read()

        # Combine prompts
        return f"{base_prompt}\n\n{state_prompt}"

    def _init_agents_with_embedded_prompts(self, model, model_turbo):
        """Initialize agents with embedded modular prompts."""
        # Load state-specific combined prompts (base + state instructions)
        greeting_prompt = self._load_modular_prompt("PROVIDE_GREETING")
        questions_prompt = self._load_modular_prompt("ASK_CLARIFYING_QUESTIONS")
        plan_prompt = self._load_modular_prompt("CREATE_CONFIRMATION_PLAN")
        strawman_prompt = self._load_modular_prompt("GENERATE_STRAWMAN")
        refine_prompt = self._load_modular_prompt("REFINE_STRAWMAN")
        content_prompt = self._load_modular_prompt("CONTENT_GENERATION")

        # Store system prompt tokens for each state (for tracking)
        self.state_prompt_tokens = {
            "PROVIDE_GREETING": len(greeting_prompt) // 4,
            "ASK_CLARIFYING_QUESTIONS": len(questions_prompt) // 4,
            "CREATE_CONFIRMATION_PLAN": len(plan_prompt) // 4,
            "GENERATE_STRAWMAN": len(strawman_prompt) // 4,
            "REFINE_STRAWMAN": len(refine_prompt) // 4,
            "CONTENT_GENERATION": len(content_prompt) // 4
        }

        # Initialize greeting agent
        self.greeting_agent = Agent(
            model=model,
            output_type=str,
            system_prompt=greeting_prompt,
            retries=2,
            name="director_greeting"
        )

        # Initialize questions agent
        self.questions_agent = Agent(
            model=model,
            output_type=ClarifyingQuestions,
            system_prompt=questions_prompt,
            retries=2,
            name="director_questions"
        )

        # Initialize plan agent
        self.plan_agent = Agent(
            model=model,
            output_type=ConfirmationPlan,
            system_prompt=plan_prompt,
            retries=2,
            name="director_plan"
        )

        # Initialize strawman agent
        self.strawman_agent = Agent(
            model=model_turbo,
            output_type=PresentationStrawman,
            system_prompt=strawman_prompt,
            retries=2,
            name="director_strawman"
        )

        # Initialize refine strawman agent
        self.refine_strawman_agent = Agent(
            model=model_turbo,
            output_type=PresentationStrawman,
            system_prompt=refine_prompt,
            retries=2,
            name="director_refine_strawman"
        )

        # v3.0: Initialize content generation agent
        self.content_agent = Agent(
            model=model,
            output_type=str,
            system_prompt=content_prompt,
            retries=2,
            name="director_content_generation"
        )

    async def process(self, state_context: StateContext) -> Union[str, ClarifyingQuestions,
                                                                   ConfirmationPlan, PresentationStrawman]:
        """
        Process based on current state following PydanticAI best practices.

        Args:
            state_context: The current state context

        Returns:
            Response appropriate for the current state
        """
        try:
            session_id = state_context.session_data.get("id", "unknown")

            # Build context for the user prompt (system prompts are already embedded in agents)
            context, user_prompt = self.context_builder.build_context(
                state=state_context.current_state,
                session_data={
                    "id": session_id,
                    "user_initial_request": state_context.session_data.get("user_initial_request"),
                    "clarifying_answers": state_context.session_data.get("clarifying_answers"),
                    "conversation_history": state_context.conversation_history,
                    # v3.0: Pass strawman data for content generation
                    "strawman": state_context.session_data.get("strawman"),
                    "presentation_strawman": state_context.session_data.get("presentation_strawman")
                },
                user_intent=state_context.user_intent.dict() if hasattr(state_context, 'user_intent') and state_context.user_intent else None
            )

            # Track token usage
            user_tokens = len(user_prompt) // 4
            system_tokens = self.state_prompt_tokens.get(state_context.current_state, 0)

            await self.token_tracker.track_modular(
                session_id,
                state_context.current_state,
                user_tokens,
                system_tokens
            )

            logger.info(
                f"Processing - State: {state_context.current_state}, "
                f"User Tokens: {user_tokens}, System Tokens: {system_tokens}, "
                f"Total: {user_tokens + system_tokens}"
            )

            # Route to appropriate agent based on state
            if state_context.current_state == "PROVIDE_GREETING":
                result = await self.greeting_agent.run(
                    user_prompt,
                    model_settings=ModelSettings(temperature=0.7, max_tokens=500)
                )
                response = result.output  # Simple string
                logger.info("Generated greeting")

            elif state_context.current_state == "ASK_CLARIFYING_QUESTIONS":
                result = await self.questions_agent.run(
                    user_prompt,
                    model_settings=ModelSettings(temperature=0.5, max_tokens=1000)
                )
                response = result.output  # ClarifyingQuestions object
                logger.info(f"Generated {len(response.questions)} clarifying questions")

            elif state_context.current_state == "CREATE_CONFIRMATION_PLAN":
                result = await self.plan_agent.run(
                    user_prompt,
                    model_settings=ModelSettings(temperature=0.3, max_tokens=2000)
                )
                response = result.output  # ConfirmationPlan object
                logger.info(f"Generated confirmation plan with {response.proposed_slide_count} slides")

            elif state_context.current_state == "GENERATE_STRAWMAN":
                logger.info("Generating strawman presentation")
                result = await self.strawman_agent.run(
                    user_prompt,
                    model_settings=ModelSettings(temperature=0.4, max_tokens=8000)
                )
                strawman = result.output  # PresentationStrawman object
                logger.info(f"Generated strawman with {len(strawman.slides)} slides")
                logger.debug(f"First slide: {strawman.slides[0].slide_id if strawman.slides else 'No slides'}")

                # Post-process to ensure asset fields are in correct format
                strawman = AssetFormatter.format_strawman(strawman)
                logger.info("Applied asset field formatting to strawman")

                # v2.0: Transform and send to deck-builder API
                if self.deck_builder_enabled:
                    try:
                        logger.info("Transforming presentation for deck-builder")
                        api_payload = self.content_transformer.transform_presentation(strawman)
                        logger.debug(f"Transformed to {len(api_payload['slides'])} deck-builder slides")

                        logger.info("Calling deck-builder API")
                        api_response = await self.deck_builder_client.create_presentation(api_payload)
                        presentation_url = self.deck_builder_client.get_full_url(api_response['url'])

                        logger.info(f"✅ Presentation created: {presentation_url}")

                        # Return URL response instead of strawman
                        response = {
                            "type": "presentation_url",
                            "url": presentation_url,
                            "presentation_id": api_response['id'],
                            "slide_count": len(strawman.slides),
                            "message": f"Your presentation is ready! View it at: {presentation_url}"
                        }
                    except Exception as e:
                        logger.error(f"Deck-builder API failed: {e}", exc_info=True)
                        logger.warning("Falling back to JSON response")
                        response = strawman
                else:
                    response = strawman

            elif state_context.current_state == "REFINE_STRAWMAN":
                logger.info("Refining strawman presentation")
                result = await self.refine_strawman_agent.run(
                    user_prompt,
                    model_settings=ModelSettings(temperature=0.4, max_tokens=8000)
                )
                strawman = result.output  # PresentationStrawman object
                logger.info(f"Refined strawman with {len(strawman.slides)} slides")

                # Post-process to ensure asset fields are in correct format
                strawman = AssetFormatter.format_strawman(strawman)
                logger.info("Applied asset field formatting to refined strawman")

                # v2.0: Transform and send to deck-builder API
                if self.deck_builder_enabled:
                    try:
                        logger.info("Transforming refined presentation for deck-builder")
                        api_payload = self.content_transformer.transform_presentation(strawman)
                        logger.debug(f"Transformed to {len(api_payload['slides'])} deck-builder slides")

                        logger.info("Calling deck-builder API")
                        api_response = await self.deck_builder_client.create_presentation(api_payload)
                        presentation_url = self.deck_builder_client.get_full_url(api_response['url'])

                        logger.info(f"✅ Refined presentation created: {presentation_url}")

                        # Return URL response instead of strawman
                        response = {
                            "type": "presentation_url",
                            "url": presentation_url,
                            "presentation_id": api_response['id'],
                            "slide_count": len(strawman.slides),
                            "message": f"Your refined presentation is ready! View it at: {presentation_url}"
                        }
                    except Exception as e:
                        logger.error(f"Deck-builder API failed: {e}", exc_info=True)
                        logger.warning("Falling back to JSON response")
                        response = strawman
                else:
                    response = strawman

            elif state_context.current_state == "CONTENT_GENERATION":
                logger.info("Starting content generation via Content Orchestrator")
                # Delegate to the content generation method
                response = await self.process_content_generation(state_context, user_prompt)

            else:
                raise ValueError(f"Unknown state: {state_context.current_state}")

            return response

        except ModelHTTPError as e:
            logger.error(f"API error in state {state_context.current_state}: {e}")
            raise
        except Exception as e:
            error_msg = str(e)
            # Handle Gemini-specific errors
            if "MALFORMED_FUNCTION_CALL" in error_msg:
                logger.error(f"Gemini function call error in state {state_context.current_state}. This may be due to complex output structure.")
                logger.error(f"Full error: {error_msg}")
            elif "MAX_TOKENS" in error_msg:
                logger.error(f"Token limit exceeded in state {state_context.current_state}. Consider increasing max_tokens.")
            elif "Connection error" in error_msg:
                logger.error(f"Connection error in state {state_context.current_state} - Please check your API key is set in .env file")
            else:
                logger.error(f"Error processing state {state_context.current_state}: {error_msg}")
            raise

    async def process_content_generation(
        self,
        state_context: StateContext,
        user_prompt: str
    ) -> Union[str, Dict[str, Any]]:
        """
        Handle content generation state by calling Content Orchestrator API.

        Args:
            state_context: Current state context with session data
            user_prompt: User prompt from context builder

        Returns:
            String message or enriched presentation response
        """
        try:
            # DEBUG: Log what we received
            logger.info(f"[CONTENT_GENERATION] process_content_generation called")
            logger.info(f"[CONTENT_GENERATION] session_data keys: {list(state_context.session_data.keys())}")

            # Get strawman from session data
            strawman_data = state_context.session_data.get('strawman')
            logger.info(f"[CONTENT_GENERATION] strawman_data type: {type(strawman_data)}")

            if not strawman_data:
                logger.error("[CONTENT_GENERATION] ❌ No strawman found in session data")
                logger.error(f"[CONTENT_GENERATION] Available keys: {list(state_context.session_data.keys())}")
                # Try alternate keys
                for alt_key in ['presentation_strawman', 'refined_strawman']:
                    if alt_key in state_context.session_data:
                        logger.info(f"[CONTENT_GENERATION] Found alternate key: {alt_key}")
                        strawman_data = state_context.session_data.get(alt_key)
                        break

            if not strawman_data:
                logger.error("[CONTENT_GENERATION] Still no strawman found after checking alternates")
                return "Error: No presentation outline found. Please generate a strawman first."

            logger.info(f"[CONTENT_GENERATION] ✓ Got strawman_data, type: {type(strawman_data)}")

            # Convert to PresentationStrawman object if it's a dict
            if isinstance(strawman_data, dict):
                strawman = PresentationStrawman.model_validate(strawman_data)
            else:
                strawman = strawman_data

            logger.info(f"Processing content generation for {len(strawman.slides)} slides")

            # Check if content orchestrator is enabled
            if not self.content_orchestrator_enabled:
                logger.warning("Content Orchestrator is disabled, falling back to v2.0 behavior")
                result = await self.content_agent.run(
                    "Content Orchestrator is not available. Please inform the user that "
                    "we'll proceed with placeholder content (v2.0 behavior).",
                    model_settings=ModelSettings(temperature=0.7, max_tokens=500)
                )
                return result.output

            # Call internal Content Orchestrator (no HTTP, direct module call)
            try:
                # Progress callback function (internal orchestrator signature)
                def progress_callback(message: str, current: int, total: int):
                    logger.info(f"Content generation progress [{current}/{total}]: {message}")
                    # TODO: Send progress update via WebSocket if needed

                logger.info("Calling internal Content Orchestrator...")
                enriched_response = await self.content_orchestrator.enrich_presentation(
                    strawman=strawman,
                    layout_assignments=None,  # Let orchestrator create defaults
                    progress_callback=progress_callback
                )

                # Generate success message using content_agent
                # Access metadata from internal orchestrator response
                metadata = enriched_response.generation_metadata
                summary = self.orchestrator_transformer.get_generation_summary(enriched_response)

                success_prompt = f"""
Content generation completed successfully!

{summary}

Generate a friendly, informative message to the user about their enriched presentation.
Focus on what was successfully generated and offer next steps.
"""

                result = await self.content_agent.run(
                    success_prompt,
                    model_settings=ModelSettings(temperature=0.7, max_tokens=800)
                )

                logger.info("Content generation successful")

                # Return response with enriched data
                return {
                    "type": "enriched_presentation",
                    "message": result.output,
                    "enriched_response": enriched_response.model_dump(),
                    "summary": {
                        "total_slides": len(enriched_response.enriched_slides),
                        "successful_items": metadata.get("successful_items", 0),
                        "failed_items": metadata.get("failed_items", 0),
                        "generation_time": metadata.get("generation_time_seconds", 0),
                        "overall_compliant": enriched_response.validation_report.overall_compliant
                    }
                }

            except Exception as e:
                logger.error(f"Content Orchestrator API failed: {e}", exc_info=True)

                # Handle failure gracefully
                error_prompt = f"""
Content generation encountered an error:
{str(e)}

Explain this to the user in a friendly way and offer alternatives:
1. Proceed with placeholder content (v2.0 behavior)
2. Retry content generation
3. Adjust the presentation and try again

Keep the tone positive and solution-oriented.
"""

                result = await self.content_agent.run(
                    error_prompt,
                    model_settings=ModelSettings(temperature=0.7, max_tokens=800)
                )

                return {
                    "type": "content_generation_failed",
                    "message": result.output,
                    "error": str(e),
                    "fallback_available": True
                }

        except Exception as e:
            logger.error(f"Error in process_content_generation: {e}", exc_info=True)
            return f"An error occurred during content generation: {str(e)}"

    def get_token_report(self, session_id: str) -> dict:
        """Get token usage report for a specific session."""
        return self.token_tracker.get_savings_report(session_id)

    def print_token_report(self, session_id: str) -> None:
        """Print formatted token usage report for a session."""
        self.token_tracker.print_session_report(session_id)

    def get_aggregate_token_report(self) -> dict:
        """Get aggregate token usage report across all sessions."""
        return self.token_tracker.get_aggregate_report()

    def print_aggregate_token_report(self) -> None:
        """Print formatted aggregate token usage report."""
        self.token_tracker.print_aggregate_report()