const moodSlider = document.getElementById('square');
const moodPointer = document.getElementById('circle');
let offsetX, offsetY;
let normalizedX = 0.5, normalizedY = 0.5;

// Set initial position of the moodPointer to the center of the moodSlider
moodPointer.style.transform = `translate(${(moodSlider.clientWidth - moodPointer.clientWidth) / 2}px, ${(moodSlider.clientHeight - moodPointer.clientHeight) / 2}px)`;

/* Function to handle mousedown event for 2D mood slider*/
const handleMouseDown = (e) => {
    e.preventDefault();
    // Calculate offset from the center of the moodPointer
    const circleRect = moodPointer.getBoundingClientRect();
    offsetX = e.clientX - circleRect.left;
    offsetY = e.clientY - circleRect.top;
    // Add event listeners for mousemove and mouseup events
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
}

/* Function to handle mouse move event for 2D mood slider */
const handleMouseMove = (e) => {
    // Calculate new position of the moodPointer based on mouse position and initial offset
    const x = e.clientX - offsetX - moodSlider.getBoundingClientRect().left;
    const y = e.clientY - offsetY - moodSlider.getBoundingClientRect().top;
    // Clamp the moodPointer position within the moodSlider bounds
    const clampedX = Math.min(moodSlider.clientWidth - moodPointer.clientWidth, Math.max(0, x));
    const clampedY = Math.min(moodSlider.clientHeight - moodPointer.clientHeight, Math.max(0, y));
    // Move the moodPointer using CSS transform
    moodPointer.style.transform = `translate(${clampedX}px, ${clampedY}px)`;
    // Calculate normalized coordinates
    normalizedX = (clampedX / (moodSlider.clientWidth - moodPointer.clientWidth)).toFixed(2);
    normalizedY = (1 - (clampedY / (moodSlider.clientHeight - moodPointer.clientHeight))).toFixed(2);
    console.log(`X: ${normalizedX}, Y: ${normalizedY}`,
        `happy: ${normalizedX * normalizedY}`,
        `aggressive: ${(1 - normalizedX) * normalizedY}`,
        `sad: ${(1 - normalizedX) * (1 - normalizedY)}`,
        `calm: ${normalizedX * (1 - normalizedY)}`);
}

/* Function to handle mouse up event for 2D mood slider */
const handleMouseUp = () => {
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
}

/* Function to handle touch start event for 2D mood slider */
const handleTouchStart = (e) => {
    e.preventDefault();
    // Calculate offset from the center of the moodPointer for touch events
    const circleRect = moodPointer.getBoundingClientRect();
    offsetX = e.touches[0].clientX - circleRect.left;
    offsetY = e.touches[0].clientY - circleRect.top;
};

/* Function to handle touch move event for 2D mood slider */
const handleTouchMove = (e) => {
    e.preventDefault();
    // Calculate new position of the moodPointer based on touch position and initial offset
    const x = e.touches[0].clientX - offsetX - moodSlider.getBoundingClientRect().left;
    const y = e.touches[0].clientY - offsetY - moodSlider.getBoundingClientRect().top;
    // Clamp the moodPointer position within the moodSlider bounds
    const clampedX = Math.min(moodSlider.clientWidth - moodPointer.clientWidth, Math.max(0, x));
    const clampedY = Math.min(moodSlider.clientHeight - moodPointer.clientHeight, Math.max(0, y));
    // Move the moodPointer using CSS transform
    moodPointer.style.transform = `translate(${clampedX}px, ${clampedY}px)`;
    // Calculate normalized coordinates
    normalizedX = (clampedX / (moodSlider.clientWidth - moodPointer.clientWidth)).toFixed(2);
    normalizedY = (1 - (clampedY / (moodSlider.clientHeight - moodPointer.clientHeight))).toFixed(2);
    console.log(`X: ${normalizedX}, Y: ${normalizedY}`);
}