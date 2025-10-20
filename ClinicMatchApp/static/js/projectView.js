var grid = new Muuri('.grid', {
  dragEnabled: true,
  dragContainer: document.body,}
);

var selectGrid = new Muuri('.select-grid', {
  dragEnabled: true,
  dragContainer: document.body,
  dragSort: function () {return [grid, selectGrid];}
});


grid._settings.dragSort = function () { return [grid, selectGrid]; };




const form = document.getElementById('submission-form')
var button = document.getElementById('submit-button')
const gridOrder = document.getElementById('grid-order')




button.addEventListener('click', (e) => {
    selectGrid.synchronize();
});