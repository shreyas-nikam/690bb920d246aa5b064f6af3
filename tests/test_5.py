import pytest
from unittest.mock import MagicMock, patch
from PIL import Image as PIL_Image, ImageDraw

# Keep a placeholder definition_bc02cbd49e494e9988c74fdb4466e2e9 for the import of the module. Keep the `your_module` block as it is. DO NOT REPLACE or REMOVE the block.
# definition_bc02cbd49e494e9988c74fdb4466e2e9 Block Start
from definition_bc02cbd49e494e9988c74fdb4466e2e9 import draw_bounding_boxes
# definition_bc02cbd49e494e9988c74fdb4466e2e9 Block End

# Mock class for layout elements
class MockElement:
    def __init__(self, bbox, class_name):
        self.bbox = bbox
        # Dynamically set 'class' attribute for element.class access as per specification
        setattr(self, 'class', class_name)

# Define test cases using parametrize
# Parameters:
# - input_image: The mock PIL Image object or an invalid input type (e.g., string for TypeError).
# - elements: A list of MockElement objects.
# - visible_classes: A list of class names for which bounding boxes should be drawn.
# - class_colors: A dictionary mapping class names to hexadecimal color codes.
# - expected_rectangle_calls: A list of tuples (bbox, outline_color) that ImageDraw.rectangle should be called with.
#                           (Note: A default width of 2 is assumed in the actual function's implementation based on common practice)
# - expected_exception: The type of exception expected, or None if no exception.
test_cases = [
    # Test Case 1: Empty elements list - no bounding boxes should be drawn.
    (
        MagicMock(spec=PIL_Image.Image, name="mock_input_image_1"),
        [],
        ['Text'],
        {'Text': '#FF0000'},
        [], # No calls to rectangle expected
        None,
    ),
    # Test Case 2: Elements present, but 'visible_classes' list is empty - no bounding boxes drawn.
    (
        MagicMock(spec=PIL_Image.Image, name="mock_input_image_2"),
        [
            MockElement([10, 10, 20, 20], 'Text'),
            MockElement([30, 30, 40, 40], 'Title'),
        ],
        [], # Empty visible_classes
        {'Text': '#FF0000', 'Title': '#00FF00'},
        [], # No calls to rectangle expected
        None,
    ),
    # Test Case 3: Mixed elements, some classes visible, some not - only visible classes should be drawn.
    (
        MagicMock(spec=PIL_Image.Image, name="mock_input_image_3"),
        [
            MockElement([10, 10, 20, 20], 'Text'),
            MockElement([30, 30, 40, 40], 'Title'),
            MockElement([50, 50, 60, 60], 'Text'),
            MockElement([70, 70, 80, 80], 'Figure'),
        ],
        ['Text', 'Title'], # Only Text and Title are visible
        {'Text': '#FF0000', 'Title': '#00FF00', 'Figure': '#0000FF'},
        [ # Expected calls for Text and Title elements, with assumed default width=2
            ([10, 10, 20, 20], '#FF0000'),
            ([30, 30, 40, 40], '#00FF00'),
            ([50, 50, 60, 60], '#FF0000'),
        ],
        None,
    ),
    # Test Case 4: All elements' classes are in 'visible_classes' - all should be drawn.
    (
        MagicMock(spec=PIL_Image.Image, name="mock_input_image_4"),
        [
            MockElement([100, 100, 110, 110], 'Section-header'),
            MockElement([120, 120, 130, 130], 'List-item'),
        ],
        ['Section-header', 'List-item'],
        {'Section-header': '#AAAAAA', 'List-item': '#BBBBBB'},
        [ # Expected calls for all elements, with assumed default width=2
            ([100, 100, 110, 110], '#AAAAAA'),
            ([120, 120, 130, 130], '#BBBBBB'),
        ],
        None,
    ),
    # Test Case 5: Invalid 'image' type - should raise TypeError.
    (
        "this is not a PIL image object", # Invalid image input (string)
        [],
        [],
        {},
        [], # No calls expected as an early TypeError should prevent drawing
        TypeError,
    ),
]

@pytest.mark.parametrize(
    "input_image, elements, visible_classes, class_colors, expected_rectangle_calls, expected_exception",
    test_cases
)
@patch('PIL.ImageDraw.Draw') # Patch ImageDraw.Draw at the module level
def test_draw_bounding_boxes(
    mock_draw_class, # This will be the patched ImageDraw.Draw class
    input_image, elements, visible_classes, class_colors, expected_rectangle_calls, expected_exception
):
    # Mock the ImageDraw.Draw instance that will be returned by the patched class
    mock_draw_object = MagicMock(spec=ImageDraw.Draw, name="mock_draw_object")
    mock_draw_class.return_value = mock_draw_object

    # Create a mock image that `input_image.copy()` would return, which Draw will then use
    mock_drawn_image = MagicMock(spec=PIL_Image.Image, name="mock_drawn_image")

    # If the input_image is a mock PIL Image, set up its 'copy' method to return our mock_drawn_image
    if isinstance(input_image, MagicMock):
        input_image.copy.return_value = mock_drawn_image

    if expected_exception:
        with pytest.raises(expected_exception):
            draw_bounding_boxes(input_image, elements, visible_classes, class_colors)
        
        # If a TypeError for the image occurs, neither copy() nor ImageDraw.Draw() should have been called
        if expected_exception == TypeError:
            # Check if input_image was a mock before asserting its copy method
            if isinstance(input_image, MagicMock): 
                input_image.copy.assert_not_called()
            mock_draw_class.assert_not_called()
    else:
        # Call the function under test
        result_image = draw_bounding_boxes(input_image, elements, visible_classes, class_colors)

        # Assert that a copy of the original image was made
        input_image.copy.assert_called_once()
        
        # Assert that ImageDraw.Draw was called exactly once with the copied image
        mock_draw_class.assert_called_once_with(mock_drawn_image)

        # Assert that the returned object is the one that was drawn on
        assert result_image is mock_drawn_image

        # Assert that ImageDraw.rectangle was called the correct number of times
        assert mock_draw_object.rectangle.call_count == len(expected_rectangle_calls)
        
        # Collect actual calls to rectangle for comparison
        actual_calls = []
        for call_args in mock_draw_object.rectangle.call_args_list:
            # bbox is the first positional argument (args[0]), outline is a keyword argument ('outline'),
            # and we assume a default width of 2 based on common implementation.
            bbox = call_args.args[0]
            outline_color = call_args.kwargs.get('outline')
            width = call_args.kwargs.get('width', 0) # Get width, default to 0 if not present
            actual_calls.append((bbox, outline_color, width))
        
        # Prepare expected calls for comparison, including the assumed default width
        expected_calls_with_width = [(bbox, color, 2) for bbox, color in expected_rectangle_calls]

        # Sort calls to compare them irrespective of order
        actual_calls.sort()
        expected_calls_with_width.sort()

        assert actual_calls == expected_calls_with_width

