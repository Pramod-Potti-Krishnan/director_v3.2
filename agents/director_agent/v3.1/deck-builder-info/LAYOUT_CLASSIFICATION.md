# Layout Classification Guide
## v7.2 Presentation System - 24 Slide Layouts (L01-L24)

**Purpose**: This document provides comprehensive specifications for all 24 slide layouts to help the slide generator engine select the optimal layout based on content type and presentation goals.

**Grid System**: All layouts use a 32×18 grid system (32 columns × 18 rows). Aspect ratios are calculated from grid positioning.

---

## Field Definitions

- **SlideID**: Layout identifier (L01-L24)
- **SlideTypeMain**: Primary classification (Title / Section / Conclusion / Content)
- **SlideSubType**: Detailed categorization for content slides (helps generator engine select appropriate layout)
- **BestUseCase**: Prescriptive guidance on when to use this layout
- **ElementsDetails**: Specifications for each element including type, character limits, line counts, and aspect ratios

---

## Quick Reference Table

| SlideID | SlideTypeMain | SlideSubType | Best For |
|---------|---------------|--------------|----------|
| L01 | Title | Opening | First slide, cover page, presentation intro |
| L02 | Section | Divider | Section transitions, chapter breaks |
| L03 | Conclusion | Closing | Final slide, thank you, contact info |
| L04 | Content | Text+Summary | Long-form content with summary box |
| L05 | Content | List | Bullet points, key takeaways |
| L06 | Content | Numbered-List | Sequential steps, processes, rankings |
| L07 | Content | Quote | Testimonials, quotes, emphasis |
| L08 | Content | Columns | Multi-topic comparison, parallel concepts |
| L09 | Content | Hero-Image | Image-driven storytelling |
| L10 | Content | Image-Left+Text-Right | Image focus with supporting text |
| L11 | Content | Text-Left+Image-Right | Text focus with supporting image |
| L12 | Content | Gallery | Image showcase, portfolio |
| L13 | Content | Diagram-Centered | Single diagram focus, process flows |
| L14 | Content | Diagram-Left+Text-Right | Diagram explanation |
| L15 | Content | Text-Left+Diagram-Right | Text-driven diagram support |
| L16 | Content | Diagram-Full-Width | Large diagrams, architecture |
| L17 | Content | Chart+Insights | Data visualization with key insights |
| L18 | Content | Table | Structured data, detailed information |
| L19 | Content | Dashboard | KPI metrics, performance indicators |
| L20 | Content | Comparison | Side-by-side comparison, pros/cons |
| L21 | Content | Table+Chart | Data table with visual chart |
| L22 | Content | Two-Column | Dual concepts, before/after |
| L23 | Content | Three-Column | Feature comparison, three pillars |
| L24 | Content | Quad-Grid | Four topics, 2×2 matrix |

---

## Detailed Layout Specifications

### L01 - Title Slide

**SlideID**: L01
**SlideTypeMain**: Title
**SlideSubType**: Opening

**BestUseCase**: Use as the first slide of any presentation. Ideal for setting the stage with presentation title, subtitle, presenter information, and organization branding. Creates a professional opening that establishes credibility and context for the audience.

**ElementsDetails**:
```json
[
  {
    "MainTitle": [
      "type:string",
      "chars:60",
      "lines:1-2",
      "alignment:center",
      "grid:rows(4-9),cols(8-26)",
      "aspect_ratio:'18:5'",
      "font:main-title"
    ]
  },
  {
    "Subtitle": [
      "type:string",
      "chars:100",
      "lines:1-3",
      "alignment:center",
      "grid:rows(8-11),cols(8-26)",
      "aspect_ratio:'18:3'",
      "font:subtitle"
    ]
  },
  {
    "PresenterName": [
      "type:string",
      "chars:40",
      "lines:1-3",
      "alignment:center",
      "grid:rows(11-14),cols(8-26)",
      "font:presenter-name"
    ]
  },
  {
    "Organization": [
      "type:string",
      "chars:50",
      "lines:1-3",
      "alignment:center",
      "grid:rows(13-16),cols(8-26)",
      "font:organization"
    ]
  },
  {
    "Date": [
      "type:string",
      "chars:20",
      "lines:1",
      "alignment:right",
      "grid:rows(17-19),cols(26-33)",
      "font:date"
    ]
  },
  {
    "Logo": [
      "type:image",
      "aspect_ratio:'5:2'",
      "position:bottom-left",
      "grid:rows(17-19),cols(2-7)"
    ]
  }
]
```

---

### L02 - Section Divider

**SlideID**: L02
**SlideTypeMain**: Section
**SlideSubType**: Divider

**BestUseCase**: Use between major presentation sections to create visual breathing room and signal topic transitions. Perfect for breaking up long presentations, introducing new chapters, or marking shifts in narrative direction. Keeps audiences oriented and engaged.

