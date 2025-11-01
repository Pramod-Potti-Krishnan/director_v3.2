# Director Agent v2.0 - Deck-Builder Integration

## What's New in v2.0

Director v2.0 introduces **deck-builder integration**, transforming the Director from a JSON generator to a **complete presentation builder** that returns actual reveal.js presentation URLs.

### Key Changes

**v1.0**: Returns JSON slide data
```python
response = {
    "type": "PresentationStrawman",
    "main_title": "My Presentation",
    "slides": [
        {"slide_id": "slide_001", "title": "...", ...},
        ...
    ]
}
```

**v2.0**: Returns presentation URL
```python
response = {
    "type": "presentation_url",
    "url": "http://localhost:8000/p/abc123-...",
    "presentation_id": "abc123-...",
    "slide_count": 10,
    "message": "Your presentation is ready! View it at: [url]"
}
```

## New Components

### 1. Layout Mapper
- Intelligently selects deck-builder layout IDs (L01-L24)
- Maps v1.0 slide types to appropriate layouts
- Ensures layout variety (no repetition)
- Configurable via JSON files

### 2. Content Transformer
- Transforms `PresentationStrawman` to deck-builder API format
- Handles field mapping for each layout type
- Respects character limits and truncates intelligently
- Generates placeholders for images/charts/diagrams

### 3. Deck-Builder Client
- Async HTTP client for deck-builder API
- Automatic retry logic (3 attempts)
- Request validation
- Comprehensive error handling
- Graceful fallback to JSON

## Supported Layouts (MVP)

8 essential layouts in MVP:
- **L01**: Title slide (opening)
- **L02**: Section divider
- **L03**: Closing slide
- **L04**: Text + Summary (long-form content)
- **L05**: Bullet list (key points)
- **L06**: Numbered list (sequential steps)
- **L10**: Image + Text (visual slides)
- **L17**: Chart + Insights (data visualization)

## Setup

### Prerequisites

1. **Deck-Builder API** running on `localhost:8000`:
   ```bash
   cd /path/to/deck-builder
   python server.py
   ```

2. **Director v2.0** configured:
   ```bash
   cd /path/to/director-agent/v2.0
   cp .env.example .env
   # Edit .env with your settings
   ```

### Configuration

Add to `.env`:
```bash
# v2.0: Deck-Builder Integration
DECK_BUILDER_ENABLED=true
DECK_BUILDER_API_URL=http://localhost:8000
DECK_BUILDER_TIMEOUT=30
```

### Install Dependencies

```bash
# All dependencies already in requirements.txt
pip install -r requirements.txt
```

## Usage

### Run Director v2.0

```bash
# Activate virtual environment
source venv/bin/activate

# Run standalone test
python test_director_standalone.py

# Or run as server
python main.py
```

### Testing

```bash
# Run deck-builder integration tests
pytest tests/test_deck_builder_integration.py -v

# Run all tests
pytest tests/ -v
```

## How It Works

### Generation Flow

1. **User Request** → Director receives request (e.g., "Create a presentation on AI")

2. **Generate Strawman** → Director agent creates `PresentationStrawman` (JSON)
   - Uses v1.0 logic (unchanged)
   - Generates slides with content guidance

3. **Layout Mapping** → `LayoutMapper` selects layouts for each slide
   - First slide → L01 (Title)
   - Content slides → L04/L05/L06 based on content
   - Visual slides → L10 (Image+Text)
   - Data slides → L17 (Chart+Insights)
   - Last slide → L03 (Closing)

4. **Content Transformation** → `ContentTransformer` converts to API format
   - Maps v1.0 fields to deck-builder content fields
   - Truncates text to respect character limits
   - Generates placeholders for images/charts

5. **API Call** → `DeckBuilderClient` creates presentation
   - POST to `/api/presentations`
   - Receives presentation ID and URL

6. **Return URL** → Director returns URL to user

### Example Transformation

**v1.0 Slide (Input)**:
```python
Slide(
    slide_number=3,
    slide_id="slide_003",
    title="Revenue Growth",
    slide_type="data_driven",
    narrative="Strong quarterly growth",
    key_points=["Q1: 20% increase", "Q2: 35% increase", "Q3: 50% increase"],
    analytics_needed="**Goal:** Show growth. **Content:** Bar chart. **Style:** Modern."
)
```

**Deck-Builder Format (Output)**:
```json
{
    "layout": "L17",
    "content": {
        "slide_title": "Revenue Growth",
        "subtitle": "Strong quarterly growth",
        "chart_url": "PLACEHOLDER_CHART: Bar chart",
        "key_insights": [
            "Q1: 20% increase",
            "Q2: 35% increase",
            "Q3: 50% increase"
        ],
        "summary": "Strong quarterly growth"
    }
}
```

## Error Handling

### Graceful Degradation

If deck-builder API is unavailable, Director automatically falls back to JSON response:

```python
# Deck-builder enabled but fails
try:
    api_response = await deck_builder_client.create_presentation(...)
    return {"type": "presentation_url", "url": ...}
except Exception as e:
    logger.error(f"Deck-builder failed: {e}")
    return strawman  # JSON fallback (v1.0 behavior)
```

### Disabling Deck-Builder

To run in v1.0 mode (JSON only):
```bash
DECK_BUILDER_ENABLED=false
```

