# Quick Start: Field Mapping and Filling

## The Problem You Had

Your test data was mapping to the wrong fields:
```json
{
  "A04t": "John Doe",      // ❌ This is "Policy no.", not name
  "A06t": "123 Main St",   // ❌ This is "First name", not address
  "A07t": "Apt 4B"         // ❌ This is "Middle name", not unit
}
```

## The Correct Mapping

```json
{
  "A05t": "Doe",           // ✓ Last name
  "A06t": "John",          // ✓ First name
  "A07t": "Michael",       // ✓ Middle name
  "A18ta": "123",          // ✓ Civic number
  "A18tb": "Main Street",  // ✓ Street
  "A18tc": "Apt 4B",       // ✓ Apartment/Office/Unit
  "A19t": "New York",      // ✓ City
  "A19ta": "NY"            // ✓ Province
}
```

## How to Find Field Names (3 Methods)

### Method 1: Search by Label (Recommended)

Find fields by their visible label on the form:

```bash
python find_field_by_label.py "form.pdf" "last name"
python find_field_by_label.py "form.pdf" "address"
python find_field_by_label.py "form.pdf" "phone"
```

**Example output:**
```
Field: A05t                           | Type: Text       | Page: 0
  → Last name

Field: A18tb                          | Type: Text       | Page: 0
  → Street
```

### Method 2: Generate Commented Template

Create a JSON template with all field descriptions:

```bash
# Generate template for Section A only
python generate_template.py "form.pdf" A section_a.json

# Generate template for multiple sections
python generate_template.py "form.pdf" A,B,C sections_abc.json

# Generate template for entire form
python generate_template.py "form.pdf" complete.json
```

**Output file looks like:**
```json
{
  "_instructions": "Fill in the values below. Remove this line when done.",
  "_note": "Checkboxes: use Yes/On/true for checked, Off/No/false for unchecked",

  "// A05t": "Last name (text)",
  "A05t": "",
  "// A06t": "First name (text)",
  "A06t": "",
  "// A18tb": "Street (text)",
  "A18tb": ""
}
```

### Method 3: List All Fields

See all fields with their types and tooltips:

```bash
python list_fields.py "form.pdf" > all_fields.txt
```

## Step-by-Step Workflow

### 1. Generate a Template for Your Section

```bash
source venv/bin/activate
python generate_template.py "ia financial group dev004391.pdf" A my_template.json
```

### 2. Edit the Template

Open `my_template.json` and fill in your data:

```json
{
  "A05t": "Smith",
  "A06t": "Jane",
  "A07t": "",
  "A08t": "",
  "A09c": "Off",
  "A11c": "Yes",
  "A12t": "19900315",
  "A10c": "Yes",
  "A18ta": "456",
  "A18tb": "Oak Avenue",
  "A18tc": "Suite 200",
  "A19t": "Boston",
  "A19ta": "MA",
  "A28t": "jane.smith@email.com"
}
```

### 3. Fill the PDF

```bash
python fill_pdf.py "ia financial group dev004391.pdf" "filled_form.pdf" my_template.json
```

### 4. Verify the Result

Open `filled_form.pdf` and check that all fields are correctly populated.

## Common Form Sections

### Section A: Proposed Insured

**Basic Info:**
- `A05t` - Last name
- `A06t` - First name
- `A07t` - Middle name
- `A08t` - Name at birth (if changed)

**Demographics:**
- `A09c` - Sex: Male
- `A11c` - Sex: Female
- `A12t` - Date of birth (YYYYMMDD)
- `A10c` - Language: English
- `A15c` - Language: French

**Address:**
- `A18ta` - Civic number
- `A18tb` - Street
- `A18tc` - Apartment/Office/Unit
- `A19t` - City
- `A19ta` - Province

**Contact:**
- `A24t` - Home phone
- `A25t` - Cell phone
- `A26t` - Work phone
- `A27t` - Extension
- `A28t` - Email

## Field Naming Convention

Understanding the pattern helps you guess field names:

```
A05t
│││└─ t = Text field (c = Checkbox, ta/tb/tc = Sub-fields)
││└── 05 = Field number in section
│└─── A = Section letter
```

**Common patterns:**
- `A##t` - Text fields
- `A##c` - Checkboxes
- `A##ta`, `A##tb`, `A##tc` - Multi-part fields (like addresses)

## Checkbox Values

Checkboxes accept multiple formats:

**To check:**
- `"Yes"`, `"YES"`, `"yes"`
- `"On"`, `"ON"`, `"on"`
- `true`
- `1` or `"1"`

**To uncheck:**
- `"Off"`, `"OFF"`, `"off"`
- `"No"`, `"NO"`, `"no"`
- `false`
- `0` or `"0"`

## Date Format

All date fields use `YYYYMMDD` format:
- June 15, 1985 → `"19850615"`
- March 3, 1990 → `"19900315"`
- December 31, 2000 → `"20001231"`

## Tips

1. **Start small** - Fill a few fields first to test your mapping
2. **Use search** - `find_field_by_label.py` is your best friend
3. **Check tooltips** - They show exactly what each field expects
4. **Save templates** - Keep your field mappings for reuse

## All Available Tools

| Tool | Purpose | Example |
|------|---------|---------|
| `find_field_by_label.py` | Search by visible label | `python find_field_by_label.py form.pdf "phone"` |
| `generate_template.py` | Create commented template | `python generate_template.py form.pdf A template.json` |
| `list_fields.py` | List all fields | `python list_fields.py form.pdf` |
| `fill_pdf.py` | Fill form from JSON | `python fill_pdf.py in.pdf out.pdf data.json` |
| `export_fields.py` | Export current values | `python export_fields.py form.pdf output.json` |
| `map_fields.py` | Detailed field mapping | `python map_fields.py form.pdf` |

## Need Help?

1. Check `FIELD_MAPPING.md` for detailed field reference
2. Use `find_field_by_label.py` to search for specific fields
3. Generate a template with `generate_template.py` to see all available fields
