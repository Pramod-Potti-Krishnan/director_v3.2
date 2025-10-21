"""
Basic tests for deck-builder integration.

Run with: pytest tests/test_deck_builder_integration.py -v
"""
import pytest
from src.models.agents import Slide, PresentationStrawman
from src.utils.layout_mapper import LayoutMapper
from src.utils.content_transformer import ContentTransformer


class TestLayoutMapper:
    """Test layout selection logic."""

    @pytest.fixture
    def mapper(self):
        """Create LayoutMapper instance."""
        return LayoutMapper()

    def test_first_slide_gets_L01(self, mapper):
        """First slide should always get L01 (Title)."""
        slide = Slide(
            slide_number=1,
            slide_id="slide_001",
            title="Test Presentation",
            slide_type="content_heavy",
            narrative="Test narrative",
            key_points=["Point 1", "Point 2"]
        )
        layout_id = mapper.select_layout(slide, slide_position="first", total_slides=5)
        assert layout_id == "L01"

    def test_last_slide_gets_L03(self, mapper):
        """Last slide should always get L03 (Closing)."""
        slide = Slide(
            slide_number=5,
            slide_id="slide_005",
            title="Thank You",
            slide_type="conclusion_slide",
            narrative="Questions?",
            key_points=[]
        )
        layout_id = mapper.select_layout(slide, slide_position="last", total_slides=5)
        assert layout_id == "L03"

    def test_section_divider_gets_L02(self, mapper):
        """Section divider slide should get L02."""
        slide = Slide(
            slide_number=2,
            slide_id="slide_002",
            title="Section Title",
            slide_type="section_divider",
            narrative="Section break",
            key_points=[]
        )
        layout_id = mapper.select_layout(slide, slide_position="middle", total_slides=5)
        assert layout_id == "L02"

    def test_analytics_slide_gets_L17(self, mapper):
        """Slide with analytics_needed should get L17 (Chart+Insights)."""
        slide = Slide(
            slide_number=3,
            slide_id="slide_003",
            title="Revenue Growth",
            slide_type="data_driven",
            narrative="Our revenue has grown",
            key_points=["Q1: 20%", "Q2: 35%", "Q3: 50%"],
            analytics_needed="**Goal:** Show growth trend. **Content:** Bar chart of quarterly revenue. **Style:** Modern."
        )
        layout_id = mapper.select_layout(slide, slide_position="middle", total_slides=5)
        assert layout_id == "L17"

    def test_visual_slide_gets_L10(self, mapper):
        """Slide with visuals_needed should get L10 (Image+Text)."""
        slide = Slide(
            slide_number=3,
            slide_id="slide_003",
            title="Our Product",
            slide_type="visual_heavy",
            narrative="Introducing our new product",
            key_points=["Feature 1", "Feature 2"],
            visuals_needed="**Goal:** Show product. **Content:** Product photo. **Style:** Clean."
        )
        layout_id = mapper.select_layout(slide, slide_position="middle", total_slides=5)
        assert layout_id == "L10"

    def test_bullet_points_get_L05(self, mapper):
        """Slide with many bullet points should get L05 (Bullet List)."""
        slide = Slide(
            slide_number=3,
            slide_id="slide_003",
            title="Key Features",
            slide_type="content_heavy",
            narrative="Our product has many features",
            key_points=["Feature 1", "Feature 2", "Feature 3", "Feature 4", "Feature 5"]
        )
        layout_id = mapper.select_layout(slide, slide_position="middle", total_slides=5)
        assert layout_id == "L05"


