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
            <p><strong>Status:</strong> ${data.status === 'J' ? 'Junior' : 'Senior'}</p>
            <p><strong>Major:</strong> ${data.major}</p>
            <p><strong>Initial Assigned Clinic:</strong> ${data.clinic}</p>
            <p><strong>Preferences:</strong> ${data.choices.join('<br>')}</p>
          `;

          detailsPane.scrollIntoView({ behavior: 'smooth' });
        })
        .catch(error => {
          console.error("Error loading student info:", error);
        });
    });
  });

  // Automatically assign students with an assigned_clinic on load
  document.querySelectorAll('.student-item').forEach(studentEl => {
    const studentId = studentEl.dataset.studentId;

    fetch(`/api/student/${studentId}/`)
      .then(res => {
        if (!res.ok) throw new Error('Student fetch failed');
        return res.json();
      })
      .then(data => {
        if (!data.assigned_clinic) return;

        // Find the .clinic-inner that matches the assigned clinic
        const matchingClinicContainer = Array.from(document.querySelectorAll('.clinic-container'))
          .find(container => container.querySelector('.clinic-title')?.textContent.trim() === data.assigned_clinic);

        if (!matchingClinicContainer) {
          console.warn(`Clinic "${data.assigned_clinic}" not found in DOM`);
          return;
        }

        const targetGridEl = matchingClinicContainer.querySelector('.clinic-inner');
        const targetGrid = clinicGrids.find(grid => grid.getElement() === targetGridEl);

        if (!targetGrid) {
          console.warn(`Muuri grid not found for clinic "${data.assigned_clinic}"`);
          return;
        }

        // Remove from current Muuri grid (studentsBoard)
        const item = studentsBoard.getItem(studentEl);
        if (!item) {
          console.warn(`Item not found in studentsBoard for student ID ${studentId}`);
          return;
        }

        // Move the item to the target grid (e.g., to the end)
        studentsBoard.move(item, targetGrid, -1);

        // Then refresh layouts
        targetGrid.refreshItems();
        targetGrid.layout();

      })
      .catch(err => console.error('Error assigning student:', err));
  });

});
