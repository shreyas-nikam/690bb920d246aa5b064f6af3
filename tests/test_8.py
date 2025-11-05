import pytest
from unittest.mock import patch, MagicMock
from definition_7b48ff5dbe534b7597656d06fe5bafdd import display_element_metadata

# Mock class for a layout element as described in the specification.
# It uses 'class' as an attribute name, which is a Python keyword.
# We use setattr to define this attribute in the constructor to avoid syntax errors
# when writing the class definition, but the attribute itself will be named 'class'.
class MockElement:
    def __init__(self, text_content, confidence, element_class_name, bbox=None):
        self.text_content = text_content
        self.confidence = confidence
        # Use setattr to dynamically set the attribute named 'class'
        setattr(self, 'class', element_class_name)
        self.bbox = bbox if bbox is not None else (0, 0, 100, 100)

# This fixture mocks the `IPython.display.display`, `IPython.display.clear_output`,
# and `IPython.display.Markdown` functions/classes, along with the `metadata_output`
# ipywidget instance which the `display_element_metadata` function interacts with.
@pytest.fixture
def mock_ipython_environment():
    # Patching functions and classes that are typically imported from IPython.display
    with patch('IPython.display.display') as mock_display, \
         patch('IPython.display.clear_output') as mock_clear_output, \
         patch('IPython.display.Markdown') as mock_markdown_constructor:

        # Mock the `metadata_output` widget.
        # This widget is assumed to be an instance of ipywidgets.Output
        # and likely declared at the module level in definition_7b48ff5dbe534b7597656d06fe5bafdd.
        mock_metadata_output = MagicMock()
        # Ensure that `with metadata_output:` block works correctly for the mock context manager.
        mock_metadata_output.__enter__.return_value = None
        mock_metadata_output.__exit__.return_value = None

        # Temporarily replace the `metadata_output` in the target module (definition_7b48ff5dbe534b7597656d06fe5bafdd)
        # so that the function under test uses our mock.
        with patch('definition_7b48ff5dbe534b7597656d06fe5bafdd.metadata_output', new=mock_metadata_output):
            yield mock_display, mock_clear_output, mock_markdown_constructor


@pytest.mark.parametrize("element_args, expected_markdown_content", [
    # Test Case 1: Standard element with all expected attributes and content.
    ({"text_content": "This is a paragraph.", "confidence": 0.987, "element_class_name": "Text"},
     "**Class:** Text\n**Confidence:** 0.99\n**Text Content:** This is a paragraph."),
    
    # Test Case 2: Element with empty text_content, ensuring it's handled gracefully.
    ({"text_content": "", "confidence": 0.75, "element_class_name": "Figure"},
     "**Class:** Figure\n**Confidence:** 0.75\n**Text Content:** "),
    
    # Test Case 3: Element with very low confidence, testing the '.2f' formatting for zero.
    ({"text_content": "Uncertain header", "confidence": 0.001, "element_class_name": "Section-header"},
     "**Class:** Section-header\n**Confidence:** 0.00\n**Text Content:** Uncertain header"),
    
    # Test Case 4: Element with confidence value requiring specific rounding behavior (0.9999 rounds to 1.00).
    ({"text_content": "A list item", "confidence": 0.9999, "element_class_name": "List-item"},
     "**Class:** List-item\n**Confidence:** 1.00\n**Text Content:** A list item"),
])
def test_display_element_metadata_functional_cases(mock_ipython_environment, element_args, expected_markdown_content):
    """
    Tests various functional scenarios for display_element_metadata,
    including standard input, empty text, and confidence formatting.
    """
    mock_display, mock_clear_output, mock_markdown_constructor = mock_ipython_environment

    # Create a MockElement instance with the provided arguments.
    element = MockElement(**element_args)

    # Call the function under test.
    display_element_metadata(element)

    # Assert that clear_output was called exactly once to clear the output widget.
    mock_clear_output.assert_called_once()

    # Assert that the Markdown object was constructed with the expected formatted content.
    mock_markdown_constructor.assert_called_once_with(expected_markdown_content)

    # Assert that the display function was called exactly once with the created Markdown object.
    mock_display.assert_called_once_with(mock_markdown_constructor.return_value)


def test_display_element_metadata_missing_attribute_raises_error(mock_ipython_environment):
    """
    Tests the edge case where the input element is missing a required attribute (e.g., text_content),
    expecting an AttributeError and no display output.
    """
    mock_display, mock_clear_output, mock_markdown_constructor = mock_ipython_environment

    # Create a mock object that intentionally lacks the 'text_content' attribute.
    class MalformedElement:
        def __init__(self, confidence, element_class_name):
            self.confidence = confidence
            setattr(self, 'class', element_class_name) # Set 'class' attribute
            self.bbox = (0,0,10,10) # Bbox attribute is not used by this function but included for completeness.

    element_missing_text = MalformedElement(confidence=0.6, element_class_name="Page-header")

    # Expect an AttributeError when the function tries to access `element.text_content`
    # or any other missing required attribute.
    with pytest.raises(AttributeError):
        display_element_metadata(element_missing_text)

    # Ensure that no display or clear_output calls happened, as the error should occur early.
    mock_clear_output.assert_not_called()
    mock_markdown_constructor.assert_not_called()
    mock_display.assert_not_called()