## Configuration Files

### Layout Specifications
**Location**: `config/deck_builder/layout_specs.json`

Defines available layouts and their content field requirements:
```json
{
    "L05": {
        "slide_id": "L05",
        "slide_type_main": "Content",
        "slide_sub_type": "List",
        "content_fields": {
            "slide_title": {"max_chars": 60, "max_lines": 1},
            "bullets": {"max_items": 8, "max_chars_per_item": 100}
        }
    }
}
```

### Layout Mapping Rules
**Location**: `config/deck_builder/layout_mapping.json`

Defines how v1.0 slide types map to deck-builder layouts:
```json
{
    "slide_type_mapping": {
        "data_driven": ["L17"],
        "visual_heavy": ["L10"],
        "content_heavy": ["L04", "L05"]
    },
    "content_type_mapping": {
        "has_analytics": ["L17"],
        "has_visuals": ["L10"],
        "has_bullets": ["L05"]
    }
}
```

**Updateable**: Modify these files to adjust layout selection without code changes.

## Architecture Comparison

### v1.0 Architecture
```
User → Director → PresentationStrawman (JSON) → Frontend
```

### v2.0 Architecture
```
User → Director → PresentationStrawman (JSON)
                       ↓
                 Layout Mapper
                       ↓
             Content Transformer
                       ↓
            Deck-Builder API Client
                       ↓
            POST /api/presentations
                       ↓
            Presentation URL → User
```

## Backwards Compatibility

**Director v2.0 maintains v1.0 compatibility**:
- All v1.0 components preserved (prompt system, state machine, agents)
- v1.0 behavior available via `DECK_BUILDER_ENABLED=false`
- Graceful fallback if deck-builder unavailable
- Same input/output for states 1-3 (greeting, questions, plan)
- Only states 4-5 (generate/refine strawman) return URLs instead of JSON

## Troubleshooting

### "Deck-builder API failed" Error

**Check**:
1. Is deck-builder running? `curl http://localhost:8000/health`
2. Is URL correct in `.env`?
3. Check Director logs for detailed error

**Solution**:
```bash
# Start deck-builder if not running
cd /path/to/deck-builder
python server.py

# Verify URL in .env
echo $DECK_BUILDER_API_URL

# Test API directly
curl -X POST http://localhost:8000/api/presentations \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","slides":[{"layout":"L01","content":{"main_title":"Test"}}]}'
```

### Slides Not Mapping to Expected Layouts

**Debug**:
```python
# Add logging to see layout selection
logger.debug(f"Slide {slide.slide_number}: {slide.slide_type} → {layout_id}")
```

**Adjust**:
- Edit `config/deck_builder/layout_mapping.json`
- Reload configuration: `mapper.reload_config()`

### Content Truncated

**Cause**: Character limits exceeded

**Solution**:
- Check limits in `layout_specs.json`
- Make v1.0 content more concise
- Adjust truncation logic in `ContentTransformer`

## Migration from v1.0

### For Developers

1. **Copy v1.0 to v2.0** (already done)
2. **Update configuration**:
   ```bash
   cp .env.example .env
   # Add DECK_BUILDER_* settings
   ```
3. **No code changes required** - deck-builder is optional

### For Users

**No changes required**:
- Same API interface
- Same WebSocket protocol
- Only difference: URL returned instead of JSON for generated presentations

## Performance

### Response Times

- **v1.0** (JSON only): ~5-10 seconds
- **v2.0** (with deck-builder):
  - Strawman generation: ~5-10 seconds
  - Transformation: <1 second
  - API call: ~1-3 seconds
  - **Total**: ~7-14 seconds

### Scalability

- **Deck-builder API** can handle concurrent requests
- **Director** async architecture supports parallel sessions
- **No performance degradation** with deck-builder enabled

## Future Roadmap

### v2.0-Full (Next)
- All 24 layouts supported (L01-L24)
- Enhanced layout variety algorithm
- Actual image/chart generation (no placeholders)
- Batch presentation updates

### v2.1 (Future)
- Presentation templates
- Custom layout configurations
- Real-time preview during generation
- Presentation versioning

### v3.0 (Future)
- Multi-agent architecture (Layout Architect, Visual Designer, etc.)
- Advanced asset generation
- Collaborative editing
- Export to PowerPoint/PDF

## Documentation

- **[DECK_BUILDER_INTEGRATION.md](./DECK_BUILDER_INTEGRATION.md)**: Comprehensive integration guide
- **[Overall_Architecture_Phase_1.md](./Overall_Architecture_Phase_1.md)**: v1.0 architecture reference
- **API Guide**: See deck-builder-info/API_GUIDE.md
- **Layout Reference**: See deck-builder-info/LAYOUT_CLASSIFICATION.md

## Support

For issues or questions:
1. Check **DECK_BUILDER_INTEGRATION.md** troubleshooting section
2. Review Director logs: `logs/director.log`
3. Test deck-builder API independently
4. Verify configuration in `.env`

## Version History

- **v1.0**: JSON-only presentation generation
- **v2.0-MVP**: Deck-builder integration (8 layouts)
- **v2.0-Full** (planned): All 24 layouts, advanced features

---

**Director v2.0** - Transform ideas into live presentations! 🎨🚀
