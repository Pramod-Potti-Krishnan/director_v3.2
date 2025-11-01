#!/usr/bin/env python3
"""
Quick test to verify format specification extraction in LayoutSchemaManager
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.layout_schema_manager import LayoutSchemaManager
from models.agents import Slide

def test_format_specs_extraction():
    """Test that format specifications are extracted correctly."""

    # Initialize schema manager
    manager = LayoutSchemaManager()
    print("✅ LayoutSchemaManager initialized")

    # Create a test slide
    test_slide = Slide(
        slide_id="test-1",
        slide_number=1,
        title="Test Slide",
        narrative="Test narrative for the slide",
        key_points=["Point 1", "Point 2"],
        slide_type="content_heavy",
        analytics_needed=None,
        visuals_needed=None,
        diagrams_needed=None,
        tables_needed=None
    )

    # Test L05 (Bullet List) - simple layout
    print("\n" + "="*60)
    print("Testing L05 (Bullet List)")
    print("="*60)

    request_l05 = manager.build_content_request("L05", test_slide)

    print("\nExtracted field specifications:")
    print(json.dumps(request_l05['field_specifications'], indent=2))

    # Verify format specs are present
    assert 'field_specifications' in request_l05
    field_specs = request_l05['field_specifications']

    # Check slide_title (should be plain_text, layout_builder)
    assert 'slide_title' in field_specs
    assert field_specs['slide_title']['format_type'] == 'plain_text'
    assert field_specs['slide_title']['format_owner'] == 'layout_builder'
    print("✅ slide_title: plain_text, layout_builder")

    # Check bullets (should be html, text_service with validation_threshold)
    assert 'bullets' in field_specs
    assert field_specs['bullets']['format_type'] == 'html'
    assert field_specs['bullets']['format_owner'] == 'text_service'
    assert field_specs['bullets']['validation_threshold'] == 0.9
    assert field_specs['bullets']['expected_structure'] == 'ul>li or ol>li'
    print("✅ bullets: html, text_service, threshold=0.9, structure='ul>li or ol>li'")

    # Test L20 (Comparison) - nested structure
    print("\n" + "="*60)
    print("Testing L20 (Comparison Layout)")
    print("="*60)

    request_l20 = manager.build_content_request("L20", test_slide)

    print("\nExtracted field specifications:")
    print(json.dumps(request_l20['field_specifications'], indent=2))

    field_specs_l20 = request_l20['field_specifications']

    # Check left_content nested structure
    assert 'left_content' in field_specs_l20
    assert 'structure' in field_specs_l20['left_content']

    left_structure = field_specs_l20['left_content']['structure']
    assert 'header' in left_structure
    assert left_structure['header']['format_type'] == 'plain_text'
    assert left_structure['header']['format_owner'] == 'layout_builder'
    print("✅ left_content.header: plain_text, layout_builder")

    assert 'items' in left_structure
    assert left_structure['items']['format_type'] == 'html'
    assert left_structure['items']['format_owner'] == 'text_service'
    assert left_structure['items']['validation_threshold'] == 0.9
    print("✅ left_content.items: html, text_service, threshold=0.9")

    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED - Format specification extraction working!")
    print("="*60)

if __name__ == '__main__':
    test_format_specs_extraction()
