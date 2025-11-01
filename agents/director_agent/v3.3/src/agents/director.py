"""
Director Agent for managing presentation creation workflow.
v3.3: Secure authentication using Application Default Credentials (ADC)
"""
import os
import json
from typing import Union, Dict, Any
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings
from pydantic_ai.exceptions import ModelHTTPError
# v3.3: Removed GoogleModel and GoogleProvider - now using Vertex AI with ADC
from src.models.agents import (
    StateContext, ClarifyingQuestions, ConfirmationPlan,
    PresentationStrawman, Slide
)
from src.models.layout_selection import LayoutSelection  # v3.2: AI layout selection
from src.utils.logger import setup_logger
from src.utils.logfire_config import instrument_agents
from src.utils.context_builder import ContextBuilder
from src.utils.token_tracker import TokenTracker
from src.utils.asset_formatter import AssetFormatter
# v2.0: Deck-builder integration
# v3.2: LayoutMapper removed - replaced by LayoutSchemaManager
from src.utils.layout_schema_manager import LayoutSchemaManager  # v3.2: Schema-driven architecture
from src.utils.content_transformer import ContentTransformer
from src.utils.deck_builder_client import DeckBuilderClient
# v3.3: GCP Authentication utility for ADC
from src.utils.gcp_auth import initialize_vertex_ai, get_project_info

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

        # v3.3: GCP/Vertex AI only - no fallback providers
        if not settings.GCP_ENABLED:
            raise ValueError(
                "GCP/Vertex AI must be enabled. Please either:\n"
                "  1. Set GCP_ENABLED=true in .env, AND\n"
                "  2. For local: Run 'gcloud auth application-default login'\n"
                "  3. For Railway: Set GCP_SERVICE_ACCOUNT_JSON environment variable"
            )

        # v3.3: Initialize Vertex AI with Application Default Credentials
        try:
            initialize_vertex_ai()
            gcp_info = get_project_info()
            logger.info(f"✓ Using Google Gemini via Vertex AI (Project: {gcp_info['project_id']})")
            logger.info(f"  Authentication: {'Service Account' if gcp_info['has_service_account'] else 'ADC (local)'}")

            # v3.3: Use individual model for each stage from settings with Vertex AI prefix
            model_greeting = f'google-vertex:{settings.GCP_MODEL_GREETING}'
            model_questions = f'google-vertex:{settings.GCP_MODEL_QUESTIONS}'
            model_plan = f'google-vertex:{settings.GCP_MODEL_PLAN}'
            model_strawman = f'google-vertex:{settings.GCP_MODEL_STRAWMAN}'
            model_refine = f'google-vertex:{settings.GCP_MODEL_REFINE}'

            logger.info(f"  Greeting model: {settings.GCP_MODEL_GREETING}")
            logger.info(f"  Questions model: {settings.GCP_MODEL_QUESTIONS}")
            logger.info(f"  Plan model: {settings.GCP_MODEL_PLAN}")
            logger.info(f"  Strawman model: {settings.GCP_MODEL_STRAWMAN}")
            logger.info(f"  Refine model: {settings.GCP_MODEL_REFINE}")

        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            raise ValueError(f"Vertex AI initialization failed: {e}")

        # Initialize agents with embedded modular prompts
        logger.info("DirectorAgent initializing with embedded modular prompts (5 individual models)")
        self._init_agents_with_embedded_prompts(
            model_greeting,
            model_questions,
            model_plan,
            model_strawman,
            model_refine
        )

        # Initialize context builder and token tracker
        self.context_builder = ContextBuilder()
        self.token_tracker = TokenTracker()

        # v2.0: Initialize deck-builder components
        self.deck_builder_enabled = getattr(settings, 'DECK_BUILDER_ENABLED', True)
        if self.deck_builder_enabled:
            try:
                # v3.2: Initialize schema-driven architecture
                self.layout_schema_manager = LayoutSchemaManager()
                # v3.2: ContentTransformer no longer requires LayoutMapper
                self.content_transformer = ContentTransformer()
                deck_builder_url = getattr(settings, 'DECK_BUILDER_API_URL', 'http://localhost:8000')
                self.deck_builder_client = DeckBuilderClient(deck_builder_url)
                logger.info(f"Deck-builder integration enabled: {deck_builder_url}")
                logger.info(f"Schema-driven architecture: {len(self.layout_schema_manager.schemas)} layouts available")
            except Exception as e:
                logger.warning(f"Failed to initialize deck-builder components: {e}")
                logger.warning("Deck-builder integration disabled, will return JSON only")
                self.deck_builder_enabled = False
        else:
            logger.info("Deck-builder integration disabled in settings")

        # v3.1: Initialize Text Service client for Stage 6
        self.text_service_enabled = getattr(settings, 'TEXT_SERVICE_ENABLED', True)
        if self.text_service_enabled:
            try:
                from src.utils.text_service_client import TextServiceClient
                text_service_url = getattr(settings, 'TEXT_SERVICE_URL',
                    'https://web-production-e3796.up.railway.app')
                self.text_client = TextServiceClient(text_service_url)
                logger.info(f"Text Service integration enabled: {text_service_url}")
            except Exception as e:
                logger.warning(f"Failed to initialize Text Service client: {e}")
                logger.warning("Text Service integration disabled, Stage 6 will use placeholders")
                self.text_service_enabled = False
        else:
            logger.info("Text Service integration disabled in settings")

        logger.info("DirectorAgent initialized with 6 individual Gemini models (granular per-stage configuration)")

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
            'CONTENT_GENERATION': 'content_generation.md'  # v3.1: Stage 6
        }

        state_file = state_prompt_map.get(state)
        if not state_file:
            raise ValueError(f"Unknown state for prompt loading: {state}")

        state_path = os.path.join(prompt_dir, state_file)
        with open(state_path, 'r') as f:
            state_prompt = f.read()

        # Combine prompts
        return f"{base_prompt}\n\n{state_prompt}"

    def _init_agents_with_embedded_prompts(
        self,
        model_greeting,
        model_questions,
        model_plan,
        model_strawman,
        model_refine
    ):
        """Initialize agents with embedded modular prompts and individual models per stage."""
        # Load state-specific combined prompts (base + state instructions)
        greeting_prompt = self._load_modular_prompt("PROVIDE_GREETING")
        questions_prompt = self._load_modular_prompt("ASK_CLARIFYING_QUESTIONS")
        plan_prompt = self._load_modular_prompt("CREATE_CONFIRMATION_PLAN")
        strawman_prompt = self._load_modular_prompt("GENERATE_STRAWMAN")
        refine_prompt = self._load_modular_prompt("REFINE_STRAWMAN")

        # Store system prompt tokens for each state (for tracking)
        self.state_prompt_tokens = {
            "PROVIDE_GREETING": len(greeting_prompt) // 4,
            "ASK_CLARIFYING_QUESTIONS": len(questions_prompt) // 4,
            "CREATE_CONFIRMATION_PLAN": len(plan_prompt) // 4,
            "GENERATE_STRAWMAN": len(strawman_prompt) // 4,
            "REFINE_STRAWMAN": len(refine_prompt) // 4,
            "CONTENT_GENERATION": 0  # v3.1: Stage 6 doesn't use LLM prompts (calls Text Service directly)
        }

        # Initialize greeting agent (Stage 1)
        self.greeting_agent = Agent(
            model=model_greeting,
            output_type=str,
            system_prompt=greeting_prompt,
            retries=2,
            name="director_greeting"
        )

        # Initialize questions agent (Stage 2)
        self.questions_agent = Agent(
            model=model_questions,
            output_type=ClarifyingQuestions,
            system_prompt=questions_prompt,
            retries=2,
            name="director_questions"
        )

        # Initialize plan agent (Stage 3)
        self.plan_agent = Agent(
            model=model_plan,
            output_type=ConfirmationPlan,
            system_prompt=plan_prompt,
            retries=2,
            name="director_plan"
        )

        # Initialize strawman agent (Stage 4)
        self.strawman_agent = Agent(
            model=model_strawman,
            output_type=PresentationStrawman,
            system_prompt=strawman_prompt,
            retries=2,
            name="director_strawman"
        )

        # Initialize refine strawman agent (Stage 5)
        self.refine_strawman_agent = Agent(
            model=model_refine,
            output_type=PresentationStrawman,
            system_prompt=refine_prompt,
            retries=2,
            name="director_refine_strawman"
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
                    "presentation_strawman": state_context.session_data.get("presentation_strawman")  # v3.2: Pass strawman for context
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

                # v3.2: AI-powered semantic layout selection
                total_slides = len(strawman.slides)
                logger.info(f"Starting AI-powered layout selection for {total_slides} slides")

                for idx, slide in enumerate(strawman.slides):
                    # Determine slide position
                    if idx == 0:
                        position = "first"
                    elif idx == total_slides - 1:
                        position = "last"
                    else:
                        position = "middle"

                    # AI-powered semantic layout selection
                    layout_selection = await self._select_layout_by_use_case(
                        slide=slide,
                        position=position,
                        total_slides=total_slides
                    )

                    # Assign selected layout and reasoning to slide
                    slide.layout_id = layout_selection.layout_id
                    slide.layout_selection_reasoning = layout_selection.reasoning
                    logger.info(
                        f"Slide {slide.slide_number} '{slide.title}': "
                        f"{layout_selection.layout_id} - {layout_selection.reasoning}"
                    )

                logger.info(f"✅ Assigned purpose-driven layouts to all {total_slides} slides")

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

                        # v3.1: Return hybrid response with both URL and strawman
                        # URL for frontend display, strawman for REFINE_STRAWMAN and CONTENT_GENERATION
                        response = {
                            "type": "presentation_url",
                            "url": presentation_url,
                            "presentation_id": api_response['id'],
                            "slide_count": len(strawman.slides),
                            "message": f"Your presentation is ready! View it at: {presentation_url}",
                            "strawman": strawman  # Include strawman for session storage
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

                        # v3.1: Return hybrid response with both URL and refined strawman
                        # URL for frontend display, refined strawman for CONTENT_GENERATION
                        response = {
                            "type": "presentation_url",
                            "url": presentation_url,
                            "presentation_id": api_response['id'],
                            "slide_count": len(strawman.slides),
                            "message": f"Your refined presentation is ready! View it at: {presentation_url}",
                            "strawman": strawman  # Include refined strawman for session storage
                        }
                    except Exception as e:
                        logger.error(f"Deck-builder API failed: {e}", exc_info=True)
                        logger.warning("Falling back to JSON response")
                        response = strawman
                else:
                    response = strawman

            elif state_context.current_state == "CONTENT_GENERATION":
                # v3.1: Stage 6 - Text Service content generation
                logger.info("Starting Stage 6: Content Generation (Text only)")

                # Get strawman from session
                strawman_data = state_context.session_data.get("presentation_strawman")
                if not strawman_data:
                    raise ValueError("No strawman found in session for content generation")

                strawman = PresentationStrawman(**strawman_data)
                logger.info(f"Processing {len(strawman.slides)} slides for text generation")

                # Import content models
                from src.models.content import EnrichedSlide, EnrichedPresentationStrawman
                from datetime import datetime

                # Generate text content for each slide
                enriched_slides = []
                successful_slides = 0
                failed_slides = 0
                start_time = datetime.utcnow()

                for idx, slide in enumerate(strawman.slides):
                    try:
                        logger.info(f"Generating text for slide {idx + 1}/{len(strawman.slides)}: {slide.slide_id}")
                        generated_text = await self._generate_slide_text(
                            slide,
                            strawman,
                            session_id,
                            idx + 1
                        )
                        enriched_slides.append(EnrichedSlide(
                            original_slide=slide,
                            slide_id=slide.slide_id,
                            generated_text=generated_text,
                            has_text_failure=False
                        ))
                        successful_slides += 1
                        logger.info(f"✅ Slide {idx + 1} text generated ({len(generated_text.content)} chars)")
                    except Exception as e:
                        logger.error(f"Text generation failed for slide {slide.slide_id}: {e}")
                        enriched_slides.append(EnrichedSlide(
                            original_slide=slide,
                            slide_id=slide.slide_id,
                            generated_text=None,
                            has_text_failure=True
                        ))
                        failed_slides += 1

                generation_time = (datetime.utcnow() - start_time).total_seconds()

                # Create enriched presentation
                enriched_presentation = EnrichedPresentationStrawman(
                    original_strawman=strawman,
                    enriched_slides=enriched_slides,
                    generation_metadata={
                        "total_slides": len(strawman.slides),
                        "successful_slides": successful_slides,
                        "failed_slides": failed_slides,
                        "generation_time_seconds": generation_time,
                        "timestamp": datetime.utcnow().isoformat(),
                        "service_used": "text_service_v1.0"
                    }
                )

                logger.info(f"Content generation complete: {successful_slides}/{len(strawman.slides)} successful")

                # Send enriched presentation to Layout Architect
                if self.deck_builder_enabled:
                    try:
                        deck_url = await self._send_enriched_to_layout_architect(enriched_presentation)
                        response = {
                            "type": "presentation_url",
                            "url": deck_url,
                            "slide_count": len(strawman.slides),
                            "content_generated": True,
                            "successful_slides": successful_slides,
                            "failed_slides": failed_slides,
                            "message": f"Your presentation with generated content is ready! View it at: {deck_url}"
                        }
                        logger.info(f"✅ Stage 6 complete: {deck_url}")
                    except Exception as e:
                        logger.error(f"Layout Architect integration failed: {e}", exc_info=True)
                        logger.warning("Falling back to v2.0-style deck with placeholders")
                        # Fallback: use v2.0 approach (strawman with placeholders)
                        api_payload = self.content_transformer.transform_presentation(strawman)
                        api_response = await self.deck_builder_client.create_presentation(api_payload)
                        fallback_url = self.deck_builder_client.get_full_url(api_response['url'])
                        response = {
                            "type": "presentation_url",
                            "url": fallback_url,
                            "slide_count": len(strawman.slides),
                            "content_generated": False,
                            "message": f"Presentation created (fallback mode): {fallback_url}"
                        }
                else:
                    # Return enriched presentation object if deck-builder disabled
                    response = enriched_presentation

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

    async def _select_layout_by_use_case(
        self,
        slide: Slide,
        position: str,
        total_slides: int
    ) -> LayoutSelection:
        """
        AI-powered layout selection using semantic matching.

        v3.2: Replaces rule-based LayoutMapper with AI semantic analysis of
        slide content against all 24 layout BestUseCases.

        Args:
            slide: Slide object with narrative, key_points, etc.
            position: Slide position ("first", "last", "middle")
            total_slides: Total number of slides in presentation

        Returns:
            LayoutSelection with layout_id and reasoning
        """
        # Handle mandatory layout positions
        if position == "first":
            return LayoutSelection(
                layout_id="L01",
                reasoning="First slide - using title layout",
                confidence=1.0
            )

        if position == "last":
            return LayoutSelection(
                layout_id="L03",
                reasoning="Last slide - using closing layout",
                confidence=1.0
            )

        if slide.slide_type == "section_divider":
            return LayoutSelection(
                layout_id="L02",
                reasoning="Section divider slide",
                confidence=1.0
            )

        # Get all available layouts with BestUseCases (excluding special layouts)
        layout_options_text = self.layout_schema_manager.format_layout_options_for_ai(
            exclude_layout_ids=["L01", "L02", "L03"]
        )

        # Build AI prompt for semantic matching
        prompt = f"""
You are selecting the most appropriate slide layout for a presentation slide.

**Slide Information:**
- Title: {slide.title}
- Narrative: {slide.narrative}
- Key Points: {', '.join(slide.key_points[:5]) if slide.key_points else 'None'}
- Slide Type: {slide.slide_type}
- Content Needs:
  - Analytics: {slide.analytics_needed or 'None'}
  - Visuals: {slide.visuals_needed or 'None'}
  - Diagrams: {slide.diagrams_needed or 'None'}
  - Tables: {slide.tables_needed or 'None'}
- Structure Preference: {slide.structure_preference or 'None'}

**Available Layouts (with BestUseCase guidance):**
{layout_options_text}

**Task:**
Select the layout whose BestUseCase most closely matches this slide's purpose and content.

Consider:
1. Semantic alignment between slide narrative and layout BestUseCase
2. Content type requirements (text, data, visuals, quotes, comparisons)
3. Presentation intent (inform, persuade, compare, emphasize, inspire)
4. Audience comprehension (clarity vs. detail vs. impact)
5. Specific keywords that match layout BestUseCase

**Important Selection Criteria:**
- If the slide contains a **customer testimonial or quote**, select **L07** (Quote Slide)
- If the slide is **comparing two options** or showing **pros/cons**, select **L20** (Comparison)
- If the slide shows **KPIs or metrics dashboard**, select **L19** (Dashboard)
- If the slide has **data visualization with insights**, select **L17** (Chart + Insights)
- If the slide has **sequential steps or process**, select **L06** (Numbered List)
- If the slide has **simple bullet points**, select **L05** (Bullet List)
- If the slide has **long-form explanation**, select **L04** (Text + Summary)

Return your selection with clear reasoning based on the semantic match between content and BestUseCase.
"""

        # Run AI selection
        try:
            result = await self.strawman_agent.run(
                prompt,
                result_type=LayoutSelection,
                model_settings=ModelSettings(temperature=0.2, max_tokens=500)
            )
            selection = result.output

            logger.info(f"AI selected layout {selection.layout_id} for slide '{slide.title}': {selection.reasoning}")
            return selection

        except Exception as e:
            # Fallback to L05 if AI selection fails
            logger.warning(f"AI layout selection failed: {str(e)}, falling back to L05")
            return LayoutSelection(
                layout_id="L05",
                reasoning=f"Fallback layout after AI selection error: {str(e)[:100]}",
                confidence=0.5
            )

    # DEPRECATED v3.1 method - removed in v3.2
    # Replaced by _build_constraints_from_schema() which uses LayoutSchemaManager

    async def _generate_slide_text(
        self,
        slide: Slide,
        presentation: PresentationStrawman,
        session_id: str,
        slide_number: int
    ):
        """
        Generate text content for a single slide using Text Service.

        v3.2: Uses schema-driven architecture with layout_schema_manager.
        Sends complete layout schema to Text Service for structured generation.

        Args:
            slide: The slide to generate text for (with layout_id assigned)
            presentation: The full presentation context
            session_id: Session identifier for context tracking
            slide_number: Position of slide in presentation (1-indexed)

        Returns:
            GeneratedText object with structured content

        Raises:
            Exception: If Text Service is disabled or call fails
        """
        if not self.text_service_enabled:
            raise Exception("Text Service is not enabled")

        # v3.2: Get layout_id (should be assigned during GENERATE_STRAWMAN)
        layout_id = slide.layout_id
        if not layout_id:
            logger.warning(f"Slide {slide_number} has no layout_id, falling back to L05")
            layout_id = "L05"

        # v3.2: Build schema-driven request using LayoutSchemaManager
        presentation_context = {
            "main_title": presentation.main_title,
            "overall_theme": presentation.overall_theme,
            "target_audience": presentation.target_audience,
            "presentation_duration": presentation.presentation_duration
        }

        schema_request = self.layout_schema_manager.build_content_request(
            layout_id=layout_id,
            slide=slide,
            presentation_context=presentation_context
        )

        # Add session tracking
        schema_request["presentation_id"] = session_id
        schema_request["slide_number"] = slide_number

        logger.info(
            f"Generating content for slide {slide_number} using layout {layout_id} ({schema_request['layout_name']})"
        )
        logger.debug(f"Schema fields: {list(schema_request['layout_schema'].keys())}")

        # TODO v3.2: When Text Service v1.1 is deployed, use structured endpoint
        # For now, convert schema request to v1.0 format (backward compatibility)
        v1_request = self._convert_schema_request_to_v1(schema_request)

        # Call Text Service (v1.0 endpoint for now)
        generated = await self.text_client.generate(v1_request)
        logger.debug(f"Generated {len(generated.content)} chars for slide {slide_number}")

        return generated

    def _convert_schema_request_to_v1(self, schema_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert v3.2 schema request to v1.0 Text Service format.

        Temporary compatibility layer until Text Service v1.1 is deployed.

        Args:
            schema_request: Schema-driven request from LayoutSchemaManager

        Returns:
            v1.0 compatible request dictionary
        """
        guidance = schema_request['content_guidance']
        layout_schema = schema_request['layout_schema']

        # Build v1.0 compatible constraints from schema
        constraints = self._build_constraints_from_schema(layout_schema)

        return {
            "presentation_id": schema_request.get("presentation_id", "default"),
            "slide_id": schema_request["slide_id"],
            "slide_number": schema_request["slide_number"],
            "topics": guidance.get("key_points", []),
            "narrative": guidance.get("narrative", ""),
            "context": {
                "presentation_context": f"{guidance.get('presentation_context', {}).get('main_title', '')} - {guidance.get('presentation_context', {}).get('overall_theme', '')}",
                "slide_context": guidance.get("narrative", ""),
                "previous_slides": []
            },
            "constraints": constraints
        }

    def _build_constraints_from_schema(self, layout_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build v1.0 constraints from v3.2 layout schema.

        Temporary helper until Text Service v1.1 supports structured generation.

        Args:
            layout_schema: Schema from layout_schemas.json

        Returns:
            v1.0 compatible constraints dictionary
        """
        # Calculate total max characters from all text fields
        total_chars = 0
        has_bullets = False
        has_numbered = False

        for field_name, field_spec in layout_schema.items():
            if field_spec.get('type') == 'string' and 'max_chars' in field_spec:
                total_chars += field_spec['max_chars']
            elif field_spec.get('type') == 'array':
                has_bullets = True
                items = field_spec.get('max_items', 5)
                chars_per = field_spec.get('max_chars_per_item', 100)
                total_chars += items * chars_per
            elif field_spec.get('type') == 'array_of_objects':
                has_numbered = True

        # Determine format
        if has_bullets:
            format_type = "bullet_points"
        elif has_numbered:
            format_type = "numbered_list"
        else:
            format_type = "paragraph"

        return {
            "max_characters": total_chars or 800,
            "tone": "professional",
            "format": format_type
        }

    async def _send_enriched_to_layout_architect(self, enriched: 'EnrichedPresentationStrawman') -> str:
        """
        Send enriched presentation to Layout Architect and get deck URL.

        Args:
            enriched: EnrichedPresentationStrawman with generated text content

        Returns:
            Full deck URL from Layout Architect

        Raises:
            Exception: If deck-builder call fails
        """
        logger.info("Sending enriched presentation to Layout Architect")

        # Transform enriched presentation to deck-builder format
        # Pass enriched data to content_transformer so it can inject real text
        api_payload = self.content_transformer.transform_presentation(
            enriched.original_strawman,
            enriched_data=enriched
        )

        logger.info(f"Transformed {len(api_payload['slides'])} slides with generated content")

        # Call deck-builder API
        api_response = await self.deck_builder_client.create_presentation(api_payload)
        deck_url = self.deck_builder_client.get_full_url(api_response['url'])

        logger.info(f"Layout Architect created deck: {deck_url}")

        return deck_url

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