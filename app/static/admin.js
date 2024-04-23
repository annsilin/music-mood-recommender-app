const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('file-input');
const progress = document.getElementById('progress');
const uploadBtn = document.getElementById('upload-btn');
const message = document.getElementById('message');

const handleDragOver = (event) => {
    event.preventDefault();
    dropArea.classList.add('hover');
};

const handleDragLeave = (event) => {
    event.preventDefault();
    dropArea.classList.remove('hover');
};

const handleDrop = (event) => {
    event.preventDefault();
    dropArea.classList.remove('hover');
    const file = event.dataTransfer.files[0];
    if (file.type !== 'text/csv') {
        message.textContent = 'Invalid file type. Please upload a CSV file.';
        return;
    }
    fileInput.files = file;
    uploadBtn.disabled = false; // Enable upload button
};

const handleInputChange = (event) => {
    const file = event.target.files[0];
    if (file.type !== 'text/csv') {
        message.textContent = 'Invalid file type. Please upload a CSV file.';
        return;
    }
    uploadBtn.disabled = false; // Enable upload button
};

const uploadFile = async () => {
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    uploadBtn.disabled = true; // Disable upload button again
    message.textContent = 'Uploading...';

    try {
        const response = await fetch('/process_csv', {
            method: 'POST',
            body: formData,
        });
        const data = await response.json();

        if (data.success) {
            message.textContent = data.message;
            fileInput.value = ''; // Clear file input after successful upload
            uploadBtn.disabled = true; // Keep upload button disabled until new file is selected
        }
    } catch (error) {
        console.error('Error uploading file:', error);
        message.textContent = 'An error occurred while uploading the file.';
        uploadBtn.disabled = false; // Re-enable upload button on error
    } finally {
        progress.style.width = '0%'; // Reset progress bar
    }
};

// Event listeners
dropArea.addEventListener('dragover', handleDragOver);
dropArea.addEventListener('dragleave', handleDragLeave);
dropArea.addEventListener('drop', handleDrop);
fileInput.addEventListener('change', handleInputChange);
uploadBtn.addEventListener('click', uploadFile);

