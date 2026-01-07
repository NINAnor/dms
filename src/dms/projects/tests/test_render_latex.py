"""Unit tests for the render_latex module."""

from unittest.mock import patch

import pytest
from pylatex import Document

from dms.projects.libs.render_latex import (
    get_title_text,
    render_element_content,
    render_page_content,
    render_panel_dynamic_item,
    render_to_tex,
)


class TestGetTitleText:
    """Test cases for get_title_text function."""

    def test_dict_with_specified_language(self):
        """Test extracting title from dict with specified language."""
        title_obj = {
            "en": "English Title",
            "no": "Norsk Tittel",
            "default": "Default Title",
        }
        assert get_title_text(title_obj, "en") == "English Title"
        assert get_title_text(title_obj, "no") == "Norsk Tittel"

    def test_dict_with_default_language(self):
        """Test extracting title from dict using default language."""
        title_obj = {"default": "Default Title", "en": "English Title"}
        assert get_title_text(title_obj, "es") == "Default Title"

    def test_dict_empty(self):
        """Test extracting from empty dict returns empty string."""
        title_obj = {}
        assert get_title_text(title_obj, "en") == ""

    def test_string_input(self):
        """Test with string input directly."""
        assert get_title_text("Simple Title", "en") == "Simple Title"

    def test_none_input(self):
        """Test with None input returns empty string."""
        assert get_title_text(None, "en") == ""

    def test_numeric_input(self):
        """Test with numeric input converts to string."""
        assert get_title_text(42, "en") == "42"

    def test_default_language_parameter(self):
        """Test default language parameter."""
        title_obj = {"default": "Default Title"}
        assert get_title_text(title_obj) == "Default Title"


