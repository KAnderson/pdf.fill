#!/usr/bin/env python3
"""
Export all form fields to a JSON template file
"""

import sys
import json
from pathlib import Path
import pikepdf


def export_fields_to_json(pdf_path, output_json=None, include_empty=True):
    """
    Export all form fields to a JSON file

    Args:
        pdf_path: Path to PDF file
        output_json: Output JSON file path (optional)
        include_empty: Include fields with no current value
    """

    try:
        pdf = pikepdf.open(pdf_path)

        if '/AcroForm' not in pdf.Root or '/Fields' not in pdf.Root.AcroForm:
            print("✗ No form fields found in this PDF")
            pdf.close()
            return None

        fields = pdf.Root.AcroForm.Fields
        field_data = {}

        print(f"Extracting {len(fields)} form fields...")

        for field in fields:
            # Get field name
            if '/T' not in field:
                continue

            field_name = str(field['/T'])

            # Get current value
            value = ""
            if '/V' in field:
                val = field['/V']
                if isinstance(val, pikepdf.Name):
                    value = str(val).lstrip('/')
                else:
                    value = str(val)

            # Add to dictionary if it has a value or include_empty is True
            if value or include_empty:
                field_data[field_name] = value

        pdf.close()

        # Determine output file
        if output_json is None:
            pdf_name = Path(pdf_path).stem
            output_json = f"{pdf_name}_fields.json"

        # Write JSON
        with open(output_json, 'w') as f:
            json.dump(field_data, f, indent=2, ensure_ascii=False)

        print(f"✓ Exported {len(field_data)} fields to: {output_json}")
        return field_data

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python export_fields.py <pdf_file> [output.json]")
        print("\nExamples:")
        print("  python export_fields.py form.pdf")
        print("  python export_fields.py form.pdf template.json")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_json = sys.argv[2] if len(sys.argv) > 2 else None

    if not Path(pdf_path).exists():
        print(f"Error: File not found - {pdf_path}")
        sys.exit(1)

    export_fields_to_json(pdf_path, output_json)


if __name__ == "__main__":
    main()