**ElementsDetails**:
```json
[
  {
    "SectionTitle": [
      "type:string",
      "chars:40",
      "lines:1-2",
      "alignment:center",
      "grid:rows(7-12),cols(8-26)",
      "aspect_ratio:'18:5'",
      "font:section-title"
    ]
  }
]
```

---

### L03 - Closing Slide

**SlideID**: L03
**SlideTypeMain**: Conclusion
**SlideSubType**: Closing

**BestUseCase**: Use as the final slide to wrap up presentations professionally. Ideal for thank you messages, calls-to-action, contact information, and leaving audiences with next steps. Provides closure while keeping communication channels open.

**ElementsDetails**:
```json
[
  {
    "ClosingMessage": [
      "type:string",
      "chars:50",
      "lines:1-2",
      "alignment:center",
      "grid:rows(5-10),cols(8-26)",
      "aspect_ratio:'18:5'",
      "font:closing-message"
    ]
  },
  {
    "Subtitle": [
      "type:string",
      "chars:80",
      "lines:1-3",
      "alignment:center",
      "grid:rows(9-12),cols(8-26)",
      "font:subtitle"
    ]
  },
  {
    "ContactInfo": [
      "type:string",
      "chars:100",
      "lines:1-3",
      "alignment:center",
      "grid:rows(12-15),cols(8-26)",
      "format:email+website"
    ]
  },
  {
    "SocialMedia": [
      "type:string",
      "chars:80",
      "lines:1-3",
      "alignment:center",
      "grid:rows(14-17),cols(8-26)"
    ]
  },
  {
    "Logo": [
      "type:image",
      "aspect_ratio:'5:2'",
      "position:bottom-left",
      "grid:rows(17-19),cols(2-7)"
    ]
  }
]
```

---

### L04 - Single Column Full Width

**SlideID**: L04
**SlideTypeMain**: Content
**SlideSubType**: Text+Summary

**BestUseCase**: Use for in-depth explanations, detailed narratives, or comprehensive topic coverage that requires substantial text space. The summary box at the bottom is perfect for highlighting key takeaways or actionable insights. Ideal for educational content, policy explanations, or detailed analysis where context and summary are both needed.

**ElementsDetails**:
```json
[
  {
    "SlideTitle": [
      "type:string",
      "chars:60",
      "lines:1",
      "alignment:left",
      "grid:rows(2-3),cols(2-17)",
      "font:slide-title"
    ]
  },
  {
    "Subtitle": [
      "type:string",
      "chars:80",
      "lines:1",
      "alignment:left",
      "grid:rows(3-4),cols(2-17)",
      "font:subtitle"
    ]
  },
  {
    "MainTextContent": [
      "type:string",
      "chars:1200",
      "lines:8-15",
      "alignment:left",
      "grid:rows(5-13),cols(2-31)",
      "aspect_ratio:'29:8'"
    ]
  },
  {
    "Summary": [
      "type:string",
      "chars:200",
      "lines:2-3",
      "alignment:left",
      "grid:rows(14-17),cols(2-31)",
      "style:summary-box"
    ]
  }
]
```

---

### L05 - Bullet List

**SlideID**: L05
**SlideTypeMain**: Content
**SlideSubType**: List

**BestUseCase**: Use for presenting key points, features, benefits, or action items in an easy-to-scan format. Perfect for executive summaries, agenda slides, feature lists, or any content where clarity and quick comprehension are priorities. The bullet format naturally breaks down complex information into digestible chunks.

**ElementsDetails**:
```json
[
  {
    "SlideTitle": [
      "type:string",
      "chars:60",
      "lines:1",
      "alignment:left",
      "grid:rows(2-3),cols(2-17)",
      "font:slide-title"
    ]
  },
  {
    "Subtitle": [
      "type:string",
      "chars:80",
      "lines:1",
      "alignment:left",
      "grid:rows(3-4),cols(2-17)",
      "font:subtitle"
    ]
  },
  {
    "Bullets": [
      "type:array",
      "items:5-8",
      "chars_per_item:100",
      "lines_per_item:1-2",
      "alignment:left",
      "grid:rows(5-12),cols(2-31)",
      "aspect_ratio:'29:7'",
      "format:ul"
    ]
  }
]
```

---

### L06 - Numbered List

**SlideID**: L06
**SlideTypeMain**: Content
**SlideSubType**: Numbered-List

**BestUseCase**: Use for sequential processes, step-by-step instructions, rankings, timelines, or prioritized lists where order matters. Each item includes a title and description, making it ideal for detailed process documentation, implementation roadmaps, or hierarchical information. The numbering reinforces sequence and progression.

