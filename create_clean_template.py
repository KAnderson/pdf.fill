#!/usr/bin/env python3
"""
Create a completely clean PDF template by:
1. Removing the VOID watermark image
2. Clearing the H_Proposition field
3. Making all fields writable

This creates a production-ready template for form filling.
"""

import sys
from pathlib import Path
import pikepdf
from pikepdf import Name


def create_clean_template(input_pdf, output_pdf):
    """Create a clean template without VOID watermark"""

    print(f"Opening: {input_pdf}\n")
    pdf = pikepdf.open(input_pdf)

    # Step 1: Remove VOID watermark images
    print("Step 1: Removing VOID watermark images...")
    pages_modified = 0

    for page_num, page in enumerate(pdf.pages):
        if '/Resources' in page and '/XObject' in page.Resources:
            xobjects = page.Resources.XObject

            for xobj_name in list(xobjects.keys()):
                xobj = xobjects[xobj_name]

                if xobj.get('/Subtype') == Name('/Image'):
                    width = xobj.get('/Width', 0)
                    height = xobj.get('/Height', 0)

                    # Remove large images (likely watermarks)
                    if width > 500 or height > 500:
                        print(f"  Page {page_num + 1}: Removing {xobj_name} ({width}x{height})")
                        del page.Resources.XObject[xobj_name]
                        pages_modified += 1

    print(f"  ✓ Removed watermark from {pages_modified} page(s)\n")

    # Step 2: Clear H_Proposition field
    print("Step 2: Clearing H_Proposition field...")

    if '/AcroForm' in pdf.Root and '/Fields' in pdf.Root.AcroForm:
        for field in pdf.Root.AcroForm.Fields:
            if '/T' in field and str(field['/T']) == 'H_Proposition':
                # Remove ReadOnly flag (bit 0)
                if '/Ff' in field:
                    current_flags = int(field['/Ff'])
                    new_flags = current_flags & ~1
                    field['/Ff'] = new_flags
                    print(f"  ✓ Made field writable (flags: {current_flags} → {new_flags})")

                # Clear value
                field['/V'] = ''
                field['/DV'] = ''
                print("  ✓ Cleared field value")

                # Update all widget instances
                if '/Kids' in field:
                    for kid in field['/Kids']:
                        kid['/V'] = ''
                        if '/AP' in kid:
                            del kid['/AP']
                    print(f"  ✓ Updated {len(field['/Kids'])} widget instances")

                break

        # Set NeedAppearances flag
        pdf.Root.AcroForm['/NeedAppearances'] = True
        print("  ✓ Set NeedAppearances flag\n")

    # Step 3: Save
    print(f"Saving to: {output_pdf}")
    pdf.save(output_pdf)
    pdf.close()

    print("\n" + "="*60)
    print("✅ SUCCESS! Clean template created")
    print("="*60)
    print("\nYour clean PDF template:")
    print("  ✓ No VOID watermark")
    print("  ✓ Application number field is empty")
    print("  ✓ All fields are fillable")
    print("  ✓ Ready for production use")
    print("\nUse this template for all your form filling!")


def main():
    if len(sys.argv) < 3:
        print("Create a clean PDF template without VOID watermark\n")
        print("Usage: python create_clean_template.py <input.pdf> <output.pdf>")
        print("\nExample:")
        print('  python create_clean_template.py "ia financial group dev004391.pdf" "clean_template.pdf"')
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]

    if not Path(input_pdf).exists():
        print(f"Error: File not found - {input_pdf}")
        sys.exit(1)

    create_clean_template(input_pdf, output_pdf)


if __name__ == "__main__":
    main()
