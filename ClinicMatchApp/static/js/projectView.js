var grid = new Muuri('.grid', {
  dragEnabled: true,
  dragContainer: document.body,
  dragSort: function (item) { //This triggers everytime an item is picked up. So when we pick up an item, we check if the chosen clinics grid has less than 8 entries. If it doesn't, then we set the allowed grids to only itself, meaning we can't drag to a different grid
  let allowedGrids = [grid];
  if (selectGrid.getItems().length < 8) {
    allowedGrids.push(selectGrid);
  } else {
    allowedGrids.pop(selectGrid);
  }
  return allowedGrids;  
  },
  dragStartPredicate: {
    distance: 10, // only start drag if mouse moves 10px
    delay: 0
  },
  sortData: {
    popularityIndex: function (item, element) {
      return parseFloat(element.dataset.popIndex) || 0;
    },
    randomValue: function (item, element) {
      return Math.random();
    }
  }
  
});

var selectGrid = new Muuri('.select-grid', {
  dragEnabled: true,
  dragContainer: document.body,
  dragSort: function () {return [grid, selectGrid];},
});

document.addEventListener('DOMContentLoaded', () => {
  console.log("DOM LOADED")
  document.querySelectorAll('.item').forEach(item => {
    item.addEventListener('click', (e) => {
      console.log("ITEM CLICKED");
      const preview = item.querySelector('.itemContents');
      const details = item.querySelector('.clinicDetails');
      preview.classList.toggle('hidden');
      
      details.classList.toggle('hidden');
    });
  });
});


const infoButton = document.getElementById("infoButton");
const infoPopOut = document.getElementById("legendPopup");

window.addEventListener('load', function() {
  infoButton.addEventListener('click', function () {
    console.log("info toggled");
    
    infoButton.classList.toggle('show');
    

    infoPopOut.classList.toggle('show');

  });

  // Filtering Functionality, can expand later to include more filters
  const departmentFilter = document.getElementById("clinic-department-filter");
  const showAcceptingCheckbox = document.getElementById("show-accepting");

  function filterClinics() {
    const selectedDepartment = departmentFilter.value;
    const showAccepting = showAcceptingCheckbox.checked;
    

    grid.filter(function (item) {
      const clinicEl = item.getElement();
      const clinicDepartment = clinicEl.dataset.department;
      const acceptingMax = clinicEl.dataset.max;

      const passesDepartmentFilter = (selectedDepartment === 'all' || clinicDepartment === selectedDepartment);
      const passesAcceptingFilter = acceptingMax > 0 || !showAccepting;

      return passesDepartmentFilter && passesAcceptingFilter;
    });
  }
  departmentFilter.addEventListener('change', filterClinics);
  showAcceptingCheckbox.addEventListener('change', filterClinics);

  // Initial filter application
  filterClinics();
})

const sortPIButton = document.getElementById("sort-PI");
if (sortPIButton) {
  sortPIButton.addEventListener('click', function() {
    console.log("Sorting by Popularity Index (descending)");

    // Make sure both grids reflect the current DOM (important after dragging between grids)
    try {
      // synchronize() updates the Muuri instance to match DOM nodes moved by drag-sort
      if (typeof selectGrid !== 'undefined' && selectGrid) selectGrid.synchronize();
      if (typeof grid !== 'undefined' && grid) grid.synchronize();
    } catch (err) {
      // synchronize might not exist depending on Muuri version — ignore safely
      console.warn("synchronize() error (ignored):", err);
    }

    // Force Muuri to refresh its internal list of items/elements
    grid.refreshItems();

    // Use comparator sort so Muuri doesn't rely on internal _sortData
    // Here we sort descending (largest PI first). Change bVal - aVal for ascending.
    grid.sort(function(a, b) {
      const aVal = parseFloat(a.getElement().dataset.popIndex) || 0;
      const bVal = parseFloat(b.getElement().dataset.popIndex) || 0;
      return aVal - bVal; // descending
    });

    // Force layout / animation after sort
    grid.layout(true);
  });
} else {
  console.warn("sort-PI button not found in DOM");
}

window.addEventListener('load', function() {
  grid.sort('randomValue');
});
//grid._settings.dragSort = function () { return [grid, selectGrid]; };




const form = document.getElementById('submission-form')
var button = document.getElementById('submit-button')
const gridOrder = document.getElementById('grid-order')




button.addEventListener('click', (e) => {
    selectGrid.synchronize();
    console.log("Grid Synced")
});