**ElementsDetails**:
```json
[
  {
    "SlideTitle": [
      "type:string",
      "chars:60",
      "lines:1",
      "alignment:left",
      "grid:rows(2-3),cols(2-17)",
      "font:slide-title"
    ]
  },
  {
    "Subtitle": [
      "type:string",
      "chars:80",
      "lines:1",
      "alignment:left",
      "grid:rows(3-4),cols(2-17)",
      "font:subtitle"
    ]
  },
  {
    "NumberedItems": [
      "type:array_of_objects",
      "items:4-6",
      "item_structure:{title:string(40chars), description:string(150chars)}",
      "lines_per_item:2-3",
      "alignment:left",
      "grid:rows(5-12),cols(2-26)",
      "aspect_ratio:'24:7'",
      "format:ol"
    ]
  }
]
```

---

### L07 - Quote Slide

**SlideID**: L07
**SlideTypeMain**: Content
**SlideSubType**: Quote

**BestUseCase**: Use for emphasizing key messages, featuring customer testimonials, highlighting expert opinions, or creating dramatic impact with important statements. The centered, prominent text design commands attention and creates memorable moments in presentations. Perfect for social proof, thought leadership, or mission statements.

**ElementsDetails**:
```json
[
  {
    "QuoteText": [
      "type:string",
      "chars:200",
      "lines:2-4",
      "alignment:center",
      "grid:rows(8-11),cols(4-29)",
      "aspect_ratio:'25:3'",
      "font:quote-text",
      "style:quoted"
    ]
  },
  {
    "Attribution": [
      "type:string",
      "chars:60",
      "lines:1-2",
      "alignment:center",
      "grid:rows(11-13),cols(4-29)",
      "font:attribution",
      "format:em-dash+name"
    ]
  }
]
```

---

### L08 - Multi-column Content

**SlideID**: L08
**SlideTypeMain**: Content
**SlideSubType**: Columns

**BestUseCase**: Use for presenting multiple parallel topics, feature comparisons, or independent concepts that benefit from side-by-side layout. Supports up to 3 columns for balanced visual weight. Ideal for product tier comparisons, service offerings, team member profiles, or any content where topics are related but distinct. The columnar structure helps audiences process multiple concepts simultaneously.

**ElementsDetails**:
```json
[
  {
    "SlideTitle": [
      "type:string",
      "chars:60",
      "lines:1",
      "alignment:left",
      "grid:rows(2-3),cols(2-17)",
      "font:slide-title"
    ]
  },
  {
    "Subtitle": [
      "type:string",
      "chars:80",
      "lines:1",
      "alignment:left",
      "grid:rows(3-4),cols(2-17)",
      "font:subtitle"
    ]
  },
  {
    "Columns": [
      "type:array_of_objects",
      "items:2-3",
      "item_structure:{header:string(30chars), content:string(300chars)}",
      "chars_per_column:350",
      "lines_per_column:10-15",
      "alignment:left",
      "grid:rows(5-17),cols(dynamic)",
      "aspect_ratio_per_column:'9:12'",
      "layout:equal-width"
    ]
  }
]
```

---

### L09 - Hero Image with Overlay

**SlideID**: L09
**SlideTypeMain**: Content
**SlideSubType**: Hero-Image

**BestUseCase**: Use for visual storytelling, product showcases, emotional appeals, or brand-focused slides where imagery takes center stage. The overlay text creates impact without overwhelming the visual. Perfect for introducing new products, setting mood or tone, showcasing portfolio work, or creating memorable "wow" moments. Image should be high-quality and thematically aligned with message.

**ElementsDetails**:
```json
[
  {
    "SlideTitle": [
      "type:string",
      "chars:60",
      "lines:1",
      "alignment:left",
      "grid:rows(2-3),cols(2-17)",
      "font:slide-title"
    ]
  },
  {
    "Subtitle": [
      "type:string",
      "chars:80",
      "lines:1",
      "alignment:left",
      "grid:rows(3-4),cols(2-17)",
      "font:subtitle"
    ]
  },
  {
    "HeroImage": [
      "type:image",
      "aspect_ratio:'29:12'",
      "position:full-content-area",
      "grid:rows(5-17),cols(2-31)",
      "fit:contain"
    ]
  },
  {
    "OverlayText": [
      "type:string",
      "chars:50",
      "lines:1-2",
      "position:absolute-bottom-left",
      "style:overlay-dark-background",
      "font:overlay-text"
    ]
  }
]
```

---

### L10 - Split Image Left (60%) / Text Right (40%)

**SlideID**: L10
**SlideTypeMain**: Content
**SlideSubType**: Image-Left+Text-Right

**BestUseCase**: Use when imagery should dominate but requires supporting text explanation. Perfect for product demonstrations, visual case studies, before/after scenarios, or technical diagrams that need context. The 60/40 split prioritizes visual information while maintaining substantial text space for details, specifications, or explanations.

