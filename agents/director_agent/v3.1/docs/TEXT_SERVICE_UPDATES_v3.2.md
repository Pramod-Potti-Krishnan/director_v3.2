# Text & Table Builder Service Updates for v3.2 Schema-Driven Architecture
**Date**: 2025-10-20
**Repository**: `/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/text_table_builder/v1.0`
**Director Version**: v3.2

---

## Executive Summary

The Director Service v3.2 introduces schema-driven architecture where layouts are selected using AI semantic matching, and content is generated in structured JSON format matching exact layout field specifications. The Text Service must be updated to support this new paradigm.

### Current State (v1.0)
- Generates HTML strings (` <p>`, `<ul>`, `<li>`, etc.)
- Word count based constraints
- No layout awareness
- Director parses HTML with string operations (error-prone)

### Target State (v1.1 - Schema-Driven)
- Generates structured JSON matching layout schemas
- Field-by-field generation (e.g., quote_text + attribution for L07)
- Layout-aware prompts
- No HTML parsing needed (direct pass-through)

---

## Required Changes

### 1. New Request Model

**File**: `app/models/requests.py`

**Add**: `StructuredTextGenerationRequest` class

```python
from typing import Dict, Any
from pydantic import BaseModel, Field


class StructuredTextGenerationRequest(BaseModel):
    """
    Structured content generation request from Director v3.2.

    New in v1.1: Layout-aware, field-by-field generation.
    """
    # Session tracking
    presentation_id: str = Field(
        description="Unique presentation identifier"
    )

    # Slide identification
    slide_id: str = Field(
        description="Unique slide identifier (e.g., 'slide_001')"
    )
    slide_number: int = Field(
        description="Slide position in presentation"
    )

    # NEW: Layout information from Director
    layout_id: str = Field(
        description="Selected layout ID (e.g., 'L07', 'L05', 'L17')"
    )
    layout_name: str = Field(
        description="Human-readable layout name (e.g., 'Quote Slide')"
    )
    layout_subtype: str = Field(
        description="Layout subtype (e.g., 'Quote', 'List', 'Chart+Insights')"
    )

    # NEW: Complete field specifications from Director
    layout_schema: Dict[str, Any] = Field(
        description="Complete content_schema from layout_schemas.json with field types, max_chars, etc."
    )

    # Content guidance from Director
    content_guidance: Dict[str, Any] = Field(
        description="Narrative, key_points, and context from slide",
        default_factory=dict
    )

    class Config:
        json_schema_extra = {
            "example": {
                "presentation_id": "pres_12345",
                "slide_id": "slide_003",
                "slide_number": 3,
                "layout_id": "L07",
                "layout_name": "Quote Slide",
                "layout_subtype": "Quote",
                "layout_schema": {
                    "quote_text": {
                        "type": "string",
                        "max_chars": 200,
                        "max_lines": 4,
                        "required": True,
                        "description": "The quote text itself"
                    },
                    "attribution": {
                        "type": "string",
                        "max_chars": 60,
                        "max_lines": 2,
                        "format": "em-dash+name",
                        "required": True,
                        "description": "Quote author/source with em-dash"
                    }
                },
                "content_guidance": {
                    "title": "Customer Success Story",
                    "narrative": "A customer shares their experience with our platform",
                    "key_points": ["Transformed work", "Saved 20 hours", "Team loves it"],
                    "presentation_context": "Business proposal presentation for executives"
                }
            }
        }
```

---

### 2. New Response Format

The response should be **pure JSON** matching the layout schema, not HTML.

**Example for L07 (Quote):**
```json
{
  "quote_text": "This platform completely transformed how our team collaborates. We've saved over 20 hours per week, and team morale has never been higher.",
  "attribution": "— Sarah Chen, VP of Operations, TechCorp"
}
```

**Example for L05 (Bullet List):**
```json
{
  "slide_title": "Key Benefits of Our Solution",
  "bullets": [
    "Increase operational efficiency by 40% through automation",
    "Reduce costs by $2M annually with optimized workflows",
    "Improve quality metrics across all departments",
    "Enable real-time decision making with analytics",
    "Scale seamlessly as your business grows"
  ]
}
```

