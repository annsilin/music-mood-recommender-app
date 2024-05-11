/* Function to fetch songs from DB based on chosen mood and genre */
const fetchSongs = async (genre, normalizedX, normalizedY) => {
    startLoadingAnimation();
    const data = {'genre': genre, 'x': normalizedX, 'y': normalizedY};
    console.log(data)
    const options = {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data),
    };

    let songs;

    try {
        const response = await fetch('/get-songs', options);
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