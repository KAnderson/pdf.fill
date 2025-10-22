# Web UI Guide - PDF Form Filler

## Overview

A beautiful, user-friendly web interface for all PDF form filling tools. No command line required!

## Features

✨ **Easy to Use**
- Drag & drop PDF upload
- Visual field explorer
- Interactive form builder
- One-click downloads

🔍 **Powerful Search**
- Search fields by label (e.g., "last name", "address")
- Filter by section (A, B, C, D)
- Live field filtering

📝 **Smart Templates**
- Generate JSON templates
- Load existing JSON files
- Export templates for reuse

🎯 **All Tools Included**
- Fill PDF forms
- Remove VOID watermark
- Clear default values
- Export field mappings

## Quick Start

### 1. Start the Server

```bash
cd /Users/kevin/Projects/pdf.fill
source venv/bin/activate
python app.py
```

### 2. Open in Browser

Navigate to: **http://localhost:5000**

### 3. Upload Your PDF

- Click or drag & drop your PDF file
- The app will analyze all form fields automatically

### 4. Explore Fields

**Tab 1: All Fields**
- View all 1,732 fields
- Filter by name or section
- Add fields to fill form with one click

**Tab 2: Search**
- Search by visible label: "last name", "address", "phone"
- Results show matching fields with descriptions

**Tab 3: Template**
- Generate JSON template for Section A, B, or all fields
- Copy template for your records

### 5. Fill Your Form

**Option A: Add Fields Manually**
1. Click "+ Add Field"
2. Enter field name and value
3. Click "Fill PDF"

**Option B: Load JSON File**
1. Click "📁 Load JSON"
2. Select your data file
3. Click "Fill PDF"

### 6. Download Result

- Click "⬇️ Download PDF"
- Your filled PDF is ready!

## Screenshots Walkthrough

### Upload Screen
```
┌─────────────────────────────────────────┐
│     📄 PDF Form Filler                  │
│     Upload, explore, and fill PDFs      │
├─────────────────────────────────────────┤
│  ┌───────────────────────────────────┐  │
│  │         📤                         │  │
│  │  Click to upload or drag and drop │  │
│  │  PDF files only, max 16MB         │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### Field Explorer
```
┌─────────────────────────────────────────┐
│  2. Explore Fields                      │
│  ┌───┬───────┬─────────┐                │
│  │📋 │  🔍   │   📝    │ (Tabs)         │
│  └───┴───────┴─────────┘                │
│  ┌─────────────────────────────────┐    │
│  │ Total fields: 1732              │    │
│  │ [Filter...] [Section ▼]        │    │
│  ├─────────────────────────────────┤    │
│  │ A05t                [+ Add]     │    │
│  │ Last name                       │    │
│  │ [text]                          │    │
│  ├─────────────────────────────────┤    │
│  │ A06t                [+ Add]     │    │
│  │ First name                      │    │
│  │ [text]                          │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### Fill Form
```
┌─────────────────────────────────────────┐
│  3. Fill PDF                            │
│  [+ Add] [📁 Load JSON] [🗑️ Clear]    │
│  ┌─────────────────────────────────┐    │
│  │ [A05t    ] [Doe          ] [×]  │    │
│  │ [A06t    ] [John         ] [×]  │    │
│  │ [A18ta   ] [123          ] [×]  │    │
│  │ [A18tb   ] [Main Street  ] [×]  │    │
│  └─────────────────────────────────┘    │
│  [        Fill PDF        ]             │
└─────────────────────────────────────────┘
```

## Common Workflows

### Workflow 1: First Time Use

```bash
1. Upload PDF
2. Click "Search" tab
3. Search for "last name" → Find A05t
4. Search for "address" → Find A18tb
5. Add fields to fill form
6. Enter values
7. Fill PDF
```

### Workflow 2: With JSON Template

```bash
1. Upload PDF
2. Click "+ Add Field" or "📁 Load JSON"
3. Load your JSON file:
   {
     "A05t": "Doe",
     "A06t": "John",
     "A18ta": "123",
     "A18tb": "Main Street"
   }
4. Click "Fill PDF"
```

### Workflow 3: Remove VOID Watermark

```bash
1. Upload PDF
2. Scroll to "4. Utilities"
3. Click "Remove VOID"
4. Download clean template
```

### Workflow 4: Export Template

```bash
1. Upload PDF
2. Go to "Template" tab
3. Select section (or all fields)
4. Click "Generate Template"
5. Copy JSON or click "💾 Export Template"
```

## API Endpoints

The web UI uses these REST API endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload` | POST | Upload PDF file |
| `/api/fields/<id>` | GET | Get all fields |
| `/api/search/<id>?q=term` | GET | Search fields |
| `/api/fill/<id>` | POST | Fill PDF with data |
| `/api/remove-defaults/<id>` | POST | Remove default values |
| `/api/template/<id>?section=A` | GET | Generate template |
| `/api/download/<id>` | GET | Download processed PDF |

## Integration with MaximOne Dashboard

### Embed as iFrame

```html
<iframe src="http://localhost:5000" width="100%" height="800px"></iframe>
```

### Call API from Your App

```javascript
// Node.js example
const FormData = require('form-data');
const form = new FormData();
form.append('file', fs.createReadStream('form.pdf'));

const response = await fetch('http://localhost:5000/api/upload', {
  method: 'POST',
  body: form
});

const { file_id } = await response.json();

// Fill the form
await fetch(`http://localhost:5000/api/fill/${file_id}`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    fields: {
      "A05t": "Doe",
      "A06t": "John"
    }
  })
});
```

## Configuration

Edit `app.py` to configure:

```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max file size
app.config['UPLOAD_FOLDER'] = '/your/upload/path'    # Upload directory
app.secret_key = 'your-secret-key'                    # Change in production
```

## Production Deployment

### Option 1: Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Option 2: Using Docker

```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

```bash
docker build -t pdf-filler .
docker run -p 5000:5000 pdf-filler
```

### Option 3: Behind Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        client_max_body_size 16M;
    }
}
```

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Or use different port
python app.py  # Edit app.py to change port
```

### Upload Fails

- Check file size (max 16MB)
- Ensure PDF is valid and not corrupted
- Check disk space in upload folder

### Fields Not Loading

- Check browser console for errors
- Verify PDF has AcroForm fields
- Try a different PDF to test

## Tips

1. **Use Search** - Much faster than scrolling through 1,732 fields
2. **Save Templates** - Export your field mappings for reuse
3. **Load JSON** - Prepare data files offline, upload when ready
4. **Section Filter** - Focus on one section at a time
5. **Remove VOID First** - Create a clean template before filling

## File Structure

```
pdf.fill/
├── app.py                 # Flask application
├── templates/
│   └── index.html        # Main UI template
├── static/
│   ├── css/
│   │   └── style.css     # Styles
│   └── js/
│       └── app.js        # Frontend JavaScript
├── venv/                  # Virtual environment
└── requirements.txt       # Python dependencies
```

## Security Notes

⚠️ **Important for Production:**

1. Change the `app.secret_key` in `app.py`
2. Add authentication/authorization
3. Implement rate limiting
4. Add HTTPS/SSL
5. Sanitize file uploads
6. Set up proper logging
7. Configure CORS if needed

## Support

- See [README.md](README.md) for command-line tools
- See [QUICK_START.md](QUICK_START.md) for field mapping guide
- See [REMOVING_VOID.md](REMOVING_VOID.md) for VOID watermark info

## Enjoy!

Your PDF form filling is now as easy as:
1. Upload
2. Fill
3. Download

No more command line! 🎉
