#!/usr/bin/env python3
"""
Create a detailed field mapping showing field names, types, positions, and tooltips
"""

import sys
from pathlib import Path
import pikepdf


def map_fields(pdf_path):
    """Create detailed field mapping"""

    print(f"\n{'='*100}")
    print(f"DETAILED FIELD MAPPING: {Path(pdf_path).name}")
    print(f"{'='*100}\n")

    try:
        pdf = pikepdf.open(pdf_path)

        if '/AcroForm' not in pdf.Root or '/Fields' not in pdf.Root.AcroForm:
            print("✗ No form fields found")
            return

        fields = pdf.Root.AcroForm.Fields
        field_list = []

        # Collect field information
        for field in fields:
            field_info = {
                'name': '',
                'type': '',
                'tooltip': '',
                'page': 0,
                'rect': None,
                'value': '',
                'kids': 0
            }

            # Get field name
            if '/T' in field:
                field_info['name'] = str(field['/T'])

            # Get field type
            if '/FT' in field:
                ft = str(field['/FT'])
                type_map = {
                    '/Tx': 'Text',
                    '/Btn': 'Button/Checkbox',
                    '/Ch': 'Choice',
                    '/Sig': 'Signature'
                }
                field_info['type'] = type_map.get(ft, ft)
            elif '/Kids' in field and len(field['/Kids']) > 0:
                field_info['kids'] = len(field['/Kids'])
                # Check first kid
                try:
                    first_kid = field['/Kids'][0]
                    if '/FT' in first_kid:
                        ft = str(first_kid['/FT'])
                        type_map = {
                            '/Tx': 'Text',
                            '/Btn': 'Button/Checkbox',
                            '/Ch': 'Choice',
                            '/Sig': 'Signature'
                        }
                        field_info['type'] = type_map.get(ft, ft)

                    # Get page from first kid
                    if '/P' in first_kid:
                        page_obj = first_kid['/P']
                        for i, page in enumerate(pdf.pages):
                            if page.objgen == page_obj.objgen:
                                field_info['page'] = i + 1
                                break

                    # Get rect from first kid
                    if '/Rect' in first_kid:
                        field_info['rect'] = [float(x) for x in first_kid['/Rect']]
                except:
                    pass

            # Get tooltip (TU = alternate description)
            if '/TU' in field:
                field_info['tooltip'] = str(field['/TU'])

            # Get current value
            if '/V' in field:
                val = field['/V']
                if isinstance(val, pikepdf.Name):
                    field_info['value'] = str(val).lstrip('/')
                else:
                    field_info['value'] = str(val)

            field_list.append(field_info)

        # Sort by page, then by Y position (top to bottom), then X position
        field_list.sort(key=lambda f: (
            f['page'],
            -f['rect'][3] if f['rect'] else 0,  # Y coordinate (inverted)
            f['rect'][0] if f['rect'] else 0     # X coordinate
        ))

        # Group by page
        current_page = 0
        for field_info in field_list:
            if field_info['page'] != current_page:
                current_page = field_info['page']
                print(f"\n{'─'*100}")
                print(f"PAGE {current_page}")
                print(f"{'─'*100}\n")

            # Print field info
            name = field_info['name'] or '<unnamed>'
            ftype = field_info['type'] or 'Unknown'
            tooltip = field_info['tooltip']
            value = field_info['value']

            print(f"{name:30s} | {ftype:15s}", end='')

            if tooltip:
                print(f" | Tooltip: {tooltip}", end='')

            if value:
                val_display = value[:40] + "..." if len(value) > 40 else value
                print(f" | Value: {val_display}", end='')

            if field_info['kids'] > 0:
                print(f" | Kids: {field_info['kids']}", end='')

            print()

        pdf.close()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    if len(sys.argv) < 2:
        print("Usage: python map_fields.py <pdf_file>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not Path(pdf_path).exists():
        print(f"Error: File not found - {pdf_path}")
        sys.exit(1)

    map_fields(pdf_path)


if __name__ == "__main__":
    main()
