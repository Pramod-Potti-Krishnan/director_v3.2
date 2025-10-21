#!/usr/bin/env python3
"""
Isolated Stage 6 (CONTENT_GENERATION) Test
==========================================

Tests ONLY Stage 6 with mocked input from Stage 5.
This isolates the Text Service integration and content generation logic.

Run: python3 tests/test_stage6_only.py
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.director import DirectorAgent
from src.models.agents import StateContext, UserIntent, Slide, PresentationStrawman
from src.utils.logger import setup_logger
from dotenv import load_dotenv

load_dotenv()
logger = setup_logger(__name__)


class Stage6Tester:
    """Focused tester for Stage 6 (CONTENT_GENERATION)"""

    def __init__(self):
        self.director = DirectorAgent()

    def create_mock_strawman(self) -> PresentationStrawman:
        """Create a realistic mock strawman as if it came from Stage 5"""

        slides = [
            Slide(
                slide_number=1,
                slide_id="slide-intro-1",
                slide_type="content_heavy",
                title="Introduction to AI in Healthcare",
                narrative="Overview of how artificial intelligence is transforming healthcare delivery and diagnostics",
                key_points=[
                    "AI-powered diagnostics improve accuracy by 30%",
                    "Predictive analytics reduce hospital readmissions",
                    "Natural language processing streamlines medical records"
                ],
                visuals_needed=None,
                diagrams_needed=None,
                analytics_needed=None
            ),
            Slide(
                slide_number=2,
                slide_id="slide-diagnostic-2",
                slide_type="data_driven",
                title="AI in Diagnostic Imaging",
                narrative="Real-world case studies of AI-powered diagnostic imaging systems",
                key_points=[
                    "Radiology AI detects tumors with 95% accuracy",
                    "Reduces diagnosis time by 50%",
                    "FDA-approved AI tools in clinical use"
                ],
                visuals_needed=None,
                diagrams_needed=None,
                analytics_needed=None
            ),
            Slide(
                slide_number=3,
                slide_id="slide-patient-3",
                slide_type="content_heavy",
                title="Patient Outcomes and Benefits",
                narrative="Measurable improvements in patient care through AI implementation",
                key_points=[
                    "Early disease detection saves lives",
                    "Reduced false positives improve patient experience",
                    "Cost savings of $150B annually projected"
                ],
                visuals_needed=None,
                diagrams_needed=None,
                analytics_needed=None
            ),
            Slide(
                slide_number=4,
                slide_id="slide-challenges-4",
                slide_type="content_heavy",
                title="Implementation Challenges",
                narrative="Key obstacles and considerations for healthcare AI adoption",
                key_points=[
                    "Data privacy and HIPAA compliance",
                    "Integration with existing EHR systems",
                    "Training medical staff on AI tools"
                ],
                visuals_needed=None,
                diagrams_needed=None,
                analytics_needed=None
            )
        ]

        strawman = PresentationStrawman(
            main_title="AI in Healthcare: Diagnostic Applications and Patient Outcomes",
            overall_theme="Healthcare Technology Innovation",
            target_audience="Healthcare professionals at medical conference",
            design_suggestions="Modern professional with medical blue tones",
            presentation_duration=20,
            slides=slides
        )

        return strawman

    def create_mock_context(self, strawman: PresentationStrawman) -> StateContext:
        """Create a StateContext with mocked Stage 5 output"""

        context = StateContext(
            current_state="CONTENT_GENERATION",
            user_intent=UserIntent(
                intent_type="Accept_Strawman",
                confidence=1.0
            ),
            session_data={
                "session_id": "test-stage6-isolated",
                "presentation_strawman": strawman.model_dump(),  # Use model_dump() instead of dict()
                "user_initial_request": "I need a presentation about AI in healthcare, focusing on diagnostic applications and patient outcomes",
                "clarifying_answers": {
                    "audience": "Healthcare professionals at a medical conference",
                    "duration": "20 minutes",
                    "focus": "Recent case studies and real-world implementations",
                    "approach": "Include both benefits and challenges"
                }
            },
            conversation_history=[]
        )

        return context

    async def test_stage6(self):
        """Test Stage 6 content generation with mocked input"""

        print("\n" + "="*70)
        print("🧪 ISOLATED STAGE 6 TEST - Text Service Content Generation")
        print("="*70)

        # Step 1: Create mock strawman
        print("\n📝 Step 1: Creating mock strawman from Stage 5...")
        strawman = self.create_mock_strawman()
        print(f"   ✅ Mock strawman created:")
        print(f"      Title: {strawman.main_title}")
        print(f"      Slides: {len(strawman.slides)}")
        print(f"      Audience: {strawman.target_audience}")

        # Step 2: Create mock context
        print("\n📝 Step 2: Creating StateContext for Stage 6...")
        context = self.create_mock_context(strawman)
        print(f"   ✅ Context created:")
        print(f"      Session ID: {context.session_data.get('session_id')}")
        print(f"      Current State: {context.current_state}")
        print(f"      Strawman in session_data: {'presentation_strawman' in context.session_data}")

        # Step 3: Call Director.process() for Stage 6
        print("\n📝 Step 3: Calling Director.process() for CONTENT_GENERATION...")
        print("   ⏳ This will take 5-15 seconds per slide (~20-60 seconds total)")
        print("   🔗 Connecting to Text Service: https://web-production-e3796.up.railway.app")

        try:
            response = await self.director.process(context)

            # Step 4: Verify response
            print("\n" + "="*70)
            print("✅ STAGE 6 TEST RESULT: SUCCESS")
            print("="*70)

            if isinstance(response, dict) and response.get("type") == "presentation_url":
                print(f"\n📊 Presentation URL:")
                print(f"   {response['url']}")

                print(f"\n📈 Content Generation Stats:")
                print(f"   Total Slides: {response.get('slide_count', 'N/A')}")
                print(f"   Content Generated: {response.get('content_generated', False)}")
                print(f"   Successful: {response.get('successful_slides', 0)}/{response.get('slide_count', 0)} slides")
                print(f"   Failed: {response.get('failed_slides', 0)} slides")

                if 'generation_metadata' in response:
                    metadata = response['generation_metadata']
                    if 'total_generation_time_ms' in metadata:
                        total_time = metadata['total_generation_time_ms'] / 1000
                        print(f"   Generation Time: {total_time:.1f}s")

                # Show enriched content preview
                if 'enriched_data' in response:
                    enriched_data = response['enriched_data']
                    print(f"\n📝 Generated Content Preview (First 2 Slides):")

                    if hasattr(enriched_data, 'enriched_slides'):
                        for idx, enriched_slide in enumerate(enriched_data.enriched_slides[:2]):
                            print(f"\n   {'─'*60}")
                            print(f"   Slide {idx + 1}: {enriched_slide.original_slide.title}")

                            if enriched_slide.has_text_failure:
                                print(f"   ⚠️  Text Generation: FAILED (using placeholder)")
                            elif enriched_slide.generated_text:
                                print(f"   ✅ Text Generation: SUCCESS")
                                content = enriched_slide.generated_text.content
                                preview = content[:200] + "..." if len(content) > 200 else content
                                print(f"   Content: {preview}")

                                if enriched_slide.generated_text.metadata:
                                    meta = enriched_slide.generated_text.metadata
                                    print(f"   Words: {meta.get('word_count', 'N/A')}")
                                    print(f"   Time: {meta.get('generation_time_ms', 'N/A')}ms")
                                    print(f"   Model: {meta.get('model_used', 'N/A')}")

                print(f"\n{'='*70}")
                print("✅ Stage 6 is working correctly!")
                print("💡 Open the URL in your browser to see the presentation with REAL CONTENT")
                print(f"{'='*70}\n")

                return True
            else:
                print(f"\n❌ Unexpected response format: {type(response)}")
                print(f"Response: {response}")
                return False

        except Exception as e:
            print(f"\n{'='*70}")
            print("❌ STAGE 6 TEST RESULT: FAILED")
            print(f"{'='*70}")
            print(f"\nError: {str(e)}")

            import traceback
            print(f"\nFull Traceback:")
            traceback.print_exc()

            print(f"\n{'='*70}")
            print("🔍 Troubleshooting Tips:")
            print("   1. Check if Text Service is running: https://web-production-e3796.up.railway.app")
            print("   2. Verify .env has TEXT_SERVICE_URL set correctly")
            print("   3. Check network connectivity")
            print(f"{'='*70}\n")

            return False


async def main():
    """Run the isolated Stage 6 test"""
    tester = Stage6Tester()
    success = await tester.test_stage6()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
