/* Function to render genres on HTML page */
const renderGenres = (genres) => {
    const genresContainer = document.querySelector('.genres-container');
    genresContainer.innerHTML = '';

    genres.forEach(genre => {
        const radioDiv = createGenreElement(genre);
        genresContainer.appendChild(radioDiv);
    });
};

/* Function to create HTML element for genre */
const createGenreElement = (genre) => {
    const genreItem = document.createElement('div');
    genreItem.classList.add('genre-radio');

    const radioInput = document.createElement('input');
    radioInput.type = 'radio';
    radioInput.id = genre.id;
    radioInput.name = 'genres-radios';

    const label = document.createElement('label');
    label.htmlFor = genre.id;
    label.textContent = genre.name;

    genreItem.appendChild(radioInput);
    genreItem.appendChild(label);

    return genreItem;
};

/* Function to render songs on HTML page */
const renderSongs = (songs) => {
    const songsContainer = document.querySelector('.songs-list');
    songsContainer.innerHTML = '';

    songs.forEach(song => {
        const songItem = createSongElement(song);
        songsContainer.appendChild(songItem);
    });
};

const displaySongsSection = () => {
    document.querySelector('.section-songs').style.display = 'flex';
}

/* Function to create HTML element for the song */
const createSongElement = (song) => {
    const songItem = document.createElement('li');
    songItem.classList.add('songs-list__item');

    const songContainer = document.createElement('div');
    songContainer.classList.add('songs-list__container');

    const songCover = document.createElement('img');
    songCover.classList.add('songs-list__cover');
    songCover.src = song.album_cover ? song.album_cover : 'https://iili.io/HlHy9Yx.png';
    songCover.alt = 'album cover';

    const artistTrackContainer = document.createElement('div');
    artistTrackContainer.classList.add('songs-list__artist-track');

    const songArtist = document.createElement('span');
    songArtist.classList.add('songs-list__artist');
    songArtist.textContent = song.artist_name;
    songArtist.title = song.artist_name;

    const songName = document.createElement('span');
    songName.classList.add('songs-list__track');
    songName.textContent = song.track_name;
    songName.title = song.track_name;

    const addCopyEventListener = (element) => {
        element.addEventListener('copy', (e) => {
            e.preventDefault();
            const fullText = element.getAttribute('title');
            if (e.clipboardData) {
                e.clipboardData.setData('text/plain', fullText);
            } else if (window.clipboardData) {
                window.clipboardData.setData('Text', fullText);
            }
        });
    };

    addCopyEventListener(songArtist);
    addCopyEventListener(songName);

    artistTrackContainer.appendChild(songArtist);
    artistTrackContainer.appendChild(songName);

    songContainer.appendChild(songCover);
    songContainer.appendChild(artistTrackContainer);

    songItem.appendChild(songContainer);

    return songItem;
};

/* Function to display loading animation */
const startLoadingAnimation = () => {
    const loadingAnimation = document.querySelector('.loading-animation');
    loadingAnimation.style.display = 'block';

    const sectionSongs = document.querySelector('.section-songs');
    sectionSongs.style.height = '100vh';

    const sectionSongsContent = sectionSongs.querySelector('.section__content');
    sectionSongsContent.style.display = 'none';

};

/* Function to stop displaying loading animation */
const stopLoadingAnimation = () => {
    const loadingAnimation = document.querySelector('.loading-animation')
    loadingAnimation.style.display = 'none';

    const sectionSongs = document.querySelector('.section-songs')
    sectionSongs.style.height = 'auto';

    const sectionSongsContent = sectionSongs.querySelector('.section__content');
    sectionSongsContent.style.display = 'flex';
};


/* Function to change the look of upload form elements depending on status */
const fileUploadFormRender = (status) => {
    if (status === 'upload-start') {
        uploadBtn.disabled = true;
        getMoodsCheckbox.disabled = true;
        getGenresCheckbox.disabled = true;
        getAlbumCoversCheckbox.disabled = true;
        logs.textContent = 'Uploading...';
    }
    if (status === 'upload-success') {
        fileInput.value = '';
        uploadBtn.disabled = true;
        getMoodsCheckbox.disabled = false;
        getGenresCheckbox.disabled = false;
        getAlbumCoversCheckbox.disabled = false;
    }
    if (status === 'upload-error') {
        uploadBtn.disabled = false;
        getMoodsCheckbox.disabled = false;
        getGenresCheckbox.disabled = false;
        getAlbumCoversCheckbox.disabled = false;
    }
};


/* Function to render background job status */
const renderJobStatus = (job) => {
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
};

/* Function to render songs by genres in log window */
const renderSongsByGenre = (songs) => {
    logs.innerHTML = "";

    songs.forEach(song => {
        const genreElement = document.createElement("div");
        genreElement.textContent = `${song.genre}: ${song.count}`;
        logs.appendChild(genreElement);
    });
};