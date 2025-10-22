#!/usr/bin/env python3
"""Extract ALL JavaScript from PDF"""
import pikepdf
import sys

pdf = pikepdf.open(sys.argv[1])

if '/Names' in pdf.Root and '/JavaScript' in pdf.Root.Names:
    js_names = pdf.Root.Names.JavaScript.Names

    for i in range(0, len(js_names), 2):
        func_name = str(js_names[i])
        script_ref = js_names[i+1]

        print(f'\n{"="*80}')
        print(f'FUNCTION: {func_name}')
        print("="*80)

        # Get /JS value
        js_value = script_ref.get('/JS')

        if js_value:
            # Check if it's a stream or string
            if hasattr(js_value, 'read_bytes'):
                # It's a stream - decompress it
                js_code = js_value.read_bytes().decode('utf-8', errors='ignore')
                print(js_code)
            elif isinstance(js_value, str):
                # It's already a string
                print(js_value)
            else:
                print(f"Unknown type: {type(js_value)}")
                print(js_value)

pdf.close()
