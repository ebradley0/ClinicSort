const clinic_type_dropdown = document.getElementById('clinic_type');
const numformList = document.getElementById('numform-list');
const majorCount = numformList.dataset.majorCount;

window.addEventListener('load', function() {
    for (let i = 0; i < majorCount; i++) {
        const majorSelectorId = "id_numberHandler-" + i + "-major";
        const numhandlerGeneralId = "id_numberHandler-" + i + "-general";
        //console.log(majorSelectorId);
        const majorSelector = document.getElementById(majorSelectorId);
        const numberhandlerGeneral = document.getElementById(numhandlerGeneralId);
        const numberhandlerGeneralLabel = document.querySelector('label[for="' + numhandlerGeneralId + '"]');

        numberhandlerGeneral.hidden = true;
        numberhandlerGeneralLabel.hidden = true;
        majorSelector.selectedIndex = i+1;
        //console.log(majorSelector);
        
        // Will need to go through and delete unnecessary code later back when general labels still existed

    }
    const isGeneral = document.getElementById("id_numberHandler-0-general").checked;
    if (isGeneral) {
        clinic_type_dropdown.value = "general";
    } else {
        clinic_type_dropdown.value = "specific";
    }
    clinic_type_changer();
    generalVsSpecificPreview();
    updateNumberHandlerPreview();
});


clinic_type_dropdown.addEventListener('input', clinic_type_changer);

function clinic_type_changer() {
    const clinic_type = clinic_type_dropdown.value;
    if (clinic_type == "general") {
        const numHandlerMajor1=document.getElementById("id_numberHandler-0-major");
        const numHandlerMajor1Label=document.querySelector('label[for="id_numberHandler-0-major"]');
        numHandlerMajor1.hidden = true;
        numHandlerMajor1Label.hidden = true;
        for (let i = 1; i < majorCount; i++) {
            const numhandlerMajorId = "id_numberHandler-" + i + "-major";
            const numhandlerMajor = document.getElementById(numhandlerMajorId);
            const numhandlerMajorLabel = document.querySelector('label[for="' + numhandlerMajorId + '"]');
            const numhandlerMinId = "id_numberHandler-" + i + "-min";
            const numhandlerMin = document.getElementById(numhandlerMinId);
            const numhandlerMinLabel = document.querySelector('label[for="' + numhandlerMinId + '"]');
            const numhandlerMaxId = "id_numberHandler-" + i + "-max";
            const numhandlerMax = document.getElementById(numhandlerMaxId);
            const numhandlerMaxLabel = document.querySelector('label[for="' + numhandlerMaxId + '"]');

            numhandlerMajor.hidden = true;
            numhandlerMajorLabel.hidden = true;
            numhandlerMin.hidden = true;
            numhandlerMinLabel.hidden = true;
            numhandlerMax.hidden = true;
            numhandlerMaxLabel.hidden = true;
        }
            const numhandlerGeneralId = "id_numberHandler-0-general";
            const numhandlerGeneral = document.getElementById(numhandlerGeneralId);
            numhandlerGeneral.checked = true;
    }
    else {
        for (let i = 0; i < majorCount; i++) {
            const numhandlerMajorId = "id_numberHandler-" + i + "-major";
            const numhandlerMajor = document.getElementById(numhandlerMajorId);
            const numhandlerMajorLabel = document.querySelector('label[for="' + numhandlerMajorId + '"]');
            const numhandlerMinId = "id_numberHandler-" + i + "-min";
            const numhandlerMin = document.getElementById(numhandlerMinId);
            const numhandlerMinLabel = document.querySelector('label[for="' + numhandlerMinId + '"]');
            const numhandlerMaxId = "id_numberHandler-" + i + "-max";
            const numhandlerMax = document.getElementById(numhandlerMaxId);
            const numhandlerMaxLabel = document.querySelector('label[for="' + numhandlerMaxId + '"]');
            
            numhandlerMajor.hidden = false;
            numhandlerMajorLabel.hidden = false;
            numhandlerMin.hidden = false;
            numhandlerMinLabel.hidden = false;
            numhandlerMax.hidden = false;
            numhandlerMaxLabel.hidden = false;
            
        }
        const numhandlerGeneralId = "id_numberHandler-0-general";
        const numhandlerGeneral = document.getElementById(numhandlerGeneralId);
        numhandlerGeneral.checked = false;
    }
}