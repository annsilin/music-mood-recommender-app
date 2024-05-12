const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');
const message = document.getElementById('message');

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
        message.textContent = 'Invalid file type. Please upload a CSV file.';
        return;
    }
    fileInput.files = file;
    uploadBtn.disabled = false;
};

const handleInputChange = (e) => {
    const file = e.target.files[0];
    if (file.type !== 'text/csv') {
        message.textContent = 'Invalid file type. Please upload a CSV file.';
        return;
    }
    uploadBtn.disabled = false;
};

const uploadFile = async () => {
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    const getMoodsCheckbox = document.getElementById('get-moods');
    const getGenresCheckbox = document.getElementById('get-genres');

    formData.append('get-moods', getMoodsCheckbox.checked);
    formData.append('get-genres', getGenresCheckbox.checked);

    uploadBtn.disabled = true;
    getMoodsCheckbox.disabled = true;
    getGenresCheckbox.disabled = true;
    message.textContent = 'Uploading...';

    try {
        const response = await fetch('/process_csv', {
            method: 'POST',
            body: formData,
        });

        const data = await response.json();

        if (response.ok) {
            message.textContent = data.message;
            fileInput.value = '';
            uploadBtn.disabled = true;
            getMoodsCheckbox.disabled = false;
            getGenresCheckbox.disabled = false;
        } else {
            throw new Error(`${data.error}`)
        }
    } catch (error) {
        console.error('Error uploading file:', error.message);
        message.textContent = `Error uploading file: ${error.message}`;
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