**Example for L20 (Comparison):**
```json
{
  "slide_title": "Our Solution vs Traditional Approach",
  "left_content": {
    "header": "Our Solution",
    "items": [
      "Automated workflows reduce manual effort",
      "Real-time collaboration across teams",
      "Cloud-based accessibility",
      "Integrated analytics dashboard",
      "Scalable to enterprise needs"
    ]
  },
  "right_content": {
    "header": "Traditional Approach",
    "items": [
      "Manual processes require constant oversight",
      "Email-based collaboration with delays",
      "On-premise limitations",
      "Separate reporting tools needed",
      "Complex scaling challenges"
    ]
  }
}
```

---

### 3. New Generator Logic

**File**: `app/core/generators.py`

**Add**: `generate_structured()` method

```python
async def generate_structured(
    self,
    request: StructuredTextGenerationRequest
) -> Dict[str, Any]:
    """
    Generate structured content matching layout schema.

    New in v1.1: Field-by-field generation based on layout_schema.

    Args:
        request: Structured generation request with layout_schema

    Returns:
        Dictionary matching layout_schema field structure
    """
    # Build layout-specific prompt
    prompt = self._build_structured_prompt(request)

    # Generate with LLM
    response_text = await self.llm_client.generate(
        prompt=prompt,
        max_tokens=self._estimate_tokens_from_schema(request.layout_schema),
        temperature=0.7
    )

    # Parse response as JSON
    try:
        generated_content = json.loads(response_text)
    except json.JSONDecodeError:
        # Fallback: extract JSON from markdown code block
        generated_content = self._extract_json_from_response(response_text)

    # Validate against schema
    is_valid, errors = self._validate_against_schema(
        generated_content,
        request.layout_schema
    )

    if not is_valid:
        logger.warning(f"Generated content validation failed: {errors}")
        # Retry or fix based on errors
        generated_content = self._fix_validation_errors(
            generated_content,
            request.layout_schema,
            errors
        )

    return generated_content


def _build_structured_prompt(
    self,
    request: StructuredTextGenerationRequest
) -> str:
    """
    Build layout-specific prompt for structured generation.

    Different prompts for each layout type:
    - L07 (Quote): Extract quote and attribution
    - L05 (Bullets): Generate array of bullet strings
    - L20 (Comparison): Generate two-column structure
    - L04 (Text+Summary): Generate paragraph + summary
    - etc.
    """
    layout_id = request.layout_id
    schema = request.layout_schema
    guidance = request.content_guidance

    # Base prompt template
    prompt = f"""
You are generating presentation slide content for a {request.layout_name} layout.

**Content Guidance:**
- Slide Title: {guidance.get('title', 'N/A')}
- Narrative: {guidance.get('narrative', 'N/A')}
- Key Points: {', '.join(guidance.get('key_points', []))}
- Presentation Context: {guidance.get('presentation_context', 'Professional presentation')}

**Required Output Format:**
Generate content as JSON matching this exact structure:
{json.dumps(self._schema_to_example(schema), indent=2)}

**Field Requirements:**
"""

    # Add field-specific instructions
    for field_name, field_spec in schema.items():
        prompt += f"\n- **{field_name}**:"
        prompt += f"\n  - Type: {field_spec['type']}"
        prompt += f"\n  - Description: {field_spec.get('description', 'N/A')}"

        if 'max_chars' in field_spec:
            prompt += f"\n  - Max Characters: {field_spec['max_chars']}"
        if 'max_items' in field_spec:
            prompt += f"\n  - Max Items: {field_spec['max_items']}"
        if 'format' in field_spec:
            prompt += f"\n  - Format: {field_spec['format']}"
        prompt += "\n"

    # Add layout-specific generation instructions
    if layout_id == "L07":  # Quote
        prompt += """
**Special Instructions for Quote Slide:**
- Extract the most impactful statement from the narrative/key points
- Keep quote_text concise and powerful (150-200 chars recommended)
- Attribution should follow format: "— Name, Title" or "— Name, Organization"
- Make the quote stand-alone compelling
"""

    elif layout_id == "L05":  # Bullet List
        prompt += """
**Special Instructions for Bullet List:**
- Each bullet should be a complete, actionable statement
- Start bullets with strong verbs (Increase, Reduce, Enable, etc.)
- Keep bullets parallel in structure
- No sub-bullets, flat array only
- Include specific metrics/numbers when available
"""

    elif layout_id == "L20":  # Comparison
        prompt += """
**Special Instructions for Comparison:**
- left_content and right_content should mirror each other
- Same number of items in both columns (parallel structure)
- Clear contrasting points
- Headers should clearly indicate what's being compared
"""

    elif layout_id in ["L04", "L11", "L15"]:  # Text layouts
        prompt += """
**Special Instructions for Text Content:**
- Use complete sentences and paragraphs
- Natural flow and readability
- Avoid bullet-like formatting
- Professional tone matching presentation context
"""

    prompt += """

**IMPORTANT:**
- Return ONLY valid JSON, no markdown formatting
- All required fields MUST be present
- Respect character limits strictly
- Use professional, clear language
- Match the tone to the presentation context

Return your response as pure JSON.
"""

    return prompt
```

