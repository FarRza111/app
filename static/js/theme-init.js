// Theme initialization
function initTheme() {
    const theme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (theme === 'light' || (!theme && !prefersDark)) {
        document.documentElement.classList.add('light');
    }
}

// Theme toggle functionality
function toggleTheme() {
    const root = document.documentElement;
    const toggleButton = document.getElementById('theme-toggle');
    const sunIcon = document.getElementById('sun-icon');
    const moonIcon = document.getElementById('moon-icon');

    root.classList.toggle('light');
    const isLight = root.classList.contains('light');
    
    // Store theme preference
    localStorage.setItem('theme', isLight ? 'light' : 'dark');
    
    // Animate icons
    if (isLight) {
        moonIcon.style.display = 'none';
        sunIcon.style.display = 'block';
        sunIcon.classList.add('rotate-scale');
    } else {
        sunIcon.style.display = 'none';
        moonIcon.style.display = 'block';
        moonIcon.classList.add('rotate-scale');
    }
    
    // Remove animation class after transition
    setTimeout(() => {
        sunIcon.classList.remove('rotate-scale');
        moonIcon.classList.remove('rotate-scale');
    }, 300);
}

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', initTheme);

// Add event listener to theme toggle button
const themeToggle = document.getElementById('theme-toggle');
if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
}

// Modal Functions
function openMeetingModal() {
    const modal = document.getElementById('meetingModal');
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeMeetingModal() {
    const modal = document.getElementById('meetingModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('meetingModal');
    if (event.target === modal) {
        closeMeetingModal();
    }
}

// Form submission
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('meetingForm');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = {
                name: form.name.value,
                email: form.email.value,
                phone: form.phone.value,
                message: form.message.value
            };

            try {
                // Send data to backend
                const response = await fetch('/api/book-meeting', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (response.ok) {
                    // Show success message
                    alert(data.message);
                    
                    // Clear form and close modal
                    form.reset();
                    closeMeetingModal();
                } else {
                    // Show error message
                    alert(data.detail || 'Xəta baş verdi. Zəhmət olmasa bir az sonra yenidən cəhd edin.');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Xəta baş verdi. Zəhmət olmasa bir az sonra yenidən cəhd edin.');
            }
        });
    }
});
