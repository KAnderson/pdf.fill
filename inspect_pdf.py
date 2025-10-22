#!/usr/bin/env python3
"""
Comprehensive PDF Inspector using pikepdf
Shows EVERYTHING in the PDF structure
"""

import sys
import json
from pathlib import Path
import pikepdf


def inspect_pdf(pdf_path):
    """Comprehensive inspection of PDF structure"""

    print(f"\n{'='*80}")
    print(f"COMPLETE PDF INSPECTION: {Path(pdf_path).name}")
    print(f"{'='*80}\n")

    try:
        pdf = pikepdf.open(pdf_path)

        # Basic info
        print(f"PDF Version: {pdf.pdf_version}")
        print(f"Pages: {len(pdf.pages)}")
        print(f"Is encrypted: {pdf.is_encrypted if hasattr(pdf, 'is_encrypted') else 'N/A'}")

        # Root catalog
        print(f"\n{'─'*80}")
        print("ROOT CATALOG")
        print(f"{'─'*80}")
        root = pdf.Root
        print(f"Root keys: {list(root.keys())}\n")

        for key in root.keys():
            print(f"/{key}: {type(root[key]).__name__}")

        # Check AcroForm
        print(f"\n{'─'*80}")
        print("ACROFORM CHECK")
        print(f"{'─'*80}")

        if '/AcroForm' in root:
            acroform = root.AcroForm
            print(f"✓ AcroForm found!")
            print(f"AcroForm keys: {list(acroform.keys())}\n")

            for key in acroform.keys():
                print(f"/{key}: {type(acroform[key]).__name__} = {acroform[key]}")

            if '/Fields' in acroform:
                fields = acroform.Fields
                print(f"\n✓ Found {len(fields)} form fields!")

                for i, field in enumerate(fields[:20], 1):  # First 20 fields
                    print(f"\n  Field {i}:")
                    field_obj = field
                    for fkey in field_obj.keys():
                        try:
                            val = field_obj[fkey]
                            print(f"    /{fkey}: {val}")
                        except:
                            print(f"    /{fkey}: <unable to read>")
            else:
                print("✗ No /Fields array found")
        else:
            print("✗ No /AcroForm in catalog")

        # Check each page
        print(f"\n{'─'*80}")
        print("PAGE INSPECTION")
        print(f"{'─'*80}")

        total_annots = 0
        for i, page in enumerate(pdf.pages[:5], 1):  # First 5 pages
            print(f"\nPage {i}:")
            print(f"  Keys: {list(page.keys())}")

            if '/Annots' in page:
                annots = page.Annots
                total_annots += len(annots)
                print(f"  ✓ Found {len(annots)} annotations")

                for j, annot in enumerate(annots[:10], 1):  # First 10 per page
                    print(f"\n    Annotation {j}:")
                    for akey in annot.keys():
                        try:
                            val = annot[akey]
                            # Truncate long values
                            val_str = str(val)
                            if len(val_str) > 100:
                                val_str = val_str[:100] + "..."
                            print(f"      /{akey}: {val_str}")
                        except:
                            print(f"      /{akey}: <unable to read>")
            else:
                print(f"  No annotations")

        print(f"\nTotal annotations across all pages: {total_annots}")

        # Check for XFA
        print(f"\n{'─'*80}")
        print("XFA CHECK")
        print(f"{'─'*80}")

        if '/AcroForm' in root and '/XFA' in root.AcroForm:
            print("✓ XFA forms detected")
        else:
            print("✗ No XFA forms")

        # Summary
        print(f"\n{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}\n")

        has_acroform = '/AcroForm' in root
        has_fields = has_acroform and '/Fields' in root.AcroForm
        field_count = len(root.AcroForm.Fields) if has_fields else 0

        if has_fields and field_count > 0:
            print(f"✓ This PDF has {field_count} AcroForm fields")
            print("  You can fill this PDF using standard PDF libraries")
        elif total_annots > 0:
            print(f"⚠ No AcroForm fields, but found {total_annots} annotations")
            print("  The 'fillable' appearance might be from:")
            print("  • Text annotations or markup")
            print("  • Flattened form fields (removed after creation)")
            print("  • Visual field indicators without actual form structure")
            print("\n  This PDF cannot be filled programmatically without:")
            print("  • Recreating the form fields in a PDF editor")
            print("  • Using OCR and coordinate-based text placement")
            print("  • Overlaying text on specific coordinates")
        else:
            print("✗ This PDF has no interactive elements")
            print("  It appears to be a static document")

        pdf.close()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    if len(sys.argv) < 2:
        print("Usage: python inspect_pdf.py <pdf_file>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not Path(pdf_path).exists():
        print(f"Error: File not found - {pdf_path}")
        sys.exit(1)

    inspect_pdf(pdf_path)


if __name__ == "__main__":
    main()
