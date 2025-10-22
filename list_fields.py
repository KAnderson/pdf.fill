#!/usr/bin/env python3
"""
List all form fields in a PDF
"""

import sys
from pathlib import Path
import pikepdf


def list_fields(pdf_path):
    """List all form fields with their names and types"""

    print(f"\n{'='*80}")
    print(f"FORM FIELDS: {Path(pdf_path).name}")
    print(f"{'='*80}\n")

    try:
        pdf = pikepdf.open(pdf_path)

        # Check AcroForm
        if '/AcroForm' not in pdf.Root:
            print("✗ No AcroForm found in this PDF")
            return

        acroform = pdf.Root.AcroForm

        if '/Fields' not in acroform:
            print("✗ No /Fields array found")
            return

        fields = acroform.Fields
        print(f"Found {len(fields)} form fields\n")
        print(f"{'─'*80}\n")

        # List all fields
        for i, field in enumerate(fields, 1):
            field_info = {}

            # Get field name
            if '/T' in field:
                field_info['name'] = str(field['/T'])
            else:
                field_info['name'] = f"<unnamed_{i}>"

            # Get field type
            if '/FT' in field:
                ft = str(field['/FT'])
                field_types = {
                    '/Tx': 'Text',
                    '/Btn': 'Button/Checkbox',
                    '/Ch': 'Choice (dropdown/list)',
                    '/Sig': 'Signature'
                }
                field_info['type'] = field_types.get(ft, ft)
            elif '/Kids' in field:
                # Check first kid for type
                try:
                    first_kid = field['/Kids'][0]
                    if '/FT' in first_kid:
                        ft = str(first_kid['/FT'])
                        field_types = {
                            '/Tx': 'Text',
                            '/Btn': 'Button/Checkbox',
                            '/Ch': 'Choice (dropdown/list)',
                            '/Sig': 'Signature'
                        }
                        field_info['type'] = field_types.get(ft, ft)
                    else:
                        field_info['type'] = 'Parent field'
                except:
                    field_info['type'] = 'Parent field'
            else:
                field_info['type'] = 'Unknown'

            # Get current value
            if '/V' in field:
                field_info['value'] = str(field['/V'])
            else:
                field_info['value'] = '<empty>'

            # Get default value
            if '/DV' in field:
                field_info['default'] = str(field['/DV'])

            # Check if it has kids (is a parent field)
            if '/Kids' in field:
                field_info['kids'] = len(field['/Kids'])

            # Print field info
            print(f"{i:4d}. {field_info['name']}")
            print(f"       Type: {field_info['type']}")
            if 'value' in field_info:
                val = field_info['value']
                if len(val) > 50:
                    val = val[:50] + "..."
                print(f"       Value: {val}")
            if 'default' in field_info:
                print(f"       Default: {field_info['default']}")
            if 'kids' in field_info:
                print(f"       Children: {field_info['kids']}")
            print()

        pdf.close()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    if len(sys.argv) < 2:
        print("Usage: python list_fields.py <pdf_file>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not Path(pdf_path).exists():
        print(f"Error: File not found - {pdf_path}")
        sys.exit(1)

    list_fields(pdf_path)


if __name__ == "__main__":
    main()
