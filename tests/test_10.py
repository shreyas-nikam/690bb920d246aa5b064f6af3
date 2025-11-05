import pytest
import sys
from io import StringIO

# definition_fe9d008da377450c9ffdf6df912bcd53 block
from definition_fe9d008da377450c9ffdf6df912bcd53 import print_sample_element_metadata
# END definition_fe9d008da377450c9ffdf6df912bcd53 block

# Define a mock Docling layout element object to simulate the real object
class MockDoclingElement:
    """
    A mock class to simulate Docling layout elements for testing purposes.
    It includes attributes like class, bbox, text_content, confidence, and optional metadata/font_info.
    """
    def __init__(self, element_class_value, bbox, text_content, confidence, metadata=None, font_info=None):
        # Using 'class_' to avoid Python keyword 'class' in the mock's attribute name.
        # The actual 'print_sample_element_metadata' implementation would likely
        # access element.class (e.g., via getattr or a property) as per the docstring.
        self.class_ = element_class_value
        self.bbox = bbox
        self.text_content = text_content
        self.confidence = confidence
        
        # Add optional attributes only if provided
        if metadata is not None:
            self.metadata = metadata
        if font_info is not None:
            self.font_info = font_info

# Helper function to generate the expected printed output string for a mock element
def _generate_expected_output_string(element_dict):
    """
    Constructs the expected stdout string based on the provided element data,
    mimicking how 'print_sample_element_metadata' is expected to format output.
    """
    # Create a temporary MockDoclingElement instance to help format the string
    element = MockDoclingElement(**element_dict)
    
    output = f"Class: {element.class_}\n"
    output += f"Bounding Box: {element.bbox}\n"
    output += f"Text Content: {element.text_content}\n"
    output += f"Confidence: {element.confidence:.2f}\n" # Format confidence to 2 decimal places

    if hasattr(element, 'metadata'):
        output += f"Metadata: {element.metadata}\n"
    if hasattr(element, 'font_info'):
        output += f"Font Info: {element.font_info}\n"
    return output

# Define test cases for print_sample_element_metadata.
# Each tuple in 'test_cases_raw' contains:
# 1. 'input_element_data_dict_or_raw_value': A dictionary (for valid elements) to construct MockDoclingElement,
#    or a raw value (e.g., None) for invalid inputs.
# 2. 'expected_result': Either the expected stdout string (placeholder None initially) or an exception type.
test_cases_raw = [
    # Test Case 1: Standard element with all expected attributes (class, bbox, text, confidence, metadata, font_info)
    (
        {"element_class_value": "Text", "bbox": [10, 20, 100, 50], "text_content": "Sample text content.",
         "confidence": 0.9543, "metadata": {'id': 'text_1'}, "font_info": {'name': 'Arial', 'size': 12}},
        None # Placeholder for expected output string, will be generated
    ),
    # Test Case 2: Element with only essential attributes (class, bbox, text, confidence)
    # Checks that optional attributes (metadata, font_info) are not printed if missing.
    (
        {"element_class_value": "Title", "bbox": [50, 60, 200, 80], "text_content": "Document Title", "confidence": 0.998},
        None # Placeholder
    ),
    # Test Case 3: Element with empty text_content and exactly zero confidence.
    # Covers edge cases for text content (empty string) and confidence (exact zero).
    (
        {"element_class_value": "Footnote", "bbox": [500, 700, 600, 720], "text_content": "", "confidence": 0.00},
        None # Placeholder
    ),
    # Test Case 4: Element with float coordinates for bbox and confidence value requiring rounding.
    # Ensures float values are handled correctly, especially confidence formatting.
    (
        {"element_class_value": "Formula", "bbox": [150.5, 300.2, 250.8, 350.1], "text_content": "E=mc^2", "confidence": 0.8765},
        None # Placeholder
    ),
    # Test Case 5: Invalid input - None.
    # If the function tries to access attributes (like .class_) on None, it should raise an AttributeError.
    (None, AttributeError),
]

# Final list of test cases for @pytest.mark.parametrize.
# This list converts dictionary inputs into MockDoclingElement instances
# and generates the expected output strings for output-based tests.
test_cases_formatted = []
for input_data, expected_result in test_cases_raw:
    if isinstance(input_data, dict):
        # Create a MockDoclingElement instance from the dictionary
        mock_element_instance = MockDoclingElement(**input_data)
        # Generate the expected output string using the dictionary data
        expected_output_str = _generate_expected_output_string(input_data)
        test_cases_formatted.append((mock_element_instance, expected_output_str))
    else:
        # For raw inputs like None, pass them as-is along with the expected exception type
        test_cases_formatted.append((input_data, expected_result))


@pytest.mark.parametrize("element_input, expected_output_or_exception", test_cases_formatted)
def test_print_sample_element_metadata(element_input, expected_output_or_exception, capfd):
    """
    Tests the 'print_sample_element_metadata' function for expected console output
    or specific exceptions based on the input element.
    """
    # Check if the test case expects an exception
    if isinstance(expected_output_or_exception, type) and issubclass(expected_output_or_exception, Exception):
        # Use pytest.raises to assert that the expected exception is raised
        with pytest.raises(expected_output_or_exception):
            print_sample_element_metadata(element_input)
    else:
        # Otherwise, expect specific stdout output
        print_sample_element_metadata(element_input)
        # Capture stdout and stderr
        captured = capfd.readouterr()
        # Assert that the captured stdout matches the expected string
        assert captured.out == expected_output_or_exception
        # Assert that no errors were printed to stderr
        assert captured.err == ""