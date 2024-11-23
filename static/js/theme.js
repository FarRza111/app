// Theme handling
document.addEventListener('alpine:init', () => {
    Alpine.data('theme', () => ({
        isDark: localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches),
        toggleTheme() {
            this.isDark = !this.isDark;
            localStorage.theme = this.isDark ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', localStorage.theme);
        },
        init() {
            document.documentElement.setAttribute('data-theme', this.isDark ? 'dark' : 'light');
        }
    }));
});

// Add animations to elements when they become visible
const animateOnScroll = () => {
    const elements = document.querySelectorAll('.animate-on-scroll');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });
    
    elements.forEach(element => observer.observe(element));
};

// Initialize animations
document.addEventListener('DOMContentLoaded', animateOnScroll);