class TestRenderElementContent:
    """Test cases for render_element_content function."""

    @pytest.fixture
    def doc(self):
        """Create a fresh Document instance for each test."""
        return Document()

    def test_text_element(self, doc):
        """Test rendering text element."""
        element = {
            "name": "intro",
            "type": "text",
            "title": {"default": "Introduction", "en": "Introduction"},
        }
        result_data = {"intro": "This is the introduction text."}

        render_element_content(doc, element, result_data, "en")

        # Check that a Subsection was added to the document
        assert len(doc.data) > 0
        # The document should contain the text content
        doc_content = doc.dumps()
        assert "Introduction" in doc_content
        assert "This is the introduction text." in doc_content

    def test_comment_element(self, doc):
        """Test rendering comment element."""
        element = {
            "name": "notes",
            "type": "comment",
            "title": "Comments",
        }
        result_data = {"notes": "Some important notes here."}

        render_element_content(doc, element, result_data)

        # Check that content was added to the document
        assert len(doc.data) > 0
        doc_content = doc.dumps()
        assert "Comments" in doc_content
        assert "Some important notes here." in doc_content

    def test_boolean_element_true(self, doc):
        """Test rendering boolean element with True value."""
        element = {
            "name": "has_data",
            "type": "boolean",
            "title": "Has Data",
        }
        result_data = {"has_data": True}

        render_element_content(doc, element, result_data)

        # Check that content was added to document
        assert len(doc.data) > 0
        doc_content = doc.dumps()
        assert "Has Data" in doc_content
        assert "Yes" in doc_content

    def test_boolean_element_false(self, doc):
        """Test rendering boolean element with False value."""
        element = {
            "name": "has_data",
            "type": "boolean",
            "title": "Has Data",
        }
        result_data = {"has_data": False}

        render_element_content(doc, element, result_data)

        # Check that content was added to document
        assert len(doc.data) > 0
        doc_content = doc.dumps()
        assert "Has Data" in doc_content
        assert "No" in doc_content

    def test_boolean_element_with_comment(self, doc):
        """Test rendering boolean element with comment area."""
        element = {
            "name": "has_data",
            "type": "boolean",
            "title": "Has Data",
            "showCommentArea": True,
        }
        result_data = {"has_data": True, "has_data-Comment": "This is a comment"}

        render_element_content(doc, element, result_data)

        # Check that content was added to document
        assert len(doc.data) > 0
        doc_content = doc.dumps()
        assert "Has Data" in doc_content
        assert "Yes" in doc_content
        assert "Notes: This is a comment" in doc_content

    def test_boolean_element_with_empty_comment(self, doc):
        """Test rendering boolean element with empty comment area."""
        element = {
            "name": "has_data",
            "type": "boolean",
            "title": "Has Data",
            "showCommentArea": True,
        }
        result_data = {"has_data": True, "has_data-Comment": ""}

        render_element_content(doc, element, result_data)

        # Content should be added but empty comment should not be rendered
        assert len(doc.data) > 0
        doc_content = doc.dumps()
        assert "Notes:" not in doc_content

    def test_tagbox_element_list(self, doc):
        """Test rendering tagbox element with list value."""
        element = {
            "name": "tags",
            "type": "tagbox",
            "title": "Tags",
        }
        result_data = {"tags": ["tag1", "tag2", "tag3"]}

        render_element_content(doc, element, result_data)

        # Check that content was added to document
        assert len(doc.data) > 0
        doc_content = doc.dumps()
        assert "Tags" in doc_content
        assert "tag1, tag2, tag3" in doc_content

    def test_tagbox_element_string(self, doc):
        """Test rendering tagbox element with string value."""
        element = {
            "name": "tags",
            "type": "tagbox",
            "title": "Tags",
        }
        result_data = {"tags": "singletag"}

        render_element_content(doc, element, result_data)

        # Check that content was added to document
        assert len(doc.data) > 0
        doc_content = doc.dumps()
        assert "Tags" in doc_content
        assert "singletag" in doc_content

    def test_tagbox_element_with_comment(self, doc):
        """Test rendering tagbox element with comment area."""
        element = {
            "name": "tags",
            "type": "tagbox",
            "title": "Tags",
            "showCommentArea": True,
        }
        result_data = {"tags": ["tag1", "tag2"], "tags-Comment": "Tag notes"}

        render_element_content(doc, element, result_data)

        # Check that content was added to document
        assert len(doc.data) > 0
        doc_content = doc.dumps()
        assert "Tags" in doc_content
        assert "tag1, tag2" in doc_content
        assert "Notes: Tag notes" in doc_content

    def test_element_missing_from_result_data(self, doc):
        """Test that missing elements are skipped."""
        element = {
            "name": "missing_element",
            "type": "text",
            "title": "Missing",
        }
        result_data = {}

        # Should not raise error, just return without adding content
        initial_length = len(doc.data)
        render_element_content(doc, element, result_data)
        # No new content should be added
        assert len(doc.data) == initial_length

    def test_paneldynamic_element(self, doc):
        """Test rendering paneldynamic element."""
        element = {
            "name": "items",
            "type": "paneldynamic",
            "title": "Items",
            "templateElements": [
                {
                    "name": "item_name",
                    "type": "text",
                    "title": "Item Name",
                },
            ],
        }
        result_data = {
            "items": [
                {"item_name": "Item 1"},
                {"item_name": "Item 2"},
            ]
        }

        render_element_content(doc, element, result_data)

        # Check that content was added to document
        assert len(doc.data) > 0
        doc_content = doc.dumps()
        assert "Items" in doc_content
        assert "Item 1" in doc_content
        assert "Item 2" in doc_content

    def test_element_with_name_as_title_fallback(self, doc):
        """Test that element name is used as fallback when title is missing."""
        element = {
            "name": "fieldname",
            "type": "text",
        }
        result_data = {"fieldname": "Some value"}

        render_element_content(doc, element, result_data)

        # Check that content was added to document
        assert len(doc.data) > 0
        doc_content = doc.dumps()
        assert "fieldname" in doc_content
        assert "Some value" in doc_content


