#!/usr/bin/env python3
"""
Fill PDF form fields programmatically
"""

import sys
import json
from pathlib import Path
import pikepdf


def fill_pdf(input_pdf, output_pdf, field_data):
    """
    Fill PDF form fields with provided data

    Args:
        input_pdf: Path to input PDF file
        output_pdf: Path to save filled PDF
        field_data: Dictionary mapping field names to values
                    Example: {"A04t": "John Doe", "A06t": "123 Main St"}
    """

    print(f"Opening: {input_pdf}")
    pdf = pikepdf.open(input_pdf)

    if '/AcroForm' not in pdf.Root or '/Fields' not in pdf.Root.AcroForm:
        print("✗ No form fields found in this PDF")
        pdf.close()
        return False

    fields = pdf.Root.AcroForm.Fields
    filled_count = 0
    not_found = []

    print(f"Found {len(fields)} form fields")
    print(f"Attempting to fill {len(field_data)} fields...\n")

    for field in fields:
        # Get field name
        if '/T' not in field:
            continue

        field_name = str(field['/T'])

        # Check if this field should be filled
        if field_name in field_data:
            value = field_data[field_name]

            # Determine field type
            field_type = None
            if '/FT' in field:
                field_type = str(field['/FT'])
            elif '/Kids' in field and len(field['/Kids']) > 0:
                # Check first kid for type
                first_kid = field['/Kids'][0]
                if '/FT' in first_kid:
                    field_type = str(first_kid['/FT'])

            # Fill based on field type
            try:
                if field_type == '/Btn':
                    # Button/Checkbox field
                    if value in [True, 'Yes', 'yes', 'ON', 'On', 1, '1']:
                        field['/V'] = pikepdf.Name('/Yes')
                        field['/AS'] = pikepdf.Name('/Yes')
                    else:
                        field['/V'] = pikepdf.Name('/Off')
                        field['/AS'] = pikepdf.Name('/Off')
                elif field_type == '/Tx':
                    # Text field
                    field['/V'] = str(value)
                elif field_type == '/Ch':
                    # Choice field (dropdown/list)
                    field['/V'] = str(value)
                else:
                    # Unknown type, try as text
                    field['/V'] = str(value)

                print(f"✓ Filled: {field_name} = {value}")
                filled_count += 1

            except Exception as e:
                print(f"✗ Error filling {field_name}: {e}")

    # Check for fields in data that weren't found
    for field_name in field_data:
        found = False
        for field in fields:
            if '/T' in field and str(field['/T']) == field_name:
                found = True
                break
        if not found:
            not_found.append(field_name)

    print(f"\n{'='*80}")
    print(f"Summary:")
    print(f"  Fields filled: {filled_count}/{len(field_data)}")

    if not_found:
        print(f"\n  Fields not found in PDF:")
        for fname in not_found[:10]:  # Show first 10
            print(f"    - {fname}")
        if len(not_found) > 10:
            print(f"    ... and {len(not_found) - 10} more")

    # Save the filled PDF
    print(f"\nSaving to: {output_pdf}")
    pdf.save(output_pdf)
    pdf.close()

    print("✓ Done!")
    return True


def main():
    if len(sys.argv) < 4:
        print("Usage: python fill_pdf.py <input_pdf> <output_pdf> <field_data_json>")
        print("\nExamples:")
        print('  python fill_pdf.py input.pdf output.pdf \'{"A04t": "John Doe", "A06t": "123 Main St"}\'')
        print('  python fill_pdf.py input.pdf output.pdf data.json')
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]
    field_data_arg = sys.argv[3]

    if not Path(input_pdf).exists():
        print(f"Error: Input file not found - {input_pdf}")
        sys.exit(1)

    # Parse field data
    try:
        # Check if it's a file path
        if Path(field_data_arg).exists():
            with open(field_data_arg, 'r') as f:
                field_data = json.load(f)
        else:
            # Parse as JSON string
            field_data = json.loads(field_data_arg)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON data - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    fill_pdf(input_pdf, output_pdf, field_data)


if __name__ == "__main__":
    main()
