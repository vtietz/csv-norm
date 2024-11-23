import os
import pytest
from replace_texts import clean_text_for_excel, reconstruct_csv
from io import StringIO
from unittest.mock import mock_open, patch

def create_test_files(numbered_csv_content, mapping_content):
    """Helper function to create test files"""
    with open('test_numbered.csv', 'w', encoding='utf-8') as f:
        f.write(numbered_csv_content)
    with open('test_mapping.txt', 'w', encoding='utf-8') as f:
        f.write(mapping_content)

def read_output_csv():
    """Helper function to read output CSV"""
    with open('test_output.csv', 'r', encoding='utf-8') as f:
        return f.read().strip()

def cleanup_test_files():
    """Helper function to clean up test files"""
    files = ['test_numbered.csv', 'test_mapping.txt', 'test_output.csv']
    for file in files:
        if os.path.exists(file):
            os.remove(file)

@pytest.fixture(autouse=True)
def run_around_tests():
    yield
    cleanup_test_files()

def test_basic_replacement():
    numbered_csv = '"[1]";"[2]"\n"[3]";"[4]"'
    mapping = '[1] Hello\n[2] World\n[3] How\n[4] Are you'
    
    create_test_files(numbered_csv, mapping)
    reconstruct_csv('test_numbered.csv', 'test_mapping.txt', 'test_output.csv')
    
    expected = '"Hello";"World"\n"How";"Are you"'
    assert read_output_csv() == expected

def test_multiple_numbers_in_cell():
    numbered_csv = '"[1];[2]";"[3]"'
    mapping = '[1] First\n[2] Second\n[3] Third'
    
    create_test_files(numbered_csv, mapping)
    reconstruct_csv('test_numbered.csv', 'test_mapping.txt', 'test_output.csv')
    
    expected = '"First;Second";"Third"'
    assert read_output_csv() == expected

def test_excel_formula_protection():
    numbered_csv = '"[1]";"[2]"'
    mapping = '[1] =SUM(A1)\n[2] Normal text'
    
    create_test_files(numbered_csv, mapping)
    reconstruct_csv('test_numbered.csv', 'test_mapping.txt', 'test_output.csv')
    
    expected = '"\'=SUM(A1)";"Normal text"'
    assert read_output_csv() == expected

def test_multiline_text():
    numbered_csv = '"[1]";"[2]"'
    mapping = '[1] Line 1\nLine 2\n[2] Simple text'
    
    written_content = []
    def mock_open_wrapper(filename, mode='r', encoding=None, newline=None):
        if filename == 'test_output.csv':
            buffer = StringIO()
            buffer.close = lambda: None  # Prevent buffer from being closed
            def mock_write(content):
                written_content.append(content)
                return len(content)
            buffer.write = mock_write
            return buffer
        return StringIO(mock_files[filename].getvalue())
    
    # Create mock file objects
    mock_files = {
        'test_numbered.csv': StringIO(numbered_csv),
        'test_mapping.txt': StringIO(mapping)
    }
    
    # Use patch to mock the file operations
    with patch('builtins.open', create=True) as mock_file:
        mock_file.side_effect = mock_open_wrapper
        reconstruct_csv('test_numbered.csv', 'test_mapping.txt', 'test_output.csv')
    
    expected = '"Line 1\rLine 2";"Simple text"'
    actual = ''.join(written_content).strip()
    assert actual == expected

def test_missing_translation():
    numbered_csv = '"[1]";"[2]"'
    mapping = '[1] Present'
    
    create_test_files(numbered_csv, mapping)
    reconstruct_csv('test_numbered.csv', 'test_mapping.txt', 'test_output.csv')
    
    expected = '"Present";"[2]"'
    assert read_output_csv() == expected

def test_clean_text_for_excel():
    assert clean_text_for_excel('=formula') == "'=formula"
    assert clean_text_for_excel('normal text') == "normal text"
    # Note: explicitly testing the line ending conversion
    assert clean_text_for_excel('line1\nline2') == "line1\rline2"
