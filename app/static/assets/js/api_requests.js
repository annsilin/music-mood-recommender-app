/* Function to fetch songs from DB based on chosen mood and genre */
const fetchSongs = async (genre, normalizedX, normalizedY) => {
    startLoadingAnimation();
    const queryParams = new URLSearchParams({
        genre: genre,
        x: normalizedX,
        y: normalizedY
    });
    const url = `/get-songs?${queryParams.toString()}`;

    let songs;

    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        songs = await response.json();
    } catch (error) {
        console.error('Error fetching songs:', error);
    } finally {
        console.log(songs);
        stopLoadingAnimation();
        renderSongs(songs);
    }
};


/* Function to fetch genres from DB */
const fetchGenres = async () => {
    try {
        const genresResponse = await fetch('/get-genres');

        const genres = await genresResponse.json();
        renderGenres(genres);
    } catch (error) {
        console.error('Error fetching genres:', error);
    }
};


/* Function to submit username and password to login form */
const submitLoginForm = async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username,
                password
            })
        });

        if (response.ok) {
            window.location.replace('/admin');
        } else {
            document.getElementById("error").textContent = "Invalid username or password";
        }
    } catch (error) {
        console.error('Error:', error);
    }
};


/* Function to get cookie value by its name */
const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
};


/* Function to upload file and submit to backend */
const uploadFile = async () => {
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append('get-moods', getMoodsCheckbox.checked);
    formData.append('get-genres', getGenresCheckbox.checked);
    formData.append('get-album-covers', getAlbumCoversCheckbox.checked);

    fileUploadFormRender('upload-start');

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
            fileUploadFormRender('upload-success');
        } else {
            throw new Error(`${data.error}`)
        }
    } catch (error) {
        console.error('Error uploading file:', error.message);
        logs.textContent = `Error uploading file: ${error.message}`;
        fileUploadFormRender('upload-error');
    }
};


/* Function to fetch statuses of all background jobs */
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
            renderJobStatus(job);
        });
    } catch (error) {
        console.error("Error fetching active jobs:", error);
    }
};


/* Function to remove background job by its ID */
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
            throw new Error(`${data.error}`);
        }
    } catch (error) {
        console.error('Error deleting job:', error);
        document.querySelector(".log").innerHTML = `${error.message}`
    }
}