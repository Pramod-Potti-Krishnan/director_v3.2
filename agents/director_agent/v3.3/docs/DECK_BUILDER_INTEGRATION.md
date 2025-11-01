# Deck-Builder Integration Guide - Director v2.0

## Overview

Director v2.0 integrates with the deck-builder API to generate actual reveal.js presentations. Instead of returning JSON slide data, the Director now returns a URL to a fully-rendered, interactive presentation.

**Key Change**:
- **v1.0**: Returns `PresentationStrawman` (JSON)
- **v2.0**: Returns presentation URL from deck-builder API

## Architecture

```
User Request
    ↓
Director Agent (Generate Strawman)
    ↓
PresentationStrawman (JSON)
    ↓
Layout Mapper (Select deck-builder layouts)
    ↓
Content Transformer (Transform to API format)
    ↓
Deck-Builder API Client
    ↓
POST /api/presentations
    ↓
Presentation URL (http://localhost:8000/p/uuid)
```

## Components

### 1. Layout Mapper (`src/utils/layout_mapper.py`)

**Purpose**: Select appropriate deck-builder layout IDs for each slide.

**Algorithm**:
1. **Special Cases**: First slide → L01, Last slide → L03, Section divider → L02
2. **Content Type Priority**: Check for analytics/visuals/diagrams/tables
3. **Structure Preference**: Match structure_preference hints
4. **Slide Type Fallback**: Use slide_type mapping
5. **Default**: L05 (Bullet List)

**Layout Selection Examples**:
- Slide with `analytics_needed` → L17 (Chart+Insights)
- Slide with `visuals_needed` → L10 (Image+Text)
- Slide with 5+ key_points → L05 (Bullet List)
- Slide with step-like points → L06 (Numbered List)

**Configuration**: `config/deck_builder/layout_mapping.json`

### 2. Content Transformer (`src/utils/content_transformer.py`)

**Purpose**: Transform v1.0 `Slide` objects to deck-builder API content format.

**Field Mapping**:

**L01 (Title Slide)**:
```python
{
    "main_title": presentation.main_title,
    "subtitle": slide.narrative,
    "presenter_name": "AI-Generated Presentation",
    "organization": presentation.target_audience,
    "date": "2025-01-15"
}
```

**L05 (Bullet List)**:
```python
{
    "slide_title": slide.title,
    "subtitle": slide.narrative[:80],
    "bullets": slide.key_points[:8]  # Max 8 items
}
```

**L17 (Chart+Insights)**:
```python
{
    "slide_title": slide.title,
    "subtitle": slide.narrative[:80],
    "chart_url": "PLACEHOLDER_CHART: [analytics_needed description]",
    "key_insights": slide.key_points[:6],
    "summary": slide.narrative[:200]
}
```

**Placeholder System**:
- Images: `PLACEHOLDER_IMAGE: [description]`
- Charts: `PLACEHOLDER_CHART: [description]`
- Diagrams: `PLACEHOLDER_DIAGRAM: [description]`

**Character Limits**: Automatically truncates text to respect deck-builder layout constraints.

### 3. Deck-Builder Client (`src/utils/deck_builder_client.py`)

**Purpose**: HTTP client for deck-builder API.

**Features**:
- Async HTTP requests (using httpx)
- Automatic retry logic (3 attempts)
- Request validation before sending
- Full error handling
- URL construction helpers

**API Calls**:
```python
# Create presentation
response = await client.create_presentation({
    "title": "My Presentation",
    "slides": [{"layout": "L01", "content": {...}}]
})
# Returns: {"success": True, "id": "uuid", "url": "/p/uuid"}

# Get full URL
full_url = client.get_full_url(response["url"])
# Returns: "http://localhost:8000/p/uuid"
```

## Configuration

### Settings (`config/settings.py`)

```python
# Deck-Builder Integration
DECK_BUILDER_ENABLED: bool = True
DECK_BUILDER_API_URL: str = "http://localhost:8000"
DECK_BUILDER_TIMEOUT: int = 30
```

### Environment Variables (`.env`)

```bash
# v2.0: Deck-Builder Integration
DECK_BUILDER_ENABLED=true
DECK_BUILDER_API_URL=http://localhost:8000
DECK_BUILDER_TIMEOUT=30
```

## Supported Layouts (MVP)

Director v2.0 MVP supports 8 essential layouts:

| Layout ID | Type | Use Case |
|-----------|------|----------|
| L01 | Title | Opening slide |
| L02 | Section | Section dividers |
| L03 | Closing | Final slide |
| L04 | Text+Summary | Long-form content |
| L05 | Bullet List | Key points |
| L06 | Numbered List | Sequential steps |
| L10 | Image+Text | Visual slides |
| L17 | Chart+Insights | Data visualization |

**Future**: All 24 layouts (L01-L24) will be supported in full v2.0.

## Error Handling

### Graceful Degradation

If deck-builder API fails, Director falls back to JSON response:

```python
try:
    # Transform and call deck-builder
    api_payload = transformer.transform_presentation(strawman)
    api_response = await client.create_presentation(api_payload)
    response = {"type": "presentation_url", "url": full_url, ...}
except Exception as e:
    logger.error(f"Deck-builder API failed: {e}")
    response = strawman  # Return JSON fallback
```

### Disabling Deck-Builder

To disable deck-builder integration:
```bash
DECK_BUILDER_ENABLED=false
```

