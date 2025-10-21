"""
Request Builder - v2.0
======================

Direct guidance→API mapping without GenAI.

This service parses guidance strings and builds API requests directly.
NO LLM calls, NO playbooks - pure deterministic parsing.

Performance: <1ms per request
"""

import logging
from typing import Dict, Any, List, Optional
from utils.guidance_parser import parse_guidance

logger = logging.getLogger(__name__)


class RequestBuilder:
    """
    Builds API requests directly from guidance strings.

    Zero GenAI calls - pure deterministic parsing and mapping.
    """

    def __init__(self):
        """Initialize request builder."""
        logger.info("RequestBuilder initialized (v2.0 - no GenAI)")

    def build_all_requests(
        self,
        slide: Any,
        layout_assignment: Any,
        presentation_context: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Build all API requests for a slide in one shot.

        Args:
            slide: Slide with guidance fields
            layout_assignment: Layout with constraints
            presentation_context: Overall presentation info

        Returns:
            Dict with API requests grouped by type:
            {
                "text": [request1, ...],
                "chart": [request1, ...],
                "image": [request1, ...],
                "diagram": [request1, ...]
            }
        """
        requests = {
            "text": [],
            "chart": [],
            "image": [],
            "diagram": []
        }

        # Build text requests from key_points
        if hasattr(slide, 'key_points') and slide.key_points:
            text_req = self.build_text_request(slide, layout_assignment, presentation_context)
            if text_req:
                requests["text"].append(text_req)

        # Build chart requests from analytics_needed
        if hasattr(slide, 'analytics_needed') and slide.analytics_needed:
            chart_req = self.build_chart_request(slide, layout_assignment, presentation_context)
            if chart_req:
                requests["chart"].append(chart_req)

        # Build image requests from visuals_needed
        if hasattr(slide, 'visuals_needed') and slide.visuals_needed:
            image_req = self.build_image_request(slide, layout_assignment, presentation_context)
            if image_req:
                requests["image"].append(image_req)

        # Build diagram requests from diagrams_needed
        if hasattr(slide, 'diagrams_needed') and slide.diagrams_needed:
            diagram_req = self.build_diagram_request(slide, layout_assignment, presentation_context)
            if diagram_req:
                requests["diagram"].append(diagram_req)

        return requests

    def build_text_request(
        self,
        slide: Any,
        layout_assignment: Any,
        presentation_context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Build text generation request from key_points.

        Direct expansion: topics → full sentences with data.

        Args:
            slide: Slide with key_points
            layout_assignment: Layout with character limits
            presentation_context: Overall theme/audience

        Returns:
            API request dict
        """
        if not hasattr(slide, 'key_points') or not slide.key_points:
            return None

        # Determine character limit from layout constraints
        char_limit = None
        if layout_assignment.constraints.character_limits:
            # Get the first text field limit (body_text, summary, etc.)
            for field in ["body_text", "summary", "description", "content"]:
                if field in layout_assignment.constraints.character_limits:
                    char_limit = layout_assignment.constraints.character_limits[field]
                    break

        return {
            "slide_id": slide.slide_id,
            "slide_number": slide.slide_number,
            "type": "text",
            "topics": slide.key_points,
            "narrative": slide.narrative if hasattr(slide, 'narrative') else "",
            "context": {
                "theme": presentation_context.get("overall_theme", ""),
                "audience": presentation_context.get("target_audience", ""),
                "slide_title": slide.title
            },
            "constraints": {
                "max_characters": char_limit,
                "style": "professional",
                "tone": "data-driven"
            }
        }

    def build_chart_request(
        self,
        slide: Any,
        layout_assignment: Any,
        presentation_context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Build chart generation request from analytics_needed guidance.

        Parses: "Goal: X, Content: Y, Style: Z" → Chart API request

        Args:
            slide: Slide with analytics_needed
            layout_assignment: Layout with dimension constraints
            presentation_context: Overall context

        Returns:
            Chart API request dict
        """
        if not hasattr(slide, 'analytics_needed') or not slide.analytics_needed:
            return None

        # Parse guidance string
        guidance = parse_guidance(slide.analytics_needed)

        # Determine chart dimensions from layout constraints
        dimensions = {"width": 800, "height": 400}  # Default
        if layout_assignment.constraints.image_dimensions:
            chart_dims = layout_assignment.constraints.image_dimensions.get("chart_url")
            if chart_dims:
                dimensions = {
                    "width": chart_dims.width,
                    "height": chart_dims.height,
                    "aspect_ratio": chart_dims.aspect_ratio
                }

        # Determine chart type from style guidance
        chart_type = "bar"  # Default
        style = guidance.get("style", "").lower()
        if "line" in style or "trend" in style:
            chart_type = "line"
        elif "pie" in style or "distribution" in style:
            chart_type = "pie"
        elif "scatter" in style:
            chart_type = "scatter"

        return {
            "slide_id": slide.slide_id,
            "slide_number": slide.slide_number,
            "type": "chart",
            "goal": guidance.get("goal", ""),
            "content": guidance.get("content", ""),
            "chart_type": chart_type,
            "style": guidance.get("style", ""),
            "dimensions": dimensions,
            "context": {
                "theme": presentation_context.get("overall_theme", ""),
                "slide_title": slide.title
            }
        }

    def build_image_request(
        self,
        slide: Any,
        layout_assignment: Any,
        presentation_context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Build image generation request from visuals_needed guidance.

        Parses: "Goal: X, Content: Y, Style: Z" → Image API request

        Args:
            slide: Slide with visuals_needed
            layout_assignment: Layout with dimension constraints
            presentation_context: Overall context

        Returns:
            Image API request dict
        """
        if not hasattr(slide, 'visuals_needed') or not slide.visuals_needed:
            return None

        # Parse guidance string
        guidance = parse_guidance(slide.visuals_needed)

        # Determine image dimensions from layout constraints
        dimensions = {"width": 1600, "height": 900, "aspect_ratio": "16:9"}  # Default
        if layout_assignment.constraints.image_dimensions:
            image_dims = layout_assignment.constraints.image_dimensions.get("image_url")
            if image_dims:
                dimensions = {
                    "width": image_dims.width,
                    "height": image_dims.height,
                    "aspect_ratio": image_dims.aspect_ratio
                }

        return {
            "slide_id": slide.slide_id,
            "slide_number": slide.slide_number,
            "type": "image",
            "goal": guidance.get("goal", ""),
            "content": guidance.get("content", ""),
            "style": guidance.get("style", ""),
            "dimensions": dimensions,
            "context": {
                "theme": presentation_context.get("overall_theme", ""),
                "audience": presentation_context.get("target_audience", ""),
                "slide_title": slide.title
            }
        }

    def build_diagram_request(
        self,
        slide: Any,
        layout_assignment: Any,
        presentation_context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Build diagram generation request from diagrams_needed guidance.

        Parses: "Goal: X, Content: Y, Style: Z" → Diagram API request

        Args:
            slide: Slide with diagrams_needed
            layout_assignment: Layout with constraints
            presentation_context: Overall context

        Returns:
            Diagram API request dict
        """
        if not hasattr(slide, 'diagrams_needed') or not slide.diagrams_needed:
            return None

        # Parse guidance string
        guidance = parse_guidance(slide.diagrams_needed)

        # Determine diagram type from style/content guidance
        diagram_type = "flowchart"  # Default
        style = guidance.get("style", "").lower()
        content = guidance.get("content", "").lower()

        if "hierarchy" in style or "org" in content:
            diagram_type = "hierarchy"
        elif "process" in style or "workflow" in content:
            diagram_type = "process"
        elif "network" in style or "connection" in content:
            diagram_type = "network"

        return {
            "slide_id": slide.slide_id,
            "slide_number": slide.slide_number,
            "type": "diagram",
            "goal": guidance.get("goal", ""),
            "content": guidance.get("content", ""),
            "diagram_type": diagram_type,
            "style": guidance.get("style", ""),
            "context": {
                "theme": presentation_context.get("overall_theme", ""),
                "slide_title": slide.title
            }
        }
