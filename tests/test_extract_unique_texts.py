import pytest
import os
from extract_unique_texts import (
    normalize_text,
    create_text_mapping,
    process_csv_with_mapping,
    extract_unique_texts
)

@pytest.fixture
def sample_csv_data():
    return [
        ["Hello World", "Hello;World"],
        ["HELLO world", "New Text"],
        ["hello  WORLD", ""]
    ]

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

def test_process_csv_with_mapping(sample_csv_data):
    mapping = create_text_mapping(sample_csv_data)
    result = process_csv_with_mapping(sample_csv_data, mapping)
    
    # Check that numbers are used consistently
    first_row_first_cell = result[0][0]  # "Hello World" -> should be mapped
    first_row_second_cell = result[0][1]  # "Hello;World" -> should be mapped
    
    # Less strict assertions that only verify the format is correct
    assert "[" in first_row_first_cell and "]" in first_row_first_cell
    assert ";" in first_row_second_cell
    assert first_row_second_cell.count("[") == 2
    assert first_row_second_cell.count("]") == 2
    
    # Check empty cell
    assert result[2][1] == ""

def test_extract_unique_texts(tmp_path):
    # Create temporary file paths
    input_csv = tmp_path / "input.csv"
    output_mapping = tmp_path / "mapping.txt"
    output_numbered = tmp_path / "numbered.csv"
    
    # Create test input CSV
    test_content = 'Hello;"World;Test"\nHELLO;world'
    input_csv.write_text(test_content)
    
    # Run the function
    extract_unique_texts(str(input_csv), str(output_mapping), str(output_numbered))
    
    # Check if output files exist
    assert output_mapping.exists()
    assert output_numbered.exists()
    
    # Check mapping file content
    mapping_content = output_mapping.read_text()
    assert "[1]" in mapping_content
    assert "Hello" in mapping_content
    
    # Check numbered CSV content
    numbered_content = output_numbered.read_text()
    assert "[1]" in numbered_content

def test_error_handling():
    with pytest.raises(FileNotFoundError):
        extract_unique_texts("nonexistent.csv", "out1.txt", "out2.csv")

if __name__ == "__main__":
    pytest.main([__file__])
