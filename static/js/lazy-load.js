document.addEventListener('DOMContentLoaded', function() {
    // Lazy load images with Intersection Observer
    const lazyImages = document.querySelectorAll('img.lazy-image');
    const lazyBackgrounds = document.querySelectorAll('.lazy-bg');
    
    if ('IntersectionObserver' in window) {
        // Image observer
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                    }
                    if (img.dataset.srcset) {
                        img.srcset = img.dataset.srcset;
                    }
                    img.classList.add('loaded');
                    observer.unobserve(img);
                }
            });
        }, {
            rootMargin: '100px',
            threshold: 0.1
        });
        
        lazyImages.forEach(img => imageObserver.observe(img));
        
        // Background image observer
        const bgObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const bg = entry.target;
                    bg.style.backgroundImage = `url('${bg.dataset.bg}')`;
                    bg.classList.add('loaded');
                    observer.unobserve(bg);
                }
            });
        }, {
            rootMargin: '200px',
            threshold: 0.1
        });
        
        lazyBackgrounds.forEach(bg => bgObserver.observe(bg));
    } else {
        // Fallback for older browsers
        lazyImages.forEach(img => {
            if (img.dataset.src) {
                img.src = img.dataset.src;
            }
            img.classList.add('loaded');
        });
        
        lazyBackgrounds.forEach(bg => {
            bg.style.backgroundImage = `url('${bg.dataset.bg}')`;
            bg.classList.add('loaded');
        });
    }
    
    // Optimized carousel initialization
    const carousels = document.querySelectorAll('.owl-slider');
    const carouselObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const carousel = entry.target;
                setTimeout(() => {
                    $(carousel).owlCarousel({
                        items: carousel.dataset.owlItem || 4,
                        loop: carousel.dataset.owlLoop === 'true',
                        margin: parseInt(carousel.dataset.owlGap) || 30,
                        nav: carousel.dataset.owlNav === 'true',
                        dots: carousel.dataset.owlDots === 'true',
                        lazyLoad: true,
                        autoplay: carousel.dataset.owlAuto === 'true',
                        autoplayTimeout: parseInt(carousel.dataset.owlSpeed) || 5000,
                        responsive: {
                            0: { items: carousel.dataset.owlItemXs || 1 },
                            576: { items: carousel.dataset.owlItemSm || 2 },
                            768: { items: carousel.dataset.owlItemMd || 3 },
                            992: { items: carousel.dataset.owlItemLg || 4 },
                            1200: { items: carousel.dataset.owlItemXl || 6 }
                        }
                    });
                }, 300); // Small delay to prioritize critical content
                observer.unobserve(carousel);
            }
        });
    }, {
        rootMargin: '300px',
        threshold: 0.05
    });
    
    carousels.forEach(carousel => carouselObserver.observe(carousel));
});