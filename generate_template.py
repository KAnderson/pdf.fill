#!/usr/bin/env python3
"""
Generate a commented JSON template with field descriptions
"""

import sys
import json
from pathlib import Path
import pikepdf


def generate_template(pdf_path, output_file=None, sections=None):
    """
    Generate a JSON template with comments showing field descriptions

    Args:
        pdf_path: Path to PDF file
        output_file: Output JSON file (optional)
        sections: List of section prefixes to include (e.g., ['A', 'B'])
    """

    try:
        pdf = pikepdf.open(pdf_path)

        if '/AcroForm' not in pdf.Root or '/Fields' not in pdf.Root.AcroForm:
            print("✗ No form fields found")
            return

        fields = pdf.Root.AcroForm.Fields
        field_map = {}

        for field in fields:
            if '/T' not in field:
                continue

            field_name = str(field['/T'])

            # Filter by sections if specified
            if sections:
                if not any(field_name.startswith(s) for s in sections):
                    continue

            # Get tooltip
            tooltip = ""
            if '/TU' in field:
                tooltip = str(field['/TU'])

            # Get field type
            field_type = "text"
            if '/FT' in field:
                ft = str(field['/FT'])
                if ft == '/Btn':
                    field_type = "checkbox"
                elif ft == '/Ch':
                    field_type = "choice"
            elif '/Kids' in field and len(field['/Kids']) > 0:
                try:
                    first_kid = field['/Kids'][0]
                    if '/FT' in first_kid:
                        ft = str(first_kid['/FT'])
                        if ft == '/Btn':
                            field_type = "checkbox"
                        elif ft == '/Ch':
                            field_type = "choice"
                except:
                    pass

            field_map[field_name] = {
                "value": "" if field_type != "checkbox" else "Off",
                "description": tooltip,
                "type": field_type
            }

        pdf.close()

        # Determine output file
        if output_file is None:
            pdf_name = Path(pdf_path).stem
            section_str = "_".join(sections) if sections else "all"
            output_file = f"{pdf_name}_template_{section_str}.json"

        # Write JSON with nice formatting
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("{\n")
            f.write('  "_instructions": "Fill in the values below. Remove this line when done.",\n')
            f.write('  "_note": "Checkboxes: use Yes/On/true for checked, Off/No/false for unchecked",\n')
            f.write('  "_dates": "Use YYYYMMDD format for dates (e.g., 19850615)",\n\n')

            items = list(field_map.items())
            for i, (fname, finfo) in enumerate(items):
                is_last = (i == len(items) - 1)

                # Write comment
                if finfo['description']:
                    f.write(f'  "// {fname}": "{finfo["description"]} ({finfo["type"]})",\n')

                # Write field
                value = finfo['value']
                if isinstance(value, str):
                    value = json.dumps(value, ensure_ascii=False)
                else:
                    value = json.dumps(value)

                comma = "" if is_last else ","
                f.write(f'  "{fname}": {value}{comma}\n')

                # Add spacing between sections
                if i < len(items) - 1:
                    current_prefix = fname[0]
                    next_prefix = items[i + 1][0][0]
                    if current_prefix != next_prefix:
                        f.write('\n')

            f.write("}\n")

        print(f"✓ Generated template: {output_file}")
        print(f"  Fields included: {len(field_map)}")

        return field_map

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_template.py <pdf_file> [sections] [output.json]")
        print("\nExamples:")
        print("  python generate_template.py form.pdf")
        print("  python generate_template.py form.pdf A")
        print("  python generate_template.py form.pdf A,B")
        print("  python generate_template.py form.pdf A my_template.json")
        sys.exit(1)

    pdf_path = sys.argv[1]

    # Parse sections
    sections = None
    output_file = None

    if len(sys.argv) > 2:
        arg2 = sys.argv[2]
        if ',' in arg2 or (len(arg2) <= 3 and arg2.isalpha()):
            # It's sections
            sections = arg2.split(',')
            if len(sys.argv) > 3:
                output_file = sys.argv[3]
        else:
            # It's output file
            output_file = arg2

    if not Path(pdf_path).exists():
        print(f"Error: File not found - {pdf_path}")
        sys.exit(1)

    generate_template(pdf_path, output_file, sections)


if __name__ == "__main__":
    main()