class TestContentTransformer:
    """Test content transformation logic."""

    @pytest.fixture
    def mapper(self):
        """Create LayoutMapper instance."""
        return LayoutMapper()

    @pytest.fixture
    def transformer(self, mapper):
        """Create ContentTransformer instance."""
        return ContentTransformer(mapper)

    def test_transform_title_slide(self, transformer):
        """Test transformation of title slide."""
        presentation = PresentationStrawman(
            type="PresentationStrawman",
            main_title="Test Presentation",
            overall_theme="Professional",
            design_suggestions="Modern blue theme",
            target_audience="Business executives",
            presentation_duration=15,
            slides=[]
        )

        slide = Slide(
            slide_number=1,
            slide_id="slide_001",
            title="Test Presentation",
            slide_type="title_slide",
            narrative="Introduction to our topic",
            key_points=[]
        )

        transformed = transformer.transform_slide(slide, "L01", presentation)

        assert transformed["layout"] == "L01"
        assert "main_title" in transformed["content"]
        assert transformed["content"]["main_title"] == "Test Presentation"
        assert "subtitle" in transformed["content"]
        assert "date" in transformed["content"]

    def test_transform_bullet_list(self, transformer):
        """Test transformation of bullet list slide."""
        presentation = PresentationStrawman(
            type="PresentationStrawman",
            main_title="Test Presentation",
            overall_theme="Professional",
            design_suggestions="Modern",
            target_audience="Everyone",
            presentation_duration=10,
            slides=[]
        )

        slide = Slide(
            slide_number=2,
            slide_id="slide_002",
            title="Key Points",
            slide_type="content_heavy",
            narrative="Here are the main ideas",
            key_points=["Point 1", "Point 2", "Point 3", "Point 4"]
        )

        transformed = transformer.transform_slide(slide, "L05", presentation)

        assert transformed["layout"] == "L05"
        assert "slide_title" in transformed["content"]
        assert "bullets" in transformed["content"]
        assert len(transformed["content"]["bullets"]) == 4
        assert transformed["content"]["bullets"][0] == "Point 1"

    def test_transform_chart_slide(self, transformer):
        """Test transformation of chart slide with placeholders."""
        presentation = PresentationStrawman(
            type="PresentationStrawman",
            main_title="Test Presentation",
            overall_theme="Data-driven",
            design_suggestions="Modern",
            target_audience="Analysts",
            presentation_duration=20,
            slides=[]
        )

        slide = Slide(
            slide_number=3,
            slide_id="slide_003",
            title="Revenue Growth",
            slide_type="data_driven",
            narrative="Strong growth trajectory",
            key_points=["20% Q1", "35% Q2", "50% Q3"],
            analytics_needed="**Goal:** Show growth. **Content:** Bar chart. **Style:** Modern."
        )

        transformed = transformer.transform_slide(slide, "L17", presentation)

        assert transformed["layout"] == "L17"
        assert "chart_url" in transformed["content"]
        assert "PLACEHOLDER_CHART" in transformed["content"]["chart_url"]
        assert "key_insights" in transformed["content"]
        assert len(transformed["content"]["key_insights"]) == 3

    def test_truncate_long_text(self, transformer):
        """Test text truncation."""
        long_text = "This is a very long text " * 50  # 125 chars repeated
        truncated = transformer.truncate(long_text, 100)

        assert len(truncated) <= 104  # Allow for "..."
        assert truncated.endswith("...") or truncated.endswith(".")

    def test_full_presentation_transform(self, transformer):
        """Test transformation of full presentation."""
        strawman = PresentationStrawman(
            type="PresentationStrawman",
            main_title="Complete Test",
            overall_theme="Professional",
            design_suggestions="Clean",
            target_audience="Everyone",
            presentation_duration=10,
            slides=[
                Slide(
                    slide_number=1,
                    slide_id="slide_001",
                    title="Title",
                    slide_type="title_slide",
                    narrative="Intro",
                    key_points=[]
                ),
                Slide(
                    slide_number=2,
                    slide_id="slide_002",
                    title="Content",
                    slide_type="content_heavy",
                    narrative="Main content",
                    key_points=["Point 1", "Point 2"]
                ),
                Slide(
                    slide_number=3,
                    slide_id="slide_003",
                    title="Closing",
                    slide_type="conclusion_slide",
                    narrative="Thank you",
                    key_points=[]
                )
            ]
        )

        api_payload = transformer.transform_presentation(strawman)

        assert "title" in api_payload
        assert api_payload["title"] == "Complete Test"
        assert "slides" in api_payload
        assert len(api_payload["slides"]) == 3
        assert api_payload["slides"][0]["layout"] == "L01"
        assert api_payload["slides"][2]["layout"] == "L03"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
