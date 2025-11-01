#!/usr/bin/env python3
"""
Script to add format_type and format_owner to layout_schemas.json

Classification Rules:
- Titles/Labels/Short text → plain_text, layout_builder
- Main content areas → html, text_service
- Arrays of content → depends on item type
"""

import json
from pathlib import Path
from typing import Dict, Any


# Field classification rules
PLAIN_TEXT_FIELDS = {
    # Titles
    'slide_title', 'main_title', 'section_title', 'closing_message',
    # Subtitles (when short)
    'subtitle',
    # Labels
    'presenter_name', 'organization', 'date', 'contact_email', 'website', 'social_media',
    # Attributions and captions
    'attribution', 'caption',
    # Headers in structures
    'header',
    # Overlay text
    'overlay_text',
}

HTML_FIELDS = {
    # Main content
    'bullets', 'main_text_content', 'text_content', 'content',
    # Descriptions
    'description',
    # Insights and summaries
    'key_insights', 'summary',
    # Items in comparisons
    'items',
}

PLACEHOLDER_FIELDS = {
    # Assets (not text)
    'image', 'hero_image', 'image_1', 'image_2', 'image_3', 'image_4',
    'diagram', 'chart', 'table',
}


def classify_field(field_name: str, field_spec: Dict[str, Any]) -> tuple[str, str]:
    """
    Classify a field as plain_text or html, and assign owner.

    Returns:
        (format_type, format_owner)
    """
    field_type = field_spec.get('type', 'string')

    # Placeholders don't need format specs
    if field_name in PLACEHOLDER_FIELDS or 'placeholder' in field_type:
        return None, None

    # Plain text fields
    if field_name in PLAIN_TEXT_FIELDS:
        return 'plain_text', 'layout_builder'

    # HTML fields
    if field_name in HTML_FIELDS:
        return 'html', 'text_service'

    # Arrays - check item type
    if field_type == 'array':
        # Arrays of content (bullets, insights) → html
        if field_name in {'bullets', 'key_insights', 'items'}:
            # For L05 bullets, convert to main_content html block
            return 'html', 'text_service'
        # Arrays of objects → check structure
        return None, None  # Will handle in nested structure

    if field_type == 'array_of_objects':
        # Structured data (metrics, numbered_items) → has nested fields
        return None, None  # Will handle in item_structure

    if field_type == 'object':
        # Structured objects (columns, quadrants) → has nested fields
        return None, None  # Will handle in structure

    # Default for main content-heavy fields
    if 'content' in field_name.lower() or 'text' in field_name.lower():
        # If it has high char limit (>200), it's main content
        if field_spec.get('max_chars', 0) > 200:
            return 'html', 'text_service'
        else:
            return 'plain_text', 'layout_builder'

    # Default: short text fields → plain_text
    return 'plain_text', 'layout_builder'


def add_format_specs_to_field(field_spec: Dict[str, Any], field_name: str) -> Dict[str, Any]:
    """Add format_type and format_owner to a field spec."""
    format_type, format_owner = classify_field(field_name, field_spec)

    if format_type is None:
        # Placeholder or nested structure - no format specs
        return field_spec

    # Add format specs
    field_spec['format_type'] = format_type
    field_spec['format_owner'] = format_owner

    # For HTML fields, add validation threshold and expected structure
    if format_type == 'html':
        field_spec['validation_threshold'] = 0.9

        # Infer expected structure
        if field_name == 'bullets' or field_name == 'key_insights':
            field_spec['expected_structure'] = 'ul>li or ol>li'
        elif field_name == 'items':
            field_spec['expected_structure'] = 'ul>li'
        elif 'content' in field_name or 'text' in field_name:
            field_spec['expected_structure'] = 'p or ul>li or mixed'
        elif field_name == 'summary':
            field_spec['expected_structure'] = 'p or strong'

    return field_spec


def process_layout(layout: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single layout, adding format specs to all fields."""
    if 'content_schema' not in layout:
        return layout

    content_schema = layout['content_schema']

    for field_name, field_spec in content_schema.items():
        # Process top-level field
        add_format_specs_to_field(field_spec, field_name)

        # Process nested structures
        if 'item_structure' in field_spec:
            # array_of_objects (L06 numbered_items, L08 columns, L19 metrics)
            for nested_field, nested_spec in field_spec['item_structure'].items():
                add_format_specs_to_field(nested_spec, nested_field)

        if 'structure' in field_spec:
            # object (L20 left_content/right_content, L22-L24 columns/quads)
            for nested_field, nested_spec in field_spec['structure'].items():
                add_format_specs_to_field(nested_spec, nested_field)

    return layout


def main():
    # Load schema
    schema_path = Path(__file__).parent / 'config' / 'deck_builder' / 'layout_schemas.json'

    print(f"Reading {schema_path}...")
    with open(schema_path, 'r') as f:
        schema_data = json.load(f)

    # Process each layout
    layouts = schema_data['layouts']
    print(f"Processing {len(layouts)} layouts...")

    for layout_id, layout in layouts.items():
        print(f"  Processing {layout_id}: {layout['name']}")
        process_layout(layout)

    # Update version
    schema_data['version'] = '2.0'
    schema_data['description'] += ' Enhanced with format ownership specifications for v3.2 architecture.'

    # Write updated schema
    output_path = schema_path
    print(f"\nWriting updated schema to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(schema_data, f, indent=2)

    print("✅ Done! Schema updated with format specifications.")
    print("\nChanges:")
    print("- Added 'format_type' (plain_text/html) to all text fields")
    print("- Added 'format_owner' (layout_builder/text_service) to all text fields")
    print("- Added 'validation_threshold': 0.9 to HTML fields")
    print("- Added 'expected_structure' to HTML fields")
    print("- Updated version to 2.0")


if __name__ == '__main__':
    main()
