const btnGeneratePlaylist = document.getElementById('generate-playlist');
const btnsScrollSections = document.querySelectorAll('.large-btn');

moodPointer.addEventListener('mousedown', handleMouseDown);
moodPointer.addEventListener('touchstart', handleTouchStart);
moodPointer.addEventListener('touchmove', handleTouchMove);

/* Function to get id of selected genre */
const getSelectedGenreId = () => {
    const selectedGenre = document.querySelector('input[type="radio"]:checked');
    if (selectedGenre) {
        return selectedGenre.id;
    } else {
        return null;
    }
};

btnGeneratePlaylist.addEventListener('click', () => {
    const genre = getSelectedGenreId();
    if (genre) {
        displaySongsSection();
        fetchSongs(getSelectedGenreId(), normalizedX, normalizedY);
    } else {
        alert('Выберите жанр!');
    }
});
document.addEventListener("DOMContentLoaded", fetchGenres);

/* Function to scroll to the next section */
const scrollToNextSection = () => {
    const sections = document.querySelectorAll('section');
    const currentIndex = Array.from(sections).findIndex(section => section.getBoundingClientRect().top >= 0);
    if (currentIndex < sections.length - 1) {
        sections[currentIndex + 1].scrollIntoView({behavior: 'smooth'});
    }
}

btnsScrollSections.forEach(button => {
    button.addEventListener('click', scrollToNextSection);
});


document.addEventListener('DOMContentLoaded', () => {
    const addCopyEventListener = (element) => {
        element.addEventListener('copy', (event) => {
            event.preventDefault();
            const fullText = element.getAttribute('title');
            if (event.clipboardData) {
                event.clipboardData.setData('text/plain', fullText);
            } else if (window.clipboardData) {
                window.clipboardData.setData('Text', fullText);
            }
        });
    };

    // Select all elements with class 'songs-list__artist' and 'songs-list__track'
    const artistElements = document.querySelectorAll('.songs-list__artist');
    const trackElements = document.querySelectorAll('.songs-list__track');

    // Add copy event listener to each artist element
    artistElements.forEach(addCopyEventListener);

    // Add copy event listener to each track element
    trackElements.forEach(addCopyEventListener);
});