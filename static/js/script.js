// script.js

// Wait for the DOM to be ready
document.addEventListener("DOMContentLoaded", function() {
    const themeToggle = document.getElementById('theme-toggle'); // The night mode toggle checkbox
    const body = document.body; // The body element

    // Check if night mode is already enabled (this can be done by checking the body's class)
    if (localStorage.getItem('theme') === 'night-mode') {
        body.classList.add('night-mode');
        body.classList.remove('light-mode');
        themeToggle.checked = true; // Keep the checkbox checked if night mode is on
    }

    // Listen for the checkbox change event
    themeToggle.addEventListener('change', function() {
        if (themeToggle.checked) {
            // Enable night mode
            body.classList.add('night-mode');
            body.classList.remove('light-mode');
            localStorage.setItem('theme', 'night-mode'); // Save user preference in localStorage
        } else {
            // Disable night mode
            body.classList.add('light-mode');
            body.classList.remove('night-mode');
            localStorage.setItem('theme', 'light-mode'); // Save user preference in localStorage
        }
    });
});