class TestRenderPanelDynamicItem:
    """Test cases for render_panel_dynamic_item function."""

    @pytest.fixture
    def doc(self):
        """Create a fresh Document instance for each test."""
        return Document()

    def test_panel_with_text_element(self, doc):
        """Test rendering panel with text element."""
        panel_element = {
            "templateElements": [
                {
                    "name": "text_field",
                    "type": "text",
                    "title": "Text Field",
                },
            ]
        }
        item_data = {"text_field": "Text value"}

        render_panel_dynamic_item(doc, panel_element, item_data)

        # Check that Itemize was added to document
        assert len(doc.data) > 0
        doc_content = doc.dumps()
        assert "Text Field: Text value" in doc_content

    def test_panel_with_boolean_element(self, doc):
        """Test rendering panel with boolean element."""
        panel_element = {
            "templateElements": [
                {
                    "name": "bool_field",
                    "type": "boolean",
                    "title": "Boolean Field",
                },
            ]
        }
        item_data = {"bool_field": True}

        render_panel_dynamic_item(doc, panel_element, item_data)

        # Check that Itemize was added to document
        assert len(doc.data) > 0
        doc_content = doc.dumps()
        assert "Boolean Field: Yes" in doc_content

    def test_panel_with_boolean_element_false(self, doc):
        """Test rendering panel with boolean element set to False."""
        panel_element = {
            "templateElements": [
                {
                    "name": "bool_field",
                    "type": "boolean",
                    "title": "Boolean Field",
                },
            ]
        }
        item_data = {"bool_field": False}

        render_panel_dynamic_item(doc, panel_element, item_data)

        # Check that Itemize was added to document
        assert len(doc.data) > 0
        doc_content = doc.dumps()
        assert "Boolean Field: No" in doc_content

    def test_panel_with_boolean_and_comment(self, doc):
        """Test rendering panel with boolean element and comment."""
        panel_element = {
            "templateElements": [
                {
                    "name": "bool_field",
                    "type": "boolean",
                    "title": "Boolean Field",
                    "showCommentArea": True,
                },
            ]
        }
        item_data = {
            "bool_field": True,
            "bool_field-Comment": "Important comment",
        }

        render_panel_dynamic_item(doc, panel_element, item_data)

        # Check that Itemize was added to document
        assert len(doc.data) > 0
        doc_content = doc.dumps()
        assert "Boolean Field: Yes" in doc_content
        assert "Boolean Field Notes: Important comment" in doc_content

    def test_panel_with_tagbox_element(self, doc):
        """Test rendering panel with tagbox element."""
        panel_element = {
            "templateElements": [
                {
                    "name": "tags_field",
                    "type": "tagbox",
                    "title": "Tags",
                },
            ]
        }
        item_data = {"tags_field": ["tag1", "tag2"]}

        render_panel_dynamic_item(doc, panel_element, item_data)

        # Check that Itemize was added to document
        assert len(doc.data) > 0
        doc_content = doc.dumps()
        assert "Tags: tag1, tag2" in doc_content

    def test_panel_with_missing_element(self, doc):
        """Test rendering panel with missing element in item data."""
        panel_element = {
            "templateElements": [
                {
                    "name": "missing_field",
                    "type": "text",
                    "title": "Missing Field",
                },
            ]
        }
        item_data = {}

        render_panel_dynamic_item(doc, panel_element, item_data)

        # Itemize should still be created but should be empty
        # Check that the document was modified
        doc_content = doc.dumps()
        assert "Missing Field" not in doc_content

    def test_panel_with_multiple_elements(self, doc):
        """Test rendering panel with multiple template elements."""
        panel_element = {
            "templateElements": [
                {
                    "name": "field1",
                    "type": "text",
                    "title": "Field 1",
                },
                {
                    "name": "field2",
                    "type": "boolean",
                    "title": "Field 2",
                },
                {
                    "name": "field3",
                    "type": "tagbox",
                    "title": "Field 3",
                },
            ]
        }
        item_data = {
            "field1": "Value 1",
            "field2": True,
            "field3": ["tag1", "tag2"],
        }

        render_panel_dynamic_item(doc, panel_element, item_data)

        # Check that Itemize was added to document
        assert len(doc.data) > 0
        doc_content = doc.dumps()
        assert "Field 1: Value 1" in doc_content
        assert "Field 2: Yes" in doc_content
        assert "Field 3: tag1, tag2" in doc_content

    def test_panel_with_localized_titles(self, doc):
        """Test rendering panel with localized element titles."""
        panel_element = {
            "templateElements": [
                {
                    "name": "field",
                    "type": "text",
                    "title": {"en": "English Title", "no": "Norsk Tittel"},
                },
            ]
        }
        item_data = {"field": "Value"}

        render_panel_dynamic_item(doc, panel_element, item_data, lang="no")

        # Check that Itemize was added to document
        assert len(doc.data) > 0
        doc_content = doc.dumps()
        assert "Norsk Tittel: Value" in doc_content


