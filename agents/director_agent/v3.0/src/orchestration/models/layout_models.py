"""
Layout Models for Director Integration
========================================

Models for layout constraints and validation.
Based on content_orchestrator_sla.md specification.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ImageDimensions(BaseModel):
    """Required dimensions for images/charts in a layout."""
    width: int = Field(description="Required width in pixels")
    height: int = Field(description="Required height in pixels")
    aspect_ratio: str = Field(description="Aspect ratio like '16:9', '4:3', '2:1'")
    format: str = Field(description="Required format: 'png', 'jpg', 'svg'")
    tolerance_percent: int = Field(
        default=5,
        description="Allowed variance percentage for dimensions"
    )


class LayoutConstraints(BaseModel):
    """
    Exact constraints for a specific layout.

    All constraints are ZERO-TOLERANCE requirements:
    - Text fields MUST NOT exceed character limits
    - Arrays MUST NOT exceed item counts
    - Array items MUST NOT exceed item limits
    - Images MUST match aspect ratio within tolerance
    - All required fields MUST be present
    """
    # Required fields for this layout
    required_fields: List[str] = Field(
        description="List of required field names",
        example=["slide_title", "chart_url", "key_insights"]
    )

    # Character limits per field
    character_limits: Dict[str, int] = Field(
        description="Maximum characters per text field",
        example={"slide_title": 80, "subtitle": 80, "summary": 200}
    )

    # Image/chart dimensions
    image_dimensions: Optional[Dict[str, ImageDimensions]] = Field(
        default=None,
        description="Required dimensions for image/chart fields"
    )

    # Array field limits (max items)
    array_limits: Dict[str, int] = Field(
        default_factory=dict,
        description="Maximum items per array field",
        example={"bullets": 8, "key_insights": 6}
    )

    # Array item character limits
    array_item_limits: Dict[str, int] = Field(
        default_factory=dict,
        description="Maximum characters per array item",
        example={"bullets_item": 60, "key_insights_item": 80}
    )


class LayoutAssignment(BaseModel):
    """
    Assignment of a specific layout to a slide.

    Director selects the layout from repository and provides
    exact constraints that content must meet.
    """
    slide_id: str = Field(description="Slide identifier like 'slide_003'")
    slide_number: int = Field(description="Slide number")
    layout_id: str = Field(description="Layout ID like 'L17'")
    layout_name: str = Field(description="Human-readable layout name")
    constraints: LayoutConstraints = Field(
        description="Exact requirements for this layout"
    )


class ValidationViolation(BaseModel):
    """A single constraint violation found during validation."""
    field: str = Field(description="Field name that violated constraint")
    constraint: str = Field(
        description="Type of constraint violated",
        example="character_limit, array_limit, required, dimensions"
    )
    expected: str = Field(description="Expected value/constraint")
    actual: Any = Field(description="Actual value found")
    severity: str = Field(
        description="Severity level: 'critical' or 'warning'",
        example="critical"
    )


class ValidationStatus(BaseModel):
    """Validation status for a single slide."""
    compliant: bool = Field(
        description="Whether slide meets all constraints"
    )
    violations: List[ValidationViolation] = Field(
        default_factory=list,
        description="List of constraint violations"
    )


class ValidationReport(BaseModel):
    """Overall validation report for entire presentation."""
    overall_compliant: bool = Field(
        description="Whether entire presentation is compliant"
    )
    total_slides: int = Field(description="Total number of slides")
    compliant_slides: int = Field(description="Number of compliant slides")
    total_violations: int = Field(description="Total violation count")
    critical_violations: int = Field(
        description="Number of critical violations"
    )


class LayoutSpecification(BaseModel):
    """
    Complete specification for a layout template.

    Defines all content fields, their types, and constraints.
    """
    layout_id: str = Field(description="Layout ID like 'L17'")
    name: str = Field(description="Layout name")
    description: str = Field(description="Layout description")
    content_fields: Dict[str, Dict[str, Any]] = Field(
        description="Field definitions with type and constraints",
        example={
            "slide_title": {"type": "text", "max_length": 80},
            "chart_url": {"type": "image", "dimensions": "800x400"},
            "key_insights": {"type": "array", "max_items": 6, "item_max_length": 80}
        }
    )
