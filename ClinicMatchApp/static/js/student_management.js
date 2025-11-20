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
        document.getElementById('statistics').classList.add('hidden');

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
                document.getElementById('cross-reference').classList.add('hidden');
                document.getElementById('statistics').classList.remove('hidden');
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

const algorithmButton = document.getElementById('run-algorithm-button');
algorithmButton.addEventListener('click', function() {
    fetch('/MatchingProcess/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(async response => {
        const text = await response.text()
        let body = text;
        try {
            body = JSON.parse(text);
        } catch (e) {
            console.error("Failed to parse response as JSON:", e);
        }
        console.log('runMatchingAlgorithm response', response.status, body);
        if (response.ok) {
            alert('Matching algorithm executed successfully!');
        } else {
            alert('Error executing matching algorithm.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error executing matching algorithm.');
    });
});

const statsButton = document.getElementById('view-statistics-button');
statsButton.addEventListener('click', function() {
    fetch('/api/statistics/mostPopularClinics/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(async response => {
        const text = await response.text();
        //console.log('mostPopularClinics response', response.status, text);
        let data;
        try {
            data = JSON.parse(text);
            console.log("Parsed clinic data:", data);
        } catch (e) {
            console.error("Failed to parse response as JSON:", e);
            alert('Error parsing statistics data.');
            return;
        }
        const parsedData = parseMostPopularClinicsData(data);
        console.log("sorted clinic data:",parsedData);
        displayMostPopularClinicsData(parsedData);
        if (response.ok) {
            alert('statistics fetched successfully');
        } else {
            alert('Error fetching statistics.');
        }
    })

    fetch('/api/statistics/mostPopularProfessors', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(async response => {
        const text = await response.text();
        //console.log('mostPopuilarProfessors response', response.status, text);
        let data;
        try {
            data = JSON.parse(text);
            console.log("Parsed prof data", data);
        } catch (e) {
            console.error("Failed to parse response as JSON:", e);
            alert('Error parsing statistics data.');
            return;
        }
        const parsedData = parseMostPopularProfessorData(data);
        console.log("sorted prof data: ",parsedData);
        displayMostPopularProfessorData(parsedData);
    })

    fetch('/api/statistics/mostPopularDepartment/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(async response => {
        const text = await response.text();
        //console.log('mostPopularDepartment response', response.status, text);
        let data;
        try {
            data = JSON.parse(text);
            console.log("parsed department data", data);
        } catch (e) {
            console.error("Failed to parse response as JSON:", e);
            alert('Error parsing statistics data.');
            return;
        }
        const parsedData = parseMostPopularDepartmentData(data);
        console.log("sorted major data:", parsedData);
        displayMostPopularDepartmentData(parsedData);
    })

    fetch('/api/statistics/proposedProjectsByDepartment/', {
        method:'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(async response => {
        const text = await response.text();
        console.log('proposedProjectsByDepartment response', response.status, text);
        let data;
        try {
            data = JSON.parse(text);
            console.log("parsed proposal data", data);
        } catch (e) {
            console.error("Failed to parse response as JSON:", e);
            alert('Error parsing statistics data.');
            return;
        }
        const parsedData = parseProposedProjectsByDepartment(data);
        console.log("sorted proposed data:", parsedData);
        displayProposedProjectsByDepartment(parsedData);
    })

    fetch('/api/statistics/studentSignupsByDepartment/', {
        method:'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(async response => {
        const text = await response.text();
        console.log("studentSignupsByDepartment response", response.status, text);
        let data;
        try {
            data = JSON.parse(text);
            console.log("parsed signup data", data);
        } catch (e) {
            console.error("Failed to parse response as JSON:", e);
            alert('Error parsing statistics data.');
            return;
        }
        const parsedData = parseStudentSignupsByDepartment(data);
        console.log("sorted signup data:", parsedData);
        displayStudentSignupsByDepartment(parsedData);
    })

    fetch('/api/statistics/studentChoiceDistribution/', {
        method:'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(async response => {
        const text = await response.text();
        console.log('studentChoiceDistribution response', response.status, text);
        let data;
        try {
            data = JSON.parse(text);
            console.log("parsed choice data", data);
        } catch (e) {
            console.error("Failed to parse response as JSON:", e);
            alert('Error parsing statistics data.');
            return;
        }
        displayStudentChoiceDistribution(data);
    })
});