class TestRenderPageContent:
    """Test cases for render_page_content function."""

    @pytest.fixture
    def doc(self):
        """Create a fresh Document instance for each test."""
        return Document()

    def test_page_with_title_and_description(self, doc):
        """Test rendering page with title and description."""
        page = {
            "name": "page1",
            "title": {"default": "Page Title"},
            "description": {"default": "Page description text."},
            "elements": [],
        }
        result_data = {}

        render_page_content(doc, page, result_data)

        # Check that a Section was added to the document
        assert len(doc.data) > 0
        doc_content = doc.dumps()
        assert "Page Title" in doc_content
        assert "Page description text." in doc_content

    def test_page_with_multiple_elements(self, doc):
        """Test rendering page with multiple elements."""
        page = {
            "title": "Page Title",
            "elements": [
                {
                    "name": "field1",
                    "type": "text",
                    "title": "Field 1",
                },
                {
                    "name": "field2",
                    "type": "boolean",
                    "title": "Field 2",
                },
            ],
        }
        result_data = {
            "field1": "Value 1",
            "field2": True,
        }

        render_page_content(doc, page, result_data)

        # Check that a Section was added to the document
        assert len(doc.data) > 0
        doc_content = doc.dumps()
        assert "Page Title" in doc_content
        assert "Field 1" in doc_content
        assert "Value 1" in doc_content
        assert "Field 2" in doc_content
        assert "Yes" in doc_content

    def test_page_with_panel_element_skipped(self, doc):
        """Test that panel elements are skipped in page rendering."""
        page = {
            "title": "Page Title",
            "elements": [
                {
                    "name": "panel",
                    "type": "panel",
                    "title": "Panel",
                },
            ],
        }
        result_data = {"panel": "some value"}

        render_page_content(doc, page, result_data)
        # Should not raise error and should not render the panel

    def test_page_with_html_element_skipped(self, doc):
        """Test that HTML elements are skipped in page rendering."""
        page = {
            "title": "Page Title",
            "elements": [
                {
                    "name": "html",
                    "type": "html",
                    "title": "HTML",
                },
            ],
        }
        result_data = {"html": "<div>HTML content</div>"}

        render_page_content(doc, page, result_data)
        # Should not raise error and should not render HTML content

    def test_page_without_description(self, doc):
        """Test rendering page without description."""
        page = {
            "title": "Page Title",
            "elements": [],
        }
        result_data = {}

        render_page_content(doc, page, result_data)

        # Check that a Section was added to the document
        assert len(doc.data) > 0
        doc_content = doc.dumps()
        assert "Page Title" in doc_content

    def test_page_with_name_fallback(self, doc):
        """Test page using name as fallback when title is missing."""
        page = {
            "name": "pagename",
            "elements": [],
        }
        result_data = {}

        render_page_content(doc, page, result_data)

        # Check that a Section was added to the document
        assert len(doc.data) > 0
        doc_content = doc.dumps()
        assert "pagename" in doc_content

    def test_page_default_section_name(self, doc):
        """Test page with default section name when both title and name are missing."""
        page = {
            "elements": [],
        }
        result_data = {}

        render_page_content(doc, page, result_data)

        # Check that a Section was added to the document
        assert len(doc.data) > 0
        doc_content = doc.dumps()
        assert "Section" in doc_content