**ElementsDetails**:
```json
[
  {
    "SlideTitle": [
      "type:string",
      "chars:60",
      "lines:1",
      "alignment:left",
      "grid:rows(2-3),cols(2-17)",
      "font:slide-title"
    ]
  },
  {
    "Subtitle": [
      "type:string",
      "chars:80",
      "lines:1",
      "alignment:left",
      "grid:rows(3-4),cols(2-17)",
      "font:subtitle"
    ]
  },
  {
    "Image": [
      "type:image",
      "aspect_ratio:'17:12'",
      "position:left",
      "grid:rows(5-17),cols(2-19)",
      "fit:contain"
    ]
  },
  {
    "TextContent": [
      "type:string",
      "chars:600",
      "lines:10-15",
      "alignment:left",
      "grid:rows(5-17),cols(20-31)",
      "aspect_ratio:'11:12'"
    ]
  }
]
```

---

### L11 - Split Text Left (40%) / Image Right (60%)

**SlideID**: L11
**SlideTypeMain**: Content
**SlideSubType**: Text-Left+Image-Right

**BestUseCase**: Use when text explanation should lead but visual support is essential. Ideal for conceptual explanations followed by visual examples, feature descriptions with product images, or instructions with reference photos. The text-first layout guides the audience through information before reinforcing with visuals. Perfect for training materials or explanatory content.

**ElementsDetails**:
```json
[
  {
    "SlideTitle": [
      "type:string",
      "chars:60",
      "lines:1",
      "alignment:left",
      "grid:rows(2-3),cols(2-17)",
      "font:slide-title"
    ]
  },
  {
    "Subtitle": [
      "type:string",
      "chars:80",
      "lines:1",
      "alignment:left",
      "grid:rows(3-4),cols(2-17)",
      "font:subtitle"
    ]
  },
  {
    "TextContent": [
      "type:string",
      "chars:600",
      "lines:10-15",
      "alignment:left",
      "grid:rows(5-17),cols(2-13)",
      "aspect_ratio:'11:12'"
    ]
  },
  {
    "Image": [
      "type:image",
      "aspect_ratio:'17:12'",
      "position:right",
      "grid:rows(5-17),cols(14-31)",
      "fit:contain"
    ]
  }
]
```

---

### L12 - Image Gallery

**SlideID**: L12
**SlideTypeMain**: Content
**SlideSubType**: Gallery

**BestUseCase**: Use for portfolio showcases, product catalogs, project photo collections, or any content requiring multiple images in balanced layout. The 2×2 grid (4 images) creates visual harmony and allows audiences to compare related visuals. Perfect for before/after comparisons, design variations, team photos, or illustrating diverse examples. Images should be thematically related for coherence.

**ElementsDetails**:
```json
[
  {
    "SlideTitle": [
      "type:string",
      "chars:60",
      "lines:1",
      "alignment:left",
      "grid:rows(2-3),cols(2-17)",
      "font:slide-title"
    ]
  },
  {
    "Subtitle": [
      "type:string",
      "chars:80",
      "lines:1",
      "alignment:left",
      "grid:rows(3-4),cols(2-17)",
      "font:subtitle"
    ]
  },
  {
    "Image1": [
      "type:image",
      "aspect_ratio:'14:6'",
      "position:top-left",
      "grid:rows(5-11),cols(2-16)",
      "fit:contain"
    ]
  },
  {
    "Image2": [
      "type:image",
      "aspect_ratio:'14:6'",
      "position:top-right",
      "grid:rows(5-11),cols(16-30)",
      "fit:contain"
    ]
  },
  {
    "Image3": [
      "type:image",
      "aspect_ratio:'14:6'",
      "position:bottom-left",
      "grid:rows(11-17),cols(2-16)",
      "fit:contain"
    ]
  },
  {
    "Image4": [
      "type:image",
      "aspect_ratio:'14:6'",
      "position:bottom-right",
      "grid:rows(11-17),cols(16-30)",
      "fit:contain"
    ]
  }
]
```

---

### L13 - Centered Diagram

**SlideID**: L13
**SlideTypeMain**: Content
**SlideSubType**: Diagram-Centered

**BestUseCase**: Use for single, important diagrams that require maximum visibility and focus. Perfect for process flows, organizational charts, system architectures, or conceptual frameworks where the diagram is the primary message. The centered positioning with caption creates a clean, professional presentation. Ideal when the visual should speak for itself with minimal text distraction.

**ElementsDetails**:
```json
[
  {
    "SlideTitle": [
      "type:string",
      "chars:60",
      "lines:1",
      "alignment:left",
      "grid:rows(2-3),cols(2-17)",
      "font:slide-title"
    ]
  },
  {
    "Subtitle": [
      "type:string",
      "chars:80",
      "lines:1",
      "alignment:left",
      "grid:rows(3-4),cols(2-17)",
      "font:subtitle"
    ]
  },
  {
    "Diagram": [
      "type:diagram",
      "aspect_ratio:'21:10'",
      "position:center",
      "grid:rows(5-15),cols(6-27)",
      "fit:contain"
    ]
  },
  {
    "Caption": [
      "type:string",
      "chars:120",
      "lines:1",
      "alignment:center",
      "grid:rows(16-17),cols(6-27)",
      "font:caption"
    ]
  }
]
```

