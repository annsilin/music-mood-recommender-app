const dropArea = document.querySelector('.drop-area');
const fileInput = document.getElementById('file-input');
const uploadBtn = document.querySelector('.upload-btn');
const logs = document.querySelector('.log');
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

const fetchBackgroundJobs = async () => {
  try {
    const response = await fetch("/all-jobs");
    const data = await response.json();

    if (data.message === "No jobs found.") {
      document.querySelector(".log").innerHTML = "No jobs found.";
      return;
    }

    document.querySelector(".log").innerHTML = "";
    data.forEach((job) => {
      const jobElement = document.createElement("div");
      jobElement.innerHTML = `
          <p><strong>ID:</strong> ${job.id || "N/A"}</p>
          <p><strong>Function:</strong> ${job.function || "N/A"}</p>
          <p><strong>Status:</strong> ${job.status || "N/A"}</p>
          <p><strong>Created At:</strong> ${job.created_at || "N/A"}</p>
          <p><strong>Started At:</strong> ${job.started_at || "N/A"}</p>
          <p><strong>Progress:</strong> ${job.meta && job.meta.progress ? job.meta.progress + "%" : "N/A"}</p>
          <hr>
      `;
      document.querySelector(".log").appendChild(jobElement);
    });
  } catch (error) {
    console.error("Error fetching active jobs:", error);
  }
}


const getJobsBtn = document.querySelector('.get-jobs-btn');
getJobsBtn.addEventListener('click', fetchBackgroundJobs);

const deleteJobBtn = document.querySelector('.delete-job-btn');

deleteJobBtn.addEventListener('click', () => {
    const jobID = document.getElementById('delete-job').value;
    deleteJob(jobID);
});

const deleteJob = async (jobID) => {
        const queryParams = new URLSearchParams({
        job_id: jobID,
    });
    const url = `/delete-job?${queryParams.toString()}`;
    try {
        const response = await fetch(url, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': getCookie('csrf_access_token'),
            },
            credentials: 'include',
        });
        const data = await response.json();


        if (response.ok) {
            document.querySelector(".log").innerHTML = `${data.message}`;
            document.getElementById('delete-job').value = '';
        } else {
            throw new Error (`${data.error}`);
        }
    } catch (error) {
        console.error('Error deleting job:', error);
        document.querySelector(".log").innerHTML = `${error.message}`
    }
}