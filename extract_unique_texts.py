import csv
import sys
from typing import List, Dict, Tuple

def normalize_text(text: str) -> str:
    """Normalize text for comparison (case-insensitive, whitespace standardized)."""
    return ' '.join(text.strip().lower().split())

def create_text_mapping(csv_data: List[List[str]]) -> Dict[str, Tuple[int, str]]:
    """Create mapping of normalized text to (ID, original text)."""
    mapping = {}  # {normalized: (id, original)}
    current_id = 1

    for row in csv_data:
        for cell in row:
            # Split cell by semicolon, respecting whitespace
            parts = [p.strip() for p in cell.split(';') if p.strip()]
            
            for original_text in parts:
                normalized = normalize_text(original_text)
                if normalized not in mapping:
                    mapping[normalized] = (current_id, original_text)
                    current_id += 1
    
    return mapping

def process_csv_with_mapping(csv_data: List[List[str]], mapping: Dict[str, Tuple[int, str]]) -> List[List[str]]:
    """Replace texts with IDs in CSV data."""
    result = []
    
    for row in csv_data:
        new_row = []
        for cell in row:
            if not cell.strip():
                new_row.append('')
                continue
                
            # Process each part in the cell
            parts = [p.strip() for p in cell.split(';') if p.strip()]
            ids = []
            for part in parts:
                normalized = normalize_text(part)
                if normalized in mapping:
                    ids.append(f"[{mapping[normalized][0]}]")
            
            new_row.append(';'.join(ids))
        result.append(new_row)
    
    return result

def extract_unique_texts(input_csv: str, output_mapping_file: str, output_numbered_csv: str, encoding: str = 'utf-8') -> None:
    """Main function to process CSV and extract unique texts."""
    # Read input CSV
    try:
        with open(input_csv, 'r', encoding=encoding) as f:
            reader = csv.reader(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            csv_data = list(reader)
    except UnicodeDecodeError:
        with open(input_csv, 'r', encoding='latin-1') as f:
            reader = csv.reader(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            csv_data = list(reader)

    # Create mapping and process CSV
    mapping = create_text_mapping(csv_data)
    numbered_data = process_csv_with_mapping(csv_data, mapping)

    # Save mapping file
    with open(output_mapping_file, 'w', encoding='utf-8') as f:
        for _, (num, original) in sorted(mapping.items(), key=lambda x: x[1][0]):
            f.write(f"[{num}] {original}\n")

    # Save numbered CSV
    with open(output_numbered_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerows(numbered_data)

if __name__ == "__main__":
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print("Usage: python extract_unique_texts.py <input_csv> <output_mapping_file> <output_numbered_csv> [encoding]")
        sys.exit(1)

    extract_unique_texts(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        sys.argv[4] if len(sys.argv) == 5 else 'utf-8'
    )