---

### L14 - Left Diagram, Right Text

**SlideID**: L14
**SlideTypeMain**: Content
**SlideSubType**: Diagram-Left+Text-Right

**BestUseCase**: Use for technical explanations where the diagram needs equal weight with descriptive text. Perfect for explaining system architectures, process flows with detailed steps, or technical concepts requiring both visual and textual explanation. The side-by-side layout allows audiences to reference the diagram while reading explanations. Ideal for technical documentation or training materials.

**ElementsDetails**:
```json
[
  {
    "SlideTitle": [
      "type:string",
      "chars:60",
      "lines:1",
      "alignment:left",
      "grid:rows(2-3),cols(2-17)",
      "font:slide-title"
    ]
  },
  {
    "Subtitle": [
      "type:string",
      "chars:80",
      "lines:1",
      "alignment:left",
      "grid:rows(3-4),cols(2-17)",
      "font:subtitle"
    ]
  },
  {
    "Diagram": [
      "type:diagram",
      "aspect_ratio:'14:12'",
      "position:left",
      "grid:rows(5-17),cols(2-16)",
      "fit:contain"
    ]
  },
  {
    "TextContent": [
      "type:string",
      "chars:600",
      "lines:10-15",
      "alignment:left",
      "grid:rows(5-17),cols(17-31)",
      "aspect_ratio:'14:12'"
    ]
  }
]
```

---

### L15 - Right Diagram, Left Text

**SlideID**: L15
**SlideTypeMain**: Content
**SlideSubType**: Text-Left+Diagram-Right

**BestUseCase**: Use when text explanation should guide the audience before revealing the diagram. Ideal for building understanding progressively, explaining methodology before showing results, or introducing concepts before visual representation. The text-first layout is particularly effective for educational content where comprehension depends on proper sequencing of information.

**ElementsDetails**:
```json
[
  {
    "SlideTitle": [
      "type:string",
      "chars:60",
      "lines:1",
      "alignment:left",
      "grid:rows(2-3),cols(2-17)",
      "font:slide-title"
    ]
  },
  {
    "Subtitle": [
      "type:string",
      "chars:80",
      "lines:1",
      "alignment:left",
      "grid:rows(3-4),cols(2-17)",
      "font:subtitle"
    ]
  },
  {
    "TextContent": [
      "type:string",
      "chars:600",
      "lines:10-15",
      "alignment:left",
      "grid:rows(5-17),cols(2-15)",
      "aspect_ratio:'13:12'"
    ]
  },
  {
    "Diagram": [
      "type:diagram",
      "aspect_ratio:'15:12'",
      "position:right",
      "grid:rows(5-17),cols(16-31)",
      "fit:contain"
    ]
  }
]
```

---

### L16 - Full-Width Diagram

**SlideID**: L16
**SlideTypeMain**: Content
**SlideSubType**: Diagram-Full-Width

**BestUseCase**: Use for large, complex diagrams requiring maximum space for detail visibility. Perfect for architectural blueprints, comprehensive system maps, detailed flowcharts, or wide-format visualizations like timelines and roadmaps. The full-width layout maximizes diagram real estate while maintaining a caption area. Best for technical audiences who need to see intricate details.

**ElementsDetails**:
```json
[
  {
    "SlideTitle": [
      "type:string",
      "chars:60",
      "lines:1",
      "alignment:left",
      "grid:rows(2-3),cols(2-17)",
      "font:slide-title"
    ]
  },
  {
    "Subtitle": [
      "type:string",
      "chars:80",
      "lines:1",
      "alignment:left",
      "grid:rows(3-4),cols(2-17)",
      "font:subtitle"
    ]
  },
  {
    "Diagram": [
      "type:diagram",
      "aspect_ratio:'29:11'",
      "position:full-width",
      "grid:rows(5-16),cols(2-31)",
      "fit:contain"
    ]
  },
  {
    "Caption": [
      "type:string",
      "chars:150",
      "lines:1",
      "alignment:center",
      "grid:rows(16-17),cols(2-31)",
      "font:caption"
    ]
  }
]
```

---

### L17 - Chart-Focused Layout

**SlideID**: L17
**SlideTypeMain**: Content
**SlideSubType**: Chart+Insights

**BestUseCase**: Use for data-driven presentations where charts need accompanying interpretation and key insights. Perfect for quarterly reviews, performance reports, market analysis, or any scenario where data visualization requires explanatory context. The split layout balances visual data with textual insights, making complex information more digestible. Ideal for executive presentations and analytical content.

