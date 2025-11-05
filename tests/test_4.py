import pytest
from unittest.mock import Mock, MagicMock
from definition_cacb56311ee74b03896fc86005190b25 import extract_page_images_and_elements
from PIL import Image as PIL_Image # Required for type checking mock images

# Helper function to create mock element objects with required attributes
def create_mock_element(bbox, class_name, text_content, confidence):
    element = Mock()
    element.bbox = bbox
    # Dynamically set 'class' attribute, as it's a keyword but valid as an attribute name on a Mock
    setattr(element, 'class', class_name) 
    element.text_content = text_content
    element.confidence = confidence
    return element

# Helper function to create mock page objects
def create_mock_page(elements_data, render_fail=False):
    page = Mock()
    if render_fail:
        # Simulate a rendering failure
        page.render.side_effect = RuntimeError("Simulated page render failure")
    else:
        # Return a mock PIL Image object
        mock_pil_image = MagicMock(spec=PIL_Image.Image)
        mock_pil_image.size = (100, 100) # Example attribute for a PIL Image
        page.render.return_value = mock_pil_image
    
    # Populate element_groups with mock elements
    page.element_groups = [create_mock_element(*e) for e in elements_data]
    return page

# Helper function to create a mock docling_result object
# pages_config is a list of (elements_data_for_page, render_fail_flag) tuples
def create_mock_docling_result(pages_config):
    docling_result = Mock()
    docling_result.pages = []
    for page_elements_data, render_fail in pages_config:
        docling_result.pages.append(create_mock_page(page_elements_data, render_fail))
    return docling_result

# Parametrized test cases covering different scenarios
@pytest.mark.parametrize("input_data, expected", [
    # Test Case 1: Standard result with multiple pages and multiple elements
    (
        # docling_result_input config: Two pages, each with elements
        [
            ([((0,0,10,10), "Text", "Hello", 0.9), ((10,10,20,20), "Title", "World", 0.95)], False), # Page 1 elements
            ([((30,30,40,40), "Figure", "", 0.8), ((50,50,60,60), "Caption", "A caption", 0.75)], False) # Page 2 elements
        ],
        # Expected output structure: 2 pages, with 2 and 2 elements respectively
        {"num_pages": 2, "elements_per_page": [2, 2]}
    ),
    # Test Case 2: Docling result object with no pages
    (
        # docling_result_input config: Empty list of pages
        [],
        # Expected output structure: 0 pages, empty elements list
        {"num_pages": 0, "elements_per_page": []}
    ),
    # Test Case 3: Docling result with pages, but each page has no elements
    (
        # docling_result_input config: Two pages, but no elements on either
        [
            ([], False), # Page 1 with no elements
            ([], False)  # Page 2 with no elements
        ],
        # Expected output structure: 2 pages, with 0 and 0 elements respectively
        {"num_pages": 2, "elements_per_page": [0, 0]}
    ),
    # Test Case 4: Invalid docling_result object (e.g., None)
    (
        None, # Directly pass None as the input 'docling_result'
        AttributeError # Expect an AttributeError as None has no 'pages' attribute
    ),
    # Test Case 5: A page's render method fails (edge case for internal page processing)
    (
        # docling_result_input config: First page's render method is configured to fail
        [
            ([((0,0,10,10), "Text", "Error page content", 0.9)], True), # Page 1 rendering fails
            ([((30,30,40,40), "Figure", "Valid page content", 0.8)], False) # This page should ideally not be processed if first fails
        ],
        RuntimeError # Expect RuntimeError propagated from the mock page.render()
    ),
])
def test_extract_page_images_and_elements(input_data, expected):
    # Prepare the mock docling_result object based on input_data
    if input_data is None:
        docling_result_mock = None
    elif isinstance(input_data, list):
        docling_result_mock = create_mock_docling_result(input_data)
    else:
        # Fallback for unexpected input_data types, though current parametrize covers list and None
        docling_result_mock = input_data 

    # Check if an exception is expected or a successful return
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            extract_page_images_and_elements(docling_result_mock)
    else:
        # Execute the function and assert the structure and types of the output
        result = extract_page_images_and_elements(docling_result_mock)
        assert isinstance(result, list)
        assert len(result) == expected["num_pages"]

        for i, (image, elements) in enumerate(result):
            assert isinstance(image, PIL_Image.Image)
            assert isinstance(elements, list)
            assert len(elements) == expected["elements_per_page"][i]
            
            # For each element, check if it has the expected attributes as described in the spec
            for element in elements:
                assert hasattr(element, 'bbox')
                assert hasattr(element, 'class') # 'class' attribute on mock
                assert hasattr(element, 'text_content')
                assert hasattr(element, 'confidence')