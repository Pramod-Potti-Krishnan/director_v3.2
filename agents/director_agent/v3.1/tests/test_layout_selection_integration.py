#!/usr/bin/env python
"""
Integration tests for AI-powered layout selection (v3.2).

Tests end-to-end flow:
1. Slide content → AI semantic matching → Layout selection
2. Layout selection → Schema-driven content request
3. Quote detection, Comparison detection, Dashboard detection
"""
import sys
import os
import asyncio
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.director import DirectorAgent
from src.models.agents import Slide, PresentationStrawman
from src.utils.layout_schema_manager import LayoutSchemaManager
from config import settings


class TestColors:
    """Terminal colors for test output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_test_header(test_name: str):
    """Print formatted test header."""
    print(f"\n{TestColors.BLUE}{TestColors.BOLD}Testing: {test_name}{TestColors.ENDC}")
    print("-" * 70)


def print_pass(message: str):
    """Print success message."""
    print(f"{TestColors.GREEN}✓ PASS:{TestColors.ENDC} {message}")


def print_fail(message: str):
    """Print failure message."""
    print(f"{TestColors.RED}✗ FAIL:{TestColors.ENDC} {message}")


def print_info(message: str):
    """Print info message."""
    print(f"{TestColors.YELLOW}ℹ INFO:{TestColors.ENDC} {message}")


async def test_quote_testimonial_detection():
    """Test that testimonial content selects L07 (Quote Slide)."""
    print_test_header("Quote/Testimonial Detection → L07")

    try:
        # Initialize Director Agent
        director = DirectorAgent()

        # Create slide with testimonial content
        testimonial_slide = Slide(
            slide_number=5,
            slide_id="slide_005",
            title="Customer Success Story",
            slide_type="content_heavy",
            narrative="A customer shares their experience with our platform and how it transformed their business operations",
            key_points=[
                "This platform completely transformed how our team collaborates",
                "We've saved over 20 hours per week on manual processes",
                "Team morale has never been higher since we started using this solution",
                "The ROI was evident within the first month of implementation"
            ],
            analytics_needed=None,
            visuals_needed=None,
            diagrams_needed=None,
            tables_needed=None
        )

        # Run AI layout selection
        layout_selection = await director._select_layout_by_use_case(
            slide=testimonial_slide,
            position="middle",
            total_slides=10
        )

        print_info(f"  Selected layout: {layout_selection.layout_id}")
        print_info(f"  Reasoning: {layout_selection.reasoning}")
        print_info(f"  Confidence: {layout_selection.confidence}")

        # Verify L07 selected
        assert layout_selection.layout_id == "L07", \
               f"Expected L07 for testimonial, got {layout_selection.layout_id}"

        print_pass("Testimonial correctly identified as L07 (Quote Slide)")

        # Test schema-driven content request
        manager = LayoutSchemaManager()
        request = manager.build_content_request(
            layout_id="L07",
            slide=testimonial_slide,
            presentation_context={"main_title": "Product Demo"}
        )

        # Verify request has correct schema
        assert "quote_text" in request["layout_schema"], \
               "L07 request should include quote_text field"
        assert "attribution" in request["layout_schema"], \
               "L07 request should include attribution field"

        print_pass("Schema-driven content request built correctly for L07")
        print_info(f"  Schema fields: {list(request['layout_schema'].keys())}")

        return True

    except Exception as e:
        print_fail(f"Quote detection test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_comparison_detection():
    """Test that comparison content selects L20 (Comparison Layout)."""
    print_test_header("Comparison/Versus Detection → L20")

    try:
        # Initialize Director Agent
        director = DirectorAgent()

        # Create slide with comparison content
        comparison_slide = Slide(
            slide_number=7,
            slide_id="slide_007",
            title="Our Solution vs Traditional Approach",
            slide_type="content_heavy",
            narrative="Comparing our innovative platform with traditional manual processes shows clear advantages across all key metrics",
            key_points=[
                "Automated workflows vs manual processes",
                "Real-time collaboration vs email-based communication",
                "Cloud accessibility vs on-premise limitations",
                "Integrated analytics vs separate reporting tools",
                "Scalable architecture vs fixed capacity systems"
            ],
            analytics_needed=None,
            visuals_needed=None,
            diagrams_needed=None,
            tables_needed=None
        )

        # Run AI layout selection
        layout_selection = await director._select_layout_by_use_case(
            slide=comparison_slide,
            position="middle",
            total_slides=10
        )

        print_info(f"  Selected layout: {layout_selection.layout_id}")
        print_info(f"  Reasoning: {layout_selection.reasoning}")
        print_info(f"  Confidence: {layout_selection.confidence}")

        # Verify L20 selected
        assert layout_selection.layout_id == "L20", \
               f"Expected L20 for comparison, got {layout_selection.layout_id}"

        print_pass("Comparison correctly identified as L20 (Comparison Layout)")

        # Test schema-driven content request
        manager = LayoutSchemaManager()
        request = manager.build_content_request(
            layout_id="L20",
            slide=comparison_slide,
            presentation_context={"main_title": "Product Demo"}
        )

        # Verify request has correct schema
        assert "left_content" in request["layout_schema"], \
               "L20 request should include left_content field"
        assert "right_content" in request["layout_schema"], \
               "L20 request should include right_content field"

        print_pass("Schema-driven content request built correctly for L20")
        print_info(f"  Schema fields: {list(request['layout_schema'].keys())}")

        return True

    except Exception as e:
        print_fail(f"Comparison detection test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_dashboard_metrics_detection():
    """Test that dashboard/metrics content selects L19 (Dashboard Layout)."""
    print_test_header("Dashboard/Metrics Detection → L19")

    try:
        # Initialize Director Agent
        director = DirectorAgent()

        # Create slide with dashboard/metrics content
        dashboard_slide = Slide(
            slide_number=4,
            slide_id="slide_004",
            title="Q4 Performance Dashboard",
            slide_type="data_driven",
            narrative="Key performance indicators show strong growth across all business metrics for the quarter",
            key_points=[
                "Revenue increased by 45% year-over-year",
                "Customer acquisition cost decreased by 30%",
                "User engagement metrics up 60%",
                "Net Promoter Score: 72 (industry leading)",
                "Market share grew from 12% to 18%"
            ],
            analytics_needed="Dashboard showing KPIs: revenue, CAC, engagement, NPS, market share",
            visuals_needed=None,
            diagrams_needed=None,
            tables_needed=None
        )

        # Run AI layout selection
        layout_selection = await director._select_layout_by_use_case(
            slide=dashboard_slide,
            position="middle",
            total_slides=10
        )

        print_info(f"  Selected layout: {layout_selection.layout_id}")
        print_info(f"  Reasoning: {layout_selection.reasoning}")
        print_info(f"  Confidence: {layout_selection.confidence}")

        # Verify L19 selected
        assert layout_selection.layout_id == "L19", \
               f"Expected L19 for dashboard, got {layout_selection.layout_id}"

        print_pass("Dashboard/metrics correctly identified as L19 (Dashboard Layout)")

        # Test schema-driven content request
        manager = LayoutSchemaManager()
        request = manager.build_content_request(
            layout_id="L19",
            slide=dashboard_slide,
            presentation_context={"main_title": "Q4 Business Review"}
        )

        # Verify request has correct schema
        assert "metrics" in request["layout_schema"], \
               "L19 request should include metrics field"

        print_pass("Schema-driven content request built correctly for L19")
        print_info(f"  Schema fields: {list(request['layout_schema'].keys())}")

        return True

    except Exception as e:
        print_fail(f"Dashboard detection test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_bullet_list_default():
    """Test that generic content defaults to L05 (Bullet List)."""
    print_test_header("Generic Content → L05 (Default)")

    try:
        # Initialize Director Agent
        director = DirectorAgent()

        # Create slide with generic bullet content
        generic_slide = Slide(
            slide_number=6,
            slide_id="slide_006",
            title="Key Features Overview",
            slide_type="content_heavy",
            narrative="Our platform offers a comprehensive set of features designed for modern teams",
            key_points=[
                "Collaborative workspace with real-time updates",
                "Advanced analytics and reporting capabilities",
                "Seamless integration with existing tools",
                "Enterprise-grade security and compliance",
                "24/7 customer support and training resources"
            ],
            analytics_needed=None,
            visuals_needed=None,
            diagrams_needed=None,
            tables_needed=None
        )

        # Run AI layout selection
        layout_selection = await director._select_layout_by_use_case(
            slide=generic_slide,
            position="middle",
            total_slides=10
        )

        print_info(f"  Selected layout: {layout_selection.layout_id}")
        print_info(f"  Reasoning: {layout_selection.reasoning}")
        print_info(f"  Confidence: {layout_selection.confidence}")

        # Verify L05 selected (most likely for bullet lists)
        assert layout_selection.layout_id == "L05", \
               f"Expected L05 for bullet list, got {layout_selection.layout_id}"

        print_pass("Generic bullet content correctly identified as L05")

        return True

    except Exception as e:
        print_fail(f"Default layout test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_chart_insights_detection():
    """Test that chart + insights content selects L17."""
    print_test_header("Chart + Insights Detection → L17")

    try:
        # Initialize Director Agent
        director = DirectorAgent()

        # Create slide with chart + insights content
        chart_slide = Slide(
            slide_number=8,
            slide_id="slide_008",
            title="Revenue Growth Trend",
            slide_type="data_driven",
            narrative="Analysis of revenue growth over the past 4 quarters shows consistent upward trajectory with key insights",
            key_points=[
                "Q1 revenue: $2.5M, 15% growth",
                "Q2 revenue: $3.1M, 24% growth",
                "Q3 revenue: $3.8M, 23% growth",
                "Q4 revenue: $4.5M, 18% growth",
                "Total year growth: 80% increase"
            ],
            analytics_needed="Line chart showing quarterly revenue trend with growth percentages",
            visuals_needed=None,
            diagrams_needed=None,
            tables_needed=None
        )

        # Run AI layout selection
        layout_selection = await director._select_layout_by_use_case(
            slide=chart_slide,
            position="middle",
            total_slides=10
        )

        print_info(f"  Selected layout: {layout_selection.layout_id}")
        print_info(f"  Reasoning: {layout_selection.reasoning}")
        print_info(f"  Confidence: {layout_selection.confidence}")

        # Verify L17 selected
        assert layout_selection.layout_id == "L17", \
               f"Expected L17 for chart+insights, got {layout_selection.layout_id}"

        print_pass("Chart + insights correctly identified as L17")

        # Test schema-driven content request
        manager = LayoutSchemaManager()
        request = manager.build_content_request(
            layout_id="L17",
            slide=chart_slide,
            presentation_context={"main_title": "Revenue Analysis"}
        )

        # Verify request has correct schema
        assert "key_insights" in request["layout_schema"], \
               "L17 request should include key_insights field"

        print_pass("Schema-driven content request built correctly for L17")

        return True

    except Exception as e:
        print_fail(f"Chart + insights test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_mandatory_layouts():
    """Test that mandatory positions get correct layouts (L01, L02, L03)."""
    print_test_header("Mandatory Layout Positions")

    try:
        # Initialize Director Agent
        director = DirectorAgent()

        # Test first slide → L01
        first_slide = Slide(
            slide_number=1,
            slide_id="slide_001",
            title="Presentation Title",
            slide_type="title_slide",
            narrative="Introduction to our product",
            key_points=[]
        )

        layout_selection = await director._select_layout_by_use_case(
            slide=first_slide,
            position="first",
            total_slides=10
        )

        assert layout_selection.layout_id == "L01", \
               f"First slide should be L01, got {layout_selection.layout_id}"

        print_pass("First slide correctly assigned L01 (Title Slide)")

        # Test last slide → L03
        last_slide = Slide(
            slide_number=10,
            slide_id="slide_010",
            title="Thank You",
            slide_type="conclusion_slide",
            narrative="Questions and contact information",
            key_points=[]
        )

        layout_selection = await director._select_layout_by_use_case(
            slide=last_slide,
            position="last",
            total_slides=10
        )

        assert layout_selection.layout_id == "L03", \
               f"Last slide should be L03, got {layout_selection.layout_id}"

        print_pass("Last slide correctly assigned L03 (Closing Slide)")

        # Test section divider → L02
        divider_slide = Slide(
            slide_number=5,
            slide_id="slide_005",
            title="Section 2: Features",
            slide_type="section_divider",
            narrative="Introduction to features section",
            key_points=[]
        )

        layout_selection = await director._select_layout_by_use_case(
            slide=divider_slide,
            position="middle",
            total_slides=10
        )

        assert layout_selection.layout_id == "L02", \
               f"Section divider should be L02, got {layout_selection.layout_id}"

        print_pass("Section divider correctly assigned L02")

        return True

    except Exception as e:
        print_fail(f"Mandatory layouts test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_integration_tests():
    """Run all integration tests."""
    print(f"\n{TestColors.BOLD}{'=' * 70}{TestColors.ENDC}")
    print(f"{TestColors.BOLD}Layout Selection Integration Tests (v3.2){TestColors.ENDC}")
    print(f"{TestColors.BOLD}{'=' * 70}{TestColors.ENDC}")
    print(f"\n{TestColors.YELLOW}NOTE: These tests require AI model access (Gemini API){TestColors.ENDC}")

    tests = [
        test_quote_testimonial_detection,
        test_comparison_detection,
        test_dashboard_metrics_detection,
        test_bullet_list_default,
        test_chart_insights_detection,
        test_mandatory_layouts
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_fail(f"Test {test.__name__} crashed: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Summary
    print(f"\n{TestColors.BOLD}{'=' * 70}{TestColors.ENDC}")
    print(f"{TestColors.BOLD}Integration Test Summary{TestColors.ENDC}")
    print(f"{TestColors.BOLD}{'=' * 70}{TestColors.ENDC}")
    print(f"Total tests: {passed + failed}")
    print(f"{TestColors.GREEN}Passed: {passed}{TestColors.ENDC}")
    print(f"{TestColors.RED}Failed: {failed}{TestColors.ENDC}")

    if failed == 0:
        print(f"\n{TestColors.GREEN}{TestColors.BOLD}✅ ALL INTEGRATION TESTS PASSED!{TestColors.ENDC}")
        return True
    else:
        print(f"\n{TestColors.RED}{TestColors.BOLD}❌ SOME INTEGRATION TESTS FAILED{TestColors.ENDC}")
        return False


if __name__ == "__main__":
    # Run async tests
    success = asyncio.run(run_all_integration_tests())
    sys.exit(0 if success else 1)
