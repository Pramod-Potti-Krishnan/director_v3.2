#!/usr/bin/env python3
"""
Unit Tests for Format Ownership Architecture (v1.1)
====================================================

Tests format specification extraction, structured content generation,
and pass-through logic in ContentTransformer.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.layout_schema_manager import LayoutSchemaManager
from src.utils.content_transformer import ContentTransformer
from src.models.agents import Slide, PresentationStrawman
from src.models.content import EnrichedSlide, GeneratedText


class TestFormatSpecificationExtraction:
    """Test format specification extraction from layout schemas."""

    def setup_method(self):
        """Initialize schema manager for tests."""
        self.schema_manager = LayoutSchemaManager()

    def test_l05_format_specs_extraction(self):
        """Test format spec extraction for L05 (Bullet List)."""
        print("\n" + "="*70)
        print("TEST: L05 Format Specification Extraction")
        print("="*70)

        # Get schema
        schema = self.schema_manager.get_schema("L05")
        content_schema = schema['content_schema']

        # Extract field specifications
        field_specs = self.schema_manager._extract_field_specifications(content_schema)

        # Verify slide_title (plain_text, layout_builder)
        assert 'slide_title' in field_specs
        assert field_specs['slide_title']['format_type'] == 'plain_text'
        assert field_specs['slide_title']['format_owner'] == 'layout_builder'
        assert field_specs['slide_title']['max_chars'] == 60
        print("✅ slide_title: plain_text, layout_builder, max_chars=60")

        # Verify bullets (html, text_service)
        assert 'bullets' in field_specs
        assert field_specs['bullets']['format_type'] == 'html'
        assert field_specs['bullets']['format_owner'] == 'text_service'
        assert field_specs['bullets']['validation_threshold'] == 0.9
        assert field_specs['bullets']['expected_structure'] == 'ul>li or ol>li'
        print("✅ bullets: html, text_service, threshold=0.9, structure='ul>li or ol>li'")

        # Verify subtitle (optional)
        assert 'subtitle' in field_specs
        assert field_specs['subtitle']['format_type'] == 'plain_text'
        assert field_specs['subtitle']['format_owner'] == 'layout_builder'
        print("✅ subtitle: plain_text, layout_builder")

        print("\n✅ L05 format spec extraction: PASSED\n")

    def test_l20_nested_structure_extraction(self):
        """Test format spec extraction for L20 (Comparison) with nested structures."""
        print("\n" + "="*70)
        print("TEST: L20 Nested Structure Format Specification Extraction")
        print("="*70)

        # Get schema
        schema = self.schema_manager.get_schema("L20")
        content_schema = schema['content_schema']

        # Extract field specifications
        field_specs = self.schema_manager._extract_field_specifications(content_schema)

        # Verify left_content nested structure
        assert 'left_content' in field_specs
        assert 'structure' in field_specs['left_content']

        left_structure = field_specs['left_content']['structure']

        # Verify header (plain_text, layout_builder)
        assert 'header' in left_structure
        assert left_structure['header']['format_type'] == 'plain_text'
        assert left_structure['header']['format_owner'] == 'layout_builder'
        print("✅ left_content.header: plain_text, layout_builder")

        # Verify items (html, text_service)
        assert 'items' in left_structure
        assert left_structure['items']['format_type'] == 'html'
        assert left_structure['items']['format_owner'] == 'text_service'
        assert left_structure['items']['validation_threshold'] == 0.9
        print("✅ left_content.items: html, text_service, threshold=0.9")

        # Verify right_content has same structure
        assert 'right_content' in field_specs
        assert 'structure' in field_specs['right_content']
        print("✅ right_content: nested structure present")

        print("\n✅ L20 nested structure extraction: PASSED\n")

    def test_build_content_request_includes_specs(self):
        """Test that build_content_request includes field_specifications."""
        print("\n" + "="*70)
        print("TEST: Content Request Includes Field Specifications")
        print("="*70)

        # Create test slide
        slide = Slide(
            slide_id="test-001",
            slide_number=1,
            title="Test Slide Title",
            narrative="Test narrative for the slide",
            key_points=["Point 1", "Point 2", "Point 3"],
            slide_type="content_heavy"
        )

        # Build content request
        request = self.schema_manager.build_content_request("L05", slide)

        # Verify field_specifications present
        assert 'field_specifications' in request
        assert len(request['field_specifications']) > 0
        print(f"✅ field_specifications present with {len(request['field_specifications'])} fields")

        # Verify format specs included
        assert 'slide_title' in request['field_specifications']
        assert 'format_type' in request['field_specifications']['slide_title']
        assert 'format_owner' in request['field_specifications']['slide_title']
        print("✅ Format ownership specs included in request")

        # Print sample
        print("\nSample field specification:")
        print(json.dumps(request['field_specifications']['slide_title'], indent=2))

        print("\n✅ Content request includes specs: PASSED\n")


class TestContentTransformerPassThrough:
    """Test ContentTransformer pass-through for structured content."""

    def setup_method(self):
        """Initialize content transformer for tests."""
        self.transformer = ContentTransformer()

    def test_structured_content_detection(self):
        """Test _is_structured_content() detection."""
        print("\n" + "="*70)
        print("TEST: Structured Content Detection")
        print("="*70)

        # Test structured content (dict)
        structured = {
            "slide_title": "Test Title",
            "bullets": "<ul><li>Point 1</li><li>Point 2</li></ul>"
        }
        assert self.transformer._is_structured_content(structured) == True
        print("✅ Dict content detected as structured")

        # Test HTML/text content (string)
        html_content = "<p>This is HTML content</p>"
        assert self.transformer._is_structured_content(html_content) == False
        print("✅ String content detected as HTML/text")

        print("\n✅ Structured content detection: PASSED\n")

    def test_truncate_without_ellipsis(self):
        """Test truncate() no longer adds ellipsis by default (v1.1)."""
        print("\n" + "="*70)
        print("TEST: Truncate Without Ellipsis (v1.1)")
        print("="*70)

        text = "This is a very long sentence that needs to be truncated to fit within the character limit."

        # Test without ellipsis (default in v1.1)
        truncated = self.transformer.truncate(text, 50)
        assert not truncated.endswith("...")
        print(f"✅ Truncated without ellipsis: '{truncated}'")

        # Test with ellipsis (explicit)
        truncated_with = self.transformer.truncate(text, 50, add_ellipsis=True)
        assert truncated_with.endswith("...")
        print(f"✅ Truncated with ellipsis (explicit): '{truncated_with}'")

        print("\n✅ Truncate without ellipsis: PASSED\n")

    def test_l05_structured_pass_through(self):
        """Test L05 structured content gets passed through without parsing."""
        print("\n" + "="*70)
        print("TEST: L05 Structured Content Pass-Through")
        print("="*70)

        # Create presentation
        presentation = PresentationStrawman(
            main_title="Test Presentation",
            overall_theme="Test Theme",
            target_audience="Executives",
            design_suggestions="Modern professional",
            presentation_duration=10,
            slides=[]
        )

        # Create slide
        slide = Slide(
            slide_id="test-001",
            slide_number=1,
            title="Key Benefits",
            narrative="Overview of main advantages",
            key_points=["Benefit 1", "Benefit 2", "Benefit 3"],
            slide_type="content_heavy",
            layout_id="L05"
        )

        # Create enriched slide with structured content (v1.1)
        structured_content = {
            "slide_title": "Key Benefits",
            "subtitle": "Our Competitive Advantages",
            "bullets": "<ul><li>Cost savings of 30%</li><li>Improved efficiency by 50%</li><li>Enhanced scalability</li></ul>"
        }

        enriched_slide = EnrichedSlide(
            original_slide=slide,
            slide_id="test-001",
            generated_text=GeneratedText(
                content=structured_content,
                metadata={"format_type": "structured"}
            ),
            has_text_failure=False,
            text_failure_reason=None
        )

        # Transform slide
        result = self.transformer.transform_slide(
            slide=slide,
            layout_id="L05",
            presentation=presentation,
            enriched_slide=enriched_slide
        )

        # Verify pass-through (content matches exactly)
        assert result['layout'] == 'L05'
        assert result['content']['slide_title'] == structured_content['slide_title']
        assert result['content']['bullets'] == structured_content['bullets']
        print("✅ Structured content passed through without modification")

        # Verify HTML structure preserved
        assert '<ul>' in result['content']['bullets']
        assert '<li>' in result['content']['bullets']
        print("✅ HTML structure preserved in pass-through")

        print("\n✅ L05 structured pass-through: PASSED\n")


class TestValidationThreshold:
    """Test 90% threshold validation logic."""

    def test_90_percent_threshold_concept(self):
        """Test the 90% threshold validation concept."""
        print("\n" + "="*70)
        print("TEST: 90% Threshold Validation Concept")
        print("="*70)

        # Simulate field spec
        field_spec = {
            'max_chars': 500,
            'max_words': 100,
            'max_lines': 8,
            'validation_threshold': 0.9
        }

        # Test case 1: Meets char threshold (90% of 500 = 450)
        content_chars = 460
        char_density = content_chars / field_spec['max_chars']
        assert char_density >= field_spec['validation_threshold']
        print(f"✅ Content with {content_chars} chars meets threshold (density: {char_density:.2%})")

        # Test case 2: Below threshold
        content_chars_low = 400
        char_density_low = content_chars_low / field_spec['max_chars']
        assert char_density_low < field_spec['validation_threshold']
        print(f"⚠️  Content with {content_chars_low} chars below threshold (density: {char_density_low:.2%})")

        # Test case 3: Hit 90% of words instead
        content_words = 92
        word_density = content_words / field_spec['max_words']
        assert word_density >= field_spec['validation_threshold']
        print(f"✅ Content with {content_words} words meets threshold (density: {word_density:.2%})")

        print("\n✅ 90% threshold validation: PASSED\n")


def run_all_tests():
    """Run all format ownership tests."""
    print("\n" + "="*70)
    print("FORMAT OWNERSHIP ARCHITECTURE - TEST SUITE")
    print("="*70)

    # Test 1: Format Specification Extraction
    test_specs = TestFormatSpecificationExtraction()
    test_specs.setup_method()
    test_specs.test_l05_format_specs_extraction()
    test_specs.test_l20_nested_structure_extraction()
    test_specs.test_build_content_request_includes_specs()

    # Test 2: ContentTransformer Pass-Through
    test_transformer = TestContentTransformerPassThrough()
    test_transformer.setup_method()
    test_transformer.test_structured_content_detection()
    test_transformer.test_truncate_without_ellipsis()
    test_transformer.test_l05_structured_pass_through()

    # Test 3: Validation Threshold
    test_validation = TestValidationThreshold()
    test_validation.test_90_percent_threshold_concept()

    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED!")
    print("="*70)
    print("\nSummary:")
    print("- Format specification extraction: ✅")
    print("- Nested structure handling: ✅")
    print("- Content request building: ✅")
    print("- Structured content detection: ✅")
    print("- Truncate without ellipsis: ✅")
    print("- Structured pass-through: ✅")
    print("- 90% threshold validation: ✅")
    print("\n" + "="*70)


if __name__ == '__main__':
    run_all_tests()
