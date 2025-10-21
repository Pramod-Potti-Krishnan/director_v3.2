# Dynamic Slide Presentation API - User Guide

## Overview

The Dynamic Slide Presentation API allows you to create custom presentations by sending JSON with slide content. You receive a shareable URL that displays your presentation.

## Quick Start

### 1. Install Dependencies

```bash
cd v7.2-deployable/
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python server.py
```

Server runs on `http://localhost:8000`

### 3. Create a Presentation

Send a POST request with your presentation JSON:

```bash
curl -X POST http://localhost:8000/api/presentations \
  -H "Content-Type: application/json" \
  -d @presentation.json
```

### 4. Get Your Presentation URL

Response:
```json
{
  "success": true,
  "id": "a7f3c912-4e5b-4a1f-9d2e-8c1b3a5e7f9d",
  "url": "/p/a7f3c912-4e5b-4a1f-9d2e-8c1b3a5e7f9d",
  "message": "Presentation created successfully"
}
```

### 5. View Your Presentation

Open: `http://localhost:8000/p/a7f3c912-4e5b-4a1f-9d2e-8c1b3a5e7f9d`

---

## API Endpoints

### POST /api/presentations

Create a new presentation.

**Request Body:**
```json
{
  "title": "My Presentation",
  "slides": [
    {
      "layout": "L01",
      "content": { ... }
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "id": "uuid",
  "url": "/p/uuid",
  "message": "Presentation created successfully"
}
```

### GET /api/presentations/{id}

Get presentation JSON data.

**Response:**
```json
{
  "id": "uuid",
  "title": "My Presentation",
  "slides": [...],
  "created_at": "2025-01-15T10:30:00"
}
```

### GET /p/{id}

View presentation in browser (returns HTML).

### DELETE /api/presentations/{id}

Delete a presentation.

**Response:**
```json
{
  "success": true,
  "message": "Presentation deleted"
}
```

### GET /api/presentations

List all presentation IDs.

**Response:**
```json
{
  "presentations": ["uuid1", "uuid2"],
  "count": 2
}
```

---

## Slide Layout Reference

### Currently Implemented Layouts:

#### L01 - Title Slide
```json
{
  "layout": "L01",
  "content": {
    "main_title": "Your Presentation Title",
    "subtitle": "Subtitle or tagline",
    "presenter_name": "John Smith",
    "organization": "ACME Corp",
    "date": "2025-01-15"
  }
}
```

#### L02 - Section Divider
```json
{
  "layout": "L02",
  "content": {
    "section_title": "Section Name"
  }
}
```

#### L03 - Closing Slide
```json
{
  "layout": "L03",
  "content": {
    "closing_message": "Thank You",
    "subtitle": "Questions? Let's Connect",
    "contact_email": "contact@example.com",
    "website": "www.example.com",
    "social_media": "@example | linkedin.com/company/example"
  }
}
```

#### L04 - Single Column Full Width
```json
{
  "layout": "L04",
  "content": {
    "slide_title": "Overview",
    "subtitle": "Complete explanation",
    "main_text_content": "Your long-form content here...",
    "summary": "Key takeaway"
  }
}
```

#### L05 - Bullet List
```json
{
  "layout": "L05",
  "content": {
    "slide_title": "Key Points",
    "subtitle": "Main highlights",
    "bullets": [
      "First point",
      "Second point",
      "Third point"
    ]
  }
}
```

#### L06 - Numbered List
```json
{
  "layout": "L06",
  "content": {
    "slide_title": "Process Steps",
    "subtitle": "Sequential workflow",
    "numbered_items": [
      {
        "title": "Step 1",
        "description": "Do this first"
      },
      {
        "title": "Step 2",
        "description": "Then do this"
      }
    ]
  }
}
```

#### L17 - Chart-Focused Layout
```json
{
  "layout": "L17",
  "content": {
    "slide_title": "Revenue Growth",
    "subtitle": "Q4 Performance",
    "chart_url": "https://example.com/chart.png",
    "key_insights": [
      "📈 Trend: Upward",
      "🎯 Target: On track",
      "⚡ Growth: 24%"
    ],
    "summary": "Strong momentum heading into next quarter"
  }
}
```

### Other Layouts (L07-L24)

See `models.py` for complete schema definitions of all 24 layouts.

---

## Complete Example

```json
{
  "title": "Q4 Business Review",
  "slides": [
    {
      "layout": "L01",
      "content": {
        "main_title": "Q4 Business Review",
        "subtitle": "Financial Performance 2024",
        "presenter_name": "Sarah Johnson",
        "organization": "Tech Corp",
        "date": "2025-01-15"
      }
    },
    {
      "layout": "L02",
      "content": {
        "section_title": "Key Achievements"
      }
    },
    {
      "layout": "L05",
      "content": {
        "slide_title": "Major Wins",
        "subtitle": "What we accomplished",
        "bullets": [
          "Revenue up 24% year-over-year",
          "150 new enterprise customers",
          "3 successful product launches",
          "Team expanded to 50 people"
        ]
      }
    },
    {
      "layout": "L17",
      "content": {
        "slide_title": "Revenue Trends",
        "subtitle": "Quarterly breakdown",
        "chart_url": "https://example.com/revenue-chart.png",
        "key_insights": [
          "📈 Trend: Consistent growth",
          "🎯 Target: 110% achieved",
          "⚡ Growth: 24% YoY"
        ],
        "summary": "Strong performance across all quarters"
      }
    },
    {
      "layout": "L03",
      "content": {
        "closing_message": "Thank You",
        "subtitle": "Questions & Discussion",
        "contact_email": "sarah.johnson@techcorp.com",
        "website": "www.techcorp.com",
        "social_media": "@techcorp | linkedin.com/company/techcorp"
      }
    }
  ]
}
```

---

## Testing with curl

Create a file `example-presentation.json` with the JSON above, then:

```bash
# Create presentation
curl -X POST http://localhost:8000/api/presentations \
  -H "Content-Type: application/json" \
  -d @example-presentation.json

# Get presentation data
curl http://localhost:8000/api/presentations/YOUR-UUID-HERE

# List all presentations
curl http://localhost:8000/api/presentations

# Delete presentation
curl -X DELETE http://localhost:8000/api/presentations/YOUR-UUID-HERE
```

---

## Testing with Python

```python
import requests
import json

# Create presentation
presentation_data = {
    "title": "My Presentation",
    "slides": [
        {
            "layout": "L01",
            "content": {
                "main_title": "Welcome",
                "subtitle": "To my presentation",
                "presenter_name": "John Doe",
                "organization": "My Company",
                "date": "2025-01-15"
            }
        }
    ]
}

response = requests.post(
    "http://localhost:8000/api/presentations",
    json=presentation_data
)

result = response.json()
print(f"Presentation URL: http://localhost:8000{result['url']}")
```

---

## Notes

- All presentations are stored as JSON files in `storage/presentations/`
- Each presentation gets a unique UUID as its ID
- URLs are shareable and persist until deleted
- The viewer dynamically builds slides from JSON
- Reveal.js features (navigation, transitions, fullscreen) work automatically

---

## Interactive API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation where you can test all endpoints directly in your browser.
