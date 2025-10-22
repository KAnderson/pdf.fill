# Field Mapping Guide for iA Financial Group Form

## Section A: Proposed Insured Identification

### Personal Information

| Visual Label | Field Name | Type | Description |
|-------------|------------|------|-------------|
| Last name | `A05t` | Text | Last name of insured |
| First name | `A06t` | Text | First name of insured |
| Middle name | `A07t` | Text | Middle name of insured |
| Name at birth | `A08t` | Text | Full name at birth (if changed) |

### Demographics

| Visual Label | Field Name | Type | Description |
|-------------|------------|------|-------------|
| Sex - M | `A09c` | Checkbox | Male |
| Sex - F | `A11c` | Checkbox | Female |
| Date of birth | `A12t` | Text | Format: YYYYMMDD |
| Language - English | `A10c` | Checkbox | English language |
| Language - French | `A15c` | Checkbox | French language |
| Social Insurance Number | `A16t` | Text | SIN (Optional) |
| Relationship to applicant | `A17t` | Text | Relationship |
| Age to save | `A13t` | Text | Age to save (if applicable) |

### Address (Section B on form)

| Visual Label | Field Name | Type | Description |
|-------------|------------|------|-------------|
| Civic number | `A18ta` | Text | House/building number |
| Street | `A18tb` | Text | Street name |
| Apartment/Office/Unit | `A18tc` | Text | Unit number |
| City | `A19t` | Text | City |
| Province | `A19ta` | Text | Province |
| Postal code | *See below* | Text | Postal code (check field list) |
| Station | `A21t` | Text | Station (Optional) |
| Rural route | *TBD* | Text | Rural route |
| P.O. Box | `A23t` | Text | P.O. Box |

### Contact Information

| Visual Label | Field Name | Type | Description |
|-------------|------------|------|-------------|
| Home phone | `A24t` | Text | Home phone number |
| Cell phone | `A25t` | Text | Cell phone number |
| Work phone | `A26t` | Text | Work phone number |
| Extension | `A27t` | Text | Phone extension |
| Email | `A28t` | Text | Email address |

### Identification Documents

| Visual Label | Field Name | Type | Description |
|-------------|------------|------|-------------|
| Type of document | `A29t` | Text | ID document type |
| Document number | `A30t` | Text | ID number |
| Place of issue | `A31t` | Text | Where issued |
| Expiry date | `A32t` | Text | Format: YYYYMMDD |

### Employment (for applicants)

| Visual Label | Field Name | Type | Description |
|-------------|------------|------|-------------|
| Main occupation | `A177t` | Text | Job title (be specific) |
| Name of employer | `A187t` | Text | Employer name |
| Business sector | `A197t` | Text | Business sector (for organizations) |

## Correct Sample Data

```json
{
  "A05t": "Doe",
  "A06t": "John",
  "A07t": "Michael",
  "A08t": "",
  "A09c": "Yes",
  "A11c": "Off",
  "A12t": "19850615",
  "A10c": "Yes",
  "A15c": "Off",
  "A16t": "",
  "A17t": "Self",
  "A18ta": "123",
  "A18tb": "Main Street",
  "A18tc": "Apt 4B",
  "A19t": "New York",
  "A19ta": "NY",
  "A24t": "555-1234",
  "A25t": "555-5678",
  "A26t": "",
  "A27t": "",
  "A28t": "john.doe@example.com"
}
```

## Field Naming Pattern

The form uses this pattern:
- **Letter** (A, B, C, etc.) = Section
- **Numbers** = Field number in section
- **Suffix**:
  - `t` = Text field
  - `c` = Checkbox
  - `ta`, `tb`, `tc` = Sub-fields (e.g., address parts)

## Common Mistakes

❌ **Wrong:**
```json
{
  "A04t": "John Doe",  // This is "Policy no.", not name!
  "A06t": "123 Main St",  // This is "First name", not address!
  "A07t": "Apt 4B"  // This is "Middle name", not apartment!
}
```

✓ **Correct:**
```json
{
  "A05t": "Doe",  // Last name
  "A06t": "John",  // First name
  "A07t": "",  // Middle name (if any)
  "A18tb": "Main Street",  // Street
  "A18tc": "Apt 4B"  // Apartment
}
```

## Notes

1. **Checkbox fields** accept: `"Yes"`, `"On"`, `true`, `1` for checked, or `"Off"`, `"No"`, `false`, `0` for unchecked
2. **Date fields** should be in `YYYYMMDD` format (e.g., `19850615` for June 15, 1985)
3. **Application number** (`H_Proposition`) shows "VOID" as default - this is set by the system
4. **Policy number** (`A04t`) is for internal use

## Finding More Fields

To find any field by its label:
```bash
python find_field_by_label.py "your_form.pdf" "search term"
```

Examples:
```bash
python find_field_by_label.py form.pdf "postal"
python find_field_by_label.py form.pdf "phone"
python find_field_by_label.py form.pdf "occupation"
```
