function updateTitlePreview() {
    const titleInput = document.getElementById('id_title');
    const titlePreviewFront = document.getElementById('clinic-title-front');
    const titlePreviewBack = document.getElementById('clinic-title-back');

    // titlePreviewFront.innerHTML = '';
    // titlePreviewBack.innerHTML = '';

    titlePreviewFront.textContent = titleInput.value || 'Clinic Title';
    titlePreviewBack.textContent = titleInput.value || 'Clinic Title';

    textFit(titlePreviewFront, {maxFontSize: 24, multiLine: true});
    textFit(titlePreviewBack, {maxFontSize: 24, multiLine: true});
}

function updateDepartmentColorPreview() {
    const majorInput = document.getElementById('id_department');
    const itemElementFront = document.querySelector('.item');
    const itemElementBack = document.querySelector('.item.back');
    const PIElementFront = document.querySelector('.pop-index');
    const PIElementBack = document.getElementById('pop-index-back');
    const majorValue = majorInput ? majorInput.value : '';

    if (!majorValue) {
        if (itemElementFront) itemElementFront.style.background = '#ffffff';
        if (itemElementBack) itemElementBack.style.background = '#ffffff';
        if (PIElementFront) PIElementFront.style.color = '#000000';
        if (PIElementBack) PIElementBack.style.color = '#000000';
        return;
    }

    fetch(`/api/major/${encodeURIComponent(majorValue)}/`)
    .then(response => {
        if (!response.ok) throw new Error(`Failed to load major color (${response.status})`);
        return response.json();
    })
    .then(data => {
        if (itemElementFront) itemElementFront.style.background = data.color;
        if (itemElementBack) itemElementBack.style.background = data.color;
        if (PIElementFront) PIElementFront.style.color = data.color;
        if (PIElementBack) PIElementBack.style.color = data.color;
    })
    .catch(error => {
        console.error("Error loading major color:", error);
    });
}

function updateImagePreview() {
    const imageInput = document.getElementById('id_image');
    const imagePreview = document.getElementById('image-slot');
    
    const file = imageInput.files[0];
    if (file) {
        const reader = new FileReader();
        imagePreview.textContent = '';
        reader.onload = function(e) {
            imagePreview.style.backgroundImage = `url(${e.target.result})`;
            imagePreview.style.backgroundSize = 'cover';
            imagePreview.style.backgroundPosition = 'center';
        }
        reader.readAsDataURL(file);
    } else {
        const imageLink = document.querySelector('a');
        if (imageLink) {
            console.log(imageLink.href);
            imagePreview.textContent = '';
            imagePreview.style.backgroundSize = 'cover';
            imagePreview.style.backgroundPosition = 'center';
            imagePreview.style.backgroundImage = `url(${imageLink.href})`;
        }
        else {
            imagePreview.textContent = 'Image Slot';
            imagePreview.style.backgroundImage = '';
        }
    }
}

function updateLinkPreview() {
    const linkInput = document.getElementById('id_links');
    const linkPreview = document.getElementById('link-list');
    
    const linksText = linkInput.value.replace(/[\[\]]/g, '');
    const links = linksText.split('\n').filter(link => link.trim() !== '');
    
    linkPreview.innerHTML = '';
    if (links.length > 0) {
        const div = document.createElement('div');
        div.textContent = "Learn More: ";
        linkPreview.appendChild(div);
    }
    links.forEach((link, index) => {
        const div = document.createElement('div');
        const a = document.createElement('a');
        a.href = link;
        a.textContent = `[${index + 1}]`;
        a.target = '_blank';
        div.appendChild(a);
        linkPreview.appendChild(div);
    });
}

function updateDescriptionPreview() {
    const descriptionInput = document.getElementById('id_description');
    const descriptionPreview = document.getElementById('clinic-description');
    
    descriptionPreview.textContent = descriptionInput.value || 'Clinic Description';
}

function generalVsSpecificPreview() {
    const isGeneral = document.getElementById('clinic_type').value == "general";
    const specificRequestHolder = document.getElementById('specific-request-holder');
    const generalRequestHolder = document.getElementById('general-request-holder');

    if (isGeneral) {
        specificRequestHolder.classList.add('hidden');
        generalRequestHolder.classList.remove('hidden');
        console.log('isGeneral');
    } else {
        specificRequestHolder.classList.remove('hidden');
        generalRequestHolder.classList.add('hidden');
        console.log('isSpecific');
    }
}

function updateNumberHandlerPreview() {
    const isGeneral = document.getElementById('clinic_type').value == "general";
    const specificRequestHolder = document.getElementById('specific-request-holder');
    const generalRequestHolder = document.getElementById('general-request-holder');
    let specificRequestArray = Array.from(specificRequestHolder.children);

    if (isGeneral) {
        let generalMax = document.getElementById('id_numberHandler-0-max').value;
        generalRequestHolder.textContent = "General: " + generalMax;
    } else {
        for (let i = 0; i < specificRequestArray.length; i++) {
            let specificMax = document.getElementById('id_numberHandler-' + i + '-max').value;
            if (specificMax == '') 
                specificMax = 'NULL';
            specificRequestArray[i].textContent = specificMax;
        }
    }

}

document.getElementById('id_description').addEventListener('input', updateDescriptionPreview);

document.getElementById('id_links').addEventListener('input', updateLinkPreview);

document.getElementById('id_image').addEventListener('change', updateImagePreview);

document.getElementById('id_department').addEventListener('input', updateDepartmentColorPreview);

document.getElementById('id_title').addEventListener('input', updateTitlePreview);

document.getElementById('clinic_type').addEventListener('input', generalVsSpecificPreview);

document.getElementById('submission-form').addEventListener('input', updateNumberHandlerPreview);

window.addEventListener('load', function () {
    updateDescriptionPreview();
    updateLinkPreview();
    updateImagePreview();
    updateDepartmentColorPreview();
    updateTitlePreview();
    //generalVsSpecificPreview();
    //updateNumberHandlerPreview(); Moved to clinic_submit.js to run after initial dropdown change script
});