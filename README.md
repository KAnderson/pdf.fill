# PDF Form Tools

A collection of Python utilities for working with PDF forms - detect, inspect, list, and fill PDF form fields programmatically.

## 🚀 Quick Start - Web UI

**NEW! Easy-to-use web interface - no command line required!**

```bash
source venv/bin/activate
python app.py
```

Then open **http://localhost:5000** in your browser.

Drag & drop your PDF, explore fields, and fill forms with a beautiful UI!

📖 **[Web UI Guide →](WEB_UI_GUIDE.md)**

---

## 📚 Documentation

- **[🌐 WEB UI GUIDE →](WEB_UI_GUIDE.md)** - **NEW!** Beautiful web interface for all tools
- **[QUICK START →](QUICK_START.md)** - Step-by-step guide to finding and filling fields
- **[REMOVE VOID WATERMARK →](REMOVE_VOID_WATERMARK.md)** - How to permanently remove the "VOID" watermark
- **[FIELD MAPPING →](FIELD_MAPPING.md)** - Complete field reference for iA Financial Group form
- **[BEFORE & AFTER →](BEFORE_AND_AFTER.md)** - See the field mapping fix explained
- **[SOLUTION →](SOLUTION.md)** - Understanding the encryption issue
- **[COMPLETE SOLUTION →](COMPLETE_SOLUTION.md)** - Everything in one place

## Features

- **Detect form types** - Identify XFA vs AcroForm fields
- **Deep inspection** - Comprehensive analysis of PDF structure
- **List all fields** - Export complete field inventory
- **Fill forms programmatically** - Batch fill PDF forms from JSON data
- **Works with encrypted PDFs** - Handles protected insurance forms
- **Find fields by label** - Search for fields by their visible name
- **Generate templates** - Create commented JSON templates with field descriptions

## Installation

### Option 1: Using virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Option 2: System-wide install

```bash
pip install -r requirements.txt
```

## Usage

### 1. Detect Form Type

Quickly check if a PDF has form fields:

```bash
python pdf_form_detector.py your_file.pdf
```

### 2. Deep Inspection

Comprehensive analysis showing catalog structure, annotations, and field details:

```bash
python inspect_pdf.py your_file.pdf
```

### 3. List All Fields

Export all field names, types, and current values:

```bash
python list_fields.py your_file.pdf
```

Save to a file:

```bash
python list_fields.py your_file.pdf > fields.txt
```

### 4. Find Fields by Label

Search for fields by their visible label (most useful tool!):

```bash
python find_field_by_label.py your_file.pdf "last name"
python find_field_by_label.py your_file.pdf "address"
python find_field_by_label.py your_file.pdf "phone"
```

### 5. Generate Template

Create a JSON template with field descriptions:

```bash
# Template for Section A only
python generate_template.py your_file.pdf A section_a.json

# Template for multiple sections
python generate_template.py your_file.pdf A,B,C template.json

# Template for entire form
python generate_template.py your_file.pdf all_fields.json
```

### 6. Fill PDF Forms

Fill form fields from JSON data:

```bash
# Using JSON string
python fill_pdf.py input.pdf output.pdf '{"A05t": "Doe", "A06t": "John"}'

# Using JSON file
python fill_pdf.py input.pdf output.pdf data.json
```

## Example: Filling Your Insurance Form

```bash
# 1. List all fields to see what's available
python list_fields.py "ia financial group dev004391.pdf" | head -50

# 2. Create a JSON file with your data
cat > my_data.json << EOF
{
  "A04t": "John Doe",
  "A06t": "123 Main Street",
  "A07t": "Apt 4B",
  "A08t": "New York",
  "A12t": "john.doe@example.com"
}
EOF

# 3. Fill the PDF
python fill_pdf.py "ia financial group dev004391.pdf" "filled_form.pdf" my_data.json
```

## Example Output

**pdf_form_detector.py:**
```
Analyzing PDF: sample_form.pdf

Form Type: AcroForm
Has AcroForm: True
Has XFA: False
Field count: 15
```

**fill_pdf.py:**
```
Opening: input.pdf
Found 1732 form fields
Attempting to fill 5 fields...

✓ Filled: A04t = John Doe
✓ Filled: A06t = 123 Main Street
✓ Filled: A07t = Apt 4B
✓ Filled: A08t = New York
✓ Filled: A12t = john.doe@example.com

Summary:
  Fields filled: 5/5

Saving to: filled_form.pdf
✓ Done!
```

## Understanding Form Types

### AcroForm
- Traditional PDF form technology
- Static form fields (text boxes, checkboxes, radio buttons, etc.)
- Widely supported by PDF readers
- Fields are defined in the PDF structure

### XFA (XML Forms Architecture)
- More advanced form technology using XML
- Supports dynamic forms that can change layout
- May not be supported by all PDF readers
- Uses XML to define form structure and behavior

### Hybrid Forms
- Contains both XFA and AcroForm data
- Provides fallback support for readers that don't support XFA

## Technical Details

The script examines the PDF's catalog (`/AcroForm` entry) to check for:
- `/XFA` key: Indicates XFA form data
- `/Fields` key: Indicates AcroForm fields

## Troubleshooting

### "PyCryptodome is required" error
Your PDF is encrypted. Install the required dependencies:
```bash
pip install pycryptodome
```

### "No form fields found" but PDF appears fillable
The original `pdf_form_detector.py` using PyPDF2 may fail on encrypted PDFs. Use the enhanced tools:
```bash
python inspect_pdf.py your_file.pdf  # More robust inspection
python list_fields.py your_file.pdf  # List all fields
```

### Field names not obvious
Use `list_fields.py` to see all available field names and their types. Insurance forms often use codes like "A04t", "B12c", etc.

## Scripts Overview

| Script | Purpose | Best For |
|--------|---------|----------|
| `remove_void.py` ⭐ | Permanently remove VOID watermark | **Creating clean templates** |
| `find_field_by_label.py` ⭐ | Search fields by visible label | **Finding correct field names** |
| `generate_template.py` ⭐ | Create commented JSON template | **Building data files** |
| `fill_pdf.py` ⭐ | Fill forms with data | **Production use** |
| `list_fields.py` | List all field names and types | Exploring form structure |
| `export_fields.py` | Export current field values | Extracting data |
| `inspect_pdf.py` | Deep PDF structure analysis | Troubleshooting |
| `map_fields.py` | Detailed field mapping | Debugging field issues |
| `pdf_form_detector.py` | Quick check for form type | Initial detection |
| `advanced_pdf_analyzer.py` | Alternative analyzer | Complex cases |

⭐ = Most commonly used

## Requirements

- Python 3.7+
- pikepdf >= 9.0.0
- pycryptodome >= 3.20.0
- PyPDF2 >= 3.0.0 (for basic detection)

## License

This is free and unencumbered software released into the public domain.