**ElementsDetails**:
```json
[
  {
    "SlideTitle": [
      "type:string",
      "chars:60",
      "lines:1",
      "alignment:left",
      "grid:rows(2-3),cols(2-17)",
      "font:slide-title"
    ]
  },
  {
    "Subtitle": [
      "type:string",
      "chars:80",
      "lines:1",
      "alignment:left",
      "grid:rows(3-4),cols(2-17)",
      "font:subtitle"
    ]
  },
  {
    "Chart": [
      "type:chart",
      "aspect_ratio:'17:9'",
      "position:left",
      "grid:rows(5-14),cols(2-19)",
      "fit:contain"
    ]
  },
  {
    "KeyInsights": [
      "type:array",
      "items:4-6",
      "chars_per_item:100",
      "lines_per_item:1-2",
      "alignment:left",
      "grid:rows(5-14),cols(20-31)",
      "aspect_ratio:'11:9'"
    ]
  },
  {
    "Summary": [
      "type:string",
      "chars:200",
      "lines:1-2",
      "alignment:left",
      "grid:rows(15-17),cols(2-31)",
      "style:summary-box"
    ]
  }
]
```

---

### L18 - Data Table

**SlideID**: L18
**SlideTypeMain**: Content
**SlideSubType**: Table

**BestUseCase**: Use for presenting structured data, detailed comparisons, specifications, or any information best organized in rows and columns. Perfect for pricing tables, feature comparisons, financial data, schedules, or inventory lists. The table format allows audiences to scan and compare information efficiently. Best when data precision and detail matter more than visual impact.

**ElementsDetails**:
```json
[
  {
    "SlideTitle": [
      "type:string",
      "chars:60",
      "lines:1",
      "alignment:left",
      "grid:rows(2-3),cols(2-17)",
      "font:slide-title"
    ]
  },
  {
    "Subtitle": [
      "type:string",
      "chars:80",
      "lines:1",
      "alignment:left",
      "grid:rows(3-4),cols(2-17)",
      "font:subtitle"
    ]
  },
  {
    "Table": [
      "type:table",
      "rows:8-12",
      "cols:3-6",
      "aspect_ratio:'29:12'",
      "grid:rows(5-17),cols(2-31)",
      "headers:true",
      "style:bordered"
    ]
  },
  {
    "TableHeaders": [
      "type:array",
      "items:3-6",
      "chars_per_header:20"
    ]
  },
  {
    "TableData": [
      "type:array_of_arrays",
      "rows:8-12",
      "chars_per_cell:30"
    ]
  }
]
```

---

### L19 - Dashboard Layout

**SlideID**: L19
**SlideTypeMain**: Content
**SlideSubType**: Dashboard

**BestUseCase**: Use for displaying key performance indicators (KPIs), metrics dashboards, scorecards, or at-a-glance status updates. Perfect for executive summaries, project health checks, sales performance, or any situation requiring quick visual scanning of multiple metrics. The grid layout (up to 6 metrics) creates a clean, organized presentation of numerical data with labels.

**ElementsDetails**:
```json
[
  {
    "SlideTitle": [
      "type:string",
      "chars:60",
      "lines:1",
      "alignment:left",
      "grid:rows(2-3),cols(2-17)",
      "font:slide-title"
    ]
  },
  {
    "Subtitle": [
      "type:string",
      "chars:80",
      "lines:1",
      "alignment:left",
      "grid:rows(3-4),cols(2-17)",
      "font:subtitle"
    ]
  },
  {
    "Metrics": [
      "type:array_of_objects",
      "items:3-6",
      "item_structure:{value:string(15chars), label:string(40chars)}",
      "layout:grid-3-columns",
      "aspect_ratio_per_metric:'9:5'",
      "grid:rows(5-17),cols(2-31)",
      "style:kpi-box"
    ]
  }
]
```

---

### L20 - Comparison Layout

**SlideID**: L20
**SlideTypeMain**: Content
**SlideSubType**: Comparison

**BestUseCase**: Use for side-by-side comparisons, pros/cons analysis, before/after scenarios, or contrasting two options/approaches. Perfect for decision-making presentations, product comparisons, competitive analysis, or highlighting differences. The equal-width columns create visual balance while the list format makes differences easy to scan. Ideal when audiences need to evaluate alternatives.

**ElementsDetails**:
```json
[
  {
    "SlideTitle": [
      "type:string",
      "chars:60",
      "lines:1",
      "alignment:left",
      "grid:rows(2-3),cols(2-17)",
      "font:slide-title"
    ]
  },
  {
    "Subtitle": [
      "type:string",
      "chars:80",
      "lines:1",
      "alignment:left",
      "grid:rows(3-4),cols(2-17)",
      "font:subtitle"
    ]
  },
  {
    "LeftContent": [
      "type:object",
      "structure:{header:string(30chars), items:array(5-8 items, 80chars each)}",
      "lines:10-15",
      "alignment:left",
      "grid:rows(5-17),cols(2-16)",
      "aspect_ratio:'14:12'"
    ]
  },
  {
    "RightContent": [
      "type:object",
      "structure:{header:string(30chars), items:array(5-8 items, 80chars each)}",
      "lines:10-15",
      "alignment:left",
      "grid:rows(5-17),cols(17-31)",
      "aspect_ratio:'14:12'"
    ]
  }
]
```