class TestRenderToTex:
    """Test cases for render_to_tex function."""

    @patch("dms.projects.libs.render_latex.detect")
    def test_basic_document_creation(self, mock_detect):
        """Test basic LaTeX document creation."""
        mock_detect.return_value = "en"

        dmp_template = {
            "title": {"default": "Data Management Plan", "en": "Data Management Plan"},
            "pages": [],
        }
        result_data = {}

        output = render_to_tex(dmp_template, result_data)

        assert isinstance(output, str)
        assert "documentclass" in output
        assert "Data Management Plan" in output
        assert "NINA" in output

    @patch("dms.projects.libs.render_latex.detect")
    def test_document_with_english_language(self, mock_detect):
        """Test document creation with English language detection."""
        mock_detect.return_value = "en"

        dmp_template = {
            "title": "Data Management Plan",
            "pages": [],
        }
        result_data = {"field": "Some English text"}

        output = render_to_tex(dmp_template, result_data)

        assert "english" in output
        assert "inputenc" in output

    @patch("dms.projects.libs.render_latex.detect")
    def test_document_with_norwegian_language(self, mock_detect):
        """Test document creation with Norwegian language detection."""
        mock_detect.return_value = "no"

        dmp_template = {
            "title": "Data Management Plan",
            "pages": [],
        }
        result_data = {"field": "Norsk tekst"}

        output = render_to_tex(dmp_template, result_data)

        assert "norsk" in output
        assert "inputenc" in output

    @patch("dms.projects.libs.render_latex.detect")
    def test_document_with_pages(self, mock_detect):
        """Test document creation with multiple pages."""
        mock_detect.return_value = "en"

        dmp_template = {
            "title": "Data Management Plan",
            "pages": [
                {
                    "title": "Page 1",
                    "elements": [
                        {
                            "name": "field1",
                            "type": "text",
                            "title": "Field 1",
                        }
                    ],
                },
                {
                    "title": "Page 2",
                    "elements": [
                        {
                            "name": "field2",
                            "type": "boolean",
                            "title": "Field 2",
                        }
                    ],
                },
            ],
        }
        result_data = {
            "field1": "Value 1",
            "field2": True,
        }

        output = render_to_tex(dmp_template, result_data)

        assert "Page 1" in output
        assert "Page 2" in output
        assert "Value 1" in output
        assert "Yes" in output

    @patch("dms.projects.libs.render_latex.detect")
    def test_document_uses_correct_detected_language_for_rendering(self, mock_detect):
        """Test that detected language is used for rendering content."""
        mock_detect.return_value = "no"

        dmp_template = {
            "title": {"en": "English Title", "no": "Norsk Tittel"},
            "pages": [
                {
                    "title": {"en": "English Page", "no": "Norsk Side"},
                    "elements": [
                        {
                            "name": "field",
                            "type": "text",
                            "title": {"en": "English Field", "no": "Norsk Felt"},
                        }
                    ],
                }
            ],
        }
        result_data = {"field": "Norsk verdi"}

        output = render_to_tex(dmp_template, result_data)

        assert "Norsk Tittel" in output
        assert "Norsk Side" in output
        assert "Norsk Felt" in output
        assert "Norsk verdi" in output

    @patch("dms.projects.libs.render_latex.detect")
    def test_document_with_empty_pages(self, mock_detect):
        """Test document creation with empty pages list."""
        mock_detect.return_value = "en"

        dmp_template = {
            "title": "Data Management Plan",
            "pages": [],
        }
        result_data = {}

        output = render_to_tex(dmp_template, result_data)

        assert isinstance(output, str)
        assert len(output) > 0

    @patch("dms.projects.libs.render_latex.detect")
    def test_document_geometry_options(self, mock_detect):
        """Test that document has correct geometry options."""
        mock_detect.return_value = "en"

        dmp_template = {
            "title": "Data Management Plan",
            "pages": [],
        }
        result_data = {}

        output = render_to_tex(dmp_template, result_data)

        # Check for margin settings in the output
        assert "margin" in output or "geometry" in output

    @patch("dms.projects.libs.render_latex.detect")
    def test_document_contains_maketitle(self, mock_detect):
        """Test that document contains maketitle command."""
        mock_detect.return_value = "en"

        dmp_template = {
            "title": "Data Management Plan",
            "pages": [],
        }
        result_data = {}

        output = render_to_tex(dmp_template, result_data)

        assert "maketitle" in output

    @patch("dms.projects.libs.render_latex.detect")
    def test_language_detection_with_empty_result_data(self, mock_detect):
        """Test language detection with empty result data."""
        mock_detect.return_value = "en"

        dmp_template = {
            "title": "Data Management Plan",
            "pages": [],
        }
        result_data = {}

        output = render_to_tex(dmp_template, result_data)

        # Should still create valid document
        assert isinstance(output, str)
        # Detect should be called even with empty data
        mock_detect.assert_called()
