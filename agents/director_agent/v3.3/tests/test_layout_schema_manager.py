#!/usr/bin/env python
"""
Unit tests for LayoutSchemaManager.

Tests schema-driven architecture (v3.2) for Director Agent.
"""
import sys
import os
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.layout_schema_manager import LayoutSchemaManager, get_schema_manager
from src.models.agents import Slide


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


def test_schema_manager_initialization():
    """Test LayoutSchemaManager initializes correctly."""
    print_test_header("LayoutSchemaManager Initialization")

    try:
        manager = LayoutSchemaManager()

        # Check schemas loaded
        assert manager.schemas is not None, "Schemas should not be None"
        assert isinstance(manager.schemas, dict), "Schemas should be a dictionary"
        assert len(manager.schemas) > 0, "Schemas should not be empty"

        print_pass(f"Loaded {len(manager.schemas)} layout schemas")

        # Check all 24 layouts present
        expected_layouts = [f"L{str(i).zfill(2)}" for i in range(1, 25)]
        missing = [lid for lid in expected_layouts if lid not in manager.schemas]

        if missing:
            print_fail(f"Missing layouts: {missing}")
            return False

        print_pass("All 24 layouts (L01-L24) are present")
        return True

    except Exception as e:
        print_fail(f"Initialization failed: {str(e)}")
        return False


def test_get_schema():
    """Test get_schema method."""
    print_test_header("get_schema() Method")

    try:
        manager = LayoutSchemaManager()

        # Test valid layout
        schema = manager.get_schema("L07")
        assert schema is not None, "Schema for L07 should not be None"
        assert "layout_id" in schema, "Schema should have layout_id"
        assert "name" in schema, "Schema should have name"
        assert "content_schema" in schema, "Schema should have content_schema"
        assert schema["layout_id"] == "L07", "Layout ID should match"

        print_pass("Retrieved schema for L07 (Quote Slide)")
        print_info(f"  Layout name: {schema['name']}")
        print_info(f"  Content fields: {list(schema['content_schema'].keys())}")

        # Test invalid layout
        try:
            manager.get_schema("L99")
            print_fail("Should raise error for invalid layout L99")
            return False
        except ValueError as e:
            print_pass(f"Correctly raised ValueError for invalid layout: {str(e)}")

        return True

    except Exception as e:
        print_fail(f"get_schema test failed: {str(e)}")
        return False


def test_get_content_schema():
    """Test get_content_schema method."""
    print_test_header("get_content_schema() Method")

    try:
        manager = LayoutSchemaManager()

        # Test L07 (Quote)
        content_schema = manager.get_content_schema("L07")
        assert "quote_text" in content_schema, "L07 should have quote_text field"
        assert "attribution" in content_schema, "L07 should have attribution field"

        # Check field specifications
        quote_field = content_schema["quote_text"]
        assert quote_field["type"] == "string", "quote_text should be string type"
        assert "max_chars" in quote_field, "quote_text should have max_chars"
        assert quote_field["required"] == True, "quote_text should be required"

        print_pass("L07 content schema has correct structure")
        print_info(f"  quote_text max_chars: {quote_field['max_chars']}")

        # Test L05 (Bullet List)
        content_schema = manager.get_content_schema("L05")
        assert "bullets" in content_schema, "L05 should have bullets field"
        bullets_field = content_schema["bullets"]
        assert bullets_field["type"] == "array", "bullets should be array type"
        assert "max_items" in bullets_field, "bullets should have max_items"

        print_pass("L05 content schema has correct structure")
        print_info(f"  bullets max_items: {bullets_field['max_items']}")

        return True

    except Exception as e:
        print_fail(f"get_content_schema test failed: {str(e)}")
        return False


def test_get_all_layouts_with_use_cases():
    """Test get_all_layouts_with_use_cases method."""
    print_test_header("get_all_layouts_with_use_cases() Method")

    try:
        manager = LayoutSchemaManager()
        layouts = manager.get_all_layouts_with_use_cases()

        assert isinstance(layouts, list), "Should return list"
        assert len(layouts) == 24, f"Should return 24 layouts, got {len(layouts)}"

        # Check structure of first layout
        layout = layouts[0]
        required_keys = ['layout_id', 'name', 'slide_subtype', 'best_use_case',
                        'best_for_keywords', 'content_fields']

        for key in required_keys:
            assert key in layout, f"Layout should have '{key}' field"

        print_pass(f"Retrieved {len(layouts)} layouts with use cases")

        # Check L07 specifically
        l07 = next((l for l in layouts if l['layout_id'] == 'L07'), None)
        assert l07 is not None, "L07 should be in layouts"
        assert 'testimonial' in ' '.join(l07['best_for_keywords']).lower(), \
               "L07 keywords should include 'testimonial'"

        print_pass("L07 has correct keywords for testimonials")
        print_info(f"  L07 keywords: {l07['best_for_keywords'][:5]}")

        return True

    except Exception as e:
        print_fail(f"get_all_layouts_with_use_cases test failed: {str(e)}")
        return False


