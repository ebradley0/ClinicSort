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
  
  
});

var selectGrid = new Muuri('.select-grid', {
  dragEnabled: true,
  dragContainer: document.body,
  dragSort: function () {return [grid, selectGrid];},
});

document.addEventListener('DOMContentLoaded', function(){
      document.querySelectorAll('.remove-button').forEach(function(button){
       button.addEventListener('click', function(){
            item = grid.getItem(button.closest('.item'));
            grid.remove(item, {removeElements: true});
       })
    })
    });









//grid._settings.dragSort = function () { return [grid, selectGrid]; };




const form = document.getElementById('submission-form')
var button = document.getElementById('submit-button')
const gridOrder = document.getElementById('grid-order')




button.addEventListener('click', (e) => {
    selectGrid.synchronize();
    console.log("Grid Synced")
});