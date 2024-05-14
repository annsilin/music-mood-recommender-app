const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');
const message = document.getElementById('message');
const getMoodsCheckbox = document.getElementById('get-moods');
const getGenresCheckbox = document.getElementById('get-genres');

const socket = io();

console.log(socket);

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

    message.textContent = 'Uploading...';

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
            message.textContent = data.message;
            fileInput.value = '';
        } else {
            throw new Error(`${data.error}`)
        }
    } catch (error) {
        console.error('Error uploading file:', error.message);
        message.textContent = `Error uploading file: ${error.message}`;
    }
};

// Event listeners
dropArea.addEventListener('dragover', handleDragOver);
dropArea.addEventListener('dragleave', handleDragLeave);
dropArea.addEventListener('drop', handleDrop);
fileInput.addEventListener('change', handleInputChange);
uploadBtn.addEventListener('click', uploadFile);

socket.on('log_message', (message) => {
    console.log(message)
    const logContainer = document.getElementById('log');
    logContainer.innerHTML += '<p>' + message + '</p>';
});

const changeUI = (status) => {
    if (status) {
        fileInput.disabled = true;
        uploadBtn.disabled = true;
        getMoodsCheckbox.disabled = true;
        getGenresCheckbox.disabled = true;
    } else {
        uploadBtn.disabled = true;
        fileInput.disabled = false;
        getMoodsCheckbox.disabled = false;
        getGenresCheckbox.disabled = false;
    }
}

socket.on('in-progress', (status) => {
    changeUI(status);
});
