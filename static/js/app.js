// Global state
let currentFileId = null;
let currentFields = [];
let fillFields = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

function setupEventListeners() {
    // Upload
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('pdf-upload');

    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--primary)';
    });
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = 'var(--gray-300)';
    });
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--gray-300)';
        if (e.dataTransfer.files.length) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFileUpload(e.target.files[0]);
        }
    });

    // Tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });

    // Search
    document.getElementById('search-btn').addEventListener('click', performSearch);
    document.getElementById('search-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });

    // Field filter
    document.getElementById('field-filter').addEventListener('input', filterFields);
    document.getElementById('section-filter').addEventListener('change', filterFields);

    // Template
    document.getElementById('generate-template-btn').addEventListener('click', generateTemplate);

    // Fill PDF
    document.getElementById('add-field-btn').addEventListener('click', addFillField);
    document.getElementById('load-json-btn').addEventListener('click', () => {
        document.getElementById('json-upload').click();
    });
    document.getElementById('json-upload').addEventListener('change', loadJSON);
    document.getElementById('clear-fields-btn').addEventListener('click', clearFillFields);
    document.getElementById('fill-pdf-btn').addEventListener('click', fillPDF);

    // Utilities
    document.getElementById('remove-void-btn').addEventListener('click', removeVoid);
    document.getElementById('clear-defaults-btn').addEventListener('click', clearDefaults);
    document.getElementById('export-template-btn').addEventListener('click', exportTemplate);

    // Results
    document.getElementById('start-over-btn').addEventListener('click', startOver);
}

async function handleFileUpload(file) {
    if (!file.name.endsWith('.pdf')) {
        showStatus('error', 'Please upload a PDF file');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    showStatus('info', 'Uploading PDF...');

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            currentFileId = data.file_id;
            showStatus('success', `Uploaded: ${data.filename}`);
            await loadFields();
            showTools();
        } else {
            showStatus('error', data.error);
        }
    } catch (error) {
        showStatus('error', 'Upload failed: ' + error.message);
    }
}

async function loadFields() {
    try {
        const response = await fetch(`/api/fields/${currentFileId}`);
        const data = await response.json();

        if (data.success) {
            currentFields = data.fields;
            displayFields(currentFields);
            updateFieldStats(data.count);
        } else {
            showStatus('error', data.error);
        }
    } catch (error) {
        showStatus('error', 'Failed to load fields: ' + error.message);
    }
}

function displayFields(fields) {
    const fieldList = document.getElementById('field-list');
    fieldList.innerHTML = '';

    fields.forEach(field => {
        const item = document.createElement('div');
        item.className = 'field-item';
        item.innerHTML = `
            <div class="field-info">
                <h4>${field.name}</h4>
                ${field.tooltip ? `<p>${field.tooltip}</p>` : ''}
                <span class="field-type ${field.type}">${field.type}</span>
            </div>
            <button class="btn btn-secondary" onclick="addToFillForm('${field.name}', '${field.type}')">+ Add</button>
        `;
        fieldList.appendChild(item);
    });
}

function filterFields() {
    const filterText = document.getElementById('field-filter').value.toLowerCase();
    const section = document.getElementById('section-filter').value;

    let filtered = currentFields;

    if (section) {
        filtered = filtered.filter(f => f.name.startsWith(section));
    }

    if (filterText) {
        filtered = filtered.filter(f =>
            f.name.toLowerCase().includes(filterText) ||
            f.tooltip.toLowerCase().includes(filterText)
        );
    }

    displayFields(filtered);
    updateFieldStats(filtered.length, currentFields.length);
}

function updateFieldStats(count, total = null) {
    const stats = document.getElementById('field-stats');
    if (total !== null) {
        stats.textContent = `Showing ${count} of ${total} fields`;
    } else {
        stats.textContent = `Total fields: ${count}`;
    }
}

