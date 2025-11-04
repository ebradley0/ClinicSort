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


infoButton.addEventListener('click', () =>{
  console.log("info toggled");
  
  infoButton.classList.toggle('show');
  

  infoPopOut.classList.toggle('show');

});




  









//grid._settings.dragSort = function () { return [grid, selectGrid]; };




const form = document.getElementById('submission-form')
var button = document.getElementById('submit-button')
const gridOrder = document.getElementById('grid-order')




button.addEventListener('click', (e) => {
    selectGrid.synchronize();
    console.log("Grid Synced")
});