---

### L21 - Table-Chart Combo

**SlideID**: L21
**SlideTypeMain**: Content
**SlideSubType**: Table+Chart

**BestUseCase**: Use when raw data and visual representation both add value to the narrative. Perfect for financial reports (numbers + trends), performance analysis (metrics + visualization), or any scenario where audiences need both detailed figures and graphical context. The side-by-side layout allows for data verification while maintaining visual engagement. Ideal for analytical presentations requiring both precision and pattern recognition.

**ElementsDetails**:
```json
[
  {
    "SlideTitle": [
      "type:string",
      "chars:60",
      "lines:1",
      "alignment:left",
      "grid:rows(2-3),cols(2-17)",
      "font:slide-title"
    ]
  },
  {
    "Subtitle": [
      "type:string",
      "chars:80",
      "lines:1",
      "alignment:left",
      "grid:rows(3-4),cols(2-17)",
      "font:subtitle"
    ]
  },
  {
    "Table": [
      "type:table",
      "rows:6-10",
      "cols:2-4",
      "aspect_ratio:'14:12'",
      "grid:rows(5-17),cols(2-16)",
      "style:bordered"
    ]
  },
  {
    "Chart": [
      "type:chart",
      "aspect_ratio:'14:12'",
      "position:right",
      "grid:rows(5-17),cols(17-31)",
      "fit:contain"
    ]
  }
]
```

---

### L22 - Two Column Layout

**SlideID**: L22
**SlideTypeMain**: Content
**SlideSubType**: Two-Column

**BestUseCase**: Use for presenting two related but distinct topics, dual concepts, paired content, or complementary information. Perfect for process steps (step 1 vs step 2), feature pairs, related case studies, or parallel narratives. The equal column width emphasizes balance and parity between topics. More flexible than comparison layout as content doesn't need to be contrasting—just related.

**ElementsDetails**:
```json
[
  {
    "SlideTitle": [
      "type:string",
      "chars:60",
      "lines:1",
      "alignment:left",
      "grid:rows(2-3),cols(2-17)",
      "font:slide-title"
    ]
  },
  {
    "Subtitle": [
      "type:string",
      "chars:80",
      "lines:1",
      "alignment:left",
      "grid:rows(3-4),cols(2-17)",
      "font:subtitle"
    ]
  },
  {
    "LeftColumn": [
      "type:object",
      "structure:{header:string(30chars), content:string(500chars)}",
      "lines:10-15",
      "alignment:left",
      "grid:rows(5-17),cols(2-16)",
      "aspect_ratio:'14:12'"
    ]
  },
  {
    "RightColumn": [
      "type:object",
      "structure:{header:string(30chars), content:string(500chars)}",
      "lines:10-15",
      "alignment:left",
      "grid:rows(5-17),cols(17-31)",
      "aspect_ratio:'14:12'"
    ]
  }
]
```

---

### L23 - Three Column Layout

**SlideID**: L23
**SlideTypeMain**: Content
**SlideSubType**: Three-Column

**BestUseCase**: Use for presenting three balanced concepts, pillars, phases, or categories. Perfect for "good/better/best" tiers, product comparison across three options, three-step processes, or organizational structures with three divisions. The equal-width columns create visual harmony and suggest co-equal importance. Ideal for framework presentations or tiered offerings where three is the natural grouping.

**ElementsDetails**:
```json
[
  {
    "SlideTitle": [
      "type:string",
      "chars:60",
      "lines:1",
      "alignment:left",
      "grid:rows(2-3),cols(2-17)",
      "font:slide-title"
    ]
  },
  {
    "Subtitle": [
      "type:string",
      "chars:80",
      "lines:1",
      "alignment:left",
      "grid:rows(3-4),cols(2-17)",
      "font:subtitle"
    ]
  },
  {
    "Column1": [
      "type:object",
      "structure:{header:string(25chars), content:string(350chars)}",
      "lines:10-15",
      "alignment:left",
      "grid:rows(5-17),cols(2-11)",
      "aspect_ratio:'9:12'"
    ]
  },
  {
    "Column2": [
      "type:object",
      "structure:{header:string(25chars), content:string(350chars)}",
      "lines:10-15",
      "alignment:left",
      "grid:rows(5-17),cols(12-21)",
      "aspect_ratio:'9:12'"
    ]
  },
  {
    "Column3": [
      "type:object",
      "structure:{header:string(25chars), content:string(350chars)}",
      "lines:10-15",
      "alignment:left",
      "grid:rows(5-17),cols(22-31)",
      "aspect_ratio:'9:12'"
    ]
  }
]
```

