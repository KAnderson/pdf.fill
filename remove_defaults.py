#!/usr/bin/env python3
"""
Remove default values from a PDF before filling
Useful for removing watermarks like "VOID"
"""

import sys
from pathlib import Path
import pikepdf


def remove_default_values(input_pdf, output_pdf, fields_to_clear=None):
    """
    Remove default values from specified fields or all fields

    Args:
        input_pdf: Path to input PDF
        output_pdf: Path to save cleaned PDF
        fields_to_clear: List of field names to clear, or None for all fields
    """

    print(f"Opening: {input_pdf}")
    pdf = pikepdf.open(input_pdf)

    if '/AcroForm' not in pdf.Root or '/Fields' not in pdf.Root.AcroForm:
        print("✗ No form fields found")
        pdf.close()
        return False

    fields = pdf.Root.AcroForm.Fields
    cleared_count = 0

    for field in fields:
        if '/T' not in field:
            continue

        field_name = str(field['/T'])

        # Check if this field should be cleared
        should_clear = False
        if fields_to_clear is None:
            # Clear all fields with values
            should_clear = '/V' in field
        else:
            # Clear only specified fields
            should_clear = field_name in fields_to_clear and '/V' in field

        if should_clear:
            # Get current value for logging
            current_value = ""
            if '/V' in field:
                val = field['/V']
                if isinstance(val, pikepdf.Name):
                    current_value = str(val).lstrip('/')
                else:
                    current_value = str(val)

            # Clear the value
            try:
                del field['/V']

                # Also clear appearance if present
                if '/AP' in field:
                    del field['/AP']

                print(f"✓ Cleared: {field_name} (was: '{current_value}')")
                cleared_count += 1
            except Exception as e:
                print(f"✗ Error clearing {field_name}: {e}")

    print(f"\n{'='*80}")
    print(f"Summary: Cleared {cleared_count} fields")
    print(f"Saving to: {output_pdf}")

    pdf.save(output_pdf)
    pdf.close()

    print("✓ Done!")
    return True


def main():
    if len(sys.argv) < 3:
        print("Usage: python remove_defaults.py <input_pdf> <output_pdf> [field_names]")
        print("\nExamples:")
        print("  # Remove VOID from application number field")
        print("  python remove_defaults.py input.pdf clean.pdf H_Proposition")
        print("")
        print("  # Remove values from multiple fields")
        print("  python remove_defaults.py input.pdf clean.pdf H_Proposition,A04t")
        print("")
        print("  # Remove ALL default values (use with caution!)")
        print("  python remove_defaults.py input.pdf clean.pdf ALL")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]

    # Parse field names
    fields_to_clear = None
    if len(sys.argv) > 3:
        arg = sys.argv[3]
        if arg.upper() == 'ALL':
            fields_to_clear = None  # Clear all
            print("⚠️  WARNING: Clearing ALL default values from the PDF\n")
        else:
            fields_to_clear = [f.strip() for f in arg.split(',')]
            print(f"Clearing fields: {', '.join(fields_to_clear)}\n")
    else:
        # Default: clear only H_Proposition (VOID watermark)
        fields_to_clear = ['H_Proposition']
        print("Clearing default fields: H_Proposition\n")

    if not Path(input_pdf).exists():
        print(f"Error: Input file not found - {input_pdf}")
        sys.exit(1)

    remove_default_values(input_pdf, output_pdf, fields_to_clear)


if __name__ == "__main__":
    main()
