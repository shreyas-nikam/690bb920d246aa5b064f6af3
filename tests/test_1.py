import pytest
# definition_d934cbc2724948218aff22c14ccee459 block starts
from definition_d934cbc2724948218aff22c14ccee459 import load_pdf_document
# definition_d934cbc2724948218aff22c14ccee459 block ends

# Mock PDF content for testing
VALID_PDF_BYTES = b'%PDF-1.4\nSample PDF content.\n%EOF'
NON_PDF_BYTES = b'This is some random text, definitely not a PDF document.'

@pytest.mark.parametrize(
    "source_type, source_value, expected_output, expected_exception, mock_setup_callback",
    [
        # Test Case 1: Successful upload of valid PDF bytes
        ('upload', VALID_PDF_BYTES, VALID_PDF_BYTES, None, None),

        # Test Case 2: Successful download from a valid PDF URL
        # Mocks requests.get to return a mock response with PDF content and a successful status.
        ('url', 'http://example.com/document.pdf', VALID_PDF_BYTES, None,
         lambda m: m.patch('requests.get', return_value=m.Mock(content=VALID_PDF_BYTES, raise_for_status=lambda: None, status_code=200))),

        # Test Case 3: Invalid source_type should raise a ValueError
        ('unsupported_type', 'some_value', None, ValueError, None),

        # Test Case 4: Uploading non-PDF content (missing PDF magic bytes) should raise a ValueError
        ('upload', NON_PDF_BYTES, None, ValueError, None),

        # Test Case 5: URL download fails due to a network error
        # Mocks requests.get to raise a generic Exception (subclass of RequestException)
        # We use a generic Exception because `requests` cannot be explicitly imported in this file.
        ('url', 'http://example.com/error.pdf', None, Exception,
         lambda m: m.patch('requests.get', side_effect=Exception("Simulated network error"))),
    ]
)
def test_load_pdf_document(source_type, source_value, expected_output, expected_exception, mock_setup_callback, mocker):
    """
    Tests the load_pdf_document function for various scenarios including successful loads,
    invalid inputs, and error conditions.
    """
    if mock_setup_callback:
        # Apply the mocking setup if provided for the test case
        mock_setup_callback(mocker)

    if expected_exception:
        # Assert that the expected exception is raised
        with pytest.raises(expected_exception):
            load_pdf_document(source_type, source_value)
    else:
        # Assert that the function returns the expected output
        result = load_pdf_document(source_type, source_value)
        assert result == expected_output