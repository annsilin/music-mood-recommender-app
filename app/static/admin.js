const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');
const logs = document.getElementById('log');
const getMoodsCheckbox = document.getElementById('get-moods');
const getGenresCheckbox = document.getElementById('get-genres');

const handleDragOver = (e) => {
    e.preventDefault();
    dropArea.classList.add('hover');
};

const handleDragLeave = (e) => {
    e.preventDefault();
    dropArea.classList.remove('hover');
};

const handleDrop = (e) => {
    e.preventDefault();
    dropArea.classList.remove('hover');
    const file = e.dataTransfer.files[0];
    if (file.type !== 'text/csv') {
        logs.textContent = 'Invalid file type. Please upload a CSV file.';
        return;
    }
    fileInput.files = file;
    uploadBtn.disabled = false;
};

const handleInputChange = (e) => {
    const file = e.target.files[0];
    if (file.type !== 'text/csv') {
        logs.textContent = 'Invalid file type. Please upload a CSV file.';
        return;
    }
    uploadBtn.disabled = false;
};

const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

const uploadFile = async () => {
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    formData.append('get-moods', getMoodsCheckbox.checked);
    formData.append('get-genres', getGenresCheckbox.checked);

    uploadBtn.disabled = true;
    getMoodsCheckbox.disabled = true;
    getGenresCheckbox.disabled = true;
    logs.textContent = 'Uploading...';

    try {
        const response = await fetch('/process-csv', {
            method: 'POST',
            headers: {
                'X-CSRF-TOKEN': getCookie('csrf_access_token'),
            },
            body: formData,
            credentials: 'include',
        });

        const data = await response.json();

        if (response.ok) {
            logs.textContent = data.message;
            fileInput.value = '';
            uploadBtn.disabled = true;
            getMoodsCheckbox.disabled = false;
            getGenresCheckbox.disabled = false;
        } else {
            throw new Error(`${data.error}`)
        }
    } catch (error) {
        console.error('Error uploading file:', error.message);
        logs.textContent = `Error uploading file: ${error.message}`;
        uploadBtn.disabled = false;
        getMoodsCheckbox.disabled = false;
        getGenresCheckbox.disabled = false;
    }
};

// Event listeners
dropArea.addEventListener('dragover', handleDragOver);
dropArea.addEventListener('dragleave', handleDragLeave);
dropArea.addEventListener('drop', handleDrop);
fileInput.addEventListener('change', handleInputChange);
uploadBtn.addEventListener('click', uploadFile);
getMoodsCheckbox.addEventListener('change', (e) => {
    if (e.target.checked) {
        document.querySelector('.table-block_features').removeAttribute('hidden');
        document.querySelector('.table-block_predictions').setAttribute('hidden', 'true')
    } else {
        document.querySelector('.table-block_features').setAttribute('hidden', 'true')
        document.querySelector('.table-block_predictions').removeAttribute('hidden');
    }
})
getGenresCheckbox.addEventListener('change', (e) => {
    if (e.target.checked) {
        document.querySelector('.table-block_genre').setAttribute('hidden', 'true');
    } else {
        document.querySelector('.table-block_genre').removeAttribute('hidden');
    }
})