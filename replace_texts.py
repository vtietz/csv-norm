import csv
import os
import sys

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
    with open(translated_mapping_file, mode='r', encoding='utf-8') as mapping_file:
        for line in mapping_file:
            parts = line.strip().split(" ", 1)
            if len(parts) == 2:
                num, text = parts
                translated_texts[num.strip("[]")] = text.strip("\"")
            else:
                print(f"Skipping invalid line in mapping file: {line}")

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
                    translated_parts = [translated_texts.get(part.strip('[]'), part) for part in parts]
                    translated_cell = ';'.join(translated_parts)
                else:
                    translated_cell = translated_texts.get(cell.strip('[]'), cell)
                translated_row.append(translated_cell)
            reconstructed_data.append(translated_row)

    # Save reconstructed CSV
    with open(output_csv, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerows(reconstructed_data)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python replace_texts.py <numbered_csv> <translated_mapping_file> <output_csv>")
        print("Example: python replace_texts.py survey_numbered.csv translations.txt survey_translated.csv")
        sys.exit(1)

    numbered_csv = sys.argv[1]
    translated_mapping_file = sys.argv[2]
    output_csv = sys.argv[3]

    reconstruct_csv(numbered_csv, translated_mapping_file, output_csv)
