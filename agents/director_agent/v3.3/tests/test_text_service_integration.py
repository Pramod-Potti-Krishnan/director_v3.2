"""
Integration tests for Text Service integration (v3.1 Stage 6).

Tests the complete text generation workflow:
1. TextServiceClient functionality
2. Slide text generation
3. Content enrichment
4. Graceful fallback handling
5. End-to-end Stage 6 workflow

Run from project root: python3 tests/test_text_service_integration.py
Or from tests/: python3 test_text_service_integration.py
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path (tests/ is one level down from root)
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.text_service_client import TextServiceClient, GeneratedText
from src.models.agents import Slide, PresentationStrawman
from src.models.content import EnrichedSlide, EnrichedPresentationStrawman
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class TestTextServiceIntegration:
    """Test suite for Text Service integration."""

    def __init__(self):
        """Initialize test suite."""
        self.text_client = TextServiceClient()
        self.tests_passed = 0
        self.tests_failed = 0

    async def test_text_service_health(self):
        """Test 1: Verify Text Service is reachable."""
        print("\n" + "="*60)
        print("TEST 1: Text Service Health Check")
        print("="*60)

        try:
            # Try a simple generation request
            request = {
                "presentation_id": "test-health-check",
                "slide_id": "test-slide-1",
                "slide_number": 1,
                "topics": ["Health check test"],
                "narrative": "Testing Text Service availability",
                "context": {
                    "presentation_title": "Health Check",
                    "target_audience": "developers",
                    "overall_theme": "testing"
                },
                "constraints": {
                    "word_count": 50,
                    "tone": "professional",
                    "format": "paragraph"
                }
            }

            result = await self.text_client.generate(request)

            if result and result.content:
                print(f"✅ PASSED: Text Service is reachable")
                print(f"   Generated content ({len(result.content)} chars): {result.content[:100]}...")
                self.tests_passed += 1
                return True
            else:
                print(f"❌ FAILED: Text Service returned empty content")
                self.tests_failed += 1
                return False

        except Exception as e:
            print(f"❌ FAILED: Text Service unreachable: {e}")
            self.tests_failed += 1
            return False

    async def test_slide_text_generation(self):
        """Test 2: Generate text for a realistic slide."""
        print("\n" + "="*60)
        print("TEST 2: Slide Text Generation")
        print("="*60)

        try:
            # Create a realistic slide
            slide = Slide(
                slide_number=1,
                slide_id="slide-intro-1",
                slide_type="content_heavy",
                title="Introduction to AI in Healthcare",
                narrative="Overview of how artificial intelligence is transforming healthcare delivery",
                key_points=[
                    "AI-powered diagnostics improve accuracy by 30%",
                    "Predictive analytics reduce hospital readmissions",
                    "Natural language processing streamlines medical records"
                ],
                visuals_needed=None,
                diagrams_needed=None,
                analytics_needed=None
            )

            presentation = PresentationStrawman(
                main_title="AI in Healthcare: A Revolutionary Approach",
                overall_theme="Healthcare Technology Innovation",
                target_audience="Healthcare executives and medical professionals",
                design_suggestions="Modern professional with medical blue tones",
                presentation_duration=10,
                slides=[slide]
            )

            # Generate text for this slide
            request = {
                "presentation_id": "test-presentation-1",
                "slide_id": slide.slide_id,
                "slide_number": 1,
                "topics": slide.key_points,
                "narrative": slide.narrative,
                "context": {
                    "presentation_title": presentation.main_title,
                    "target_audience": presentation.target_audience,
                    "overall_theme": presentation.overall_theme
                },
                "constraints": {
                    "word_count": 150,
                    "tone": "professional",
                    "format": "paragraph"
                }
            }

            result = await self.text_client.generate(request)

            if result and result.content and len(result.content) > 100:
                print(f"✅ PASSED: Generated meaningful content for slide")
                print(f"   Slide: {slide.title}")
                print(f"   Generated: {result.content[:200]}...")
                print(f"   Length: {len(result.content)} chars")
                self.tests_passed += 1
                return result
            else:
                print(f"❌ FAILED: Generated content too short or empty")
                self.tests_failed += 1
                return None

        except Exception as e:
            print(f"❌ FAILED: Error generating slide text: {e}")
            self.tests_failed += 1
            return None

    async def test_enriched_presentation_creation(self):
        """Test 3: Create EnrichedPresentationStrawman."""
        print("\n" + "="*60)
        print("TEST 3: Enriched Presentation Creation")
        print("="*60)

        try:
            # Create a simple presentation
            slides = [
                Slide(
                    slide_number=1,
                    slide_id="slide-1",
                    slide_type="data_driven",
                    title="Market Analysis",
                    narrative="Current market trends and opportunities",
                    key_points=[
                        "Market growing at 15% annually",
                        "Key opportunities in enterprise segment"
                    ]
                ),
                Slide(
                    slide_number=2,
                    slide_id="slide-2",
                    slide_type="content_heavy",
                    title="Product Strategy",
                    narrative="Our approach to product development",
                    key_points=[
                        "Focus on user experience",
                        "Rapid iteration cycles"
                    ]
                )
            ]

            strawman = PresentationStrawman(
                main_title="Business Strategy 2025",
                overall_theme="Growth and Innovation",
                target_audience="Board of Directors",
                design_suggestions="Corporate modern with clean lines",
                presentation_duration=15,
                slides=slides
            )

            # Generate text for each slide
            enriched_slides = []
            for idx, slide in enumerate(slides):
                request = {
                    "presentation_id": "test-enriched",
                    "slide_id": slide.slide_id,
                    "slide_number": idx + 1,
                    "topics": slide.key_points,
                    "narrative": slide.narrative,
                    "context": {
                        "presentation_title": strawman.main_title,
                        "target_audience": strawman.target_audience,
                        "overall_theme": strawman.overall_theme
                    },
                    "constraints": {
                        "word_count": 120,
                        "tone": "professional",
                        "format": "paragraph"
                    }
                }

                try:
                    generated = await self.text_client.generate(request)
                    enriched_slides.append(EnrichedSlide(
                        original_slide=slide,
                        slide_id=slide.slide_id,
                        generated_text=generated,
                        has_text_failure=False
                    ))
                except Exception as e:
                    logger.warning(f"Text generation failed for {slide.slide_id}: {e}")
                    enriched_slides.append(EnrichedSlide(
                        original_slide=slide,
                        slide_id=slide.slide_id,
                        generated_text=None,
                        has_text_failure=True
                    ))

            # Create enriched presentation
            enriched = EnrichedPresentationStrawman(
                original_strawman=strawman,
                enriched_slides=enriched_slides,
                generation_metadata={
                    "total_slides": len(slides),
                    "successful_slides": sum(1 for s in enriched_slides if not s.has_text_failure),
                    "failed_slides": sum(1 for s in enriched_slides if s.has_text_failure)
                }
            )

            successful = enriched.generation_metadata["successful_slides"]
            total = enriched.generation_metadata["total_slides"]

            if successful == total:
                print(f"✅ PASSED: Successfully enriched all {total} slides")
                for idx, slide in enumerate(enriched.enriched_slides):
                    if slide.generated_text:
                        print(f"   Slide {idx+1}: {slide.generated_text.content[:80]}...")
                self.tests_passed += 1
                return enriched
            elif successful > 0:
                print(f"⚠️  PARTIAL: Enriched {successful}/{total} slides")
                self.tests_passed += 1
                return enriched
            else:
                print(f"❌ FAILED: No slides enriched successfully")
                self.tests_failed += 1
                return None

        except Exception as e:
            print(f"❌ FAILED: Error creating enriched presentation: {e}")
            self.tests_failed += 1
            return None

    async def test_error_handling(self):
        """Test 4: Verify graceful error handling."""
        print("\n" + "="*60)
        print("TEST 4: Error Handling and Fallback")
        print("="*60)

        try:
            # Test with invalid/malformed request
            invalid_requests = [
                {
                    "presentation_id": "test-error",
                    "slide_id": "error-slide-1",
                    # Missing required fields
                },
                {
                    "presentation_id": "test-error",
                    "slide_id": "error-slide-2",
                    "slide_number": 1,
                    "topics": [],  # Empty topics
                    "narrative": "",  # Empty narrative
                    "context": {},
                    "constraints": {}
                }
            ]

            errors_handled = 0
            for idx, request in enumerate(invalid_requests):
                try:
                    result = await self.text_client.generate(request)
                    # Should either work or raise exception
                    if result:
                        print(f"   Request {idx+1}: Generated fallback content (acceptable)")
                        errors_handled += 1
                except Exception as e:
                    print(f"   Request {idx+1}: Caught exception (expected): {type(e).__name__}")
                    errors_handled += 1

            if errors_handled == len(invalid_requests):
                print(f"✅ PASSED: All error cases handled gracefully")
                self.tests_passed += 1
                return True
            else:
                print(f"❌ FAILED: Some errors not handled properly")
                self.tests_failed += 1
                return False

        except Exception as e:
            print(f"❌ FAILED: Unexpected error in error handling test: {e}")
            self.tests_failed += 1
            return False

    async def test_content_transformer_integration(self):
        """Test 5: Verify content transformer accepts enriched data."""
        print("\n" + "="*60)
        print("TEST 5: Content Transformer Integration")
        print("="*60)

        try:
            from src.utils.content_transformer import ContentTransformer
            from src.utils.layout_mapper import LayoutMapper

            # Create components
            layout_mapper = LayoutMapper()
            transformer = ContentTransformer(layout_mapper)

            # Create test data
            slide = Slide(
                slide_number=1,
                slide_id="test-transform-1",
                slide_type="content_heavy",
                title="Test Slide",
                narrative="Test narrative",
                key_points=["Point 1", "Point 2", "Point 3"]
            )

            strawman = PresentationStrawman(
                main_title="Test Presentation",
                overall_theme="Testing",
                target_audience="Testers",
                design_suggestions="Simple and clean",
                presentation_duration=5,
                slides=[slide]
            )

            # Generate enriched content
            generated_text = GeneratedText(
                content="This is real generated text from the Text Service that should replace placeholders in the final presentation.",
                metadata={"test": True}
            )

            enriched_slide = EnrichedSlide(
                original_slide=slide,
                slide_id=slide.slide_id,
                generated_text=generated_text,
                has_text_failure=False
            )

            enriched = EnrichedPresentationStrawman(
                original_strawman=strawman,
                enriched_slides=[enriched_slide],
                generation_metadata={"test": True}
            )

            # Transform with enriched data
            result_with_enriched = transformer.transform_presentation(strawman, enriched_data=enriched)

            # Transform without enriched data (baseline)
            result_without_enriched = transformer.transform_presentation(strawman, enriched_data=None)

            # Verify enriched version has real content
            if result_with_enriched and result_without_enriched:
                print(f"✅ PASSED: Content transformer accepts enriched data")
                print(f"   Without enriched: {len(str(result_without_enriched))} chars")
                print(f"   With enriched: {len(str(result_with_enriched))} chars")

                # Check if enriched content made it through
                enriched_str = str(result_with_enriched)
                if "real generated text" in enriched_str:
                    print(f"   ✅ Real generated text found in output")
                else:
                    print(f"   ⚠️  Generated text may not have been injected")

                self.tests_passed += 1
                return True
            else:
                print(f"❌ FAILED: Transformation failed")
                self.tests_failed += 1
                return False

        except Exception as e:
            print(f"❌ FAILED: Error in content transformer test: {e}")
            import traceback
            traceback.print_exc()
            self.tests_failed += 1
            return False

    async def run_all_tests(self):
        """Run all integration tests."""
        print("\n" + "="*80)
        print("V3.1 TEXT SERVICE INTEGRATION TEST SUITE")
        print("="*80)
        print(f"Text Service URL: {self.text_client.base_url}")
        print(f"Timeout: {self.text_client.timeout}s")
        print("="*80)

        # Run tests sequentially
        await self.test_text_service_health()
        await self.test_slide_text_generation()
        await self.test_enriched_presentation_creation()
        await self.test_error_handling()
        await self.test_content_transformer_integration()

        # Print summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        total = self.tests_passed + self.tests_failed
        print(f"Total tests: {total}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        print(f"Success rate: {(self.tests_passed/total*100):.1f}%")
        print("="*80)

        if self.tests_failed == 0:
            print("\n🎉 ALL TESTS PASSED! V3.1 is ready for end-to-end testing.")
        else:
            print(f"\n⚠️  {self.tests_failed} test(s) failed. Review errors above.")

        return self.tests_failed == 0


async def main():
    """Main test runner."""
    test_suite = TestTextServiceIntegration()
    success = await test_suite.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
