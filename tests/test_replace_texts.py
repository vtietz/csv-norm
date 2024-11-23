import pytest
from replace_texts import clean_text_for_excel, reconstruct_csv
from io import StringIO
from unittest.mock import patch

def setup_mock_files(numbered_csv_content, mapping_content):
    """Helper function to setup mock file objects"""
    return {
        'test_numbered.csv': StringIO(numbered_csv_content),
        'test_mapping.txt': StringIO(mapping_content),
        'test_output.csv': StringIO()
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

@patch('builtins.open', create=True)
def test_basic_replacement(mock_file):
    numbered_csv = '"[1]";"[2]"\n"[3]";"[4]"'
    mapping = '[1] Hello\n[2] World\n[3] How\n[4] Are you'
    
    mock_files = setup_mock_files(numbered_csv, mapping)
    mock_file.side_effect = mock_open_wrapper(mock_files)
    
    reconstruct_csv('test_numbered.csv', 'test_mapping.txt', 'test_output.csv')
    
    expected = '"Hello";"World"\n"How";"Are you"'
    assert mock_files['test_output.csv'].getvalue().strip() == expected

@patch('builtins.open', create=True)
def test_multiple_numbers_in_cell(mock_file):
    numbered_csv = '"[1];[2]";"[3]"'
    mapping = '[1] First\n[2] Second\n[3] Third'
    
    mock_files = setup_mock_files(numbered_csv, mapping)
    mock_file.side_effect = mock_open_wrapper(mock_files)
    
    reconstruct_csv('test_numbered.csv', 'test_mapping.txt', 'test_output.csv')
    
    expected = '"First;Second";"Third"'
    assert mock_files['test_output.csv'].getvalue().strip() == expected

@patch('builtins.open', create=True)
def test_excel_formula_protection(mock_file):
    numbered_csv = '"[1]";"[2]"'
    mapping = '[1] =SUM(A1)\n[2] Normal text'
    
    mock_files = setup_mock_files(numbered_csv, mapping)
    mock_file.side_effect = mock_open_wrapper(mock_files)
    
    reconstruct_csv('test_numbered.csv', 'test_mapping.txt', 'test_output.csv')
    
    expected = '"\'=SUM(A1)";"Normal text"'
    assert mock_files['test_output.csv'].getvalue().strip() == expected

@patch('builtins.open', create=True)
def test_multiline_text(mock_file):
    numbered_csv = '"[1]";"[2]"'
    mapping = '[1] Line 1\nLine 2\n[2] Simple text'
    
    mock_files = setup_mock_files(numbered_csv, mapping)
    mock_file.side_effect = mock_open_wrapper(mock_files)
    
    reconstruct_csv('test_numbered.csv', 'test_mapping.txt', 'test_output.csv')
    
    expected = '"Line 1\rLine 2";"Simple text"'
    assert mock_files['test_output.csv'].getvalue().strip() == expected

@patch('builtins.open', create=True)
def test_missing_translation(mock_file):
    numbered_csv = '"[1]";"[2]"'
    mapping = '[1] Present'
    
    mock_files = setup_mock_files(numbered_csv, mapping)
    mock_file.side_effect = mock_open_wrapper(mock_files)
    
    reconstruct_csv('test_numbered.csv', 'test_mapping.txt', 'test_output.csv')
    
    expected = '"Present";"[2]"'
    assert mock_files['test_output.csv'].getvalue().strip() == expected

def test_clean_text_for_excel():
    assert clean_text_for_excel('=formula') == "'=formula"
    assert clean_text_for_excel('normal text') == "normal text"
    assert clean_text_for_excel('line1\nline2') == "line1\rline2"