def test_build_content_request():
    """Test build_content_request method."""
    print_test_header("build_content_request() Method")

    try:
        manager = LayoutSchemaManager()

        # Create test slide
        slide = Slide(
            slide_number=3,
            slide_id="slide_003",
            title="Customer Success Story",
            slide_type="content_heavy",
            narrative="A customer shares their experience with our platform",
            key_points=["Transformed work", "Saved 20 hours", "Team loves it"],
            analytics_needed=None,
            visuals_needed=None,
            diagrams_needed=None,
            tables_needed=None
        )

        # Build request for L07
        request = manager.build_content_request(
            layout_id="L07",
            slide=slide,
            presentation_context={"main_title": "Test Presentation"}
        )

        # Validate request structure
        assert "layout_id" in request, "Request should have layout_id"
        assert request["layout_id"] == "L07", "Layout ID should be L07"
        assert "layout_name" in request, "Request should have layout_name"
        assert "layout_subtype" in request, "Request should have layout_subtype"
        assert "layout_schema" in request, "Request should have layout_schema"
        assert "content_guidance" in request, "Request should have content_guidance"
        assert "slide_id" in request, "Request should have slide_id"
        assert "slide_number" in request, "Request should have slide_number"

        print_pass("Content request has correct structure")

        # Check content_guidance
        guidance = request["content_guidance"]
        assert guidance["title"] == slide.title, "Guidance should include slide title"
        assert guidance["narrative"] == slide.narrative, "Guidance should include narrative"
        assert len(guidance["key_points"]) == 3, "Guidance should include key points"

        print_pass("Content guidance populated correctly")
        print_info(f"  Slide: {slide.title}")
        print_info(f"  Layout: {request['layout_name']}")
        print_info(f"  Fields: {list(request['layout_schema'].keys())}")

        return True

    except Exception as e:
        print_fail(f"build_content_request test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_validate_content():
    """Test validate_content method."""
    print_test_header("validate_content() Method")

    try:
        manager = LayoutSchemaManager()

        # Test valid content for L07
        valid_content = {
            "quote_text": "This platform completely transformed our workflow.",
            "attribution": "— Sarah Chen, VP of Operations"
        }

        is_valid, errors = manager.validate_content("L07", valid_content)
        assert is_valid == True, "Valid content should pass validation"
        assert len(errors) == 0, "Valid content should have no errors"

        print_pass("Valid L07 content passes validation")

        # Test missing required field
        invalid_content = {
            "quote_text": "This is a quote."
            # Missing attribution
        }

        is_valid, errors = manager.validate_content("L07", invalid_content)
        assert is_valid == False, "Content missing required field should fail"
        assert len(errors) > 0, "Should have validation errors"
        assert any("attribution" in err.lower() for err in errors), \
               "Should report missing attribution"

        print_pass("Missing required field detected")
        print_info(f"  Errors: {errors}")

        # Test exceeding max_chars
        too_long_content = {
            "quote_text": "x" * 300,  # L07 max_chars is 200
            "attribution": "— Test"
        }

        is_valid, errors = manager.validate_content("L07", too_long_content)
        assert is_valid == False, "Content exceeding max_chars should fail"
        assert any("max_chars" in err.lower() for err in errors), \
               "Should report max_chars violation"

        print_pass("Character limit violation detected")

        # Test valid L05 (Bullet List)
        valid_bullets = {
            "slide_title": "Key Benefits",
            "bullets": [
                "Increase efficiency by 40%",
                "Reduce costs by $2M annually",
                "Improve quality metrics",
                "Enable real-time collaboration",
                "Scale seamlessly as you grow"
            ]
        }

        is_valid, errors = manager.validate_content("L05", valid_bullets)
        if not is_valid:
            print_fail(f"L05 validation failed: {errors}")
        assert is_valid == True, f"Valid L05 content should pass, errors: {errors}"

        print_pass("Valid L05 (Bullet List) content passes validation")

        # Test invalid array type
        invalid_bullets = {
            "slide_title": "Test",
            "bullets": "not an array"  # Should be array
        }

        is_valid, errors = manager.validate_content("L05", invalid_bullets)
        assert is_valid == False, "Wrong type should fail validation"

        print_pass("Type validation works correctly")

        return True

    except Exception as e:
        print_fail(f"validate_content test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_format_layout_options_for_ai():
    """Test format_layout_options_for_ai method."""
    print_test_header("format_layout_options_for_ai() Method")

    try:
        manager = LayoutSchemaManager()

        # Test without exclusions
        formatted = manager.format_layout_options_for_ai()
        assert isinstance(formatted, str), "Should return string"
        assert "L07" in formatted, "Should include L07"
        assert "Quote Slide" in formatted, "Should include layout names"
        assert "Best Use Case" in formatted, "Should include use case labels"

        print_pass("Formatted layout options for AI (all layouts)")
        print_info(f"  Output length: {len(formatted)} characters")

        # Test with exclusions
        formatted_excluded = manager.format_layout_options_for_ai(
            exclude_layout_ids=["L01", "L02", "L03"]
        )
        assert "L01" not in formatted_excluded, "Should exclude L01"
        assert "L02" not in formatted_excluded, "Should exclude L02"
        assert "L03" not in formatted_excluded, "Should exclude L03"
        assert "L07" in formatted_excluded, "Should include L07"

        print_pass("Exclusion filter works correctly")
        print_info(f"  Excluded: L01, L02, L03")

        # Check format includes keywords
        assert "testimonial" in formatted.lower() or "quote" in formatted.lower(), \
               "Should include relevant keywords"

        print_pass("Formatted text includes keywords")

        return True

    except Exception as e:
        print_fail(f"format_layout_options_for_ai test failed: {str(e)}")
        return False


def test_get_layout_by_keywords():
    """Test get_layout_by_keywords method."""
    print_test_header("get_layout_by_keywords() Method")

    try:
        manager = LayoutSchemaManager()

        # Test testimonial keyword
        layouts = manager.get_layout_by_keywords(["testimonial"])
        assert "L07" in layouts, "Should find L07 for 'testimonial'"

        print_pass("Found L07 for 'testimonial' keyword")

        # Test comparison keyword
        layouts = manager.get_layout_by_keywords(["comparison", "versus"])
        assert "L20" in layouts, "Should find L20 for comparison keywords"

        print_pass("Found L20 for comparison keywords")

        # Test dashboard/metrics keyword
        layouts = manager.get_layout_by_keywords(["dashboard", "metrics"])
        assert "L19" in layouts, "Should find L19 for dashboard keywords"

        print_pass("Found L19 for dashboard keywords")

        return True

    except Exception as e:
        print_fail(f"get_layout_by_keywords test failed: {str(e)}")
        return False


def test_singleton_instance():
    """Test get_schema_manager singleton."""
    print_test_header("Singleton Pattern (get_schema_manager)")

    try:
        manager1 = get_schema_manager()
        manager2 = get_schema_manager()

        assert manager1 is manager2, "Should return same instance"

        print_pass("Singleton pattern works correctly")
        print_info(f"  Instance ID: {id(manager1)}")

        return True

    except Exception as e:
        print_fail(f"Singleton test failed: {str(e)}")
        return False


def test_schema_field_completeness():
    """Test that all layouts have complete schema definitions."""
    print_test_header("Schema Field Completeness")

    try:
        manager = LayoutSchemaManager()

        required_top_level = ['layout_id', 'name', 'slide_type_main', 'slide_subtype',
                             'best_use_case', 'best_for_keywords', 'content_schema']

        incomplete = []

        for layout_id in manager.schemas.keys():
            schema = manager.schemas[layout_id]

            # Check top-level fields
            missing = [field for field in required_top_level if field not in schema]
            if missing:
                incomplete.append(f"{layout_id}: missing {missing}")
                continue

            # Check content_schema has fields
            if not schema['content_schema']:
                incomplete.append(f"{layout_id}: empty content_schema")
                continue

            # Check each content field has type
            for field_name, field_spec in schema['content_schema'].items():
                if 'type' not in field_spec:
                    incomplete.append(f"{layout_id}.{field_name}: missing type")

        if incomplete:
            print_fail(f"Found {len(incomplete)} incomplete schemas:")
            for issue in incomplete[:5]:  # Show first 5
                print_info(f"  {issue}")
            return False

        print_pass("All 24 layouts have complete schema definitions")
        return True

    except Exception as e:
        print_fail(f"Completeness test failed: {str(e)}")
        return False


def run_all_tests():
    """Run all unit tests."""
    print(f"\n{TestColors.BOLD}{'=' * 70}{TestColors.ENDC}")
    print(f"{TestColors.BOLD}LayoutSchemaManager Unit Tests (v3.2){TestColors.ENDC}")
    print(f"{TestColors.BOLD}{'=' * 70}{TestColors.ENDC}")

    tests = [
        test_schema_manager_initialization,
        test_get_schema,
        test_get_content_schema,
        test_get_all_layouts_with_use_cases,
        test_build_content_request,
        test_validate_content,
        test_format_layout_options_for_ai,
        test_get_layout_by_keywords,
        test_singleton_instance,
        test_schema_field_completeness
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
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
    print(f"{TestColors.BOLD}Test Summary{TestColors.ENDC}")
    print(f"{TestColors.BOLD}{'=' * 70}{TestColors.ENDC}")
    print(f"Total tests: {passed + failed}")
    print(f"{TestColors.GREEN}Passed: {passed}{TestColors.ENDC}")
    print(f"{TestColors.RED}Failed: {failed}{TestColors.ENDC}")

    if failed == 0:
        print(f"\n{TestColors.GREEN}{TestColors.BOLD}✅ ALL TESTS PASSED!{TestColors.ENDC}")
        return True
    else:
        print(f"\n{TestColors.RED}{TestColors.BOLD}❌ SOME TESTS FAILED{TestColors.ENDC}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