async function performSearch() {
    const searchTerm = document.getElementById('search-input').value.trim();
    if (!searchTerm) return;

    const resultsDiv = document.getElementById('search-results');
    resultsDiv.innerHTML = '<p>Searching...</p>';

    try {
        const response = await fetch(`/api/search/${currentFileId}?q=${encodeURIComponent(searchTerm)}`);
        const data = await response.json();

        if (data.success) {
            if (data.count === 0) {
                resultsDiv.innerHTML = '<p>No fields found matching your search.</p>';
            } else {
                resultsDiv.innerHTML = '<div class="field-list"></div>';
                const fieldList = resultsDiv.querySelector('.field-list');

                data.results.forEach(field => {
                    const item = document.createElement('div');
                    item.className = 'field-item';
                    item.innerHTML = `
                        <div class="field-info">
                            <h4>${field.name}</h4>
                            ${field.tooltip ? `<p>${field.tooltip}</p>` : ''}
                            <span class="field-type ${field.type}">${field.type}</span>
                        </div>
                        <button class="btn btn-secondary" onclick="addToFillForm('${field.name}', '${field.type}')">+ Add</button>
                    `;
                    fieldList.appendChild(item);
                });
            }
        } else {
            resultsDiv.innerHTML = `<p class="error">${data.error}</p>`;
        }
    } catch (error) {
        resultsDiv.innerHTML = `<p class="error">Search failed: ${error.message}</p>`;
    }
}

async function generateTemplate() {
    const section = document.querySelector('input[name="template-section"]:checked').value;
    const output = document.getElementById('template-output');

    output.textContent = 'Generating template...';

    try {
        const url = `/api/template/${currentFileId}${section ? '?section=' + section : ''}`;
        const response = await fetch(url);
        const data = await response.json();

        if (data.success) {
            // Build JSON with descriptions as inline comments
            let jsonLines = ['{\n'];
            const fields = data.template;

            fields.forEach((field, index) => {
                const isLast = index === fields.length - 1;
                const description = field.description ? ` // ${field.description}` : '';
                const fieldValue = JSON.stringify(field.value);

                jsonLines.push(`  "${field.name}": ${fieldValue}${isLast ? '' : ','}${description}\n`);
            });

            jsonLines.push('}');
            output.textContent = jsonLines.join('');
        } else {
            output.textContent = `Error: ${data.error}`;
        }
    } catch (error) {
        output.textContent = `Error: ${error.message}`;
    }
}

function addToFillForm(fieldName, fieldType) {
    addFillField(fieldName, fieldType, '');
}

function addFillField(fieldName = '', fieldType = 'text', value = '') {
    const form = document.getElementById('fill-form');
    const fieldId = `field-${Date.now()}`;

    const fieldDiv = document.createElement('div');
    fieldDiv.className = 'form-field';
    fieldDiv.dataset.fieldId = fieldId;

    if (fieldType === 'checkbox') {
        fieldDiv.innerHTML = `
            <input type="text" placeholder="Field name" value="${fieldName}" data-field-name>
            <label><input type="checkbox" ${value === 'Yes' ? 'checked' : ''}> Checked</label>
            <button onclick="removeField('${fieldId}')">✕</button>
        `;
    } else {
        fieldDiv.innerHTML = `
            <input type="text" placeholder="Field name" value="${fieldName}" data-field-name>
            <input type="text" placeholder="Value" value="${value}" data-field-value>
            <button onclick="removeField('${fieldId}')">✕</button>
        `;
    }

    form.appendChild(fieldDiv);
    document.getElementById('fill-pdf-btn').disabled = false;
}

function removeField(fieldId) {
    const field = document.querySelector(`[data-field-id="${fieldId}"]`);
    if (field) field.remove();

    const form = document.getElementById('fill-form');
    if (form.children.length === 0) {
        document.getElementById('fill-pdf-btn').disabled = true;
    }
}

