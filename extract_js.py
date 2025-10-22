#!/usr/bin/env python3
import pikepdf
import sys

pdf = pikepdf.open(sys.argv[1])

if '/Names' in pdf.Root and '/JavaScript' in pdf.Root.Names:
    js_names = pdf.Root.Names.JavaScript.Names

    for i in range(0, len(js_names), 2):
        func_name = str(js_names[i])
        script_ref = js_names[i+1]

        # Dereference if needed
        script_obj = pdf.get_object(script_ref.objgen) if hasattr(script_ref, 'objgen') else script_ref

        # Read stream content
        if hasattr(script_obj, 'read_bytes'):
            js_code = bytes(script_obj.read_bytes()).decode('utf-8', errors='ignore')
            print(f'\n=== {func_name} ===\n')
            print(js_code)
            print('\n' + '='*80)

pdf.close()
