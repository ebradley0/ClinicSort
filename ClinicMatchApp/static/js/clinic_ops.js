var dragContainer = document.body;
var clinicsBoard;
var studentsBoard;
var clinicGrids = [];

window.addEventListener('load', function () {

  // 1. Set each clinic .item to 1000px width BEFORE Muuri initializes
  document.querySelectorAll('.clinics-board .item').forEach(function (item) {
    item.style.width = '1000px';     // ✅ full width of the board
    item.style.height = '200px';     // match .clinic-container height
  });

  // 2. Initialize the students board
  studentsBoard = new Muuri('.students-board-inner', {
    items: '.student-item',
    dragEnabled: true,
    dragHandle: ".student-card",
    dragContainer: dragContainer,
    dragScroll: true,
    dragAutoScroll: {
      targets: (item) => {
        return [
          { element: window, priority: 0 },
          { element: item.getGrid().getElement().parentNode, priority: 1 },
        ]
      }
    },
    layout: {
      fillGaps: false,
      rounding: true,
      horizontal: false
    },
    dragSort: function () {
      return clinicGrids;
    }
  });

  // 3. Initialize the clinics board
  clinicsBoard = new Muuri('.clinics-board', {
    items: '.item',
    dragEnabled: false,
    layout: {
      fillGaps: false,
      rounding: true,
      horizontal: false
    }
  });

  // 4. Initialize each .clinic-inner as a Muuri grid
  document.querySelectorAll('.clinic-inner').forEach(function (el) {
    var grid = new Muuri(el, {
      items: '.student-item',
      dragEnabled: true,
      dragHandle: ".student-card",
      dragContainer: dragContainer,
      layout: {
        horizontal: true,
        fillGaps: true,
        width: 1000
      },
      dragSort: function () {
        return [studentsBoard].concat(clinicGrids.filter(function (g) {
          return g !== grid;
        }));
      },
      dragAutoScroll: {
        targets: (item) => {
          return [
            { element: window, priority: 0 },
            { element: item.getGrid().getElement().parentNode, priority: 1 },
          ]
        }
      },
    });

    clinicGrids.push(grid);
  });

  // 5. Force layout after all items are sized
  clinicsBoard.refreshItems();
  clinicsBoard.layout();
  clinicGrids.forEach(grid => {
    grid.refreshItems();
    grid.layout();
  });

  // 6. Student info button click handler
  document.querySelectorAll('.student-item .info').forEach(function(button) {
    button.addEventListener('click', function(event) {
      event.stopPropagation();

      const studentItem = button.closest('.student-item');
      const studentId = studentItem?.dataset?.studentId;

      if (!studentId) {
        console.warn("No student ID found");
        return;
      }

      fetch(`/api/student/${studentId}/`)
        .then(response => {
          if (!response.ok) throw new Error("Failed to load student info");
          return response.json();
        })
        .then(data => {
          const detailsPane = document.getElementById('details-pane');
          if (!detailsPane) return;

          detailsPane.innerHTML = `
            <h2>${data.name}</h2>
            <p><strong>Email:</strong> ${data.email}</p>
            <p><strong>Banner ID:</strong> ${data.banner_id}</p>
            <p><strong>Status:</strong> ${data.j_or_s === 'J' ? 'Junior' : 'Senior'}</p>
            <p><strong>Major:</strong> ${data.alternative_major ? (data.major === "ECE" ? 'EET' : 'MET') : data.major}</p>
            <p><strong>Initial Assigned Clinic:</strong> ${data.initial_assignment}</p>
            <p><strong>Preferences:</strong> ${data.choices.join('<br>')}</p>
            <p><strong>Requested For:</strong> ${data.requested_by.join('<br>')}</p>
          `;

          detailsPane.scrollIntoView({ behavior: 'smooth' });
        })
        .catch(error => {
          console.error("Error loading student info:", error);
        });
    });
  });

  // 7. Filter controls: major dropdown + accepting checkbox + show-empty checkbox
  const majorFilter = document.getElementById('major-filter');
  const acceptingMajorCheckbox = document.getElementById('accepting-major');
  const showEmptyCheckbox = document.getElementById('show-empty');

  function filterClinics() {
    const selectedMajor = (majorFilter.value || '').toLowerCase();
    const onlyAccepting = acceptingMajorCheckbox.checked;
    const showEmptyOnly = showEmptyCheckbox?.checked;

    clinicsBoard.filter(function (item) {
      const clinicEl = item.getElement();
      const clinicMajor = (clinicEl.dataset.major || '').toLowerCase();
      const clinicGeneral = clinicEl.dataset.isGeneral === 'True';
      const clinicTotal = Number(clinicEl.dataset.total);
      const totalMax = Number(clinicEl.dataset.totalMax);
      const totalMin = Number(clinicEl.dataset.totalMin);

      // Count assigned students inside this clinic's .clinic-inner by matching clinic id
      const clinicId = clinicEl.dataset.clinicId;
      const clinicInner = document.querySelector(`.clinic-inner[data-clinic-id="${clinicId}"]`);
      const assignedCount = clinicInner ? clinicInner.querySelectorAll('.student-item').length : 0;

      // Filter by major dropdown:
      const passesMajorFilter = (selectedMajor === '' || selectedMajor === 'all') || (clinicMajor === selectedMajor);

      // Filter by accepting checkbox (totalMax > 0):
      const passesAcceptingFilter = !onlyAccepting || (totalMax > 0);

      // Filter by show-empty checkbox (assignedCount < totalMin):
      const passesShowEmptyFilter = 
        !showEmptyOnly ||
        (clinicGeneral
          ? Number.isFinite(clinicTotal) &&
            Number.isFinite(totalMin) &&
            clinicTotal < totalMin
          : assignedCount < totalMin);

      // Must satisfy all active filters
      return passesMajorFilter && passesAcceptingFilter && passesShowEmptyFilter;
    });
  }

  // Attach listeners to filter controls
  if (majorFilter) {
    majorFilter.addEventListener('change', filterClinics);
  }
  if (acceptingMajorCheckbox) {
    acceptingMajorCheckbox.addEventListener('change', filterClinics);
  }
  if (showEmptyCheckbox) {
    showEmptyCheckbox.addEventListener('change', filterClinics);
  }

  // Initial filter on page load
  filterClinics();

  const saveAssignmentsBtn = document.getElementById('save-assignments');

  if (saveAssignmentsBtn) {
    saveAssignmentsBtn.addEventListener('click', function () {
      // Prepare an array to hold student-to-clinic assignments
      const assignments = [];

      // For each clinic container, get clinic id and student ids inside it
      document.querySelectorAll('.clinic-container.item').forEach(clinicEl => {
        const clinicId = clinicEl.dataset.clinicId;
        const clinicInner = clinicEl.querySelector('.clinic-inner');

        if (!clinicInner) return;

        // Find all student items inside this clinic
        clinicInner.querySelectorAll('.student-item').forEach(studentEl => {
          const studentId = studentEl.dataset.studentId;

          if (studentId && clinicId) {
            assignments.push({
              student_id: studentId,
              clinic_id: clinicId
            });
          }
        });
      });

      // Optional: disable button to prevent multiple clicks while saving
      saveAssignmentsBtn.disabled = true;

      // Send assignments to backend via fetch POST request
      fetch('/api/update-student-assignments/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken') // assuming you have CSRF token function
        },
        body: JSON.stringify({ assignments })
      })
      .then(response => {
        console.log(response);
        if (!response.ok) throw new Error('Failed to save assignments');
        return response.json();
      })
      .then(data => {
        alert('Assignments saved successfully!');
      })
      .then(data => {
        fetch('/api/mapStudentsToClinics/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // assuming you have CSRF token function
          },
          body: JSON.stringify({ assignments })
        })
        .then(response => {
          if (!response.ok) throw new Error('Failed to map students to clinics');
          return response.json();
        })
        .then(data => {
          console.log('Students mapped to clinics successfully');
        })
        .catch(error => {
          console.error('Error mapping students to clinics:', error);
        });
      })
      .catch(error => {
        console.error('Error saving assignments:', error);
        alert('Error saving assignments.');
      })
      .finally(() => {
        saveAssignmentsBtn.disabled = false;
        location.reload();
      });
    });
  }

  //RESET ASSIGNMENTS BUTTON HANDLER
  const resetAssignmentsBtn = document.getElementById('reset-assignments');

  if (resetAssignmentsBtn) {
    resetAssignmentsBtn.addEventListener('click', async function () {
      if (!confirm('Are you sure you want to reset all assignments to their initial state?')) {
        return;
      }

      // Build normalized assignments: use numbers for IDs, null for no assignment
      const initial_assignments = [];
      document.querySelectorAll('.student-item').forEach(studentEl => {
        const studentIdStr = studentEl.dataset.studentId;
        const initialClinicIdStr = studentEl.dataset.initialAssignment;

        if (!studentIdStr) return;

        const student_id = Number.isFinite(Number(studentIdStr)) ? parseInt(studentIdStr, 10) : studentIdStr;
        let clinic_id = null;
        if (initialClinicIdStr !== undefined && initialClinicIdStr !== 'null' && initialClinicIdStr !== '') {
          // convert numeric string to integer if possible, otherwise keep raw
          clinic_id = Number.isFinite(Number(initialClinicIdStr)) ? parseInt(initialClinicIdStr, 10) : initialClinicIdStr;
        }

        initial_assignments.push({
          student_id,
          clinic_id
        });
      });

      try {
        // 1) Reset assignments on backend
        const resp = await fetch('/api/update-student-assignments/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
          },
          body: JSON.stringify({ assignments: initial_assignments })
        });

        if (!resp.ok) throw new Error('Failed to reset assignments');

        alert('Assignments have been reset to initial state.');

        // 2) Optionally call mapStudentsToClinics with the same payload (use initial_assignments)
        try {
          const mapResp = await fetch('/api/mapStudentsToClinics/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ assignments: initial_assignments })
          });
          if (!mapResp.ok) {
            console.warn('mapStudentsToClinics returned non-ok status', mapResp.status);
          } else {
            console.log('Students mapped to clinics successfully');
          }
        } catch (mapErr) {
          console.warn('Error mapping students to clinics:', mapErr);
        }

      } catch (error) {
        console.error('Error resetting assignments:', error);
        alert('Error resetting assignments.');
      } finally {
        // Reload to reflect server state (or replace with a more targeted UI update)
        location.reload();
      }
    });
  }

  // Helper function to get CSRF token from cookie (common Django approach)
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i=0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length+1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length+1));
          break;
        }
      }
    }
    return cookieValue;
  }
});