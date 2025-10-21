"""
SLA Validator - v2.0
=====================

Minimal validation for performance.

Unlike v1.0's comprehensive validation + smart truncation, v2.0 assumes
API clients return compliant content. We only do basic sanity checks.

Performance: <1ms per slide
"""

import logging
from typing import Dict, List, Any
from orchestration.models.layout_models import (
    LayoutConstraints,
    ValidationStatus,
    ValidationViolation,
    LayoutAssignment
)

logger = logging.getLogger(__name__)


class SLAValidator:
    """
    Minimal SLA validation for v2.0.

    Philosophy: Trust but verify. API clients should return compliant
    content, we just check critical violations.
    """

    def __init__(self):
        """Initialize SLA validator."""
        logger.info("SLAValidator initialized (v2.0 - minimal mode)")

    def validate_batch(
        self,
        all_content: Dict[str, Dict[str, Any]],
        layout_assignments: List[Any]
    ) -> Dict[str, ValidationStatus]:
        """
        Validate a batch of slides in one go.

        Args:
            all_content: Dict of content by slide_id
            layout_assignments: List of layout assignments

        Returns:
            Dict of ValidationStatus by slide_id
        """
        validation_results = {}

        for layout_assignment in layout_assignments:
            slide_id = layout_assignment.slide_id
            content = all_content.get(slide_id, {})

            validation_status = self.validate_slide(
                content=content,
                constraints=layout_assignment.constraints,
                slide_id=slide_id
            )

            validation_results[slide_id] = validation_status

        return validation_results

    def validate_slide(
        self,
        content: Dict[str, Any],
        constraints: LayoutConstraints,
        slide_id: str
    ) -> ValidationStatus:
        """
        Minimal validation for a single slide.

        Only checks:
        1. Required fields present
        2. Critical character limit violations (>2x limit)
        3. Critical array violations (>2x limit)

        Args:
            content: Generated content dict
            constraints: Layout constraints
            slide_id: Slide identifier

        Returns:
            ValidationStatus
        """
        violations = []

        # Check required fields
        violations.extend(self._check_required_fields(content, constraints, slide_id))

        # Check critical character limits (only if >2x limit)
        violations.extend(self._check_critical_char_limits(content, constraints, slide_id))

        # Check critical array limits (only if >2x limit)
        violations.extend(self._check_critical_array_limits(content, constraints, slide_id))

        is_compliant = len([v for v in violations if v.severity == "critical"]) == 0

        return ValidationStatus(
            compliant=is_compliant,
            violations=violations
        )

    def _check_required_fields(
        self,
        content: Dict[str, Any],
        constraints: LayoutConstraints,
        slide_id: str
    ) -> List[ValidationViolation]:
        """Check required fields are present."""
        violations = []

        for field in constraints.required_fields:
            if field not in content or content[field] is None:
                violations.append(
                    ValidationViolation(
                        field=field,
                        constraint="required",
                        expected="present",
                        actual="missing",
                        severity="critical"
                    )
                )
                logger.warning(f"Slide {slide_id}: Required field '{field}' missing")

        return violations

    def _check_critical_char_limits(
        self,
        content: Dict[str, Any],
        constraints: LayoutConstraints,
        slide_id: str
    ) -> List[ValidationViolation]:
        """
        Check only CRITICAL character limit violations (>2x limit).

        We assume API clients mostly return compliant content.
        Only flag egregious violations.
        """
        violations = []

        for field, max_length in constraints.character_limits.items():
            if field in content and isinstance(content[field], str):
                actual_length = len(content[field])

                # Only flag if >2x the limit (critical violation)
                if actual_length > max_length * 2:
                    violations.append(
                        ValidationViolation(
                            field=field,
                            constraint="character_limit",
                            expected=f"≤{max_length}",
                            actual=actual_length,
                            severity="critical"
                        )
                    )
                    logger.error(
                        f"Slide {slide_id}: CRITICAL - Field '{field}' is {actual_length} chars "
                        f"(limit: {max_length}, 2x limit: {max_length * 2})"
                    )
                # Log warning for minor violations but don't fail
                elif actual_length > max_length:
                    logger.warning(
                        f"Slide {slide_id}: Field '{field}' exceeds limit: {actual_length} > {max_length} "
                        "(not critical, <2x limit)"
                    )

        return violations

    def _check_critical_array_limits(
        self,
        content: Dict[str, Any],
        constraints: LayoutConstraints,
        slide_id: str
    ) -> List[ValidationViolation]:
        """
        Check only CRITICAL array violations (>2x limit).

        We assume API clients mostly return compliant arrays.
        Only flag egregious violations.
        """
        violations = []

        for field, max_items in constraints.array_limits.items():
            if field in content and isinstance(content[field], list):
                actual_count = len(content[field])

                # Only flag if >2x the limit
                if actual_count > max_items * 2:
                    violations.append(
                        ValidationViolation(
                            field=field,
                            constraint="array_limit",
                            expected=f"≤{max_items} items",
                            actual=actual_count,
                            severity="critical"
                        )
                    )
                    logger.error(
                        f"Slide {slide_id}: CRITICAL - Array '{field}' has {actual_count} items "
                        f"(limit: {max_items}, 2x limit: {max_items * 2})"
                    )
                # Log warning for minor violations
                elif actual_count > max_items:
                    logger.warning(
                        f"Slide {slide_id}: Array '{field}' exceeds limit: {actual_count} > {max_items} "
                        "(not critical, <2x limit)"
                    )

        return violations

    def quick_validate(
        self,
        content: Dict[str, Any],
        constraints: LayoutConstraints
    ) -> bool:
        """
        Ultra-fast validation - just checks required fields.

        For when you need maximum performance and trust API clients.

        Args:
            content: Generated content
            constraints: Layout constraints

        Returns:
            True if all required fields present
        """
        for field in constraints.required_fields:
            if field not in content or content[field] is None:
                return False
        return True
