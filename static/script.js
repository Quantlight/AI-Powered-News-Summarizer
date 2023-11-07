// Define variables for key elements
const themeToggle = document.getElementById('theme-toggle');
const themeLight = document.getElementById('theme-light');
const themeDark = document.getElementById('theme-dark');
const themeCustom = document.getElementById('theme-custom');
const body = document.body;

// Retrieve current theme from local storage or default to 'light'
let currentTheme = localStorage.getItem('theme')|| 'light';

// Function to set theme
function setTheme(theme) {
    // Remove any previous theme classes
    body.classList.remove('light-theme', 'dark-theme', 'custom-theme');

    // Add the chosen theme class
    body.classList.add(theme);

    // Update the current theme in local storage
    localStorage.setItem('theme', theme);

    // Update the currentTheme variable
    currentTheme = theme;
}

// Event listener for themeToggle click
themeToggle.addEventListener('click', () => {
    // Cycle through possible theme choices
    if (currentTheme === 'light') {
        setTheme('dark-theme');
    } else if (currentTheme === 'dark-theme') {
        setTheme('custom-theme');
    } else if (currentTheme === 'custom-theme') {
        setTheme('light-theme');
    } else if (currentTheme === 'light-theme') {
        setTheme('dark-theme');
    }
});

// Event listeners to set specific themes on button click
themeLight.addEventListener('click', () => setTheme('light-theme'));
themeDark.addEventListener('click', () => setTheme('dark-theme'));
themeCustom.addEventListener('click', () => setTheme('custom-theme'));

// Set the initial theme when the page loads
setTheme(currentTheme);

// Initialize Materialize's custom select elements
document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('select');
    var instances = M.FormSelect.init(elems);
});