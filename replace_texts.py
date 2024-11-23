import csv
import os
import sys

def clean_text_for_excel(text):
    """Clean and format text to be Excel-safe and preserve line breaks."""
    if text.startswith('='):
        text = "'" + text  # Prefix with single quote to prevent formula interpretation
    # Replace regular line breaks with Excel-compatible line breaks
    return text.replace('\n', '\r')

def reconstruct_csv(numbered_csv, translated_mapping_file, output_csv):
    """
    Reconstruct a CSV file by replacing numbered placeholders with translated texts.

    Parameters:
    numbered_csv (str): Path to the input CSV file with numbered texts.
    translated_mapping_file (str): Path to the file with translated texts mapping.
    output_csv (str): Path to the output CSV file.
    """
    # Load translated mapping
    translated_texts = {}
    current_num = None
    current_text = []
    
    with open(translated_mapping_file, mode='r', encoding='utf-8') as mapping_file:
        for line in mapping_file:
            if line.strip().startswith('['):
                # If we were building a previous entry, save it
                if current_num and current_text:
                    translated_texts[current_num] = '\r'.join(current_text)  # Changed from '\n' to '\r'
                    current_text = []
                
                # Start new entry
                parts = line.strip().split(" ", 1)
                if len(parts) == 2:
                    current_num = parts[0].strip("[]")
                    current_text.append(parts[1].strip('"'))
            else:
                # Continue building current text
                if current_num:
                    current_text.append(line.strip())
        
        # Save the last entry
        if current_num and current_text:
            translated_texts[current_num] = '\r'.join(current_text)  # Changed from '\n' to '\r'

    # Replace numbers in the CSV with translated text
    reconstructed_data = []
    with open(numbered_csv, mode='r', encoding='utf-8') as infile:
        reader = csv.reader(infile, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
        for row in reader:
            translated_row = []
            for cell in row:
                # Handle cells with multiple numbers separated by semicolons
                if ';' in cell and '[' in cell:
                    parts = cell.strip('"').split(';')
                    translated_parts = [clean_text_for_excel(translated_texts.get(part.strip('[]'), part)) 
                                     for part in parts]
                    translated_cell = ';'.join(translated_parts)
                else:
                    cell_num = cell.strip('[]')
                    cell_content = translated_texts.get(cell_num, cell)
                    translated_cell = clean_text_for_excel(cell_content)
                translated_row.append(translated_cell)
            reconstructed_data.append(translated_row)

    # Manually write the reconstructed CSV to preserve line breaks
    with open(output_csv, mode='w', encoding='utf-8', newline='') as outfile:
        for row in reconstructed_data:
            escaped_row = []
            for field in row:
                # Escape any existing double quotes in the field
                escaped_field = '"' + field.replace('"', '""') + '"'
                escaped_row.append(escaped_field)
            line = ';'.join(escaped_row) + '\n'
            outfile.write(line)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python replace_texts.py <numbered_csv> <translated_mapping_file> <output_csv>")
        print("Example: python replace_texts.py survey_numbered.csv translations.txt survey_translated.csv")
        sys.exit(1)

    numbered_csv = sys.argv[1]
    translated_mapping_file = sys.argv[2]
    output_csv = sys.argv[3]

    reconstruct_csv(numbered_csv, translated_mapping_file, output_csv)