Director will return JSON-only responses like v1.0.

## Testing

### Run Tests

```bash
cd /Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/director_agent/v2.0

# Run deck-builder integration tests
pytest tests/test_deck_builder_integration.py -v

# Run all tests
pytest tests/ -v
```

### Manual Testing

1. **Start Deck-Builder API**:
   ```bash
   cd /path/to/deck-builder
   python server.py
   # Server runs on http://localhost:8000
   ```

2. **Configure Director v2.0**:
   ```bash
   cd /path/to/director-agent/v2.0
   cp .env.example .env
   # Edit .env: Set DECK_BUILDER_API_URL=http://localhost:8000
   ```

3. **Test Presentation Generation**:
   ```bash
   python test_director_standalone.py
   # Select scenario and generate presentation
   # Should return URL instead of JSON
   ```

## Usage Examples

### Example 1: Simple Presentation

**User Request**: "Create a 5-slide presentation on AI in healthcare"

**Director Flow**:
1. Generates `PresentationStrawman` with 5 slides
2. Maps slides to layouts:
   - Slide 1 (title_slide) → L01
   - Slide 2 (content_heavy) → L05 (bullets)
   - Slide 3 (data_driven, analytics_needed) → L17 (chart)
   - Slide 4 (visual_heavy, visuals_needed) → L10 (image+text)
   - Slide 5 (conclusion_slide) → L03
3. Transforms to deck-builder format
4. POST to `/api/presentations`
5. Returns: `{"url": "http://localhost:8000/p/abc123-..."}`

### Example 2: Refinement

**User Request**: "Add more data to slide 3"

**Director Flow**:
1. Refines `PresentationStrawman` (updates slide 3)
2. Maps all slides to layouts again
3. Transforms entire presentation
4. POST to `/api/presentations` (creates NEW presentation)
5. Returns new URL

**Note**: Each generation/refinement creates a new presentation with a new URL.

## Troubleshooting

### Issue: "Deck-builder API failed"

**Causes**:
1. Deck-builder server not running
2. Wrong URL in configuration
3. Network connectivity issues

**Solutions**:
```bash
# Check if deck-builder is running
curl http://localhost:8000/health

# Test API directly
curl -X POST http://localhost:8000/api/presentations \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "slides": [{"layout": "L01", "content": {...}}]}'

# Check Director logs
tail -f logs/director.log
```

### Issue: Slides not mapping to expected layouts

**Solutions**:
1. Check `config/deck_builder/layout_mapping.json`
2. Add logging to see layout selection:
   ```python
   logger.debug(f"Slide {slide.slide_number}: Selected {layout_id}")
   ```
3. Adjust mapping rules in `layout_mapping.json`

### Issue: Content truncated or missing

**Causes**: Character limits exceeded

**Solutions**:
1. Check `layout_specs.json` for field limits
2. Verify truncation logic in `ContentTransformer`
3. Adjust content in v1.0 prompts to be more concise

## Future Enhancements

### Phase 2: Full Layout Support
- Add remaining 16 layouts (L07-L24)
- Enhanced layout variety algorithm
- Smart layout rotation (no repetition)

### Phase 3: Advanced Features
- Actual image generation (replacing placeholders)
- Chart generation from data
- Diagram generation
- Real-time preview during generation
- Presentation versioning

### Phase 4: Integration Improvements
- Batch presentation updates (update specific slides)
- Presentation templates
- Custom layout configurations
- Layout recommendation system

## API Reference

### LayoutMapper

```python
mapper = LayoutMapper()

# Select layout for a slide
layout_id = mapper.select_layout(
    slide=slide_object,
    slide_position="middle",  # "first", "middle", or "last"
    total_slides=10
)

# Get layout specification
spec = mapper.get_layout_spec("L05")

# Reload configuration (for updates)
mapper.reload_config()
```

### ContentTransformer

```python
transformer = ContentTransformer(layout_mapper)

# Transform full presentation
api_payload = transformer.transform_presentation(strawman)

# Transform single slide
transformed_slide = transformer.transform_slide(
    slide=slide_object,
    layout_id="L05",
    presentation=strawman
)

# Utility functions
truncated = transformer.truncate("Long text...", max_chars=100)
placeholder = transformer.generate_placeholder(
    "Bar chart showing revenue",
    "CHART"
)
```

### DeckBuilderClient

```python
client = DeckBuilderClient("http://localhost:8000")

# Create presentation
response = await client.create_presentation({
    "title": "My Presentation",
    "slides": [...]
})

# Get full URL
url = client.get_full_url(response["url"])

# Health check
is_healthy = await client.health_check()
```

## Best Practices

1. **Always validate** deck-builder API is running before starting Director
2. **Use logging** extensively to track layout selection and transformation
3. **Test with** various slide types and content lengths
4. **Monitor** deck-builder API response times
5. **Have fallback** ready (JSON response) for production reliability
6. **Update** layout configurations periodically as deck-builder adds layouts
7. **Document** any custom layout mapping rules

## Changelog

### v2.0-MVP (Current)
- Initial deck-builder integration
- 8 supported layouts (L01-L06, L10, L17)
- Layout selection algorithm
- Content transformation with placeholders
- Async HTTP client with retries
- Graceful degradation to JSON
- Basic test coverage

### v2.0-Future
- All 24 layouts supported
- Actual asset generation
- Enhanced layout variety
- Batch updates
- Performance optimizations
