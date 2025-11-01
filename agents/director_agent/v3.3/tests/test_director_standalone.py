#!/usr/bin/env python3
"""
End-to-end automated testing tool for the standalone Director Agent.
Tests complete conversation flows through stages 1-6 with predefined scenarios.
Supports both legacy and streamlined WebSocket protocols.

v3.1: Added Stage 6 (CONTENT_GENERATION) testing with actual text generation display.
v3.1.1: Enhanced for Format Ownership Architecture - handles both:
    - v1.1 Text Service: Structured content (dict) with format specifications
    - v1.0 Text Service: Legacy HTML/text (string) content

    Displays format type, field-level content, and format ownership metadata.
"""
import asyncio
import json
import argparse
import sys
import os
import warnings
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path (tests/ is one level down from root)
sys.path.insert(0, str(Path(__file__).parent.parent))

# Suppress the PydanticAI warning about additionalProperties
warnings.filterwarnings("ignore", message=".*additionalProperties.*is not supported by Gemini.*")

# Load environment variables from .env file
load_dotenv()

# Import from local standalone agent structure
from src.agents.director import DirectorAgent
from src.agents.intent_router import IntentRouter
from src.models.agents import StateContext, UserIntent
from src.workflows.state_machine import WorkflowOrchestrator
from src.utils.streamlined_packager import StreamlinedMessagePackager
from src.utils.message_packager import MessagePackager
from config.settings import get_settings

# Import test utilities
from checkpoint_manager import CheckpointManager
from test_utils import (
    Colors, format_state, format_user_message, format_agent_message,
    format_error, format_success, print_separator,
    create_initial_context, add_to_history,
    format_clarifying_questions, format_confirmation_plan,
    format_strawman_summary, save_conversation, format_validation_results
)


