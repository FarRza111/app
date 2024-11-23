// Theme toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    // Get the theme toggle button
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;
    
    // Check for saved theme preference, otherwise use system preference
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Set initial theme
    if (savedTheme) {
        html.classList.toggle('dark', savedTheme === 'dark');
    } else {
        html.classList.toggle('dark', systemPrefersDark);
    }
    
    // Update icon based on current theme
    function updateIcon() {
        const isDark = html.classList.contains('dark');
        const sunIcon = themeToggle.querySelector('.sun-icon');
        const moonIcon = themeToggle.querySelector('.moon-icon');
        
        if (isDark) {
            sunIcon.classList.add('hidden');
            moonIcon.classList.remove('hidden');
        } else {
            sunIcon.classList.remove('hidden');
            moonIcon.classList.add('hidden');
        }
    }
    
    // Toggle theme
    themeToggle.addEventListener('click', function() {
        html.classList.toggle('dark');
        localStorage.setItem('theme', html.classList.contains('dark') ? 'dark' : 'light');
        updateIcon();
        
        // Add animation class
        themeToggle.classList.add('rotate-scale');
        setTimeout(() => {
            themeToggle.classList.remove('rotate-scale');
        }, 300);
    });
    
    // Initial icon update
    updateIcon();
});
