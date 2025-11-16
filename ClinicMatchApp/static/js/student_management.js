document.getElementById('student-xlsx-input').addEventListener('change', function(event) {
    const file = event.target.files[0];
    const majorsListDiv = document.getElementById('major-mapping');
    const loadButton = document.getElementById('load-students-button');

    // clear previous UI
    majorsListDiv.innerHTML = '';
    if (!file) {
        loadButton.disabled = true;
        loadButton.classList.add('hidden');
        majorsListDiv.classList.add('hidden');
        return;
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });
        const sheetNames = workbook.SheetNames || [];

        // safe access of sheets
        const juniorData = sheetNames[0]
            ? XLSX.utils.sheet_to_json(workbook.Sheets[sheetNames[0]], { header: 1 })
            : [];
        const seniorData = sheetNames[1]
            ? XLSX.utils.sheet_to_json(workbook.Sheets[sheetNames[1]], { header: 1 })
            : [];

        const juniorMajors = pullMajorsFromSheet(juniorData);
        const seniorMajors = pullMajorsFromSheet(seniorData);

        const allMajors = Array.from(new Set([...juniorMajors, ...seniorMajors])).sort();
        console.log("All Majors:", allMajors);

        const databaseMajors = pullMajorsFromHTML();
        console.log("Majors from DB:", databaseMajors);

        if (!allMajors.length) {
            majorsListDiv.classList.add('hidden');
            return;
        }

        majorsListDiv.classList.remove('hidden');
        loadButton.disabled = false;
        loadButton.classList.remove('hidden');

        allMajors.forEach(major => {
            const wrapper = document.createElement('div');
            wrapper.className = 'major-mapping-row';

            const label = document.createElement('label');
            label.textContent = major + ': ';
            label.htmlFor = `map-${major}`;

            const select = document.createElement('select');
            select.id = `map-${major}`;
            select.name = `map-${major}`;

            databaseMajors.forEach(dbMajor => {
                const option = document.createElement('option');
                option.value = dbMajor;
                option.textContent = dbMajor;
                select.appendChild(option);
            });

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `alt-${major}`;
            checkbox.name = `alt-${major}`;

            const checkboxLabel = document.createElement('label');
            checkboxLabel.htmlFor = `alt-${major}`;
            checkboxLabel.textContent = ' (EET/MET)';

            wrapper.appendChild(label);
            wrapper.appendChild(select);
            wrapper.appendChild(checkbox);
            wrapper.appendChild(checkboxLabel);
            majorsListDiv.appendChild(wrapper);
        });
    };

    reader.readAsArrayBuffer(file);
});

function pullMajorsFromSheet(sheetData) {
    const majors = new Set();
    if (!Array.isArray(sheetData)) return []; // make sure sheet exists
    for (let i = 15; i < sheetData.length; i++) {
        const row = sheetData[i] || [];
        const major = row[4];
        if (major && String(major).trim() !== '') {
            majors.add(String(major).trim());
        }
    }
    return Array.from(majors);
}

function pullMajorsFromHTML() {
    const majorsDiv = document.getElementById('major-mapping');
    if (!majorsDiv) return [];
    const raw = majorsDiv.dataset.majors || '';
    return raw.split(',').map(s => s.trim()).filter(Boolean);
}

function collectMajorMappings() {
    const majorsDiv = document.getElementById('major-mapping');
    const selects = majorsDiv.querySelectorAll('select');
    const mappings = {};
    selects.forEach(select => {
        const major = select.id.replace('map-', '');
        const mappedValue = select.value;
        const isAlt = document.getElementById(`alt-${major}`).checked;
        mappings[major] = {
            mappedTo: mappedValue,
            isAlt: isAlt
        };
    });
    return mappings;
}

document.getElementById('load-students-button').addEventListener('click', function() {
    const fileInput = document.getElementById('student-xlsx-input');
    const file = fileInput.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });
        const sheetNames = workbook.SheetNames || [];

        const juniorData = sheetNames[0]
            ? XLSX.utils.sheet_to_json(workbook.Sheets[sheetNames[0]], { header: 1 })
            : [];
        const seniorData = sheetNames[1]
            ? XLSX.utils.sheet_to_json(workbook.Sheets[sheetNames[1]], { header: 1 })
            : [];

        const majorMappings = collectMajorMappings();

        const studentsToImport = [];

        [juniorData, seniorData].forEach((sheetData, sheetIndex) => {
            const isSenior = sheetIndex === 1;
            for (let i = 15; i < sheetData.length; i++) {
                const row = sheetData[i] || [];
                const name = row[1] ? String(row[1]).trim() : '';
                const firstName = name.split(',')[1] ? name.split(',')[1].trim() : '';
                const lastName = name.split(',')[0] ? name.split(',')[0].trim() : '';
                const bannerId = row[2] ? String(row[2]).trim() : '';
                const email = row[7] ? String(row[7]).trim() : '';
                const majorRaw = row[4] ? String(row[4]).trim() : '';
                //if (!firstName || !lastName || ~bannerId || !email || !majorRaw) continue;

                const mapping = majorMappings[majorRaw];
                if (!mapping) continue;

                studentsToImport.push({
                    "first_name": firstName,
                    "last_name": lastName,
                    "email": email,
                    "banner_id": bannerId,
                    "j_or_s": isSenior ? 'S' : 'J',
                    "major": mapping.mappedTo,
                    "alternative_major": mapping.isAlt,
                });
            }
        });

        console.log("Students to Import:", studentsToImport);

        fetch('/importStudents/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(studentsToImport)
        })
        .then(async response => {
            const text = await response.text()
            let body = text;
            try {
                body = JSON.parse(text);
            } catch (e) {
                console.error("Failed to parse response as JSON:", e);
            }
            console.log('importStudents response', response.status, body);
            if (response.ok) {
                alert('Students imported successfully!');
            } else {
                alert('Error importing students.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error importing students.');
        });
    };

    reader.readAsArrayBuffer(file);
});

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}