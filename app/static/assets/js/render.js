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

/* Function to create HTML element for song */
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

    const songName = document.createElement('span');
    songName.classList.add('songs-list__track');
    songName.textContent = song.track_name;

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