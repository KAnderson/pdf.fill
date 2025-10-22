#!/usr/bin/env python3
"""Check if PDF has XFA forms"""
import sys
import pikepdf

pdf_path = sys.argv[1]
pdf = pikepdf.open(pdf_path)

print(f"Analyzing: {pdf_path}\n")
print("="*80)

# Check for AcroForm
if '/AcroForm' in pdf.Root:
    print("✓ Has AcroForm")
    acroform = pdf.Root.AcroForm

    # Check for XFA
    if '/XFA' in acroform:
        print("✓ Has XFA (XML Forms Architecture)")
        print("\nThis is an XFA form!")
        print("\nXFA forms store data in XML format, not in traditional PDF fields.")
        print("They require special handling and may not show fields in the same way.")

        # Try to get XFA data
        xfa = acroform.XFA
        print(f"\nXFA type: {type(xfa)}")

        if isinstance(xfa, list):
            print(f"XFA has {len(xfa)} elements")
            for i in range(0, min(len(xfa), 10), 2):
                if i+1 < len(xfa):
                    print(f"  [{i}] {xfa[i]}")
    else:
        print("✗ No XFA")

    # Check for fields
    if '/Fields' in acroform:
        fields = acroform.Fields
        print(f"✓ Has {len(fields)} AcroForm fields")

        for i, field in enumerate(fields[:10]):
            if '/T' in field:
                name = str(field['/T'])
                ftype = str(field.get('/FT', 'unknown'))
                print(f"  Field {i+1}: {name} (type: {ftype})")

                # Check for kids
                if '/Kids' in field:
                    print(f"    - Has {len(field['/Kids'])} children")
    else:
        print("✗ No Fields in AcroForm")
else:
    print("✗ No AcroForm")

print("="*80)
pdf.close()
