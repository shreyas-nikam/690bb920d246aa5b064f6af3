import pytest
from unittest.mock import MagicMock

# definition_de0cf1df29634fee8a676c4f281809a1 block
from definition_de0cf1df29634fee8a676c4f281809a1 import on_image_click
# end definition_de0cf1df29634fee8a676c4f281809a1 block

class MockElement:
    """Mock for a Docling element object with essential attributes."""
    def __init__(self, bbox, class_name="Text", text_content="Sample text", confidence=0.9):
        self.bbox = bbox  # [x_min, y_min, x_max, y_max]
        self.class_ = class_name # Using class_ to avoid keyword conflict if directly used.
                                # The actual Docling object attribute is 'class'.
        self.text_content = text_content
        self.confidence = confidence

    # For patching purposes, if the actual implementation accesses element.class
    @property
    def class_(self):
        return self.__class_name

    @class_.setter
    def class_(self, value):
        self.__class_name = value


class MockMouseEvent:
    """Mock for matplotlib.backend_bases.MouseEvent."""
    def __init__(self, xdata, ydata):
        self.xdata = xdata
        self.ydata = ydata

@pytest.fixture
def mock_dependencies(mocker):
    """
    Fixture to mock module-level dependencies that `on_image_click` would interact with.
    This assumes `current_elements`, `metadata_output`, and `display_element_metadata`
    are defined in the same module as `on_image_click`.
    """
    # Mock the list of elements currently visible on the page
    mocker_elements = mocker.patch('definition_de0cf1df29634fee8a676c4f281809a1.current_elements', new=[])
    # Mock the output widget for metadata display
    mocker_output = mocker.patch('definition_de0cf1df29634fee8a676c4f281809a1.metadata_output', new=MagicMock())
    # Mock the function called to display element metadata
    mocker_display = mocker.patch('definition_de0cf1df29634fee8a676c4f281809a1.display_element_metadata', new=MagicMock())
    
    return {
        'current_elements': mocker_elements,
        'metadata_output': mocker_output,
        'display_element_metadata': mocker_display
    }

def test_on_image_click_within_bbox(mock_dependencies):
    """
    Test case: A click event occurs within the bounding box of a visible element.
    Expected: `metadata_output.clear_output()` is called, and `display_element_metadata()`
    is called with the correct element.
    """
    # Setup mock elements for the current page
    element1 = MockElement(bbox=[10, 10, 50, 50], class_name="Text", text_content="Hello World")
    element2 = MockElement(bbox=[100, 100, 150, 150], class_name="Title")
    mock_dependencies['current_elements'].extend([element1, element2])

    # Simulate a click event within element1's bounding box
    event = MockMouseEvent(xdata=30, ydata=30)
    
    on_image_click(event)
    
    # Assertions: Check if the expected functions were called with the correct arguments
    mock_dependencies['metadata_output'].clear_output.assert_called_once()
    mock_dependencies['display_element_metadata'].assert_called_once_with(element1)

def test_on_image_click_outside_any_bbox(mock_dependencies):
    """
    Test case: A click event occurs outside all defined bounding boxes on the page.
    Expected: No metadata display functions are called.
    """
    # Setup mock elements
    element1 = MockElement(bbox=[10, 10, 50, 50])
    mock_dependencies['current_elements'].append(element1)

    # Simulate a click event outside any bounding box
    event = MockMouseEvent(xdata=70, ydata=70) # Outside [10,10,50,50]
    
    on_image_click(event)
    
    # Assertions: Check that the functions were NOT called
    mock_dependencies['metadata_output'].clear_output.assert_not_called()
    mock_dependencies['display_element_metadata'].assert_not_called()

def test_on_image_click_no_elements_on_page(mock_dependencies):
    """
    Test case: No elements are loaded on the current page (`current_elements` is empty).
    Expected: No metadata display functions are called, regardless of click coordinates.
    """
    # `current_elements` is empty by default from the fixture setup
    
    # Simulate a click event
    event = MockMouseEvent(xdata=30, ydata=30)
    
    on_image_click(event)
    
    # Assertions: Check that the functions were NOT called
    mock_dependencies['metadata_output'].clear_output.assert_not_called()
    mock_dependencies['display_element_metadata'].assert_not_called()

def test_on_image_click_none_coordinates(mock_dependencies):
    """
    Test case: The click event object has `None` for `xdata` or `ydata`
    (e.g., click outside the data area of the plot).
    Expected: No metadata display functions are called.
    """
    # Setup elements (their presence should not affect outcome for None coordinates)
    element1 = MockElement(bbox=[10, 10, 50, 50])
    mock_dependencies['current_elements'].append(element1)
    
    # Simulate a click event with None coordinates
    event = MockMouseEvent(xdata=None, ydata=None)
    
    on_image_click(event)
    
    # Assertions: Check that the functions were NOT called
    mock_dependencies['metadata_output'].clear_output.assert_not_called()
    mock_dependencies['display_element_metadata'].assert_not_called()

def test_on_image_click_on_bbox_edge(mock_dependencies):
    """
    Test case: A click event occurs exactly on the boundary (e.g., top-left corner)
    of a bounding box. This should be considered a "hit".
    Expected: `metadata_output.clear_output()` is called, and `display_element_metadata()`
    is called with the corresponding element.
    """
    element1 = MockElement(bbox=[10, 10, 50, 50], class_name="Figure")
    mock_dependencies['current_elements'].append(element1)

    # Simulate a click on the top-left corner edge
    event = MockMouseEvent(xdata=10, ydata=10) 
    
    on_image_click(event)
    
    # Assertions
    mock_dependencies['metadata_output'].clear_output.assert_called_once()
    mock_dependencies['display_element_metadata'].assert_called_once_with(element1)