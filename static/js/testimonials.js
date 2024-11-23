document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('testimonials-container');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const dotsContainer = document.getElementById('testimonial-dots');
    
    let currentSlide = 0;
    let testimonials = [];
    let autoSlideInterval;

    // Fetch testimonials from API
    async function fetchTestimonials() {
        try {
            const response = await fetch('/api/testimonials/latest/6');
            testimonials = await response.json();
            renderTestimonials();
            renderDots();
            startAutoSlide();
        } catch (error) {
            console.error('Error fetching testimonials:', error);
            // Use sample testimonials as fallback
            testimonials = [
                {
                    author_name: "Əli Məmmədov",
                    content: "Fariz müəllimin Python kursunda iştirak etmək mənim üçün çox faydalı oldu. Onun praktiki yanaşması və real layihələr üzərində işləmək imkanı mənim proqramlaşdırma bacarıqlarımı xeyli inkişaf etdirdi.",
                    rating: 5
                },
                {
                    author_name: "Aynur Hüseynova",
                    content: "Data Science kursunda əldə etdiyim biliklər sayəsində iş həyatımda böyük irəliləyiş əldə etdim. Fariz müəllimin peşəkar təcrübəsi və dəstəyi çox dəyərli idi.",
                    rating: 5
                },
                {
                    author_name: "Orxan Əliyev",
                    content: "Machine Learning kursunda öyrəndiklərim mənim üçün yeni qapılar açdı. Nəzəri biliklərlə yanaşı, praktiki təcrübə qazanmaq imkanı da çox əhəmiyyətli idi.",
                    rating: 5
                }
            ];
            renderTestimonials();
            renderDots();
            startAutoSlide();
        }
    }

    function renderTestimonials() {
        container.innerHTML = testimonials.map((testimonial, index) => `
            <div class="testimonial-slide w-full md:w-1/2 lg:w-1/3 flex-shrink-0 px-4 transition-transform duration-500 transform ${index === currentSlide ? 'scale-105' : 'scale-100'}"
                 style="transform: translateX(-${currentSlide * 100}%)">
                <div class="bg-gray-800 p-6 rounded-lg shadow-lg h-full">
                    <div class="flex items-center mb-4">
                        <div class="w-12 h-12 bg-teal-400 rounded-full flex items-center justify-center text-white text-xl font-bold">
                            ${testimonial.author_name.charAt(0)}
                        </div>
                        <div class="ml-4">
                            <h4 class="text-white font-semibold">${testimonial.author_name}</h4>
                            <div class="flex text-yellow-400">
                                ${Array(testimonial.rating).fill('★').join('')}
                            </div>
                        </div>
                    </div>
                    <p class="text-gray-300">${testimonial.content}</p>
                </div>
            </div>
        `).join('');
    }

    function renderDots() {
        dotsContainer.innerHTML = testimonials.map((_, index) => `
            <button class="w-2 h-2 rounded-full ${index === currentSlide ? 'bg-teal-400' : 'bg-gray-600'}"
                    onclick="goToSlide(${index})"></button>
        `).join('');
    }

    function startAutoSlide() {
        if (autoSlideInterval) clearInterval(autoSlideInterval);
        autoSlideInterval = setInterval(() => {
            nextSlide();
        }, 5000);
    }

    function nextSlide() {
        currentSlide = (currentSlide + 1) % testimonials.length;
        updateSlider();
    }

    function prevSlide() {
        currentSlide = currentSlide === 0 ? testimonials.length - 1 : currentSlide - 1;
        updateSlider();
    }

    function goToSlide(index) {
        currentSlide = index;
        updateSlider();
    }

    function updateSlider() {
        renderTestimonials();
        renderDots();
        startAutoSlide();
    }

    // Event listeners
    prevBtn.addEventListener('click', prevSlide);
    nextBtn.addEventListener('click', nextSlide);

    // Make goToSlide available globally
    window.goToSlide = goToSlide;

    // Initialize
    fetchTestimonials();
});