---

### 4. New API Endpoint

**File**: `app/api/routes.py`

**Add**: Structured generation endpoint

```python
@router.post("/api/v1/generate/structured")
async def generate_structured_content(
    request: StructuredTextGenerationRequest
) -> Dict[str, Any]:
    """
    Generate structured content matching layout schema.

    New in v1.1: Schema-driven generation for Director v3.2.

    Returns:
        Dictionary with generated content matching layout_schema structure
        plus metadata about generation
    """
    try:
        # Initialize generator
        generator = TextGenerator(llm_client=get_llm_client())

        # Generate structured content
        generated_content = await generator.generate_structured(request)

        # Build response
        return {
            "content": generated_content,  # Structured JSON, not HTML
            "metadata": {
                "layout_id": request.layout_id,
                "layout_name": request.layout_name,
                "generation_time_ms": generator.last_generation_time,
                "model_used": generator.model_name,
                "field_count": len(generated_content),
                "validation_passed": True
            },
            "session_id": f"{request.presentation_id}_{request.slide_id}"
        }

    except Exception as e:
        logger.error(f"Structured generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Structured content generation failed: {str(e)}"
        )
```

---

### 5. Schema Validation Utilities

**File**: `app/utils/schema_validator.py` (NEW)

```python
"""Schema validation for structured content generation."""

from typing import Dict, Any, List, Tuple


def validate_against_schema(
    content: Dict[str, Any],
    schema: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """
    Validate generated content against layout schema.

    Args:
        content: Generated content dictionary
        schema: Layout schema from Director

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check required fields
    for field_name, field_spec in schema.items():
        if field_spec.get('required', False) and field_name not in content:
            errors.append(f"Missing required field: {field_name}")

    # Check field types and constraints
    for field_name, field_value in content.items():
        if field_name not in schema:
            errors.append(f"Unexpected field: {field_name}")
            continue

        field_spec = schema[field_name]
        field_type = field_spec['type']

        # Type validation
        if field_type == 'string':
            if not isinstance(field_value, str):
                errors.append(f"Field {field_name} must be string")
            elif 'max_chars' in field_spec and len(field_value) > field_spec['max_chars']:
                errors.append(
                    f"Field {field_name} exceeds max_chars: "
                    f"{len(field_value)} > {field_spec['max_chars']}"
                )

        elif field_type == 'array':
            if not isinstance(field_value, list):
                errors.append(f"Field {field_name} must be array")
            elif 'max_items' in field_spec and len(field_value) > field_spec['max_items']:
                errors.append(f"Field {field_name} exceeds max_items")

    is_valid = len(errors) == 0
    return is_valid, errors
```

