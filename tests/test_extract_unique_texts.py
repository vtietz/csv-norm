import pytest
from io import StringIO
from unittest.mock import patch
from extract_unique_texts import (
    normalize_text,
    create_text_mapping,
    process_csv_with_mapping,
    extract_unique_texts
)

def setup_mock_files(input_csv_content):
    """Helper function to setup mock file objects"""
    return {
        'test_input.csv': StringIO(input_csv_content),
        'test_mapping.txt': StringIO(),
        'test_numbered.csv': StringIO()
    }

def mock_open_wrapper(mock_files):
    """Creates a mock open function with the given mock files"""
    def _mock_open(filename, mode='r', encoding=None, newline=None):
        if filename in mock_files:
            buffer = mock_files[filename]
            buffer.close = lambda: None  # Prevent buffer from being closed
            return buffer
        raise FileNotFoundError(f"Mock file '{filename}' not found")
    return _mock_open

def test_normalize_text():
    assert normalize_text("Hello World") == "hello world"
    assert normalize_text("  HELLO   world  ") == "hello world"
    assert normalize_text("hello  WORLD") == "hello world"
    assert normalize_text("") == ""

def test_create_text_mapping():
    data = [["Hello;World", "Test"], ["HELLO", "world"]]
    mapping = create_text_mapping(data)
    
    assert len(mapping) == 3  # "hello", "world", "test"
    assert mapping["hello"][0] == 1
    assert mapping["world"][0] == 2
    assert mapping["test"][0] == 3
    assert mapping["hello"][1] in ["Hello", "HELLO"]

@patch('builtins.open', create=True)
def test_basic_extraction(mock_file):
    input_csv = 'Hello;"World;Test"\nHELLO;world'
    expected_mapping = "[1] Hello\n[2] World\n[3] Test"
    expected_numbered = '"[1]";"[2];[3]"\n"[1]";"[2]"'
    
    mock_files = setup_mock_files(input_csv)
    mock_file.side_effect = mock_open_wrapper(mock_files)
    
    extract_unique_texts('test_input.csv', 'test_mapping.txt', 'test_numbered.csv')
    
    assert mock_files['test_mapping.txt'].getvalue().strip() == expected_mapping
    assert mock_files['test_numbered.csv'].getvalue().strip().replace('\r\n', '\n') == expected_numbered

@patch('builtins.open', create=True)
def test_empty_cells(mock_file):
    input_csv = 'Hello;\nWorld;""'
    expected_mapping = "[1] Hello\n[2] World"
    expected_numbered = '"[1]";""\n"[2]";""'
    
    mock_files = setup_mock_files(input_csv)
    mock_file.side_effect = mock_open_wrapper(mock_files)
    
    extract_unique_texts('test_input.csv', 'test_mapping.txt', 'test_numbered.csv')
    
    assert mock_files['test_mapping.txt'].getvalue().strip() == expected_mapping
    assert mock_files['test_numbered.csv'].getvalue().strip().replace('\r\n', '\n') == expected_numbered

@patch('builtins.open', create=True)
def test_error_handling(mock_file):
    mock_file.side_effect = FileNotFoundError()
    with pytest.raises(FileNotFoundError):
        extract_unique_texts("nonexistent.csv", "out1.txt", "out2.csv")

if __name__ == "__main__":
    pytest.main([__file__])
