// Optimized carousel for performance
$(document).ready(function() {
    // Initialize only when needed
    let carouselsInitialized = false;
    
    function initCarousels() {
        if (!carouselsInitialized) {
            $('.ps-carousel--nav').each(function() {
                const $this = $(this);
                if ($this.is(':visible')) {
                    $this.owlCarousel({
                        items: $this.data('owl-item') || 4,
                        loop: $this.data('owl-loop') || false,
                        margin: $this.data('owl-gap') || 30,
                        nav: $this.data('owl-nav') || true,
                        dots: $this.data('owl-dots') || true,
                        lazyLoad: true,
                        autoplay: $this.data('owl-auto') || false,
                        autoplayTimeout: $this.data('owl-speed') || 10000,
                        responsive: {
                            0: { items: $this.data('owl-item-xs') || 1 },
                            576: { items: $this.data('owl-item-sm') || 2 },
                            768: { items: $this.data('owl-item-md') || 3 },
                            992: { items: $this.data('owl-item-lg') || 4 },
                            1200: { items: $this.data('owl-item-xl') || 6 }
                        }
                    });
                }
            });
            carouselsInitialized = true;
        }
    }
    
    // Initialize on scroll or after delay
    let initTimeout;
    function scheduleCarouselInit() {
        clearTimeout(initTimeout);
        initTimeout = setTimeout(initCarousels, 1000);
    }
    
    // Initialize when carousels are near viewport
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                scheduleCarouselInit();
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.ps-carousel--nav').forEach(carousel => {
        observer.observe(carousel);
    });
    
    // Fallback initialization after 3 seconds
    setTimeout(scheduleCarouselInit, 3000);
});