# CSV Text Normalization

A tool for efficient text normalization of CSV files. This utility helps manage text content in CSV files by extracting unique text entries, enabling batch processing, and reconstructing the CSV with processed content. E. g. it can be used for translation of survey data.

## Key Features

- Extracts unique text entries from CSV files
- Handles multiple text entries in single cells (semicolon-separated)
- Maintains text relationships by assigning unique identifiers
- Case-insensitive text matching to avoid duplicates
- Supports different file encodings
- Preserves CSV structure during processing

## Use Cases

### Translation Workflow
Perfect for translating CSV files while maintaining consistency:
1. Extract unique texts for translation
2. Use external translation tool (e.g., ChatGPT, Google Translate) to translate unique entries
3. Save translations to a mapping file
4. Reconstruct the CSV with translated content

Note: This tool does not perform translations itself. You'll need to use an external translation service or AI tool for the actual translation work.

### Text Standardization
Useful for standardizing text across large datasets:
- Replace variations of the same text with a standard version
- Maintain consistency across the entire dataset
- Reduce redundancy in text content

## Usage

### 1. Extract Unique Texts
Processes the original CSV and creates:
- A mapping file with unique texts and their IDs
- A numbered version of the CSV file

```bash
python extract_unique_texts.py <input_csv> <output_mapping_file> <output_numbered_csv> [encoding]

# Example:
python extract_unique_texts.py survey_original.csv mappings.txt survey_numbered.csv
```

### 2. Replace Texts
Reconstructs the CSV using translated or modified texts:

```bash
python replace_texts.py <numbered_csv> <translated_mapping_file> <output_csv>

# Example:
python replace_texts.py survey_numbered.csv translations.txt survey_translated.csv
```
## Use Cases

### Translation Workflow
Perfect for translating CSV files while maintaining consistency:
1. Extract unique texts for translation
2. Use external translation tool (e.g., ChatGPT, Google Translate) to translate unique entries
3. Save translations to a mapping file
4. Reconstruct the CSV with translated content

Note: This tool does not perform translations itself. You'll need to use an external translation service or AI tool for the actual translation work.

## Translation Process Example

1. First, extract unique texts:
```bash
python extract_unique_texts.py survey_original.csv mappings.txt survey_numbered.csv
```

2. Use the content of mappings.txt to create a translation prompt. For example, with ChatGPT:

```
Please translate to English while preserving numbers:

[1] Wie alt sind Sie?
[2] Was ist Ihr Geschlecht?
[3] männlich
[4] weiblich
[5] keine Angabe
```

3. Copy ChatGPT's response into translations.txt:
```
[1] How old are you?
[2] What is your gender?
[3] male
[4] female
[5] prefer not to say
```

4. Use the translations to create the final CSV:
```bash
python replace_texts.py survey_numbered.csv translations.txt survey_translated.csv
```

## File Format Examples

### Original CSV (survey_original.csv):
```csv
"Question 1";"Answer A";"Answer B"
"Question 2";"Answer A";"Answer C"
```

### Mapping File (mappings.txt):
```
[1] Question 1
[2] Question 2
[3] Answer A
[4] Answer B
[5] Answer C
```

### Numbered CSV (survey_numbered.csv):
```csv
"[1]";"[3]";"[4]"
"[2]";"[3]";"[5]"
```

### Translated Mapping (translations.txt):
```
[1] Frage 1
[2] Frage 2
[3] Antwort A
[4] Antwort B
[5] Antwort C
```

## Notes
- Use UTF-8 encoding by default
- Text matching is case-insensitive
- Semicolon-separated entries in cells are processed individually
- Quotes are handled automatically