---

## Migration Strategy

### Phase 1: Add New Endpoint (Backward Compatible)
1. Add `StructuredTextGenerationRequest` model
2. Add `/api/v1/generate/structured` endpoint
3. Keep existing `/api/v1/generate/text` endpoint (for v3.1 compatibility)
4. Test structured generation with Director v3.2

### Phase 2: Validate & Refine
1. Test with all 24 layout types
2. Refine prompts for each layout
3. Handle edge cases (validation errors, retries)
4. Performance optimization

### Phase 3: Production Deployment
1. Deploy v1.1 to Railway
2. Update Director v3.2 to use structured endpoint
3. Monitor logs for validation errors
4. Deprecate old HTML endpoint after validation

---

## Testing Checklist

### Layout Coverage
Test structured generation for key layouts:
- ✅ L07 (Quote) - Extract quote + attribution
- ✅ L05 (Bullet List) - Generate array of strings
- ✅ L04 (Text+Summary) - Paragraph + summary box
- ✅ L06 (Numbered List) - Array of objects with title+description
- ✅ L17 (Chart+Insights) - Chart placeholder + insights array
- ✅ L19 (Dashboard) - Metrics array with value+label
- ✅ L20 (Comparison) - Two-column structure
- ✅ L22 (Two-Column) - Dual content blocks
- ✅ L23 (Three-Column) - Three parallel sections
- ✅ L24 (Quad Grid) - Four quadrants

### Validation Tests
- ✅ All required fields present
- ✅ Character limits respected
- ✅ Array item counts within limits
- ✅ Object structures match schema
- ✅ Nested structures validated
- ✅ Format constraints (e.g., em-dash in attribution)

### Integration Tests
- ✅ Director → Text Service → Layout Builder flow
- ✅ Session context retention works
- ✅ Error handling (validation failures, retries)
- ✅ Performance (response time <5s)

---

## Example Prompts by Layout

### L07 (Quote)
```
Generate a compelling quote slide:
- Extract the most impactful customer statement
- Format attribution as "— Name, Title/Organization"
- Keep quote punchy and memorable (150-200 chars)
```

### L05 (Bullet List)
```
Generate 5-8 concise bullet points:
- Start with action verbs (Increase, Reduce, Enable)
- Include specific metrics when possible
- Keep parallel structure
- Each bullet 80-100 characters
```

### L20 (Comparison)
```
Generate side-by-side comparison:
- Left column: Our solution's strengths
- Right column: Alternative approach challenges
- Same number of items in both columns
- Clear contrasting points
```

---

## Expected Performance

### Response Times
- Simple layouts (L05, L06): 2-4 seconds
- Complex layouts (L20, L23, L24): 4-6 seconds
- Target: < 5 seconds for 95% of requests

### Validation Success Rate
- Target: > 95% of responses pass validation on first try
- Retry mechanism for validation failures
- Automatic field fixing for minor issues (truncation, formatting)

---

## Implementation Priority

### Week 1 (High Priority)
1. StructuredTextGenerationRequest model
2. generate_structured() method
3. Structured generation endpoint
4. Schema validation utilities

### Week 2 (Medium Priority)
5. Layout-specific prompt templates (L04, L05, L06, L07, L17, L19, L20)
6. Validation error handling and auto-fix
7. Integration tests with Director v3.2

### Week 3 (Lower Priority)
8. Remaining layout prompts (L08-L16, L21-L24)
9. Performance optimization
10. Railway deployment

---

## Success Criteria

✅ **All 24 layouts supported** with structured generation
✅ **>95% validation success rate** on first generation
✅ **No HTML parsing needed** in Director
✅ **<5 second response time** for 95% of requests
✅ **Quote detection works** (L07 automatically selected and generated correctly)
✅ **Format purity** (bullets are arrays, not mixed with paragraphs)
✅ **No content truncation** (per-field limits respected)

---

**End of Text Service Updates Specification**
