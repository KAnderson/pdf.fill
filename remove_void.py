#!/usr/bin/env python3
"""
Remove VOID Watermark from PDF

The VOID watermark in iA Financial Group PDFs is a button field called 'btnVoid'
with appearance streams that draw the actual "VOID" text.

This script permanently removes the watermark by:
1. Setting the btnVoid field to hidden (flag bit 1)
2. Removing all appearance streams (/AP) that render "VOID"
3. Clearing button captions
4. Clearing the H_Proposition field value

Works in ALL PDF viewers (not just Adobe Acrobat).
"""

import sys
from pathlib import Path
import pikepdf
from pikepdf import Name


def remove_void_actual(input_pdf, output_pdf):
    """
    Remove VOID by hiding the btnVoid button field permanently
    """

    print(f"Opening: {input_pdf}\n")
    pdf = pikepdf.open(input_pdf)

    if '/AcroForm' not in pdf.Root or '/Fields' not in pdf.Root.AcroForm:
        print("✗ No form fields found")
        return False

    fields = pdf.Root.AcroForm.Fields
    found_btnvoid = False
    found_h_prop = False

    for field in fields:
        if '/T' not in field:
            continue

        field_name = str(field['/T'])

        # Hide the btnVoid button (the VOID watermark)
        if field_name == 'btnVoid':
            found_btnvoid = True
            print("✓ Found btnVoid field (the VOID watermark)")

            # Set field flags to make it hidden
            # Bit 1 = Hidden (field value: 2)
            # Bit 2 = NoView (field value: 32)
            current_flags = int(field.get('/Ff', 0))
            new_flags = current_flags | 2  # Set hidden bit
            field['/Ff'] = new_flags

            print(f"  Changed flags: {current_flags} → {new_flags} (hidden)")

            # Clear the caption AND appearance streams
            if '/Kids' in field:
                for kid in field['/Kids']:
                    # Clear button caption
                    if '/MK' in kid:
                        kid['/MK']['/CA'] = ''  # Clear button caption

                    # Remove appearance stream (this is what actually draws VOID!)
                    if '/AP' in kid:
                        del kid['/AP']

                print(f"  Cleared caption and appearance on {len(field['/Kids'])} button widgets")

            # Also remove appearance from parent field if present
            if '/AP' in field:
                del field['/AP']
                print(f"  Removed parent field appearance stream")

        # Clear H_Proposition field
        if field_name == 'H_Proposition':
            found_h_prop = True
            print("\n✓ Found H_Proposition field")

            # Remove ReadOnly flag
            if '/Ff' in field:
                current_flags = int(field['/Ff'])
                new_flags = current_flags & ~1  # Clear ReadOnly bit
                field['/Ff'] = new_flags
                print(f"  Made writable: {current_flags} → {new_flags}")

            # Set to empty
            field['/V'] = ''
            field['/DV'] = ''
            print("  Cleared value")

            if '/Kids' in field:
                for kid in field['/Kids']:
                    kid['/V'] = ''
                    if '/AP' in kid:
                        del kid['/AP']
                print(f"  Updated {len(field['/Kids'])} widgets")

    if not found_btnvoid:
        print("\n⚠️  btnVoid field not found - watermark might be different")

    if not found_h_prop:
        print("\n⚠️  H_Proposition field not found")

    if found_btnvoid or found_h_prop:
        # Set NeedAppearances
        pdf.Root.AcroForm['/NeedAppearances'] = True

        print(f"\nSaving to: {output_pdf}")
        pdf.save(output_pdf)

        print("\n" + "="*60)
        print("✅ SUCCESS!")
        print("="*60)
        print("\nVOID watermark has been hidden:")
        print("  ✓ btnVoid field set to hidden")
        print("  ✓ H_Proposition cleared")
        print("  ✓ All other fields remain fillable")
        print("\nThis should work in ALL PDF viewers!")
        return True
    else:
        print("\n✗ Could not find required fields")
        return False

    pdf.close()


def main():
    if len(sys.argv) < 3:
        print("Remove VOID watermark from PDF\n")
        print("Usage: python remove_void.py <input.pdf> <output.pdf>")
        print("\nExample:")
        print('  python remove_void.py "original.pdf" "clean_template.pdf"')
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]

    if not Path(input_pdf).exists():
        print(f"Error: File not found - {input_pdf}")
        sys.exit(1)

    remove_void_actual(input_pdf, output_pdf)


if __name__ == "__main__":
    main()
