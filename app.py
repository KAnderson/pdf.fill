#!/usr/bin/env python3
"""
PDF Form Filler - Web UI
A Flask-based web interface for all PDF form filling tools
"""

from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
import os
import json
import tempfile
import pikepdf
from pathlib import Path
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_form_fields(pdf_path):
    """Extract all form fields from a PDF (including children)"""
    try:
        pdf = pikepdf.open(pdf_path)

        if '/AcroForm' not in pdf.Root or '/Fields' not in pdf.Root.AcroForm:
            return None

        fields = []

        def extract_field_info(field, parent_name=''):
            """Recursively extract field information"""
            field_info = {
                'name': '',
                'type': '',
                'tooltip': '',
                'value': ''
            }

            # Get field name
            if '/T' in field:
                field_name = str(field['/T'])
                field_info['name'] = f"{parent_name}.{field_name}" if parent_name else field_name
            elif parent_name:
                # Child widget without its own name
                return None

            # Get tooltip
            if '/TU' in field:
                field_info['tooltip'] = str(field['/TU'])

            # Get field type
            if '/FT' in field:
                ft = str(field['/FT'])
                type_map = {'/Tx': 'text', '/Btn': 'checkbox', '/Ch': 'choice', '/Sig': 'signature'}
                field_info['type'] = type_map.get(ft, 'unknown')

            # Get value
            if '/V' in field:
                val = field['/V']
                if isinstance(val, pikepdf.Name):
                    field_info['value'] = str(val).lstrip('/')
                else:
                    field_info['value'] = str(val)

            # Check if this field has children
            has_children = '/Kids' in field and len(field['/Kids']) > 0

            # If field has /FT, it's a terminal field - add it
            if '/FT' in field:
                fields.append(field_info)

            # Recursively process children
            if has_children:
                for kid in field['/Kids']:
                    try:
                        child_info = extract_field_info(kid, field_info['name'])
                        if child_info:
                            fields.append(child_info)
                    except:
                        pass

        # Process all top-level fields
        for field in pdf.Root.AcroForm.Fields:
            try:
                extract_field_info(field)
            except Exception as e:
                print(f"Error processing field: {e}")

        pdf.close()
        return fields

    except Exception as e:
        print(f"Error: {e}")
        return None


def search_fields(pdf_path, search_term):
    """Search for fields by name or tooltip"""
    fields = get_form_fields(pdf_path)
    if not fields:
        return []

    search_lower = search_term.lower()
    results = []

    for field in fields:
        if (search_lower in field['name'].lower() or
            search_lower in field['tooltip'].lower()):
            results.append(field)

    return results


def fill_pdf(input_pdf, output_pdf, field_data):
    """Fill PDF form fields"""
    try:
        pdf = pikepdf.open(input_pdf)

        if '/AcroForm' not in pdf.Root or '/Fields' not in pdf.Root.AcroForm:
            return False, "No form fields found"

        filled_count = 0
        fields = pdf.Root.AcroForm.Fields

        for field in fields:
            if '/T' not in field:
                continue

            field_name = str(field['/T'])

            if field_name in field_data:
                value = field_data[field_name]

                # Determine field type
                field_type = None
                if '/FT' in field:
                    field_type = str(field['/FT'])
                elif '/Kids' in field and len(field['/Kids']) > 0:
                    try:
                        first_kid = field['/Kids'][0]
                        if '/FT' in first_kid:
                            field_type = str(first_kid['/FT'])
                    except:
                        pass

                # Fill based on field type
                try:
                    if field_type == '/Btn':
                        if value in [True, 'Yes', 'yes', 'ON', 'On', 1, '1']:
                            field['/V'] = pikepdf.Name('/Yes')
                            field['/AS'] = pikepdf.Name('/Yes')
                        else:
                            field['/V'] = pikepdf.Name('/Off')
                            field['/AS'] = pikepdf.Name('/Off')
                    else:
                        field['/V'] = str(value)

                    filled_count += 1
                except Exception as e:
                    print(f"Error filling {field_name}: {e}")

        pdf.save(output_pdf)
        pdf.close()

        return True, f"Filled {filled_count} fields"

    except Exception as e:
        return False, str(e)


def remove_defaults(input_pdf, output_pdf, fields_to_clear=None):
    """Remove default values from fields"""
    try:
        pdf = pikepdf.open(input_pdf)

        if '/AcroForm' not in pdf.Root or '/Fields' not in pdf.Root.AcroForm:
            return False, "No form fields found"

        cleared_count = 0
        fields = pdf.Root.AcroForm.Fields

        for field in fields:
            if '/T' not in field:
                continue

            field_name = str(field['/T'])

            should_clear = False
            if fields_to_clear is None:
                should_clear = '/V' in field
            else:
                should_clear = field_name in fields_to_clear and '/V' in field

            if should_clear:
                try:
                    del field['/V']
                    if '/AP' in field:
                        del field['/AP']
                    cleared_count += 1
                except:
                    pass

        pdf.save(output_pdf)
        pdf.close()

        return True, f"Cleared {cleared_count} fields"

    except Exception as e:
        return False, str(e)


