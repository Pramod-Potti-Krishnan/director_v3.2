"""
Content Orchestrator v2 - Models Package
=========================================

All data models for Content Orchestrator v2.
Self-contained - no external dependencies.
"""

from .agents import PresentationStrawman, Slide
from .layout_models import (
    LayoutAssignment,
    LayoutConstraints,
    ValidationStatus,
    ValidationViolation,
    ValidationReport,
    ImageDimensions
)
from .director_models import (
    EnrichedPresentationStrawman,
    EnrichedSlide,
    GeneratedText,
    GeneratedChart,
    GeneratedImage,
    GeneratedDiagram,
    ContentGenerationError
)

__all__ = [
    # Agents
    "PresentationStrawman",
    "Slide",
    # Layout
    "LayoutAssignment",
    "LayoutConstraints",
    "ValidationStatus",
    "ValidationViolation",
    "ValidationReport",
    "ImageDimensions",
    # Director
    "EnrichedPresentationStrawman",
    "EnrichedSlide",
    "GeneratedText",
    "GeneratedChart",
    "GeneratedImage",
    "GeneratedDiagram",
    "ContentGenerationError",
]
