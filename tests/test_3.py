import pytest
from unittest.mock import Mock

# Keep the definition_954d5bd256cb48408bf0219cacd4669c block as it is. DO NOT REPLACE or REMOVE the block.
from definition_954d5bd256cb48408bf0219cacd4669c import process_pdf_with_docling

# --- Mock Docling components for testing ---

class MockDoclingResult:
    """A mock object to simulate the structured result from Docling."""
    def __init__(self, pages=1):
        self.pages = [Mock() for _ in range(pages)]
        self.metadata = {'version': '1.0'}

class DoclingProcessingError(Exception):
    """Custom exception to simulate Docling internal processing failures."""
    pass

# --- Setup mock DocumentConverter instances for different test scenarios ---

# Scenario 1: Successful conversion
mock_converter_success = Mock()
# This mock is configured to return a MockDoclingResult with 3 pages on successful conversion.
mock_converter_success.convert_single.return_value = MockDoclingResult(pages=3)

# Scenario 2: Converter raises ValueError for empty PDF bytes
mock_converter_empty_pdf_error = Mock()
mock_converter_empty_pdf_error.convert_single.side_effect = ValueError("PDF bytes cannot be empty")

# Scenario 3: Converter raises a Docling-specific error for malformed PDF content.
# The `process_pdf_with_docling` function is expected to wrap this into a generic ValueError.
mock_converter_malformed_pdf_error = Mock()
mock_converter_malformed_pdf_error.convert_single.side_effect = DoclingProcessingError("Failed to parse malformed PDF content")

# Scenario 4: Converter raises TypeError if pdf_bytes is not of type bytes.
mock_converter_type_error_bytes = Mock()
mock_converter_type_error_bytes.convert_single.side_effect = TypeError("pdf_bytes must be of type bytes")

@pytest.mark.parametrize(
    "converter, pdf_bytes, expected_result_or_exception_type",
    [
        # Test Case 1: Happy path - valid converter and PDF bytes.
        # Expects a MockDoclingResult object.
        (mock_converter_success, b"valid_pdf_content_placeholder", MockDoclingResult),

        # Test Case 2: Empty PDF bytes.
        # Expects a ValueError, assuming `process_pdf_with_docling` handles or re-raises it.
        (mock_converter_empty_pdf_error, b"", ValueError),

        # Test Case 3: Malformed/Invalid PDF content causing a Docling-specific error.
        # Expects a ValueError, assuming `process_pdf_with_docling` wraps DoclingProcessingError.
        (mock_converter_malformed_pdf_error, b"malformed_pdf_content_placeholder", ValueError),

        # Test Case 4: Invalid converter object (e.g., None).
        # Expects an AttributeError when attempting to call `None.convert_single()`.
        (None, b"any_pdf_content_placeholder", AttributeError),

        # Test Case 5: pdf_bytes is not of type bytes (e.g., str).
        # Expects a TypeError, assuming `process_pdf_with_docling` passes this to `converter.convert_single`
        # which then raises a TypeError.
        (mock_converter_type_error_bytes, "invalid_type_content", TypeError),
    ]
)
def test_process_pdf_with_docling(converter, pdf_bytes, expected_result_or_exception_type):
    try:
        result = process_pdf_with_docling(converter, pdf_bytes)
        # If execution reaches here, no exception was raised, so it must be a happy path.
        assert isinstance(result, expected_result_or_exception_type)

        # Additional assertions for the successful execution case (Test Case 1)
        if expected_result_or_exception_type == MockDoclingResult:
            assert len(result.pages) == 3  # Based on mock_converter_success configuration
            # Verify that the convert_single method was called with the correct arguments
            if converter is mock_converter_success:
                converter.convert_single.assert_called_with(pdf_bytes)

    except Exception as e:
        # If an exception was raised, assert that its type matches the expected exception type.
        assert isinstance(e, expected_result_or_exception_type)

        # For scenarios where converter is a mock and expected to be called before raising an error.
        # This verifies the mock was interacted with.
        if converter is not None and hasattr(converter, 'convert_single') and callable(converter.convert_single):
            # We don't assert_called_with for specific content if it's the `side_effect` that caused the immediate error
            # as the mock's call itself would be valid before its internal error logic.
            # Example: `converter.convert_single.assert_called_with(pdf_bytes)`
            pass # Skipping specific call check here as `side_effect` itself implies it was called.