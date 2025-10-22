#!/usr/bin/env python3
"""
PDF Form Type Detector
Identifies whether a PDF uses XFA (XML Forms Architecture) or AcroForm (traditional PDF forms)
"""

import sys
import PyPDF2
from pathlib import Path


def detect_form_type(pdf_path):
    """
    Analyze a PDF file to determine if it uses XFA or AcroForm.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        dict with keys:
            - form_type: "XFA", "AcroForm", "Both", or "None"
            - has_acroform: boolean
            - has_xfa: boolean
            - details: additional information
    """
    result = {
        "form_type": "None",
        "has_acroform": False,
        "has_xfa": False,
        "details": {}
    }

    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)

            # Store basic PDF info
            result["details"]["page_count"] = len(reader.pages)
            result["details"]["is_encrypted"] = reader.is_encrypted

            # Check the catalog for form information
            if '/AcroForm' in reader.trailer['/Root']:
                acroform = reader.trailer['/Root']['/AcroForm']

                # Check for XFA
                if '/XFA' in acroform:
                    result["has_xfa"] = True
                    result["details"]["xfa_present"] = True

                # Check for Fields (traditional AcroForm)
                if '/Fields' in acroform:
                    result["has_acroform"] = True
                    fields = acroform['/Fields']
                    result["details"]["field_count"] = len(fields)

                # Determine the form type
                if result["has_xfa"] and result["has_acroform"]:
                    result["form_type"] = "Both (Hybrid)"
                elif result["has_xfa"]:
                    result["form_type"] = "XFA"
                elif result["has_acroform"]:
                    result["form_type"] = "AcroForm"
                else:
                    result["form_type"] = "AcroForm structure (empty)"

            else:
                result["details"]["message"] = "No /AcroForm in catalog"

            # Check for annotations on pages (which might include form widgets)
            annotation_count = 0
            widget_annotations = 0
            annotation_types = set()

            for page_num, page in enumerate(reader.pages):
                if '/Annots' in page:
                    annots = page['/Annots']
                    annotation_count += len(annots)

                    for annot in annots:
                        annot_obj = annot.get_object()
                        if '/Subtype' in annot_obj:
                            subtype = annot_obj['/Subtype']
                            annotation_types.add(str(subtype))
                            if subtype == '/Widget':
                                widget_annotations += 1

            if annotation_count > 0:
                result["details"]["annotation_count"] = annotation_count
                result["details"]["widget_annotations"] = widget_annotations
                result["details"]["annotation_types"] = list(annotation_types)

            # Check if there are widget annotations but no AcroForm
            if widget_annotations > 0 and not result["has_acroform"]:
                result["details"]["warning"] = "Found widget annotations but no AcroForm definition"

    except Exception as e:
        result["details"]["error"] = str(e)

    return result


def format_result(result, pdf_path):
    """Format the detection result for display"""
    output = []
    output.append(f"\n{'='*60}")
    output.append(f"PDF Form Analysis: {Path(pdf_path).name}")
    output.append(f"{'='*60}")
    output.append(f"\nForm Type: {result['form_type']}")
    output.append(f"Has AcroForm: {result['has_acroform']}")
    output.append(f"Has XFA: {result['has_xfa']}")

    if result['details']:
        output.append(f"\nDetails:")
        for key, value in result['details'].items():
            output.append(f"  - {key}: {value}")

    output.append(f"{'='*60}\n")
    return '\n'.join(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: python pdf_form_detector.py <pdf_file>")
        print("\nExample:")
        print("  python pdf_form_detector.py sample.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not Path(pdf_path).exists():
        print(f"Error: File not found - {pdf_path}")
        sys.exit(1)

    if not pdf_path.lower().endswith('.pdf'):
        print(f"Warning: File may not be a PDF - {pdf_path}")

    print(f"Analyzing PDF: {pdf_path}")
    result = detect_form_type(pdf_path)
    print(format_result(result, pdf_path))

    # Summary
    if result['form_type'] == "XFA":
        print("ℹ️  This PDF uses XFA forms (XML Forms Architecture)")
        print("   XFA forms are dynamic and may require special handling.")
    elif result['form_type'] == "AcroForm":
        print("ℹ️  This PDF uses traditional AcroForm fields")
        print("   These are standard PDF form fields.")
    elif result['form_type'] == "Both (Hybrid)":
        print("ℹ️  This PDF contains both XFA and AcroForm data")
        print("   This is a hybrid form that supports both formats.")
    else:
        print("ℹ️  No standard form fields detected in this PDF")

        # Provide suggestions if no forms found
        if result['details'].get('annotation_count', 0) > 0:
            print("\n   However, annotations were found:")
            print(f"   - Total annotations: {result['details']['annotation_count']}")
            if result['details'].get('annotation_types'):
                print(f"   - Types: {', '.join(result['details']['annotation_types'])}")
            print("\n   This PDF might:")
            print("   • Have fillable fields created as annotations (not standard forms)")
            print("   • Be a scanned document with field overlays")
            print("   • Have interactive elements that aren't traditional form fields")
            print("\n   Try using PDF editing software like Adobe Acrobat to:")
            print("   • Check if fields can be detected/edited")
            print("   • Run OCR if it's a scanned document")
            print("   • Convert annotations to form fields if needed")
        else:
            print("\n   This PDF appears to have no interactive fields.")
            print("   It might be:")
            print("   • A static document (scanned or printed PDF)")
            print("   • A form that needs to be filled manually or with OCR")
            print("   • A document where fields need to be added")


if __name__ == "__main__":
    main()
