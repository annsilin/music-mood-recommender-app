const dropArea = document.querySelector('.drop-area');
const fileInput = document.getElementById('file-input');
const uploadBtn = document.querySelector('.upload-btn');
const logs = document.querySelector('.log');
const getMoodsCheckbox = document.getElementById('get-moods');
const getGenresCheckbox = document.getElementById('get-genres');
const getAlbumCoversCheckbox = document.getElementById('get-album-covers');
const getJobsBtn = document.querySelector('.get-jobs-btn');
const deleteJobBtn = document.querySelector('.delete-job-btn');


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


/* Event listeners */
dropArea.addEventListener('dragover', handleDragOver);
dropArea.addEventListener('dragleave', handleDragLeave);
dropArea.addEventListener('drop', handleDrop);
fileInput.addEventListener('change', handleInputChange);
uploadBtn.addEventListener('click', uploadFile);
getMoodsCheckbox.addEventListener('change', (e) => {
    if (e.target.checked) {
        document.querySelector('.table-block_features').removeAttribute('hidden');
        document.querySelector('.table-block_predictions').setAttribute('hidden', 'true');
    } else {
        document.querySelector('.table-block_features').setAttribute('hidden', 'true');
        document.querySelector('.table-block_predictions').removeAttribute('hidden');
    }
});
getGenresCheckbox.addEventListener('change', (e) => {
    if (e.target.checked) {
        document.querySelector('.table-block_genre').setAttribute('hidden', 'true');
    } else {
        document.querySelector('.table-block_genre').removeAttribute('hidden');
    }
});

getAlbumCoversCheckbox.addEventListener('change', (e) => {
    if (e.target.checked) {
        document.querySelector('.table-block_album-cover').setAttribute('hidden', 'true');
    } else {
        document.querySelector('.table-block_album-cover').removeAttribute('hidden');
    }
});

getJobsBtn.addEventListener('click', fetchBackgroundJobs);

deleteJobBtn.addEventListener('click', () => {
    const jobID = document.getElementById('delete-job').value;
    deleteJob(jobID);
});

