#!/usr/bin/env python3
"""
Advanced PDF Form Analyzer
Deep inspection of PDF structure to find all types of fillable elements
"""

import sys
from pathlib import Path
import PyPDF2


def analyze_pdf_structure(pdf_path):
    """Deep analysis of PDF structure"""
    result = {
        "has_acroform": False,
        "has_xfa": False,
        "pages": [],
        "catalog_keys": [],
        "form_fields": [],
        "annotations": [],
        "warnings": []
    }

    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)

            # Basic info
            result["page_count"] = len(reader.pages)
            result["is_encrypted"] = reader.is_encrypted

            # Check catalog
            catalog = reader.trailer['/Root']
            result["catalog_keys"] = [str(k) for k in catalog.keys()]

            # Check AcroForm
            if '/AcroForm' in catalog:
                result["has_acroform"] = True
                acroform = catalog['/AcroForm']
                result["acroform_keys"] = [str(k) for k in acroform.keys()]

                if '/XFA' in acroform:
                    result["has_xfa"] = True

                if '/Fields' in acroform:
                    fields = acroform['/Fields']
                    result["field_count"] = len(fields)

                    # Try to get field details
                    for i, field in enumerate(fields[:10]):  # First 10 fields
                        try:
                            field_obj = field.get_object()
                            field_info = {}
                            if '/T' in field_obj:
                                field_info['name'] = str(field_obj['/T'])
                            if '/FT' in field_obj:
                                field_info['type'] = str(field_obj['/FT'])
                            if '/V' in field_obj:
                                field_info['value'] = str(field_obj['/V'])
                            result["form_fields"].append(field_info)
                        except:
                            pass

            # Analyze each page
            for page_num, page in enumerate(reader.pages):
                page_info = {
                    "page_num": page_num + 1,
                    "keys": [str(k) for k in page.keys()],
                    "annotations": []
                }

                # Check for annotations
                if '/Annots' in page:
                    try:
                        annots = page['/Annots']
                        for annot in annots:
                            annot_obj = annot.get_object()
                            annot_info = {}

                            if '/Subtype' in annot_obj:
                                annot_info['subtype'] = str(annot_obj['/Subtype'])
                            if '/FT' in annot_obj:
                                annot_info['field_type'] = str(annot_obj['/FT'])
                            if '/T' in annot_obj:
                                annot_info['name'] = str(annot_obj['/T'])
                            if '/Rect' in annot_obj:
                                annot_info['has_rect'] = True

                            page_info["annotations"].append(annot_info)
                            result["annotations"].append({
                                "page": page_num + 1,
                                **annot_info
                            })
                    except Exception as e:
                        page_info["annot_error"] = str(e)

                if page_info["annotations"] or '/Annots' in page.keys():
                    result["pages"].append(page_info)

    except Exception as e:
        result["error"] = str(e)

    return result


def print_analysis(result, pdf_path):
    """Print detailed analysis"""
    print(f"\n{'='*70}")
    print(f"ADVANCED PDF ANALYSIS: {Path(pdf_path).name}")
    print(f"{'='*70}\n")

    print(f"Pages: {result.get('page_count', 'Unknown')}")
    print(f"Encrypted: {result.get('is_encrypted', 'Unknown')}")
    print(f"Has AcroForm: {result['has_acroform']}")
    print(f"Has XFA: {result['has_xfa']}")

    print(f"\n{'─'*70}")
    print("CATALOG STRUCTURE")
    print(f"{'─'*70}")
    print(f"Keys in catalog: {', '.join(result.get('catalog_keys', []))}")

    if result['has_acroform']:
        print(f"\n{'─'*70}")
        print("ACROFORM DETAILS")
        print(f"{'─'*70}")
        print(f"AcroForm keys: {', '.join(result.get('acroform_keys', []))}")
        print(f"Field count: {result.get('field_count', 0)}")

        if result.get('form_fields'):
            print("\nSample fields:")
            for i, field in enumerate(result['form_fields'][:5], 1):
                print(f"  {i}. {field}")

    if result.get('annotations'):
        print(f"\n{'─'*70}")
        print(f"ANNOTATIONS FOUND: {len(result['annotations'])} total")
        print(f"{'─'*70}")

        # Group by type
        by_type = {}
        by_page = {}

        for annot in result['annotations']:
            subtype = annot.get('subtype', 'Unknown')
            by_type[subtype] = by_type.get(subtype, 0) + 1

            page = annot.get('page', 0)
            by_page[page] = by_page.get(page, 0) + 1

        print("\nBy type:")
        for atype, count in sorted(by_type.items()):
            print(f"  {atype}: {count}")

        print("\nBy page:")
        for page, count in sorted(by_page.items()):
            print(f"  Page {page}: {count} annotations")

        print("\nFirst 10 annotations:")
        for i, annot in enumerate(result['annotations'][:10], 1):
            print(f"  {i}. Page {annot.get('page', '?')}: {annot}")

    if result.get('pages'):
        print(f"\n{'─'*70}")
        print("PAGES WITH INTERACTIVE ELEMENTS")
        print(f"{'─'*70}")
        for page in result['pages'][:5]:  # First 5 pages
            print(f"\nPage {page['page_num']}:")
            print(f"  Keys: {', '.join(page['keys'])}")
            if page.get('annotations'):
                print(f"  Annotations: {len(page['annotations'])}")

    print(f"\n{'='*70}")
    print("DIAGNOSIS")
    print(f"{'='*70}\n")

    if result['has_acroform'] and result.get('field_count', 0) > 0:
        print("✓ This PDF has standard AcroForm fields")
        print(f"  Found {result['field_count']} form fields")
    elif result.get('annotations'):
        print("⚠ No standard form fields found, but annotations detected")
        print(f"  Found {len(result['annotations'])} annotations")
        print("\n  Possible reasons:")
        print("  • Fields created as annotations without proper AcroForm structure")
        print("  • PDF was created with non-standard form tools")
        print("  • Form fields exist but are not in the /Fields array")
        print("\n  Solutions:")
        print("  • Try opening in Adobe Acrobat and use 'Prepare Form' tool")
        print("  • Use pdftk to dump data and check structure")
        print("  • Use a PDF editor to rebuild form fields")
    else:
        print("✗ No form fields or annotations found")
        print("\n  This appears to be a static PDF")
        print("  You may need to:")
        print("  • Add form fields manually using PDF editing software")
        print("  • Use OCR if it's a scanned document")
        print("  • Convert to an editable format")

    if result.get('error'):
        print(f"\n⚠ Error during analysis: {result['error']}")

    print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python advanced_pdf_analyzer.py <pdf_file>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not Path(pdf_path).exists():
        print(f"Error: File not found - {pdf_path}")
        sys.exit(1)

    result = analyze_pdf_structure(pdf_path)
    print_analysis(result, pdf_path)


if __name__ == "__main__":
    main()
