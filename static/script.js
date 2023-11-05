const themeToggle = document.getElementById('theme-toggle');
const themeLight = document.getElementById('theme-light');
const themeDark = document.getElementById('theme-dark');
const themeCustom = document.getElementById('theme-custom');
const body = document.body;
let currentTheme = localStorage.getItem('theme') || 'light';

// Function to convert Markdown to HTML
function convertMarkdownToHTML(markdown) {
    return marked(markdown);
}

function setTheme(theme) {
    body.classList.remove('light-theme', 'dark-theme', 'custom-theme');
    body.classList.add(theme);
    localStorage.setItem('theme', theme);
    currentTheme = theme;
}

themeToggle.addEventListener('click', () => {
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

themeLight.addEventListener('click', () => setTheme('light-theme'));
themeDark.addEventListener('click', () => setTheme('dark-theme'));
themeCustom.addEventListener('click', () => setTheme('custom-theme'));

setTheme(currentTheme);

// Replace the content of elements with class "markdown-content" with the converted HTML
document.querySelectorAll('.markdown-content').forEach((element) => {
    const markdown = element.textContent; // Get the Markdown content
    const html = convertMarkdownToHTML(markdown); // Convert to HTML
    element.innerHTML = html; // Replace the content with HTML
});

//  Materialize’s custom select elements require initialization before they function properly
document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('select');
    var instances = M.FormSelect.init(elems);
});
