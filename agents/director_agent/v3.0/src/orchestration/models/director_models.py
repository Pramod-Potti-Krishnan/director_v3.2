"""
Director Integration Models
============================

Models for integrating with the Director agent that calls this orchestrator.

Based on content_orchestrator_integration.md and content_orchestrator_sla.md specifications.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from .agents import Slide, PresentationStrawman
from .layout_models import ValidationStatus, ValidationReport


class GeneratedText(BaseModel):
    """
    Generated text content from key_points topics.

    Example transformation:
    Input topic: "Q3 revenue growth"
    Output: GeneratedText(content="Q3 revenue reached $127M, up 32% from Q2")
    """
    content: str = Field(description="The actual generated text")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata like word_count, tone, etc."
    )


class GeneratedImage(BaseModel):
    """
    Generated image with URL.

    Director expects actual image URLs, not specifications.
    """
    url: str = Field(description="URL to the generated image")
    caption: Optional[str] = Field(
        default=None,
        description="Optional caption for the image"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata like size, format, generation params"
    )


class GeneratedChart(BaseModel):
    """
    Generated chart with URL and Chart.js data.

    Must include both rendered chart URL and structured data.
    """
    type: str = Field(
        description="Chart type: 'bar', 'line', 'pie', 'area', etc."
    )
    data: Dict[str, Any] = Field(
        description="Chart data in Chart.js format with labels and datasets"
    )
    url: Optional[str] = Field(
        default=None,
        description="Optional URL to rendered chart image"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata like dimensions, colors, etc."
    )


class GeneratedDiagram(BaseModel):
    """
    Generated diagram with URL.

    Director expects actual diagram URLs (SVG, PNG, etc.).
    """
    type: str = Field(
        description="Diagram type: 'flowchart', 'hierarchy', 'process', etc."
    )
    url: str = Field(description="URL to diagram (SVG or PNG)")
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional structured diagram data"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata"
    )


class EnrichedSlide(BaseModel):
    """
    A slide with generated content attached.

    CRITICAL: This structure MUST match Director's expectations exactly.
    - original_slide: The full input Slide
    - generated_content: Dict with actual content (text, images, charts, diagrams)
    - validation_status: Validation against layout constraints
    """
    original_slide: Slide = Field(
        description="The full input slide from strawman"
    )
    slide_id: str = Field(
        description="Slide identifier for easy reference"
    )
    layout_id: str = Field(
        description="Layout ID used for this slide (e.g., 'L17')"
    )
    generated_content: Dict[str, Any] = Field(
        description="Actual generated content",
        example={
            "text": "GeneratedText object or None",
            "images": "[GeneratedImage objects] or []",
            "charts": "[GeneratedChart objects] or []",
            "diagrams": "[GeneratedDiagram objects] or []"
        }
    )
    validation_status: ValidationStatus = Field(
        description="Validation status against layout constraints"
    )


class EnrichedPresentationStrawman(BaseModel):
    """
    Presentation with generated content.

    CRITICAL: This is the EXACT structure Director expects.
    - original_strawman: The full input PresentationStrawman
    - enriched_slides: Array of EnrichedSlide (not "slides"!)
    - validation_report: Overall validation status
    - generation_metadata: Stats about generation process
    """
    original_strawman: PresentationStrawman = Field(
        description="The full input strawman from Director"
    )
    enriched_slides: List[EnrichedSlide] = Field(
        description="Slides with generated content (note: field name is enriched_slides, not slides!)"
    )
    validation_report: ValidationReport = Field(
        description="Overall validation report for entire presentation"
    )
    generation_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata about generation process",
        example={
            "total_items_generated": 12,
            "successful_items": 11,
            "failed_items": 1,
            "generation_time_seconds": 45,
            "timestamp": "2025-01-18T12:34:56Z",
            "failures": [
                {"slide": 5, "type": "image", "error": "API timeout"}
            ]
        }
    )


class ContentGenerationError(BaseModel):
    """
    Error information for failed content generation.

    Used in generation_metadata.failures array.
    """
    slide_number: int = Field(description="Slide where error occurred")
    component_type: str = Field(
        description="Component type that failed",
        example="text, analytics, image, diagram, table"
    )
    error_message: str = Field(description="Error details")
    recoverable: bool = Field(
        default=True,
        description="Whether the error is recoverable or fatal"
    )


# DEPRECATED: This wrapper is no longer used. Director expects EnrichedPresentationStrawman directly.
# Kept for backward compatibility during transition.
class OrchestratorResponse(BaseModel):
    """
    DEPRECATED: Director expects EnrichedPresentationStrawman directly.

    This wrapper was used in v1.0 but is no longer needed.
    Errors/warnings should be embedded in generation_metadata.
    """
    enriched_strawman: EnrichedPresentationStrawman
    errors: List[ContentGenerationError] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    processing_time_seconds: float = 0.0
    total_slides_processed: int = 0
    successful_components: int = 0
    failed_components: int = 0