class DirectorStandaloneTester:
    """Automated end-to-end tester for standalone Director Agent (Stages 1-6).

    v3.1: Now includes Stage 6 (CONTENT_GENERATION) with actual text generation.
    v3.1.1: Enhanced to test Format Ownership Architecture:
        - Detects and displays structured (dict) vs legacy (string) content
        - Shows format specifications and field-level metadata
        - Validates v1.1 Text Service integration with format ownership
    """

    def __init__(self, scenario_file: str = "test_scenarios.json",
                 save_checkpoints: bool = False, start_stage: str = None,
                 checkpoint_file: str = None):
        """Initialize the tester with scenarios."""
        self.director = DirectorAgent()
        self.intent_router = IntentRouter()
        self.workflow = WorkflowOrchestrator()

        # Get settings and determine protocol
        self.settings = get_settings()
        self.use_streamlined = self.settings.USE_STREAMLINED_PROTOCOL

        # Checkpoint settings
        self.save_checkpoints = save_checkpoints
        self.start_stage = start_stage
        self.checkpoint_file = checkpoint_file
        self.checkpoint_manager = CheckpointManager()

        # Initialize packagers for protocol handling
        self.streamlined_packager = StreamlinedMessagePackager()
        self.legacy_packager = MessagePackager()

        # Load test scenarios
        scenario_path = os.path.join(os.path.dirname(__file__), scenario_file)
        with open(scenario_path, 'r') as f:
            self.scenarios_data = json.load(f)
            self.scenarios = self.scenarios_data["scenarios"]
            self.validation_rules = self.scenarios_data["validation_rules"]

    def show_scenarios_menu(self):
        """Display available scenarios in a formatted menu."""
        print(f"\n{Colors.BOLD}🎯 Available Scenarios:{Colors.ENDC}")
        print("═" * 60)

        scenarios_list = [
            ("1", "default", "AI in Healthcare", "Standard presentation about AI applications in healthcare"),
            ("2", "executive", "Q3 Financial Results", "Board presentation on quarterly financial performance"),
            ("3", "technical", "Microservices Architecture", "Technical presentation for engineering team"),
            ("4", "educational", "Climate Change Basics", "Educational presentation for high school students"),
            ("5", "sales", "Product Launch", "Sales presentation for new SaaS product")
        ]

        for num, key, name, desc in scenarios_list:
            print(f"\n{Colors.BOLD}{num}️⃣  {name}{Colors.ENDC}")
            print(f"    {desc}")

    def format_streamlined_messages(self, messages: List[Any]) -> str:
        """Format streamlined messages for display."""
        output = []
        for msg in messages:
            if msg.type == "chat_message":
                if msg.payload.list_items:
                    output.append(f"{msg.payload.text}")
                    for item in msg.payload.list_items:
                        output.append(f"  • {item}")
                else:
                    output.append(msg.payload.text)
                    if msg.payload.sub_title:
                        output.append(f"\n{msg.payload.sub_title}")
            elif msg.type == "action_request":
                output.append(f"\n{msg.payload.prompt_text}")
                for action in msg.payload.actions:
                    marker = "►" if action.primary else "▷"
                    output.append(f"  {marker} {action.label}")
            elif msg.type == "slide_update":
                output.append(f"\n📊 Presentation ready: {msg.payload.metadata.main_title}")
                output.append(f"   {len(msg.payload.slides)} slides")
                output.append(f"   Theme: {msg.payload.metadata.overall_theme}")
                output.append(f"   Audience: {msg.payload.metadata.target_audience}")
                output.append(f"   Duration: {msg.payload.metadata.presentation_duration} minutes")
            elif msg.type == "status_update":
                output.append(f"⏳ {msg.payload.text}")
        return "\n".join(output)

    def format_slide_details(self, slide) -> str:
        """Format a single slide with all planning fields."""
        output = []
        output.append(f"\n{Colors.GREEN}Slide {slide.slide_number}: {slide.title}{Colors.ENDC}")
        output.append(f"  Type: {slide.slide_type}")
        output.append(f"  ID: {slide.slide_id}")
        output.append(f"  Narrative: {slide.narrative}")

        output.append(f"  Key Points:")
        for point in slide.key_points:
            output.append(f"    • {point}")

        # Display planning fields if present
        if hasattr(slide, 'analytics_needed') and slide.analytics_needed:
            output.append(f"  {Colors.CYAN}Analytics Needed:{Colors.ENDC}")
            output.append(f"    {slide.analytics_needed}")

        if hasattr(slide, 'visuals_needed') and slide.visuals_needed:
            output.append(f"  {Colors.HEADER}Visuals Needed:{Colors.ENDC}")
            output.append(f"    {slide.visuals_needed}")

        if hasattr(slide, 'diagrams_needed') and slide.diagrams_needed:
            output.append(f"  {Colors.YELLOW}Diagrams Needed:{Colors.ENDC}")
            output.append(f"    {slide.diagrams_needed}")

        if hasattr(slide, 'structure_preference') and slide.structure_preference:
            output.append(f"  {Colors.BLUE}Layout Preference:{Colors.ENDC} {slide.structure_preference}")

        return "\n".join(output)

    def format_enriched_slide(self, enriched_slide, slide_number: int) -> str:
        """Format an enriched slide with generated content (v3.1 Stage 6).

        v3.1.1: Enhanced to handle both structured (dict) and legacy (string) content formats.

        Args:
            enriched_slide: EnrichedSlide object with generated text
            slide_number: Slide number for display

        Returns:
            Formatted string with slide details and generated content
        """
        output = []
        slide = enriched_slide.original_slide

        output.append(f"\n{Colors.BOLD}{Colors.GREEN}Slide {slide_number}: {slide.title}{Colors.ENDC}")
        output.append(f"  Type: {slide.slide_type}")
        output.append(f"  ID: {enriched_slide.slide_id}")

        # Show generation status
        if enriched_slide.has_text_failure:
            output.append(f"  {Colors.RED}⚠️  Text Generation: FAILED{Colors.ENDC}")
            output.append(f"  {Colors.YELLOW}(Using placeholder content){Colors.ENDC}")
        elif enriched_slide.generated_text:
            output.append(f"  {Colors.GREEN}✅ Text Generation: SUCCESS{Colors.ENDC}")

            content = enriched_slide.generated_text.content

            # v3.1.1: Detect content format (structured dict vs legacy string)
            if isinstance(content, dict):
                # v1.1: Structured content with format ownership
                output.append(f"  {Colors.CYAN}📊 Format: Structured (v1.1 Text Service){Colors.ENDC}")
                output.append(f"\n  {Colors.BOLD}{Colors.CYAN}📝 Generated Fields:{Colors.ENDC}")

                for field_name, field_content in content.items():
                    output.append(f"\n    {Colors.BOLD}{field_name}:{Colors.ENDC}")

                    # Display field content with truncation
                    field_str = str(field_content)
                    if len(field_str) > 200:
                        field_preview = field_str[:200] + "..."
                    else:
                        field_preview = field_str

                    # Add indentation
                    for line in field_preview.split('\n'):
                        output.append(f"      {Colors.CYAN}│{Colors.ENDC} {line}")

                # Show field count
                output.append(f"\n    {Colors.BLUE}Total fields: {len(content)}{Colors.ENDC}")
            else:
                # v1.0: Legacy HTML/text string content
                output.append(f"  {Colors.YELLOW}📄 Format: Legacy HTML/Text (v1.0 Text Service){Colors.ENDC}")
                output.append(f"\n  {Colors.BOLD}{Colors.CYAN}📝 Generated Content:{Colors.ENDC}")

                # Truncate HTML for display
                if len(content) > 300:
                    content_preview = content[:300] + "..."
                else:
                    content_preview = content

                # Add indentation to content
                for line in content_preview.split('\n'):
                    output.append(f"  {Colors.CYAN}│{Colors.ENDC} {line}")

            # Show metadata
            if enriched_slide.generated_text.metadata:
                metadata = enriched_slide.generated_text.metadata
                output.append(f"\n  {Colors.BLUE}Metadata:{Colors.ENDC}")

                # v3.1.1: Show format ownership metadata if present
                if 'format_type' in metadata:
                    output.append(f"    Format Type: {metadata['format_type']}")
                if 'fields_generated' in metadata:
                    output.append(f"    Fields Generated: {metadata['fields_generated']}")

                # Standard metadata
                if 'word_count' in metadata:
                    output.append(f"    Words: {metadata['word_count']}")
                if 'generation_time_ms' in metadata:
                    output.append(f"    Generation Time: {metadata['generation_time_ms']}ms")
                if 'model_used' in metadata:
                    output.append(f"    Model: {metadata['model_used']}")
        else:
            output.append(f"  {Colors.YELLOW}No generated content{Colors.ENDC}")

        # Also show original planning info
        output.append(f"\n  {Colors.BOLD}Original Planning:{Colors.ENDC}")
        output.append(f"    Narrative: {slide.narrative}")
        output.append(f"    Key Points: {len(slide.key_points)} items")

        return "\n".join(output)

    def _restore_context_from_checkpoint(self, checkpoint_data: Dict[str, Any]):
        """Restore context from checkpoint data."""
        from src.models.agents import StateContext, UserIntent

        # Restore context data
        context_data = checkpoint_data["context"]

        # Handle user intent restoration
        user_intent = None
        if context_data.get("user_intent"):
            # If it's a string (legacy format), map it to proper intent
            if isinstance(context_data["user_intent"], str):
                # Map old format to new intent types
                intent_map = {
                    "BUILD_PRESENTATION": "Submit_Initial_Topic",
                    "REFINE": "Submit_Refinement_Request"
                }
                intent_type = intent_map.get(context_data["user_intent"], "Submit_Initial_Topic")
                user_intent = UserIntent(intent_type=intent_type, confidence=1.0)
            else:
                # It's already a dict with proper structure
                user_intent = UserIntent(**context_data["user_intent"])

        # Create context with required fields
        context = StateContext(
            current_state=context_data["current_state"],
            conversation_history=context_data.get("conversation_history", []),
            session_data=context_data.get("session_data", {}),
            user_intent=user_intent
        )

        return context

    def choose_scenario(self) -> Optional[str]:
        """Let user choose a scenario interactively."""
        print(f"\n{Colors.BOLD}Choose a scenario (1-5) or 'q' to quit:{Colors.ENDC} ", end="")

        scenario_map = {
            "1": "default",
            "2": "executive",
            "3": "technical",
            "4": "educational",
            "5": "sales"
        }

        while True:
            choice = input().strip().lower()
            if choice == 'q':
                print(f"{Colors.YELLOW}Exiting...{Colors.ENDC}")
                return None
            elif choice in scenario_map:
                return scenario_map[choice]
            else:
                print(f"{Colors.RED}Invalid choice. Please enter 1-5 or 'q':{Colors.ENDC} ", end="")

    async def run_scenario(self, scenario_name: str, test_stage_6: bool = True) -> Dict[str, Any]:
        """Run a test scenario through stages 1-6 (v3.1: includes CONTENT_GENERATION).

        Args:
            scenario_name: Name of the scenario to run
            test_stage_6: If True, includes Stage 6 (CONTENT_GENERATION) testing

        Returns:
            Dict with test results
        """
        if scenario_name not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}")

        scenario = self.scenarios[scenario_name]
        print(f"\n{Colors.BOLD}🎬 Running Scenario: {scenario['name']}{Colors.ENDC}")
        print(f"📖 Description: {scenario['description']}")
        if test_stage_6:
            print(f"📊 Testing Stages 1-6 (includes v3.1 CONTENT_GENERATION)")
        else:
            print(f"📊 Testing Stages 1-5 (up to REFINE_STRAWMAN - v2.0 mode)")

        # Show checkpoint info if applicable
        if self.start_stage or self.checkpoint_file:
            print(f"{Colors.CYAN}🔄 Using checkpoint to start from: {self.start_stage or 'loaded stage'}{Colors.ENDC}")
        if self.save_checkpoints:
            print(f"{Colors.YELLOW}💾 Checkpoints will be saved at each stage{Colors.ENDC}")

        print_separator()

        # Check debug mode
        debug_mode = os.getenv('DEBUG', '').lower() == 'true'

        results = {
            "scenario": scenario_name,
            "name": scenario["name"],
            "passed": True,
            "errors": [],
            "states_completed": [],
            "outputs": {}
        }

        # Initialize context and load checkpoint if specified
        context = None
        checkpoint_data = None
        skip_to_stage = None

        if self.checkpoint_file:
            # Load from specific checkpoint file
            try:
                checkpoint_data = self.checkpoint_manager.load_checkpoint_file(self.checkpoint_file)
                skip_to_stage = checkpoint_data["stage"]
                context = self._restore_context_from_checkpoint(checkpoint_data)
                results["outputs"] = checkpoint_data.get("stage_outputs", {})
                print(f"{Colors.GREEN}✅ Loaded checkpoint from: {self.checkpoint_file}{Colors.ENDC}")
                print(f"   Resuming from stage: {skip_to_stage}")
            except Exception as e:
                print(format_error(f"Failed to load checkpoint: {e}"))
                return results
        elif self.start_stage:
            # Load checkpoint for specified stage
            try:
                checkpoint_data = self.checkpoint_manager.load_checkpoint(scenario_name, self.start_stage)
                skip_to_stage = self.start_stage
                context = self._restore_context_from_checkpoint(checkpoint_data)
                results["outputs"] = checkpoint_data.get("stage_outputs", {})
                print(f"{Colors.GREEN}✅ Loaded checkpoint for stage: {self.start_stage}{Colors.ENDC}")
            except FileNotFoundError:
                print(format_error(f"No checkpoint found for {scenario_name}/{self.start_stage}"))
                print("Run with --save-checkpoints first to generate checkpoints")
                return results
            except Exception as e:
                print(format_error(f"Failed to load checkpoint: {e}"))
                return results

        if not context:
            # Initialize fresh context
            context = create_initial_context()

        try:
            # Define stage execution flags based on skip_to_stage (only stages 1-5)
            should_skip = {
                "PROVIDE_GREETING": False,
                "ASK_CLARIFYING_QUESTIONS": False,
                "CREATE_CONFIRMATION_PLAN": False,
                "GENERATE_STRAWMAN": False,
                "REFINE_STRAWMAN": False
            }

            if skip_to_stage:
                # Skip all stages before the target stage
                stage_index = self.checkpoint_manager.get_stage_index(skip_to_stage)
                for i, stage in enumerate(self.checkpoint_manager.STAGES[:5]):  # Only first 5 stages
                    if i < stage_index:
                        should_skip[stage] = True
                        results["states_completed"].append(stage)  # Mark as completed from checkpoint

            # Stage 1: PROVIDE_GREETING
            if not should_skip["PROVIDE_GREETING"]:
                print(f"\n{format_state('PROVIDE_GREETING')}")
                print("─" * 60)
                greeting = await self.director.process(context)

                # Handle protocol-specific display
                if self.use_streamlined:
                    messages = self.streamlined_packager.package_messages(
                        session_id=f"test_{scenario_name}",
                        state="PROVIDE_GREETING",
                        agent_output=greeting,
                        context=context
                    )
                    print(format_agent_message(self.format_streamlined_messages(messages)))
                else:
                    print(format_agent_message(greeting))

                add_to_history(context, "assistant", greeting)
                results["states_completed"].append("PROVIDE_GREETING")
                results["outputs"]["greeting"] = greeting

                # Simulate user providing initial topic
                user_topic = scenario["responses"]["initial_topic"]
                print(format_user_message(user_topic))
                add_to_history(context, "user", user_topic)

                # Classify intent and transition to next state
                intent = await self.intent_router.classify(
                    user_topic,
                    {
                        'current_state': context.current_state,
                        'recent_history': context.conversation_history[-3:] if context.conversation_history else []
                    }
                )
                context.user_intent = intent

                # Save initial topic to session data (simulating what websocket handler does)
                context.session_data['user_initial_request'] = user_topic
                context.current_state = "ASK_CLARIFYING_QUESTIONS"

                # Save checkpoint if enabled
                if self.save_checkpoints:
                    self.checkpoint_manager.save_checkpoint(
                        scenario_name,
                        "ASK_CLARIFYING_QUESTIONS",
                        context,
                        results["outputs"]
                    )

            # Stage 2: ASK_CLARIFYING_QUESTIONS
            if not should_skip["ASK_CLARIFYING_QUESTIONS"]:
                print(f"\n{format_state('ASK_CLARIFYING_QUESTIONS')}")
                print("─" * 60)
                questions = await self.director.process(context)

                # Handle protocol-specific display
                if self.use_streamlined:
                    messages = self.streamlined_packager.package_messages(
                        session_id=f"test_{scenario_name}",
                        state="ASK_CLARIFYING_QUESTIONS",
                        agent_output=questions,
                        context=context
                    )
                    print(format_agent_message(self.format_streamlined_messages(messages)))
                else:
                    print(format_agent_message(format_clarifying_questions(questions)))

                add_to_history(context, "assistant", questions)
                results["states_completed"].append("ASK_CLARIFYING_QUESTIONS")
                results["outputs"]["questions"] = questions

                # Validate questions
                if not self._validate_questions(questions, results):
                    return results

                # Simulate user answering questions
                user_answers = "\n".join(scenario["responses"]["clarifying_answers"])
                print(format_user_message(user_answers))
                add_to_history(context, "user", user_answers)

                # Save clarifying answers to session data
                context.session_data['clarifying_answers'] = {
                    "raw_answers": user_answers,
                    "timestamp": datetime.now().isoformat()
                }

                # Transition to CREATE_CONFIRMATION_PLAN
                context.current_state = "CREATE_CONFIRMATION_PLAN"

            # Stage 3: CREATE_CONFIRMATION_PLAN
            if not should_skip["CREATE_CONFIRMATION_PLAN"]:
                print(f"\n{format_state('CREATE_CONFIRMATION_PLAN')}")
                print("─" * 60)
                plan = await self.director.process(context)

                # Handle protocol-specific display
                if self.use_streamlined:
                    messages = self.streamlined_packager.package_messages(
                        session_id=f"test_{scenario_name}",
                        state="CREATE_CONFIRMATION_PLAN",
                        agent_output=plan,
                        context=context
                    )
                    print(format_agent_message(self.format_streamlined_messages(messages)))
                else:
                    print(format_agent_message(format_confirmation_plan(plan)))

                add_to_history(context, "assistant", plan)
                results["states_completed"].append("CREATE_CONFIRMATION_PLAN")
                results["outputs"]["plan"] = plan

                # Validate plan
                if not self._validate_plan(plan, results):
                    return results

                # Simulate user accepting plan
                print(format_user_message("Great, let's proceed with this plan."))
                add_to_history(context, "user", "Great, let's proceed with this plan.")

                # Transition to GENERATE_STRAWMAN
                context.current_state = "GENERATE_STRAWMAN"

            # Stage 4: GENERATE_STRAWMAN
            strawman = None
            if should_skip["GENERATE_STRAWMAN"] and "strawman" in results["outputs"]:
                strawman = results["outputs"]["strawman"]
                print(f"{Colors.CYAN}Using strawman from checkpoint{Colors.ENDC}")
            elif not should_skip["GENERATE_STRAWMAN"]:
                print(f"\n{format_state('GENERATE_STRAWMAN')}")
                print("─" * 60)

                # Show pre-generation status if streamlined
                if self.use_streamlined:
                    status_msg = self.streamlined_packager.create_pre_generation_status(
                        session_id=f"test_{scenario_name}",
                        state="GENERATE_STRAWMAN"
                    )
                    print(format_agent_message(f"⏳ {status_msg.payload.text}"))

                response = await self.director.process(context)

                # v2.0: Check if response is a URL (dict) or PresentationStrawman (object)
                if isinstance(response, dict) and response.get("type") == "presentation_url":
                    # v2.0 mode: deck-builder returned a URL
                    print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 Presentation Generated! (v2.0 deck-builder){Colors.ENDC}")
                    print(f"\n{Colors.CYAN}{'═' * 60}{Colors.ENDC}")
                    print(f"{Colors.BOLD}📊 Presentation URL:{Colors.ENDC}")
                    print(f"{Colors.GREEN}{response['url']}{Colors.ENDC}")
                    print(f"\n{Colors.BOLD}Details:{Colors.ENDC}")
                    print(f"  • Presentation ID: {response.get('presentation_id', 'N/A')}")
                    print(f"  • Number of Slides: {response.get('slide_count', 'N/A')}")
                    print(f"  • Message: {response.get('message', 'N/A')}")
                    print(f"{Colors.CYAN}{'═' * 60}{Colors.ENDC}")
                    print(f"\n{Colors.YELLOW}💡 Open the URL in your browser to view the presentation!{Colors.ENDC}")

                    # Store the URL response
                    strawman = response
                else:
                    # v1.0 mode: JSON response (fallback or deck-builder disabled)
                    strawman = response
                    print(f"{Colors.YELLOW}ℹ️  Returned JSON format (deck-builder disabled or unavailable){Colors.ENDC}")

                    # Handle protocol-specific display
                    if self.use_streamlined:
                        messages = self.streamlined_packager.package_messages(
                            session_id=f"test_{scenario_name}",
                            state="GENERATE_STRAWMAN",
                            agent_output=strawman,
                            context=context
                        )
                        print(format_agent_message(self.format_streamlined_messages(messages)))
                        print(f"{Colors.CYAN}[Streamlined: {len(messages)} messages with full JSON data]{Colors.ENDC}")

                        # Show slide details from the slide_update message
                        slide_update_msg = next((msg for msg in messages if msg.type == "slide_update"), None)
                        if slide_update_msg:
                            print(f"\n{Colors.BOLD}📄 Slide Content:{Colors.ENDC}")
                            for slide_data in slide_update_msg.payload.slides:
                                print(self.format_slide_details(slide_data))
                    else:
                        print(format_agent_message(format_strawman_summary(strawman)))
                        # Also show slide details for legacy protocol
                        print(f"\n{Colors.BOLD}📄 Slide Content:{Colors.ENDC}")
                        for slide in strawman.slides:
                            print(self.format_slide_details(slide))

                add_to_history(context, "assistant", strawman)
                results["states_completed"].append("GENERATE_STRAWMAN")
                results["outputs"]["strawman"] = strawman

                # v3.1: Extract and store strawman in session_data for subsequent stages
                if isinstance(strawman, dict) and strawman.get("type") == "presentation_url":
                    # Hybrid response with embedded strawman
                    if "strawman" in strawman:
                        strawman_obj = strawman["strawman"]
                        # Store in session_data for REFINE_STRAWMAN and CONTENT_GENERATION
                        if hasattr(strawman_obj, 'model_dump'):
                            context.session_data['presentation_strawman'] = strawman_obj.model_dump()
                        elif hasattr(strawman_obj, 'dict'):
                            context.session_data['presentation_strawman'] = strawman_obj.dict()
                        else:
                            context.session_data['presentation_strawman'] = strawman_obj
                elif hasattr(strawman, 'model_dump'):
                    # Direct PresentationStrawman object (fallback mode)
                    context.session_data['presentation_strawman'] = strawman.model_dump()
                elif hasattr(strawman, 'dict'):
                    context.session_data['presentation_strawman'] = strawman.dict()

                # Save checkpoint if enabled
                if self.save_checkpoints:
                    self.checkpoint_manager.save_checkpoint(
                        scenario_name,
                        "REFINE_STRAWMAN",
                        context,
                        results["outputs"]
                    )

            # Stage 5: REFINE_STRAWMAN (final stage for this test)
            refined_strawman = strawman
            if not should_skip["REFINE_STRAWMAN"]:
                # Simulate user requesting refinement
                refinement_request = scenario["responses"].get("refinement_request",
                    "Please enhance slide 3 with more specific data points and metrics.")
                print(format_user_message(refinement_request))
                add_to_history(context, "user", refinement_request)

                # Update intent to refinement
                context.user_intent = UserIntent(
                    intent_type="Submit_Refinement_Request",
                    confidence=1.0,
                    extracted_info=refinement_request
                )
                context.current_state = "REFINE_STRAWMAN"

                print(f"\n{format_state('REFINE_STRAWMAN')}")
                print("─" * 60)

                # Show pre-generation status if streamlined
                if self.use_streamlined:
                    status_msg = self.streamlined_packager.create_pre_generation_status(
                        session_id=f"test_{scenario_name}",
                        state="REFINE_STRAWMAN"
                    )
                    print(format_agent_message(f"⏳ {status_msg.payload.text}"))

                response = await self.director.process(context)

                # v2.0: Check if response is a URL (dict) or PresentationStrawman (object)
                if isinstance(response, dict) and response.get("type") == "presentation_url":
                    # v2.0 mode: deck-builder returned a URL
                    print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 Refined Presentation Generated! (v2.0 deck-builder){Colors.ENDC}")
                    print(f"\n{Colors.CYAN}{'═' * 60}{Colors.ENDC}")
                    print(f"{Colors.BOLD}📊 Refined Presentation URL:{Colors.ENDC}")
                    print(f"{Colors.GREEN}{response['url']}{Colors.ENDC}")
                    print(f"\n{Colors.BOLD}Details:{Colors.ENDC}")
                    print(f"  • Presentation ID: {response.get('presentation_id', 'N/A')}")
                    print(f"  • Number of Slides: {response.get('slide_count', 'N/A')}")
                    print(f"  • Message: {response.get('message', 'N/A')}")
                    print(f"{Colors.CYAN}{'═' * 60}{Colors.ENDC}")
                    print(f"\n{Colors.YELLOW}💡 Open the URL in your browser to view the refined presentation!{Colors.ENDC}")

                    # Store the URL response
                    refined_strawman = response
                else:
                    # v1.0 mode: JSON response (fallback or deck-builder disabled)
                    refined_strawman = response
                    print(f"{Colors.YELLOW}ℹ️  Returned JSON format (deck-builder disabled or unavailable){Colors.ENDC}")

                    # Handle protocol-specific display
                    if self.use_streamlined:
                        messages = self.streamlined_packager.package_messages(
                            session_id=f"test_{scenario_name}",
                            state="REFINE_STRAWMAN",
                            agent_output=refined_strawman,
                            context=context
                        )
                        print(format_agent_message(self.format_streamlined_messages(messages)))
                        print(f"{Colors.CYAN}[Streamlined: {len(messages)} messages with refined JSON data]{Colors.ENDC}")

                        # Show detailed slide content from the slide_update message
                        slide_update_msg = next((msg for msg in messages if msg.type == "slide_update"), None)
                        if slide_update_msg:
                            print(f"\n{Colors.BOLD}📄 Refined Slide Content:{Colors.ENDC}")
                            # Show only the affected slides
                            if slide_update_msg.payload.affected_slides:
                                print(f"{Colors.YELLOW}Affected slides: {', '.join(slide_update_msg.payload.affected_slides)}{Colors.ENDC}")
                            for slide_data in slide_update_msg.payload.slides:
                                print(self.format_slide_details(slide_data))
                    else:
                        print(format_agent_message("Strawman refined based on your feedback."))
                        # Also show refined slide details for legacy protocol
                        print(f"\n{Colors.BOLD}📄 Refined Slide Content:{Colors.ENDC}")
                        for slide in refined_strawman.slides:
                            print(self.format_slide_details(slide))

                # Validate refinement (only if JSON format)
                if 'strawman' in results["outputs"]:
                    # Check if both are JSON (have slides attribute)
                    if hasattr(refined_strawman, 'slides') and not isinstance(results["outputs"]["strawman"], dict):
                        original_strawman = results["outputs"]["strawman"]
                        if hasattr(original_strawman, 'slides'):
                            original_count = len(original_strawman.slides)
                            refined_count = len(refined_strawman.slides)
                            if refined_count != original_count:
                                print(format_error(f"Refinement changed slide count: {original_count} → {refined_count}"))
                                results["errors"].append(f"Refinement changed slide count from {original_count} to {refined_count}")
                            else:
                                print(format_success(f"Refinement preserved slide count: {refined_count} slides"))
                    elif isinstance(refined_strawman, dict) and isinstance(results["outputs"]["strawman"], dict):
                        # Both are URLs - compare slide counts if available
                        original_count = results["outputs"]["strawman"].get('slide_count', 'unknown')
                        refined_count = refined_strawman.get('slide_count', 'unknown')
                        print(f"{Colors.CYAN}Slide counts - Original: {original_count}, Refined: {refined_count}{Colors.ENDC}")

                add_to_history(context, "assistant", refined_strawman)
                results["states_completed"].append("REFINE_STRAWMAN")
                results["outputs"]["refined_strawman"] = refined_strawman

                # v3.1: Update session_data with refined strawman for CONTENT_GENERATION
                if isinstance(refined_strawman, dict) and refined_strawman.get("type") == "presentation_url":
                    # Hybrid response with embedded strawman
                    if "strawman" in refined_strawman:
                        strawman_obj = refined_strawman["strawman"]
                        # Update session_data for CONTENT_GENERATION
                        if hasattr(strawman_obj, 'model_dump'):
                            context.session_data['presentation_strawman'] = strawman_obj.model_dump()
                        elif hasattr(strawman_obj, 'dict'):
                            context.session_data['presentation_strawman'] = strawman_obj.dict()
                        else:
                            context.session_data['presentation_strawman'] = strawman_obj
                elif hasattr(refined_strawman, 'model_dump'):
                    # Direct PresentationStrawman object (fallback mode)
                    context.session_data['presentation_strawman'] = refined_strawman.model_dump()
                elif hasattr(refined_strawman, 'dict'):
                    context.session_data['presentation_strawman'] = refined_strawman.dict()

            # Stage 6: CONTENT_GENERATION (v3.1 NEW)
            if test_stage_6:
                # Simulate user accepting the strawman to trigger Stage 6
                print(format_user_message("Yes, I'm happy with this strawman. Please generate the presentation with real content."))
                add_to_history(context, "user", "Yes, I'm happy with this strawman. Please generate the presentation.")

                # Update intent and state for Stage 6
                context.user_intent = UserIntent(
                    intent_type="Accept_Strawman",
                    confidence=1.0
                )

                # v3.1: Store strawman in session_data for Stage 6 processing
                # Extract strawman from hybrid response (URL + embedded strawman)
                if isinstance(refined_strawman, dict) and refined_strawman.get("type") == "presentation_url" and "strawman" in refined_strawman:
                    # v2.0/v3.1: Hybrid response with embedded strawman
                    strawman_obj = refined_strawman["strawman"]
                    if hasattr(strawman_obj, 'model_dump'):
                        context.session_data['presentation_strawman'] = strawman_obj.model_dump()
                    elif hasattr(strawman_obj, 'dict'):
                        context.session_data['presentation_strawman'] = strawman_obj.dict()
                    elif isinstance(strawman_obj, dict):
                        context.session_data['presentation_strawman'] = strawman_obj
                elif not isinstance(refined_strawman, dict):  # If it's a PresentationStrawman object
                    # v1.0: Direct strawman object
                    context.session_data['presentation_strawman'] = refined_strawman.model_dump() if hasattr(refined_strawman, 'model_dump') else refined_strawman.dict()
                elif 'presentation_strawman' not in context.session_data:
                    # Fallback: Use the original strawman from outputs
                    original_strawman = results["outputs"].get("strawman")
                    if original_strawman:
                        if hasattr(original_strawman, 'model_dump'):
                            context.session_data['presentation_strawman'] = original_strawman.model_dump()
                        elif hasattr(original_strawman, 'dict'):
                            context.session_data['presentation_strawman'] = original_strawman.dict()
                        elif isinstance(original_strawman, dict):
                            context.session_data['presentation_strawman'] = original_strawman

                context.current_state = "CONTENT_GENERATION"

                print(f"\n{format_state('CONTENT_GENERATION')} {Colors.CYAN}(v3.1 NEW){Colors.ENDC}")
                print("─" * 60)
                print(f"{Colors.YELLOW}⏳ Generating real text content for slides (5-15s per slide)...{Colors.ENDC}")

                # Show pre-generation status if streamlined
                if self.use_streamlined:
                    status_msg = self.streamlined_packager.create_pre_generation_status(
                        session_id=f"test_{scenario_name}",
                        state="CONTENT_GENERATION"
                    )
                    print(format_agent_message(f"⏳ {status_msg.payload.text}"))

                # Process Stage 6
                response = await self.director.process(context)

                # Check response type (v3.1 should return dict with URL and content info)
                if isinstance(response, dict) and response.get("type") == "presentation_url":
                    print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 Presentation with Real Content Generated! (v3.1){Colors.ENDC}")
                    print(f"\n{Colors.CYAN}{'═' * 60}{Colors.ENDC}")
                    print(f"{Colors.BOLD}📊 Presentation URL:{Colors.ENDC}")
                    print(f"{Colors.GREEN}{response['url']}{Colors.ENDC}")
                    print(f"\n{Colors.BOLD}Content Generation Results:{Colors.ENDC}")
                    print(f"  • Total Slides: {response.get('slide_count', 'N/A')}")
                    print(f"  • Content Generated: {response.get('content_generated', False)}")
                    if 'successful_slides' in response:
                        print(f"  • Successful: {response['successful_slides']}/{response.get('slide_count', 0)} slides")
                    if 'failed_slides' in response:
                        failed = response['failed_slides']
                        if failed > 0:
                            print(f"  • {Colors.YELLOW}Failed: {failed} slides (using placeholders){Colors.ENDC}")
                    if 'generation_metadata' in response:
                        metadata = response['generation_metadata']
                        if 'total_generation_time_ms' in metadata:
                            total_time = metadata['total_generation_time_ms'] / 1000
                            print(f"  • Generation Time: {total_time:.1f}s")

                    # Show enriched content preview if available
                    if 'enriched_data' in response:
                        enriched_data = response['enriched_data']
                        print(f"\n{Colors.BOLD}{Colors.CYAN}📝 Generated Content Preview:{Colors.ENDC}")
                        if hasattr(enriched_data, 'enriched_slides'):
                            for idx, enriched_slide in enumerate(enriched_data.enriched_slides[:3]):  # Show first 3
                                print(self.format_enriched_slide(enriched_slide, idx + 1))
                            if len(enriched_data.enriched_slides) > 3:
                                print(f"\n  {Colors.CYAN}... and {len(enriched_data.enriched_slides) - 3} more slides{Colors.ENDC}")

                    print(f"{Colors.CYAN}{'═' * 60}{Colors.ENDC}")
                    print(f"\n{Colors.YELLOW}💡 Open the URL in your browser to view the presentation with REAL CONTENT!{Colors.ENDC}")

                    results["states_completed"].append("CONTENT_GENERATION")
                    results["outputs"]["content_generation"] = response
                else:
                    print(f"{Colors.YELLOW}⚠️  Stage 6 returned unexpected format{Colors.ENDC}")
                    results["errors"].append("Stage 6 did not return expected presentation URL format")

                add_to_history(context, "assistant", response)

            # Test complete
            if test_stage_6:
                print(f"\n{Colors.BOLD}{Colors.GREEN}✅ Test Complete - Stages 1-6 Successfully Executed (v3.1){Colors.ENDC}")
            else:
                print(f"\n{Colors.BOLD}{Colors.GREEN}✅ Test Complete - Stages 1-5 Successfully Executed{Colors.ENDC}")
            print(f"   States completed: {', '.join(results['states_completed'])}")

            # Final validation
            validation_results = self._run_validation(results, test_stage_6=test_stage_6)

            # Display validation results
            if validation_results["passed"]:
                print(f"\n{Colors.GREEN}✅ Validation: PASSED{Colors.ENDC}")
            else:
                print(f"\n{Colors.RED}❌ Validation: FAILED{Colors.ENDC}")

            print(f"\n{Colors.BOLD}Validation Checks:{Colors.ENDC}")
            for check, status in validation_results["checks"].items():
                print(f"  {check}: {status}")

            # v3.1.1: Display format ownership validation
            if "format_ownership" in validation_results:
                format_val = validation_results["format_ownership"]
                print(f"\n{Colors.BOLD}{Colors.CYAN}Format Ownership Validation (v3.1.1):{Colors.ENDC}")
                print(f"  Content Format: {format_val['content_format']}")
                print(f"  Structured: {format_val['is_structured']}")
                print(f"  Has Format Specs: {format_val['has_format_specs']}")
                if format_val['notes']:
                    print(f"\n  {Colors.BOLD}Notes:{Colors.ENDC}")
                    for note in format_val['notes']:
                        print(f"    {note}")

            # Save conversation history if debug mode
            # Disabled for now - save_conversation expects different format
            # if debug_mode:
            #     save_conversation(scenario_name, context)

            return results

        except Exception as e:
            print(format_error(f"Test failed with error: {str(e)}"))
            results["passed"] = False
            results["errors"].append(str(e))

            if debug_mode:
                import traceback
                print(f"\n{Colors.YELLOW}Debug Traceback:{Colors.ENDC}")
                print(traceback.format_exc())

            return results

    def _validate_questions(self, questions, results: Dict[str, Any]) -> bool:
        """Validate clarifying questions."""
        if not questions or not hasattr(questions, 'questions'):
            results["errors"].append("No clarifying questions generated")
            results["passed"] = False
            return False

        # Use the validation rules from the flat structure
        min_questions = self.validation_rules.get("min_questions", 3)
        max_questions = self.validation_rules.get("max_questions", 7)
        question_count = len(questions.questions)

        if question_count < min_questions:
            error = f"Too few questions: {question_count} < {min_questions}"
            print(format_error(error))
            results["errors"].append(error)
            results["passed"] = False
            return False

        if question_count > max_questions:
            error = f"Too many questions: {question_count} > {max_questions}"
            print(format_error(error))
            results["errors"].append(error)
            results["passed"] = False
            return False

        print(format_success(f"✓ Generated {question_count} clarifying questions"))
        return True

    def _validate_plan(self, plan, results: Dict[str, Any]) -> bool:
        """Validate confirmation plan."""
        if not plan:
            results["errors"].append("No confirmation plan generated")
            results["passed"] = False
            return False

        # Use the validation rules from the flat structure
        min_slides = self.validation_rules.get("min_slides", 5)
        max_slides = self.validation_rules.get("max_slides", 20)

        # Check slide count
        slide_count = plan.proposed_slide_count if hasattr(plan, 'proposed_slide_count') else 0
        if slide_count < min_slides:
            error = f"Too few slides: {slide_count} < {min_slides}"
            print(format_error(error))
            results["errors"].append(error)
            results["passed"] = False
            return False

        if slide_count > max_slides:
            error = f"Too many slides: {slide_count} > {max_slides}"
            print(format_error(error))
            results["errors"].append(error)
            results["passed"] = False
            return False

        print(format_success(f"✓ Plan proposes {slide_count} slides"))
        return True

    def _validate_format_ownership(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Format Ownership Architecture features (v3.1.1).

        Checks if content is using v1.1 structured format and if format
        specifications are properly included.

        Args:
            results: Test results dictionary

        Returns:
            Dictionary with format ownership validation results
        """
        format_validation = {
            "content_format": "unknown",
            "is_structured": False,
            "has_format_specs": False,
            "notes": []
        }

        # Check if content_generation output exists
        if "content_generation" not in results["outputs"]:
            format_validation["notes"].append("No content generation output to validate")
            return format_validation

        content_gen = results["outputs"]["content_generation"]

        # Check for enriched data
        if "enriched_data" in content_gen:
            enriched_data = content_gen["enriched_data"]

            if hasattr(enriched_data, 'enriched_slides') and enriched_data.enriched_slides:
                # Check first slide's content format
                first_slide = enriched_data.enriched_slides[0]

                if first_slide.generated_text:
                    content = first_slide.generated_text.content

                    # Detect format
                    if isinstance(content, dict):
                        format_validation["content_format"] = "structured (v1.1)"
                        format_validation["is_structured"] = True
                        format_validation["notes"].append(f"✅ Using v1.1 structured content with {len(content)} fields")
                    else:
                        format_validation["content_format"] = "legacy HTML/text (v1.0)"
                        format_validation["is_structured"] = False
                        format_validation["notes"].append("ℹ️  Using v1.0 legacy content format")

                    # Check for format specifications in metadata
                    if first_slide.generated_text.metadata:
                        metadata = first_slide.generated_text.metadata

                        if 'field_metadata' in metadata or 'format_type' in metadata:
                            format_validation["has_format_specs"] = True
                            format_validation["notes"].append("✅ Format specifications present in metadata")
                        else:
                            format_validation["notes"].append("⚠️  No format specifications in metadata")

        return format_validation

    def _run_validation(self, results: Dict[str, Any], test_stage_6: bool = True) -> Dict[str, Any]:
        """Run comprehensive validation on test results.

        Args:
            results: Test results dictionary
            test_stage_6: If True, validates Stage 6 (CONTENT_GENERATION) completion

        Returns:
            Dictionary with validation status and checks
        """
        validation = {
            "passed": True,
            "checks": {}
        }

        # Check required states completed (Stages 1-5 always required)
        required_states = ["PROVIDE_GREETING", "ASK_CLARIFYING_QUESTIONS",
                         "CREATE_CONFIRMATION_PLAN", "GENERATE_STRAWMAN"]

        # Add Stage 6 if testing it
        if test_stage_6:
            required_states.append("CONTENT_GENERATION")

        for state in required_states:
            if state in results["states_completed"]:
                validation["checks"][state] = "✓"
            else:
                validation["checks"][state] = "✗"
                validation["passed"] = False

        # Check outputs (Stages 1-5 always required)
        required_outputs = ["greeting", "questions", "plan", "strawman"]

        # Add content_generation output if testing Stage 6
        if test_stage_6:
            required_outputs.append("content_generation")

        for output in required_outputs:
            if output in results["outputs"] and results["outputs"][output]:
                validation["checks"][f"output_{output}"] = "✓"
            else:
                validation["checks"][f"output_{output}"] = "✗"
                validation["passed"] = False

        # v3.1.1: Validate Format Ownership Architecture features
        if test_stage_6:
            format_validation = self._validate_format_ownership(results)
            validation["format_ownership"] = format_validation

            # Add format validation to checks
            if format_validation["is_structured"]:
                validation["checks"]["v1.1_structured_content"] = "✓"
            else:
                validation["checks"]["v1.0_legacy_content"] = "✓"

        return validation


async def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="Test the standalone Director Agent (Stages 1-6)")
    parser.add_argument(
        "--scenario",
        type=str,
        choices=["default", "executive", "technical", "educational", "sales"],
        help="Specific scenario to run"
    )
    parser.add_argument(
        "--save-checkpoints",
        action="store_true",
        help="Save checkpoints at each stage for resumption"
    )
    parser.add_argument(
        "--start-stage",
        type=str,
        choices=["ASK_CLARIFYING_QUESTIONS", "CREATE_CONFIRMATION_PLAN",
                "GENERATE_STRAWMAN", "REFINE_STRAWMAN"],
        help="Start from a specific stage (requires --save-checkpoints to have been run first)"
    )
    parser.add_argument(
        "--load-checkpoint",
        type=str,
        help="Load from a specific checkpoint file"
    )
    parser.add_argument(
        "--no-stage-6",
        action="store_true",
        help="Skip Stage 6 (CONTENT_GENERATION) testing, only test Stages 1-5 (v2.0 compatibility mode)"
    )

    args = parser.parse_args()

    # Initialize tester
    tester = DirectorStandaloneTester(
        save_checkpoints=args.save_checkpoints,
        start_stage=args.start_stage,
        checkpoint_file=args.load_checkpoint
    )

    # Print header
    test_mode = "Stages 1-5" if args.no_stage_6 else "Stages 1-6"
    print(f"\n{Colors.BOLD}{Colors.HEADER}═══════════════════════════════════════════════════════════{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}     Director Agent Standalone Test Suite ({test_mode})     {Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}═══════════════════════════════════════════════════════════{Colors.ENDC}")

    if args.no_stage_6:
        print(f"{Colors.YELLOW}ℹ️  Stage 6 (CONTENT_GENERATION) testing disabled - v2.0 compatibility mode{Colors.ENDC}")

    # Show protocol info
    if tester.use_streamlined:
        print(f"{Colors.CYAN}Protocol: Streamlined WebSocket (enabled){Colors.ENDC}")
    else:
        print(f"{Colors.YELLOW}Protocol: Legacy (streamlined disabled){Colors.ENDC}")

    # Determine which scenario to run
    if args.scenario:
        scenario_name = args.scenario
    else:
        # Interactive mode
        tester.show_scenarios_menu()
        scenario_name = tester.choose_scenario()

        if not scenario_name:
            return

    # Run the test (with or without Stage 6 based on flag)
    results = await tester.run_scenario(scenario_name, test_stage_6=not args.no_stage_6)

    # Print summary
    expected_states = 5 if args.no_stage_6 else 6
    print(f"\n{Colors.BOLD}═══════════════════════════════════════════════════════════{Colors.ENDC}")
    print(f"{Colors.BOLD}Test Summary:{Colors.ENDC}")
    print(f"  Scenario: {results['name']}")
    print(f"  States Completed: {len(results['states_completed'])}/{expected_states}")
    print(f"  Errors: {len(results['errors'])}")

    if results['passed']:
        print(f"  {Colors.GREEN}Result: PASSED ✅{Colors.ENDC}")
    else:
        print(f"  {Colors.RED}Result: FAILED ❌{Colors.ENDC}")
        if results['errors']:
            print(f"\n  Errors:")
            for error in results['errors']:
                print(f"    • {error}")

    print(f"{Colors.BOLD}═══════════════════════════════════════════════════════════{Colors.ENDC}")

if __name__ == "__main__":
    asyncio.run(main())