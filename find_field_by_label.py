#!/usr/bin/env python3
"""
Search for fields by their tooltip/label text
"""

import sys
from pathlib import Path
import pikepdf
import json


def search_fields(pdf_path, search_term=None):
    """Search fields by tooltip or name"""

    try:
        pdf = pikepdf.open(pdf_path)

        if '/AcroForm' not in pdf.Root or '/Fields' not in pdf.Root.AcroForm:
            print("✗ No form fields found")
            return

        fields = pdf.Root.AcroForm.Fields
        results = []

        for field in fields:
            field_info = {
                'name': '',
                'tooltip': '',
                'page': 0,
                'type': ''
            }

            # Get field name
            if '/T' in field:
                field_info['name'] = str(field['/T'])

            # Get tooltip
            if '/TU' in field:
                field_info['tooltip'] = str(field['/TU'])

            # Get type
            if '/FT' in field:
                ft = str(field['/FT'])
                type_map = {'/Tx': 'Text', '/Btn': 'Button', '/Ch': 'Choice', '/Sig': 'Signature'}
                field_info['type'] = type_map.get(ft, ft)
            elif '/Kids' in field and len(field['/Kids']) > 0:
                try:
                    first_kid = field['/Kids'][0]
                    if '/FT' in first_kid:
                        ft = str(first_kid['/FT'])
                        type_map = {'/Tx': 'Text', '/Btn': 'Button', '/Ch': 'Choice', '/Sig': 'Signature'}
                        field_info['type'] = type_map.get(ft, ft)
                    if '/P' in first_kid:
                        page_obj = first_kid['/P']
                        for i, page in enumerate(pdf.pages):
                            if page.objgen == page_obj.objgen:
                                field_info['page'] = i + 1
                                break
                except:
                    pass

            # Filter by search term if provided
            if search_term:
                search_lower = search_term.lower()
                if (search_lower in field_info['name'].lower() or
                    search_lower in field_info['tooltip'].lower()):
                    results.append(field_info)
            else:
                results.append(field_info)

        pdf.close()
        return results

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def main():
    if len(sys.argv) < 2:
        print("Usage: python find_field_by_label.py <pdf_file> [search_term]")
        print("\nExamples:")
        print("  python find_field_by_label.py form.pdf 'last name'")
        print("  python find_field_by_label.py form.pdf 'address'")
        print("  python find_field_by_label.py form.pdf 'A0'")
        sys.exit(1)

    pdf_path = sys.argv[1]
    search_term = sys.argv[2] if len(sys.argv) > 2 else None

    if not Path(pdf_path).exists():
        print(f"Error: File not found - {pdf_path}")
        sys.exit(1)

    results = search_fields(pdf_path, search_term)

    if search_term:
        print(f"\nSearching for: '{search_term}'")
        print(f"Found {len(results)} matches\n")
        print(f"{'─'*100}\n")
    else:
        print(f"\nAll fields with tooltips:\n")
        print(f"{'─'*100}\n")

    for field in results:
        print(f"Field: {field['name']:30s} | Type: {field['type']:10s} | Page: {field['page']}")
        if field['tooltip']:
            print(f"  → {field['tooltip']}")
        print()


if __name__ == "__main__":
    main()
