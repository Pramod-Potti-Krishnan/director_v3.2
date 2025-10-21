"""
Result Stitcher - v2.0
=======================

Fast assembly of API results into Director-compliant format.

This service takes raw API results and maps them to layout-specific
fields, creating the final EnrichedSlide structure.

Performance: <1ms per slide
"""

import logging
from typing import Dict, List, Any, Optional
from orchestration.models.director_models import (
    EnrichedSlide,
    GeneratedText,
    GeneratedChart,
    GeneratedImage,
    GeneratedDiagram
)
from orchestration.models.layout_models import LayoutAssignment, ValidationStatus

logger = logging.getLogger(__name__)


class ResultStitcher:
    """
    Stitches API results into Director-compliant EnrichedSlide format.

    Pure data transformation - no business logic, no validation.
    Just fast assembly of the final structure.
    """

    def __init__(self):
        """Initialize result stitcher."""
        logger.info("ResultStitcher initialized (v2.0)")

    def stitch_slide(
        self,
        slide: Any,
        layout_assignment: LayoutAssignment,
        api_results: Dict[str, Any],
        validation_status: ValidationStatus
    ) -> EnrichedSlide:
        """
        Stitch API results into an EnrichedSlide.

        Args:
            slide: Original slide from strawman
            layout_assignment: Layout assignment for this slide
            api_results: Results from API dispatcher:
                {
                    "text": GeneratedText or None,
                    "charts": [GeneratedChart, ...],
                    "images": [GeneratedImage, ...],
                    "diagrams": [GeneratedDiagram, ...],
                    "errors": [...]
                }
            validation_status: Validation status from SLAValidator

        Returns:
            EnrichedSlide ready for Director
        """
        # Map results to layout-specific fields
        mapped_content = self._map_to_layout(
            slide=slide,
            api_results=api_results,
            layout_id=layout_assignment.layout_id
        )

        # Create enriched slide
        enriched_slide = EnrichedSlide(
            original_slide=slide,
            slide_id=slide.slide_id,
            layout_id=layout_assignment.layout_id,
            generated_content=mapped_content,
            validation_status=validation_status
        )

        return enriched_slide

    def _map_to_layout(
        self,
        slide: Any,
        api_results: Dict[str, Any],
        layout_id: str
    ) -> Dict[str, Any]:
        """
        Map API results to layout-specific field names.

        Args:
            slide: Original slide
            api_results: Raw API results
            layout_id: Layout ID (L01, L05, L10, L17, etc.)

        Returns:
            Dict with layout-specific fields
        """
        # Route to layout-specific mapper
        if layout_id == "L01":
            return self._map_title_slide(slide, api_results)
        elif layout_id == "L05":
            return self._map_bullet_list(slide, api_results)
        elif layout_id == "L10":
            return self._map_image_text(slide, api_results)
        elif layout_id == "L17":
            return self._map_chart_insights(slide, api_results)
        else:
            # Generic mapper
            return self._map_generic(slide, api_results)

    def _map_title_slide(self, slide: Any, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map for L01 (Title Slide).

        Required: main_title, subtitle, presenter_name, organization, date
        """
        text = results.get("text")
        subtitle = text.content if text and isinstance(text, GeneratedText) else ""

        return {
            "main_title": slide.title,
            "subtitle": subtitle,
            "presenter_name": "Content Orchestrator",
            "organization": "AI-Generated",
            "date": "2025-01-18"
        }

    def _map_bullet_list(self, slide: Any, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map for L05 (Bullet List).

        Required: slide_title, subtitle, bullets
        """
        bullets = []

        # Use key_points if available
        if hasattr(slide, 'key_points') and slide.key_points:
            bullets = slide.key_points

        # If we have generated text, split into bullets
        text = results.get("text")
        if text and isinstance(text, GeneratedText):
            sentences = [s.strip() for s in text.content.split(". ") if s.strip()]
            if sentences:
                bullets = sentences

        return {
            "slide_title": slide.title,
            "subtitle": slide.narrative if hasattr(slide, 'narrative') else "",
            "bullets": bullets
        }

    def _map_image_text(self, slide: Any, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map for L10 (Image + Text).

        Required: slide_title, image_url, caption, body_text
        """
        image_url = "https://via.placeholder.com/800x600"
        caption = "Illustrative image"

        # Get first generated image
        images = results.get("images", [])
        if images and len(images) > 0:
            first_image = images[0]
            if isinstance(first_image, GeneratedImage):
                image_url = first_image.url
                caption = first_image.caption

        # Get generated text
        body_text = ""
        text = results.get("text")
        if text and isinstance(text, GeneratedText):
            body_text = text.content

        return {
            "slide_title": slide.title,
            "image_url": image_url,
            "caption": caption,
            "body_text": body_text
        }

    def _map_chart_insights(self, slide: Any, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map for L17 (Chart + Insights).

        Required: slide_title, subtitle, chart_url, chart_data, key_insights, summary
        """
        chart_url = "https://via.placeholder.com/800x400"
        chart_data = {}

        # Get first generated chart
        charts = results.get("charts", [])
        if charts and len(charts) > 0:
            first_chart = charts[0]
            if isinstance(first_chart, GeneratedChart):
                chart_url = first_chart.url if first_chart.url else chart_url
                chart_data = first_chart.data

        # Generate key_insights from key_points or text
        key_insights = []
        if hasattr(slide, 'key_points') and slide.key_points:
            key_insights = slide.key_points

        # If we have generated text, use it for insights
        text = results.get("text")
        if text and isinstance(text, GeneratedText):
            sentences = [s.strip() + "." for s in text.content.split(". ") if s.strip()]
            key_insights = sentences[:6]  # Max 6 for L17

        # Create summary
        summary = slide.narrative if hasattr(slide, 'narrative') else ""
        if not summary and text:
            summary = text.content[:200]  # First 200 chars

        return {
            "slide_title": slide.title,
            "subtitle": slide.narrative if hasattr(slide, 'narrative') else "",
            "chart_url": chart_url,
            "chart_data": chart_data,
            "key_insights": key_insights,
            "summary": summary
        }

    def _map_generic(self, slide: Any, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generic mapper for unknown layouts.

        Creates a reasonable default structure.
        """
        mapped = {
            "slide_title": slide.title,
            "subtitle": slide.narrative if hasattr(slide, 'narrative') else ""
        }

        # Add text if generated
        text = results.get("text")
        if text and isinstance(text, GeneratedText):
            mapped["body_text"] = text.content

        # Add first image if generated
        images = results.get("images", [])
        if images and len(images) > 0:
            mapped["image_url"] = images[0].url

        # Add first chart if generated
        charts = results.get("charts", [])
        if charts and len(charts) > 0:
            mapped["chart_url"] = charts[0].url
            mapped["chart_data"] = charts[0].data

        # Add first diagram if generated
        diagrams = results.get("diagrams", [])
        if diagrams and len(diagrams) > 0:
            mapped["diagram_url"] = diagrams[0].url

        # Add key points as bullets
        if hasattr(slide, 'key_points') and slide.key_points:
            mapped["bullets"] = slide.key_points

        return mapped

    def stitch_batch(
        self,
        slides: List[Any],
        layout_assignments: List[LayoutAssignment],
        all_api_results: Dict[str, Dict[str, Any]],
        all_validation_statuses: Dict[str, ValidationStatus]
    ) -> List[EnrichedSlide]:
        """
        Stitch a batch of slides in one go.

        Args:
            slides: List of slides
            layout_assignments: List of layout assignments
            all_api_results: Dict of API results by slide_id
            all_validation_statuses: Dict of validation statuses by slide_id

        Returns:
            List of EnrichedSlide objects
        """
        enriched_slides = []

        for slide, layout_assignment in zip(slides, layout_assignments):
            api_results = all_api_results.get(slide.slide_id, {
                "text": None,
                "charts": [],
                "images": [],
                "diagrams": [],
                "errors": []
            })

            validation_status = all_validation_statuses.get(
                slide.slide_id,
                ValidationStatus(compliant=False, violations=[])
            )

            enriched_slide = self.stitch_slide(
                slide=slide,
                layout_assignment=layout_assignment,
                api_results=api_results,
                validation_status=validation_status
            )

            enriched_slides.append(enriched_slide)

        return enriched_slides
