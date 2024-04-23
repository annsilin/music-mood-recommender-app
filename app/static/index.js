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

btnGeneratePlaylist.addEventListener('click', () => fetchSongs(getSelectedGenreId(), normalizedX, normalizedY));
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
