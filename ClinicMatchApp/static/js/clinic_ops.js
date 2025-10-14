var dragContainer = document.body;
var clinicsBoard;
var studentsBoard;
var clinicGrids = [];
var __isDragging = false; // <-- new flag

// helper sizing functions (use per-element stored originWidth captured at dragStart)
function fixDragSizing(el) {
  if (!el) return;
  // measure the visible inner card if present
  var card = el.querySelector('.student-card') || el;
  var rect = card.getBoundingClientRect();

  // prefer originWidth stored at dragStart (clamped), fallback to container closest width
  var originWidth = el.__originWidth || null;
  if (!originWidth) {
    var container = el.closest('.students-board-inner, .clinic-inner, .students-board, .clinics-board');
    if (container) originWidth = Math.max(0, Math.floor(container.getBoundingClientRect().width - 12));
  }

  var measuredW = Math.round(rect.width);
  if (originWidth && originWidth < measuredW) measuredW = originWidth;

  var w = measuredW + 'px';
  var h = Math.round(rect.height) + 'px';

  // defensive: ensure no global var pollution
  document.documentElement.style.removeProperty('--muuri-drag-w');
  document.documentElement.style.removeProperty('--muuri-drag-h');
  document.body.style.removeProperty('--muuri-drag-w');
  document.body.style.removeProperty('--muuri-drag-h');

  // set per-element vars + inline fallbacks on the outer element
  el.style.setProperty('--muuri-drag-w', w);
  el.style.setProperty('--muuri-drag-h', h);
  el.style.setProperty('width', w, 'important');
  el.style.setProperty('min-width', w, 'important');
  el.style.setProperty('max-width', w, 'important');
  el.style.setProperty('height', h, 'important');
  el.style.setProperty('min-height', h, 'important');
  el.style.setProperty('max-height', h, 'important');

  // ALSO apply explicit pixel width to the inner card to prevent child CSS from stretching it
  if (card && card !== el) {
    card.style.setProperty('width', w, 'important');
    card.style.setProperty('min-width', w, 'important');
    card.style.setProperty('max-width', w, 'important');
    card.style.boxSizing = 'border-box';
  }

  el.style.setProperty('will-change', 'transform', 'important');
  el.style.setProperty('z-index', '999999', 'important');
  el.classList.add('muuri-fixed-drag');
}

function clearDragSizing(el) {
  if (!el) return;
  var card = el.querySelector('.student-card') || el;

  el.style.removeProperty('--muuri-drag-w');
  el.style.removeProperty('--muuri-drag-h');

  el.style.removeProperty('width');
  el.style.removeProperty('min-width');
  el.style.removeProperty('max-width');
  el.style.removeProperty('height');
  el.style.removeProperty('min-height');
  el.style.removeProperty('max-height');

  el.style.removeProperty('will-change');
  el.style.removeProperty('z-index');

  el.classList.remove('muuri-fixed-drag');

  // clear card overrides
  if (card && card !== el) {
    card.style.removeProperty('width');
    card.style.removeProperty('min-width');
    card.style.removeProperty('max-width');
    card.style.boxSizing = '';
  }

  // defensive cleanup of any leftover global vars
  document.documentElement.style.removeProperty('--muuri-drag-w');
  document.documentElement.style.removeProperty('--muuri-drag-h');
  document.body.style.removeProperty('--muuri-drag-w');
  document.body.style.removeProperty('--muuri-drag-h');
}

// init sequence - ensure boards exist before attaching handlers
window.addEventListener('load', function () {

  // initialize studentsBoard first
  studentsBoard = new Muuri('.students-board-inner', {
    items: '.student-item',
    dragEnabled: true,
    dragHandle: ".student-card",
    dragContainer: dragContainer,
    layout: { fillGaps: false, rounding: true, horizontal: false },
    dragSort: function () { return clinicGrids; }
  });

  // attach studentsBoard drag handlers (capture origin width before Muuri moves element)
  studentsBoard.on('dragStart', function (item) {
    __isDragging = true; // <-- set dragging flag
    var el = item.getElement();
    // store origin container width before Muuri detaches/moves the element
    var parent = el.parentElement;
    if (parent) {
      el.__originWidth = Math.max(0, Math.floor(parent.getBoundingClientRect().width - 12));
    }
    // allow Muuri to apply its initial transform, then lock sizes
    setTimeout(function () { fixDragSizing(el); }, 0);
  });
  studentsBoard.on('dragReleaseEnd', function (item) {
    var el = item.getElement();
    clearDragSizing(el);
    __isDragging = false; // <-- clear dragging flag
    studentsBoard.refreshItems().layout();
  });

  // initialize clinicsBoard (containers of clinics)
  clinicsBoard = new Muuri('.clinics-board', {
    items: '.item',
    dragEnabled: false,
    layout: { fillGaps: false, rounding: true, horizontal: false }
  });

  // initialize each clinic-inner as its own Muuri grid
  document.querySelectorAll('.clinic-inner').forEach(function (el) {
    // create grid for this clinic inner
    var grid = new Muuri(el, {
      items: '.student-item',
      dragEnabled: true,
      dragHandle: ".student-card",
      dragContainer: dragContainer,
      layout: { fillGaps: false, rounding: true, horizontal: false },
      dragSort: function () {
        return [studentsBoard].concat(clinicGrids.filter(function(g){ return g !== grid; }));
      }
    });

    // push to clinicGrids BEFORE attaching handlers so dragSort can return full list
    clinicGrids.push(grid);

    // attach handlers safely (grid should be defined here)
    grid.on('dragStart', function (item) {
      __isDragging = true; // <-- set dragging flag
      var el = item.getElement();
      var parent = el.parentElement;
      if (parent) {
        el.__originWidth = Math.max(0, Math.floor(parent.getBoundingClientRect().width - 12));
      }
      setTimeout(function () { fixDragSizing(el); }, 0);
    });
    grid.on('dragReleaseEnd', function (item) {
      var el = item.getElement();
      clearDragSizing(el);
      __isDragging = false; // <-- clear dragging flag
      grid.refreshItems().layout();
    });

    grid.on('receive', function (data) {
      var el = data.item.getElement();
      // ensure correct classes
      el.classList.remove('item');
      el.classList.add('student-item');
      // clear any originWidth so future drags recompute correctly
      delete el.__originWidth;
      grid.refreshItems().layout();
      studentsBoard.refreshItems().layout(true);
      clinicsBoard.refreshItems().layout(true);
    });
  });

  // final layout pass
  clinicGrids.forEach(function (g) { g.refreshItems().layout(true); });
  studentsBoard.refreshItems().layout(true);
  clinicsBoard.refreshItems().layout(true);

  requestAnimationFrame(function () {
    clinicGrids.forEach(function (g) { g.refreshItems().layout(); });
    studentsBoard.refreshItems().layout();
    clinicsBoard.refreshItems().layout();
    setTimeout(function () {
      clinicGrids.forEach(function (g) { g.refreshItems().layout(); });
      studentsBoard.refreshItems().layout();
      clinicsBoard.refreshItems().layout();
    }, 120);
  });

  // expose for debugging
  window.clinicGrids = clinicGrids;
  window.studentsBoard = studentsBoard;
  window.clinicsBoard = clinicsBoard;
});

// prevent resize-driven reflows while dragging
window.addEventListener('resize', function () {
  if (__isDragging) return; // skip layout while a drag is active
  clinicGrids.forEach(function (g) { g.refreshItems().layout(); });
  studentsBoard && studentsBoard.refreshItems().layout();
  clinicsBoard && clinicsBoard.refreshItems().layout();
});