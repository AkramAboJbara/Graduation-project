document.addEventListener('DOMContentLoaded', function() {
    // Typed.js initialization
    if (document.querySelector('.typed')) {
        var typed = new Typed('.typed', {
            strings: ["Django Developer", "Laravel Developer", "PostgreSQL Expert"],
            typeSpeed: 50,
            backSpeed: 30,
            loop: true
        });
    }

    // Animation on scroll
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.animate__animated');
        
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementPosition < windowHeight - 100) {
                element.style.visibility = 'visible';
            }
        });
    };
    
    window.addEventListener('scroll', animateOnScroll);
    animateOnScroll(); // Run once on page load
});