def remove_void_watermark(input_pdf, output_pdf):
    """Remove VOID watermark by hiding btnVoid field and clearing appearance streams"""
    try:
        pdf = pikepdf.open(input_pdf)

        if '/AcroForm' not in pdf.Root or '/Fields' not in pdf.Root.AcroForm:
            return False, "No form fields found"

        fields = pdf.Root.AcroForm.Fields
        found_btnvoid = False
        found_h_prop = False

        for field in fields:
            if '/T' not in field:
                continue

            field_name = str(field['/T'])

            # Hide the btnVoid button (the VOID watermark)
            if field_name == 'btnVoid':
                found_btnvoid = True

                # Set field flags to make it hidden (bit 1 = hidden)
                current_flags = int(field.get('/Ff', 0))
                new_flags = current_flags | 2
                field['/Ff'] = new_flags

                # Clear caption and appearance streams
                if '/Kids' in field:
                    for kid in field['/Kids']:
                        if '/MK' in kid:
                            kid['/MK']['/CA'] = ''
                        if '/AP' in kid:
                            del kid['/AP']

                # Remove parent field appearance
                if '/AP' in field:
                    del field['/AP']

            # Clear H_Proposition field
            if field_name == 'H_Proposition':
                found_h_prop = True

                # Remove ReadOnly flag
                if '/Ff' in field:
                    current_flags = int(field['/Ff'])
                    new_flags = current_flags & ~1
                    field['/Ff'] = new_flags

                # Set to empty
                field['/V'] = ''
                field['/DV'] = ''

                if '/Kids' in field:
                    for kid in field['/Kids']:
                        kid['/V'] = ''
                        if '/AP' in kid:
                            del kid['/AP']

        if found_btnvoid or found_h_prop:
            pdf.Root.AcroForm['/NeedAppearances'] = True
            pdf.save(output_pdf)
            pdf.close()

            result_msg = "VOID watermark removed successfully!"
            if found_btnvoid:
                result_msg += " (btnVoid field hidden)"
            if found_h_prop:
                result_msg += " (H_Proposition cleared)"

            return True, result_msg
        else:
            pdf.close()
            return False, "btnVoid or H_Proposition field not found"

    except Exception as e:
        return False, str(e)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    """Upload a PDF file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF files are allowed'}), 400

    # Save file with unique name
    file_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
    file.save(filepath)

    # Store file info in session
    session[file_id] = filepath

    return jsonify({
        'success': True,
        'file_id': file_id,
        'filename': filename
    })


@app.route('/api/fields/<file_id>')
def get_fields(file_id):
    """Get all fields from a PDF"""
    filepath = session.get(file_id)
    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404

    fields = get_form_fields(filepath)
    if fields is None:
        return jsonify({'error': 'No form fields found'}), 400

    return jsonify({
        'success': True,
        'count': len(fields),
        'fields': fields
    })


@app.route('/api/search/<file_id>')
def search_fields_api(file_id):
    """Search for fields"""
    filepath = session.get(file_id)
    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404

    search_term = request.args.get('q', '')
    if not search_term:
        return jsonify({'error': 'Search term required'}), 400

    results = search_fields(filepath, search_term)

    return jsonify({
        'success': True,
        'count': len(results),
        'results': results
    })


@app.route('/api/fill/<file_id>', methods=['POST'])
def fill_pdf_api(file_id):
    """Fill PDF with data"""
    filepath = session.get(file_id)
    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404

    data = request.json
    if not data or 'fields' not in data:
        return jsonify({'error': 'Field data required'}), 400

    # Create output file
    output_id = str(uuid.uuid4())
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{output_id}_filled.pdf")

    success, message = fill_pdf(filepath, output_path, data['fields'])

    if not success:
        return jsonify({'error': message}), 400

    session[output_id] = output_path

    return jsonify({
        'success': True,
        'message': message,
        'output_id': output_id
    })


@app.route('/api/remove-defaults/<file_id>', methods=['POST'])
def remove_defaults_api(file_id):
    """Remove default values"""
    filepath = session.get(file_id)
    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404

    data = request.json or {}
    fields_to_clear = data.get('fields')

    # Create output file
    output_id = str(uuid.uuid4())
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{output_id}_clean.pdf")

    success, message = remove_defaults(filepath, output_path, fields_to_clear)

    if not success:
        return jsonify({'error': message}), 400

    session[output_id] = output_path

    return jsonify({
        'success': True,
        'message': message,
        'output_id': output_id
    })


@app.route('/api/download/<file_id>')
def download_file(file_id):
    """Download a processed PDF"""
    filepath = session.get(file_id)
    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404

    return send_file(filepath, as_attachment=True, download_name=f"output_{file_id}.pdf")


@app.route('/api/template/<file_id>')
def generate_template_api(file_id):
    """Generate JSON template"""
    filepath = session.get(file_id)
    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404

    section = request.args.get('section', '').upper()

    fields = get_form_fields(filepath)
    if not fields:
        return jsonify({'error': 'No form fields found'}), 400

    # Filter by section if specified
    if section:
        fields = [f for f in fields if f['name'].startswith(section)]

    # Create template
    template = {}
    for field in fields:
        template[field['name']] = {
            'value': '' if field['type'] != 'checkbox' else 'Off',
            'type': field['type'],
            'description': field['tooltip']
        }

    return jsonify({
        'success': True,
        'template': template,
        'count': len(template)
    })


@app.route('/api/remove-void/<file_id>', methods=['POST'])
def remove_void_api(file_id):
    """Remove VOID watermark from PDF"""
    filepath = session.get(file_id)
    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404

    # Create output file
    output_id = str(uuid.uuid4())
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{output_id}_no_void.pdf")

    success, message = remove_void_watermark(filepath, output_path)

    if not success:
        return jsonify({'error': message}), 400

    session[output_id] = output_path

    return jsonify({
        'success': True,
        'message': message,
        'output_id': output_id
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
