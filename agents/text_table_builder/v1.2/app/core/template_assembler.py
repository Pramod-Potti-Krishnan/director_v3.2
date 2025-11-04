"""
Template Assembler for v1.2 Deterministic Assembly Architecture

This module loads HTML templates and assembles them with generated content
by replacing placeholders. Templates are cached for performance.

Architecture:
    Load template by variant_id → Replace placeholders with content
    → Return assembled HTML → Cache for future use
"""

from pathlib import Path
from typing import Dict, Optional
import re


class TemplateAssembler:
    """Loads and assembles HTML templates with generated content."""

    def __init__(self, templates_dir: str = "app/templates"):
        """
        Initialize the TemplateAssembler.

        Args:
            templates_dir: Base directory containing template files
        """
        self.templates_dir = Path(templates_dir)
        self._template_cache: Dict[str, str] = {}

    def load_template(self, template_path: str) -> str:
        """
        Load an HTML template from file.

        Args:
            template_path: Relative path to template (e.g., "matrix/matrix_2x2.html")

        Returns:
            Template HTML string with placeholders

        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        # Check cache first
        if template_path in self._template_cache:
            return self._template_cache[template_path]

        # Normalize template_path (remove base directory if it's included)
        # This handles cases where variant specs include "app/templates/" in path
        template_path_str = str(template_path)
        base_dir_str = str(self.templates_dir) + "/"
        if template_path_str.startswith(base_dir_str):
            template_path = template_path_str[len(base_dir_str):]
        elif template_path_str.startswith("app/templates/"):
            template_path = template_path_str[len("app/templates/"):]

        # Load from file
        full_path = self.templates_dir / template_path

        if not full_path.exists():
            raise FileNotFoundError(f"Template not found: {full_path}")

        with open(full_path, 'r', encoding='utf-8') as f:
            template_html = f.read()

        # Cache for future use
        self._template_cache[template_path] = template_html

        return template_html

    def assemble_template(
        self,
        template_path: str,
        content_map: Dict[str, str]
    ) -> str:
        """
        Assemble template by replacing placeholders with content.

        Args:
            template_path: Relative path to template
            content_map: Dictionary mapping placeholder names to content values
                        e.g., {"box_1_title": "Innovation", "box_1_description": "..."}

        Returns:
            Assembled HTML with all placeholders replaced

        Raises:
            ValueError: If required placeholders are missing
        """
        # Load template
        template_html = self.load_template(template_path)

        # Find all placeholders in template
        # Match only valid placeholder names: letters, numbers, underscores
        # This prevents matching CSS curly braces like { color: #xxx; }
        placeholder_pattern = r'\{([a-z_][a-z0-9_]*)\}'
        placeholders = set(re.findall(placeholder_pattern, template_html, re.IGNORECASE))

        # Check for missing placeholders
        missing = placeholders - set(content_map.keys())
        if missing:
            raise ValueError(
                f"Missing content for placeholders: {', '.join(sorted(missing))}"
            )

        # Replace placeholders
        assembled_html = template_html
        for placeholder, content in content_map.items():
            # Escape the placeholder for regex
            placeholder_pattern = '{' + placeholder + '}'
            assembled_html = assembled_html.replace(placeholder_pattern, content)

        return assembled_html

    def get_template_placeholders(self, template_path: str) -> set:
        """
        Extract all placeholders from a template.

        Args:
            template_path: Relative path to template

        Returns:
            Set of placeholder names found in template
        """
        template_html = self.load_template(template_path)
        # Match only valid placeholder names: letters, numbers, underscores
        # This prevents matching CSS curly braces like { color: #xxx; }
        placeholder_pattern = r'\{([a-z_][a-z0-9_]*)\}'
        placeholders = set(re.findall(placeholder_pattern, template_html, re.IGNORECASE))
        return placeholders

    def validate_content_map(
        self,
        template_path: str,
        content_map: Dict[str, str]
    ) -> Dict[str, list]:
        """
        Validate that content map matches template requirements.

        Args:
            template_path: Relative path to template
            content_map: Dictionary of placeholder -> content mappings

        Returns:
            Dictionary with "missing" and "extra" keys containing lists of placeholders
        """
        template_placeholders = self.get_template_placeholders(template_path)
        content_keys = set(content_map.keys())

        return {
            "missing": sorted(template_placeholders - content_keys),
            "extra": sorted(content_keys - template_placeholders)
        }

    def clear_cache(self):
        """Clear the template cache."""
        self._template_cache.clear()

    def get_cache_stats(self) -> Dict:
        """
        Get statistics about the template cache.

        Returns:
            Dictionary with cache statistics
        """
        return {
            "cached_templates": len(self._template_cache),
            "template_paths": sorted(self._template_cache.keys())
        }