---

### L24 - Quad Layout (2×2 Grid)

**SlideID**: L24
**SlideTypeMain**: Content
**SlideSubType**: Quad-Grid

**BestUseCase**: Use for 2×2 matrices, four-quadrant models (like SWOT analysis), four distinct topics of equal importance, or segmented content requiring visual separation. Perfect for framework presentations (Eisenhower Matrix, BCG Matrix), four product features, four team goals, or any content naturally grouped into four categories. The bordered boxes create clear visual separation while maintaining balanced layout.

**ElementsDetails**:
```json
[
  {
    "SlideTitle": [
      "type:string",
      "chars:60",
      "lines:1",
      "alignment:left",
      "grid:rows(2-3),cols(2-17)",
      "font:slide-title"
    ]
  },
  {
    "Subtitle": [
      "type:string",
      "chars:80",
      "lines:1",
      "alignment:left",
      "grid:rows(3-4),cols(2-17)",
      "font:subtitle"
    ]
  },
  {
    "Quad1": [
      "type:object",
      "structure:{header:string(25chars), content:string(250chars)}",
      "lines:5-7",
      "alignment:left",
      "grid:rows(5-11),cols(2-16)",
      "aspect_ratio:'14:6'",
      "style:bordered-box"
    ]
  },
  {
    "Quad2": [
      "type:object",
      "structure:{header:string(25chars), content:string(250chars)}",
      "lines:5-7",
      "alignment:left",
      "grid:rows(5-11),cols(17-31)",
      "aspect_ratio:'14:6'",
      "style:bordered-box"
    ]
  },
  {
    "Quad3": [
      "type:object",
      "structure:{header:string(25chars), content:string(250chars)}",
      "lines:5-7",
      "alignment:left",
      "grid:rows(11-17),cols(2-16)",
      "aspect_ratio:'14:6'",
      "style:bordered-box"
    ]
  },
  {
    "Quad4": [
      "type:object",
      "structure:{header:string(25chars), content:string(250chars)}",
      "lines:5-7",
      "alignment:left",
      "grid:rows(11-17),cols(17-31)",
      "aspect_ratio:'14:6'",
      "style:bordered-box"
    ]
  }
]
```

---

## Grid System Notes

### Aspect Ratio Calculation
Aspect ratios are calculated from grid positioning:
- **Formula**: `(col_end - col_start) : (row_end - row_start)`
- **Example**: `grid:rows(5-13),cols(2-19)` = 17 columns × 8 rows = `17:8` (simplified to closest standard ratio)
- All ratios provided as strings (e.g., `aspect_ratio:'16:9'`) to avoid parsing ambiguity

### Common Grid Patterns
- **Title area**: `rows(2-3),cols(2-17)` - Top-left title position
- **Subtitle area**: `rows(3-4),cols(2-17)` - Below title
- **Full content**: `rows(5-17),cols(2-31)` - Maximum content area
- **Footer**: `rows(18),cols(2-31)` - Bottom strip for layout ID
- **50/50 split**: Columns at boundary 16/17 for equal halves
- **60/40 split**: Columns at boundary 19/20 for 60% left
- **40/60 split**: Columns at boundary 13/14 for 40% left

---

## Layout Selection Guide

### By Content Type

**Text-Heavy Content**: L04, L05, L06
**Visual-Heavy Content**: L09, L12, L16
**Balanced Text+Visual**: L10, L11, L13, L14, L15
**Data & Analytics**: L17, L18, L19, L21
**Multiple Topics**: L08, L20, L22, L23, L24
**Emphasis & Impact**: L07, L09
**Structure & Navigation**: L01, L02, L03

### By Use Case

**Opening/Closing**: L01 (title), L02 (section), L03 (closing)
**Teaching/Training**: L04, L06, L14, L15
**Marketing/Sales**: L09, L10, L11, L12, L20
**Executive/Reports**: L17, L18, L19, L21
**Technical/Architecture**: L13, L14, L15, L16
**Feature Comparison**: L08, L20, L22, L23, L24

---

## Implementation Notes

1. **Character Limits**: Approximate maximums for optimal readability at 1920×1080 resolution
2. **Line Counts**: Estimated ranges based on standard font sizes
3. **Aspect Ratios**: Critical for chart/diagram generators to produce properly-fitted visuals
4. **Grid Boundaries**: All elements respect 32×18 grid for consistency
5. **Footer Space**: Row 18 reserved for layout ID display (debugging/reference)

---

**Document Version**: 1.0
**Last Updated**: 2025-10-11
**Grid System**: 32×18
**Total Layouts**: 24 (L01-L24)
