function updateTitlePreview() {
    const titleInput = document.getElementById('id_title');
    const titlePreviewFront = document.getElementById('clinic-title-front');
    const titlePreviewBack = document.getElementById('clinic-title-back');

    titlePreviewFront.textContent = titleInput.value || 'Clinic Title';
    titlePreviewBack.textContent = titleInput.value || 'Clinic Title';
}

function updateDepartmentColorPreview() {
    const majorInput = document.getElementById('id_department');
    const itemElementFront = document.querySelector('.item');
    const itemElementBack = document.querySelector('.item.back');
    const majorValue = majorInput ? majorInput.value : '';

    if (!majorValue) {
        if (itemElementFront) itemElementFront.style.background = '#ffffff';
        if (itemElementBack) itemElementBack.style.background = '#ffffff';
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
        imagePreview.style.backgroundImage = '';
    }
}

function updateLinkPreview() {
    const linkInput = document.getElementById('id_links');
    const linkPreview = document.getElementById('link-list');
    
    const linksText = linkInput.value;
    const links = linksText.split('\n').filter(link => link.trim() !== '');
    
    linkPreview.innerHTML = '';
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

document.getElementById('id_description').addEventListener('input', updateDescriptionPreview);

document.getElementById('id_links').addEventListener('input', updateLinkPreview);

document.getElementById('id_image').addEventListener('change', updateImagePreview);

document.getElementById('id_department').addEventListener('input', updateDepartmentColorPreview);

document.getElementById('id_title').addEventListener('input', updateTitlePreview);