function loadJSON(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
        try {
            const data = JSON.parse(event.target.result);
            clearFillFields();

            Object.entries(data).forEach(([key, value]) => {
                if (!key.startsWith('_')) {
                    const field = currentFields.find(f => f.name === key);
                    const fieldType = field ? field.type : 'text';
                    addFillField(key, fieldType, value);
                }
            });
        } catch (error) {
            alert('Invalid JSON file: ' + error.message);
        }
    };
    reader.readAsText(file);
}

function clearFillFields() {
    document.getElementById('fill-form').innerHTML = '';
    document.getElementById('fill-pdf-btn').disabled = true;
}

async function fillPDF() {
    const form = document.getElementById('fill-form');
    const fields = {};

    form.querySelectorAll('.form-field').forEach(fieldDiv => {
        const nameInput = fieldDiv.querySelector('[data-field-name]');
        const checkbox = fieldDiv.querySelector('input[type="checkbox"]');

        if (nameInput && nameInput.value) {
            if (checkbox) {
                fields[nameInput.value] = checkbox.checked ? 'Yes' : 'Off';
            } else {
                const valueInput = fieldDiv.querySelector('[data-field-value]');
                if (valueInput) {
                    fields[nameInput.value] = valueInput.value;
                }
            }
        }
    });

    const btn = document.getElementById('fill-pdf-btn');
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Filling PDF...';

    try {
        const response = await fetch(`/api/fill/${currentFileId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fields })
        });

        const data = await response.json();

        if (data.success) {
            showResults(data.message, data.output_id);
        } else {
            alert('Error: ' + data.error);
            btn.disabled = false;
            btn.textContent = 'Fill PDF';
        }
    } catch (error) {
        alert('Failed to fill PDF: ' + error.message);
        btn.disabled = false;
        btn.textContent = 'Fill PDF';
    }
}

async function removeVoid() {
    try {
        const response = await fetch(`/api/remove-void/${currentFileId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            showResults(data.message, data.output_id);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Failed: ' + error.message);
    }
}

async function clearDefaults() {
    if (!confirm('This will remove ALL default values from the PDF. Continue?')) {
        return;
    }
    await removeDefaults(null, 'Cleared all default values');
}

async function removeDefaults(fields, successMessage) {
    try {
        const response = await fetch(`/api/remove-defaults/${currentFileId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fields })
        });

        const data = await response.json();

        if (data.success) {
            showResults(successMessage, data.output_id);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Failed: ' + error.message);
    }
}

async function exportTemplate() {
    try {
        const response = await fetch(`/api/template/${currentFileId}`);
        const data = await response.json();

        if (data.success) {
            // Build JSON with descriptions as inline comments
            let jsonLines = ['{\n'];
            const fields = data.template;

            fields.forEach((field, index) => {
                const isLast = index === fields.length - 1;
                const description = field.description ? ` // ${field.description}` : '';
                const fieldValue = JSON.stringify(field.value);

                jsonLines.push(`  "${field.name}": ${fieldValue}${isLast ? '' : ','}${description}\n`);
            });

            jsonLines.push('}');
            const jsonString = jsonLines.join('');

            const blob = new Blob([jsonString], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'template.json';
            a.click();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Failed to export: ' + error.message);
    }
}

function showResults(message, outputId) {
    document.getElementById('tools-section').classList.add('hidden');
    document.getElementById('results-section').classList.remove('hidden');
    document.getElementById('result-message').textContent = message;

    const downloadBtn = document.getElementById('download-btn');
    downloadBtn.onclick = () => window.location.href = `/api/download/${outputId}`;
}

function startOver() {
    location.reload();
}

function showTools() {
    document.getElementById('upload-section').style.opacity = '0.6';
    document.getElementById('tools-section').classList.remove('hidden');
}

function showStatus(type, message) {
    const status = document.getElementById('upload-status');
    status.className = `status ${type}`;
    status.textContent = message;
    status.classList.remove('hidden');
}

function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });

    // Update tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });
}
