window.addEventListener('load', function() {
    for (let i = 0; i < 6; i++) {
        const majorSelectorId = "id_numberHandler-" + i + "-major";
        //console.log(majorSelectorId);
        const majorSelector = document.getElementById(majorSelectorId);
        majorSelector.selectedIndex = i+1;
        //console.log(majorSelector);
    }
});