function parseMostPopularClinicsData(data1) {
    let data = data1;
    let result = [];
    let maxClinicIndex=0;

    //basic selection sort, could be optimized later
    let clinicCount = data.length
    for(let i = 0; i < clinicCount; i++) {
        for (let j = 0; j < data.length; j++) {
            if (data[j].requests > data[maxClinicIndex].requests)
                maxClinicIndex = j;
        }
        let maxClinic = data.splice(maxClinicIndex,1);
        result.push({
            title: maxClinic[0].title,
            requests: maxClinic[0].requests,
            color: maxClinic[0].major_color
        });
        maxClinicIndex=0;
    }

    return result;
}

function parseMostPopularProfessorData(data1) {
    let data = data1;
    let result = [];
    let maxRequestIndex = 0;

    //basic selection sort, could be optimized later
    let professorCount = data.length
    for (let i = 0; i < professorCount; i++) {
        for (let j = 0; j < data.length; j++) {
            if (data[j].requests > data[maxRequestIndex].requests)
                maxRequestIndex = j;
        }
        let maxRequestProf = data.splice(maxRequestIndex,1);
        result.push({
            name: maxRequestProf[0].name,
            requests: maxRequestProf[0].requests
        });
        maxRequestIndex = 0;
    }

    return result;
}

function parseMostPopularDepartmentData(data1) {
    let data = data1;
    let result = [];
    let maxRequestIndex = 0;

    //basic selection sort, could be optimized later
    let majorCount = data.length
    for (let i = 0; i < majorCount; i++) {
        for (let j = 0; j < data.length; j++) {
            if (data[j].requests > data[maxRequestIndex].requests)
                maxRequestIndex = j;
        }
        let maxRequestMajor = data.splice(maxRequestIndex,1);
        result.push({
            major: maxRequestMajor[0].major,
            color: maxRequestMajor[0].color,
            requests: maxRequestMajor[0].requests
        })
        maxRequestIndex = 0;
    }

    return result;
}

function parseProposedProjectsByDepartment(data1) {
    let data = data1;
    let result = [];
    let maxProposedIndex = 0;

    //basic selection sort, could be optimized later
    let proposalCount = data.length
    for (let i = 0; i < proposalCount; i++) {
        for (let j = 0; j < data.length; j++) {
            if (data[j].proposed > data[maxProposedIndex].proposed)
                maxProposedIndex = j;
        }
        let maxProposedMajor = data.splice(maxProposedIndex,1);
        result.push({
            major: maxProposedMajor[0].major,
            color: maxProposedMajor[0].color,
            proposed: maxProposedMajor[0].proposed
        })
        maxProposedIndex = 0;
    }

    return result;
}

function parseStudentSignupsByDepartment(data1) {
    let data = data1;
    let result = [];
    let maxSignupIndex = 0;

    //basic selection sort, could be optimized later
    let departmentCount = data.length
    for (let i = 0; i < departmentCount; i++) {
        for (let j = 0; j < data.length; j++) {
            if (data[j].signups > data[maxSignupIndex].signups)
                maxSignupIndex = j;
        }
        let maxSignupMajor = data.splice(maxSignupIndex,1);
        result.push({
            major: maxSignupMajor[0].major,
            color: maxSignupMajor[0].color,
            signups: maxSignupMajor[0].signups
        })
        maxSignupIndex = 0;
    }

    return result;
}

function displayMostPopularClinicsData(data) {
    const wrapper = document.createElement('div');
    wrapper.className = "most-pop-clinics";
    const title = document.createElement('h1');
    title.textContent = "Most Popular Clinics";
    wrapper.appendChild(title);

    for (let i = 0; i < 10; i++) {
        const p = document.createElement('p');
        p.className = "pop-clinic";
        p.style.setProperty("--color",data[i].color);
        p.textContent = data[i].title;

        wrapper.appendChild(p);
    }

    const statisticsPage = document.getElementById("statistics");
    statisticsPage.appendChild(wrapper);
}

function displayMostPopularProfessorData(data) {
    const wrapper = document.createElement('div');
    wrapper.className = "most-pop-profs";
    const title = document.createElement('h1');
    title.textContent = "Most Popular Professors";
    wrapper.appendChild(title);

    for (let i = 0; i < 10; i++) {
        const p = document.createElement('p');
        p.className = "pop-prof";
        p.textContent = data[i].name;

        wrapper.appendChild(p);
    }

    const statisticsPage = document.getElementById("statistics");
    statisticsPage.appendChild(wrapper);

}

function displayMostPopularDepartmentData(data) {
    const wrapper = document.createElement('div');
    wrapper.className = "most-pop-major";
    const title = document.createElement('h1');
    title.textContent = "Most Popular Department";
    wrapper.appendChild(title);

    for (let i = 0; i < data.length; i++) {
        const p = document.createElement('p');
        p.className = "pop-major";
        p.style.setProperty("--color",data[i].color);
        p.textContent = data[i].major;

        wrapper.appendChild(p);
    }

    const statisticsPage = document.getElementById("statistics");
    statisticsPage.appendChild(wrapper);
}

function displayProposedProjectsByDepartment(data) {
    const wrapper = document.createElement('div');
    wrapper.className = "proposed-projects";
    const title = document.createElement('h1');
    title.textContent = "Proposed Projects By Department";
    wrapper.appendChild(title);
    let total = 0;
    let labels = [];
    let values = [];
    let backgroundColors = [];

    for (let i = 0; i < data.length; i++) {
        const p = document.createElement('p');
        p.className = "proposed-project";
        p.style.setProperty("--color",data[i].color);
        p.textContent = data[i].major + " -- " + data[i].proposed;

        labels.push(data[i].major);
        values.push(data[i].proposed);
        backgroundColors.push(data[i].color);

        total += data[i].proposed;

        wrapper.appendChild(p);
    }

    const p = document.createElement('p');
    p.className = "proposed-project";
    p.style.setProperty("--color", "#ddd");
    p.textContent = "total -- " + total;

    wrapper.appendChild(p);

    const canvasDiv = document.createElement('div');
    canvasDiv.className = "proposed-project-wrapper graph";
    const canvas = document.createElement('canvas');
    canvas.className = "proposed-project-graph";
    canvas.id = "proposed-project-graph";
    canvasDiv.appendChild(canvas);
    wrapper.appendChild(canvasDiv);
    
    new Chart (
        canvas.getContext('2d'),
        {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    label: "# of Projects",
                    data: values,
                    backgroundColor: backgroundColors,
                }]
            }
        }
    )

    const statisticsPage = document.getElementById("statistics");
    statisticsPage.appendChild(wrapper);
}

function displayStudentSignupsByDepartment(data) {
    const wrapper = document.createElement('div');
    wrapper.className = "student-signups";
    const title = document.createElement('h1');
    title.textContent = "Student Sign-ups By Department";
    wrapper.appendChild(title);
    let total = 0;
    let labels = [];
    let values = [];
    let backgroundColors = [];

    for (let i = 0; i < data.length; i++) {
        const p = document.createElement('p');
        p.className = "student-major";
        p.style.setProperty("--color",data[i].color);
        p.textContent = data[i].major + " -- " + data[i].signups;

        labels.push(data[i].major);
        values.push(data[i].signups);
        backgroundColors.push(data[i].color);

        total += data[i].signups;

        wrapper.appendChild(p);
    }

    const p = document.createElement('p');
    p.className = "student-major";
    p.style.setProperty("--color", "#ddd");
    p.textContent = "total -- " + total;

    const canvasDiv = document.createElement('div');
    canvasDiv.className = "student-major-wrapper graph";
    const canvas = document.createElement('canvas');
    canvas.className = "student-major-graph";
    canvas.id = "student-major-graph";
    canvasDiv.appendChild(canvas);
    wrapper.appendChild(canvasDiv);

    new Chart(
        canvas.getContext('2d'),
        {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    label: "# of Students",
                    data: values,
                    backgroundColor: backgroundColors,
                }]
            }
        }
    );

    
    wrapper.appendChild(p);

    const statisticsPage = document.getElementById("statistics");
    statisticsPage.appendChild(wrapper);
}

function displayStudentChoiceDistribution(data) {
    const wrapper = document.createElement('div');
    wrapper.className = "student-choices";
    const title = document.createElement('h1');
    title.textContent = "Student Choice Distribution";
    wrapper.appendChild(title);
    let total = 0;
    let labels = [];
    let values = [];

    for (let i = 0; i < data.length; i++) {
        const p = document.createElement('p');
        p.className = "student-choice";
        p.textContent = data[i].choice + " -- " + data[i].count;

        labels.push(data[i].choice);
        values.push(data[i].count);
        total += data[i].count;

        wrapper.appendChild(p);
    }

    const p = document.createElement('p');
    p.className = "student-choice";
    p.textContent = "total -- " + total;

    wrapper.appendChild(p);

    const canvasDiv = document.createElement('div');
    canvasDiv.className = "student-choices-wrapper graph";
    const canvas = document.createElement('canvas');
    canvas.className="student-choices-graph";
    canvas.id="student-choices-graph";
    canvasDiv.appendChild(canvas);
    wrapper.appendChild(canvasDiv);
    
    new Chart(
        canvas.getContext('2d'),
        {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    label: '# of students',
                    data: values,
                }]
            }
        }
    );


    const statisticsPage = document.getElementById("statistics");
    statisticsPage.appendChild(wrapper);
}