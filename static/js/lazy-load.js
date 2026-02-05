// Lazy Image Loader Class
class LazyImageLoader {
    constructor(options = {}) {
        this.options = {
            root: null,
            rootMargin: '50px 0px',
            threshold: 0.01,
            placeholder: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
            errorImage: '/static/img/no-image.jpg',
            ...options
        };
        
        this.images = new Set();
        this.observer = null;
        this.initialized = false;
        
        this.init();
    }
    
    init() {
        if (this.initialized) return;
        
        // Check if IntersectionObserver is supported
        if ('IntersectionObserver' in window) {
            this.observer = new IntersectionObserver(
                (entries) => this.handleIntersect(entries),
                {
                    root: this.options.root,
                    rootMargin: this.options.rootMargin,
                    threshold: this.options.threshold
                }
            );
        }
        
        // Load initial images
        this.loadInitialImages();
        this.initialized = true;
    }
    
    loadInitialImages() {
        // Get all images that should be lazy loaded
        const lazyImages = document.querySelectorAll('img[data-src], img[data-srcset]');
        const lazyBackgrounds = document.querySelectorAll('[data-bg]');
        
        // Convert NodeList to Array
        const allElements = [
            ...Array.from(lazyImages),
            ...Array.from(lazyBackgrounds)
        ];
        
        // Add to tracking set
        allElements.forEach(element => this.images.add(element));
        
        // Start observing
        allElements.forEach(element => {
            if (this.observer) {
                this.observer.observe(element);
            } else {
                // Fallback for browsers without IntersectionObserver
                this.loadElement(element);
            }
        });
    }
    
    handleIntersect(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                this.loadElement(element);
                this.observer.unobserve(element);
                this.images.delete(element);
            }
        });
    }
    
    loadElement(element) {
        if (element.tagName === 'IMG') {
            this.loadImage(element);
        } else if (element.hasAttribute('data-bg')) {
            this.loadBackground(element);
        }
    }
    
    loadImage(img) {
        // Get source attributes
        const src = img.getAttribute('data-src');
        const srcset = img.getAttribute('data-srcset');
        
        if (!src && !srcset) return;
        
        // Create temporary image for preloading
        const tempImg = new Image();
        
        tempImg.onload = () => {
            // Set the real sources
            if (src) img.src = src;
            if (srcset) img.srcset = srcset;
            
            // Add loaded class for CSS transitions
            img.classList.add('loaded');
            
            // Remove placeholder if it exists
            if (img.src === this.options.placeholder) {
                setTimeout(() => {
                    img.style.background = 'none';
                }, 300);
            }
            
            // Dispatch custom event
            img.dispatchEvent(new Event('lazyloaded'));
        };
        
        tempImg.onerror = () => {
            // Use error image
            img.src = this.options.errorImage;
            img.classList.add('loaded');
            img.classList.add('error');
            
            // Dispatch error event
            img.dispatchEvent(new Event('lazyloaderror'));
        };
        
        // Start loading
        if (src) tempImg.src = src;
        if (srcset) tempImg.srcset = srcset;
    }
    
    loadBackground(element) {
        const bgImage = element.getAttribute('data-bg');
        if (!bgImage) return;
        
        const tempImg = new Image();
        
        tempImg.onload = () => {
            element.style.backgroundImage = `url(${bgImage})`;
            element.classList.add('loaded');
            element.dispatchEvent(new Event('lazyloaded'));
        };
        
        tempImg.onerror = () => {
            element.style.backgroundImage = `url(${this.options.errorImage})`;
            element.classList.add('loaded');
            element.classList.add('error');
            element.dispatchEvent(new Event('lazyloaderror'));
        };
        
        tempImg.src = bgImage;
    }
    
    addElements(elements) {
        if (!Array.isArray(elements)) elements = [elements];
        
        elements.forEach(element => {
            if (!this.images.has(element)) {
                this.images.add(element);
                if (this.observer) {
                    this.observer.observe(element);
                } else {
                    this.loadElement(element);
                }
            }
        });
    }
    
    refresh() {
        // Re-observe all images (useful after DOM updates)
        this.images.forEach(element => {
            if (this.observer) {
                this.observer.unobserve(element);
                this.observer.observe(element);
            }
        });
    }
    
    destroy() {
        if (this.observer) {
            this.observer.disconnect();
        }
        this.images.clear();
        this.initialized = false;
    }
}

// Infinite Scroll Manager
class InfiniteScrollManager {
    constructor(options = {}) {
        this.options = {
            container: document.body,
            contentSelector: '.infinite-content',
            itemSelector: '.infinite-item',
            nextSelector: '.load-more-btn',
            loadingSelector: '.loading-spinner',
            endSelector: '.end-message',
            path: '/load-more-products/',
            appendMethod: 'append',
            data: {},
            threshold: 100,
            debounce: 100,
            ...options
        };
        
        this.state = {
            loading: false,
            hasMore: true,
            currentPage: 1,
            totalPages: 1,
            totalItems: 0
        };
        
        this.container = typeof this.options.container === 'string' 
            ? document.querySelector(this.options.container)
            : this.options.container;
        
        this.init();
    }
    
    init() {
        if (!this.container) {
            console.error('InfiniteScroll: Container not found');
            return;
        }
        
        // Set up scroll listener
        this.setupScrollListener();
        
        // Set up load more button
        this.setupLoadMoreButton();
        
        // Initial state
        this.updateUI();
    }
    
    setupScrollListener() {
        let timeout;
        
        const scrollHandler = () => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                this.checkScrollPosition();
            }, this.options.debounce);
        };
        
        // Use passive listener for better performance
        window.addEventListener('scroll', scrollHandler, { passive: true });
        this.container.addEventListener('scroll', scrollHandler, { passive: true });
        
        // Store for cleanup
        this.scrollHandler = scrollHandler;
    }
    
    setupLoadMoreButton() {
        const loadMoreBtn = this.container.querySelector(this.options.nextSelector);
        if (loadMoreBtn) {
            loadMoreBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.loadMore();
            });
            this.loadMoreBtn = loadMoreBtn;
        }
    }
    
    checkScrollPosition() {
        if (this.state.loading || !this.state.hasMore) return;
        
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;
        
        // Check if we're near the bottom
        if (scrollTop + windowHeight >= documentHeight - this.options.threshold) {
            this.loadMore();
        }
    }
    
    async loadMore() {
        if (this.state.loading || !this.state.hasMore) return;
        
        this.setState({ loading: true });
        
        try {
            // Build URL with query parameters
            const url = new URL(this.options.path, window.location.origin);
            const params = new URLSearchParams({
                page: this.state.currentPage + 1,
                ...this.options.data
            });
            url.search = params.toString();
            
            // Make request
            const response = await fetch(url.toString(), {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                // Update state
                this.setState({
                    loading: false,
                    currentPage: data.current_page || this.state.currentPage + 1,
                    hasMore: data.has_next || false,
                    totalPages: data.total_pages || this.state.totalPages,
                    totalItems: data.total_products || this.state.totalItems
                });
                
                // Append new content
                this.appendContent(data);
                
                // Update UI
                this.updateUI();
                
                // Dispatch event
                this.container.dispatchEvent(new CustomEvent('infiniteScrollLoaded', {
                    detail: { data, state: this.state }
                }));
            } else {
                throw new Error(data.message || 'Failed to load more content');
            }
            
        } catch (error) {
            console.error('InfiniteScroll Error:', error);
            this.setState({ loading: false });
            this.showError(error.message);
        }
    }
    
    appendContent(data) {
        // This should be implemented based on your content structure
        // Example:
        const contentContainer = this.container.querySelector(this.options.contentSelector);
        if (contentContainer && data.products) {
            // Create HTML for new products
            const newContent = this.createProductHTML(data.products, data.currency_symbol);
            if (this.options.appendMethod === 'append') {
                contentContainer.insertAdjacentHTML('beforeend', newContent);
            } else if (this.options.appendMethod === 'prepend') {
                contentContainer.insertAdjacentHTML('afterbegin', newContent);
            }
            
            // Reinitialize lazy loading for new images
            if (window.lazyLoader) {
                const newImages = contentContainer.querySelectorAll('img[data-src]:not(.loaded)');
                window.lazyLoader.addElements(Array.from(newImages));
            }
        }
    }
    
    createProductHTML(products, currencySymbol = '$') {
        // Implement based on your product HTML structure
        let html = '';
        
        products.forEach(product => {
            const discountBadge = product.discount_percentage > 0 
                ? `<div class="ps-product__badge">-${product.discount_percentage}%</div>` 
                : '';
            
            const priceHTML = product.discount_price 
                ? `<p class="ps-product__price sale">${currencySymbol}${product.discount_price}<del>${currencySymbol}${product.price}</del></p>`
                : `<p class="ps-product__price">${currencySymbol}${product.price}</p>`;
            
            html += `
                <div class="col-xl-3 col-lg-4 col-md-4 col-sm-6 col-12 infinite-item">
                    <div class="ps-product">
                        <div class="ps-product__thumbnail">
                            <a href="${product.url}">
                                <img class="lazy-image" 
                                     data-src="${product.image_url}" 
                                     src="/static/img/placeholder.png"
                                     alt="${product.name}">
                            </a>
                            ${discountBadge}
                        </div>
                        <div class="ps-product__container">
                            ${product.brand_name ? `<a class="ps-product__vendor" href="/brand/${product.brand_name.toLowerCase()}/">${product.brand_name}</a>` : ''}
                            <div class="ps-product__content">
                                <a class="ps-product__title" href="${product.url}">
                                    ${product.name}
                                </a>
                                ${priceHTML}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        return html;
    }
    
    setState(newState) {
        this.state = { ...this.state, ...newState };
    }
    
    updateUI() {
        // Show/hide loading spinner
        const loadingElement = this.container.querySelector(this.options.loadingSelector);
        if (loadingElement) {
            loadingElement.classList.toggle('active', this.state.loading);
        }
        
        // Show/hide load more button
        if (this.loadMoreBtn) {
            this.loadMoreBtn.style.display = this.state.hasMore ? 'block' : 'none';
            this.loadMoreBtn.disabled = this.state.loading;
            
            // Update button text
            if (this.state.hasMore) {
                this.loadMoreBtn.textContent = this.state.loading 
                    ? 'Loading...' 
                    : `Load More (${this.state.currentPage}/${this.state.totalPages})`;
            }
        }
        
        // Show end message
        const endElement = this.container.querySelector(this.options.endSelector);
        if (endElement) {
            endElement.style.display = !this.state.hasMore && this.state.currentPage > 1 ? 'block' : 'none';
        }
    }
    
    showError(message) {
        // Create or show error element
        let errorElement = this.container.querySelector('.load-error');
        
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'load-error';
            this.container.appendChild(errorElement);
        }
        
        errorElement.innerHTML = `
            <i class="icon-alert-circle"></i>
            <p>${message}</p>
            <button class="retry-btn">Retry</button>
        `;
        
        errorElement.style.display = 'block';
        
        // Add retry button listener
        const retryBtn = errorElement.querySelector('.retry-btn');
        if (retryBtn) {
            retryBtn.onclick = () => {
                errorElement.style.display = 'none';
                this.loadMore();
            };
        }
    }
    
    reset() {
        this.setState({
            loading: false,
            hasMore: true,
            currentPage: 1,
            totalPages: 1,
            totalItems: 0
        });
        
        this.updateUI();
    }
    
    destroy() {
        if (this.scrollHandler) {
            window.removeEventListener('scroll', this.scrollHandler);
            this.container.removeEventListener('scroll', this.scrollHandler);
        }
        
        if (this.loadMoreBtn) {
            this.loadMoreBtn.removeEventListener('click', this.loadMore);
        }
    }
}

// Utility Functions
class PerformanceUtils {
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    static throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
    
    static measurePerformance(name, func) {
        const start = performance.now();
        const result = func();
        const end = performance.now();
        console.log(`${name} took ${(end - start).toFixed(2)}ms`);
        return result;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize lazy image loader
    window.lazyLoader = new LazyImageLoader({
        rootMargin: '100px 0px',
        threshold: 0.01
    });
    
    // Initialize infinite scroll for new arrivals
    const newArrivalsContainer = document.getElementById('new-arrivals-container');
    if (newArrivalsContainer) {
        window.newArrivalsScroll = new InfiniteScrollManager({
            container: newArrivalsContainer,
            contentSelector: '#new-arrivals-grid',
            itemSelector: '.col-xl-3',
            nextSelector: '#load-more-arrivals',
            loadingSelector: '#arrivals-loading',
            endSelector: '#arrivals-end',
            path: '/load-more-products/',
            data: { type: 'new_arrivals' },
            threshold: 300,
            debounce: 150
        });
    }
    
    // Initialize infinite scroll for deals
    const dealsContainer = document.getElementById('deals-container');
    if (dealsContainer) {
        window.dealsScroll = new InfiniteScrollManager({
            container: dealsContainer,
            contentSelector: '.deals-carousel',
            itemSelector: '.ps-product--inner',
            path: '/load-more-products/',
            data: { type: 'deals' },
            threshold: 500,
            debounce: 200
        });
    }
    
    // Handle category loading
    setupCategoryLoading();
    
    // Performance monitoring
    setupPerformanceMonitoring();
});

// Category Loading
function setupCategoryLoading() {
    const categoryTabs = document.querySelectorAll('.category-tab');
    
    categoryTabs.forEach(tab => {
        tab.addEventListener('click', async function(e) {
            e.preventDefault();
            
            const categoryId = this.dataset.categoryId;
            const categoryName = this.textContent;
            
            // Show loading state
            showCategoryLoading(categoryId);
            
            try {
                const response = await fetch(`/load-category-products/?category_id=${categoryId}&page=1`);
                const data = await response.json();
                
                if (data.success) {
                    displayCategoryProducts(categoryId, categoryName, data);
                } else {
                    throw new Error(data.message);
                }
            } catch (error) {
                console.error('Error loading category:', error);
                showCategoryError(categoryId, error.message);
            }
        });
    });
}

function showCategoryLoading(categoryId) {
    const container = document.getElementById('category-products-container');
    
    const loadingHTML = `
        <div class="category-loading" id="category-${categoryId}-loading">
            <div class="product-skeleton">
                <div class="skeleton skeleton-image"></div>
                <div class="skeleton skeleton-text" style="width: 80%"></div>
                <div class="skeleton skeleton-text" style="width: 60%"></div>
                <div class="skeleton skeleton-text" style="width: 40%"></div>
            </div>
            <div class="loading-spinner active">
                <div class="spinner"></div>
                <p class="loading-text">Loading ${categoryId} products...</p>
            </div>
        </div>
    `;
    
    container.innerHTML = loadingHTML;
}

function displayCategoryProducts(categoryId, categoryName, data) {
    const container = document.getElementById('category-products-container');
    
    // Create products HTML
    let productsHTML = '';
    data.products.forEach(product => {
        const discountBadge = product.discount_percentage > 0 
            ? `<div class="ps-product__badge">-${product.discount_percentage}%</div>` 
            : '';
        
        const priceHTML = product.discount_price 
            ? `<p class="ps-product__price sale">${data.currency_symbol}${product.discount_price}<del>${data.currency_symbol}${product.price}</del></p>`
            : `<p class="ps-product__price">${data.currency_symbol}${product.price}</p>`;
        
        productsHTML += `
            <div class="col-xl-3 col-lg-4 col-md-4 col-sm-6 col-12">
                <div class="ps-product">
                    <div class="ps-product__thumbnail">
                        <a href="${product.url}">
                            <img class="lazy-image" 
                                 data-src="${product.image_url}" 
                                 src="/static/img/placeholder.png"
                                 alt="${product.name}">
                        </a>
                        ${discountBadge}
                    </div>
                    <div class="ps-product__container">
                        ${product.brand_name ? `<a class="ps-product__vendor" href="#">${product.brand_name}</a>` : ''}
                        <div class="ps-product__content">
                            <a class="ps-product__title" href="${product.url}">
                                ${product.name.length > 40 ? product.name.substring(0, 37) + '...' : product.name}
                            </a>
                            ${priceHTML}
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    // Create section HTML
    const sectionHTML = `
        <div class="ps-product-list ps-clothings category-products-section" id="category-${categoryId}">
            <div class="ps-container">
                <div class="ps-section__header">
                    <h3>${categoryName}</h3>
                    <div class="ps-section__meta">
                        <span>${data.total_products} products</span>
                        <span>Page ${data.current_page} of ${data.total_pages}</span>
                    </div>
                </div>
                <div class="ps-section__content">
                    <div class="row" id="category-${categoryId}-grid">
                        ${productsHTML}
                    </div>
                    
                    ${data.has_next ? `
                        <div class="text-center mt-4">
                            <button class="load-more-btn" 
                                    onclick="loadMoreCategoryProducts('${categoryId}', ${data.next_page})">
                                Load More
                            </button>
                        </div>
                        <div class="loading-spinner" id="category-${categoryId}-loading-more" style="display: none;">
                            <div class="spinner"></div>
                            <p class="loading-text">Loading more products...</p>
                        </div>
                    ` : `
                        <div class="end-message" id="category-${categoryId}-end">
                            <i class="icon-check-circle"></i>
                            <p>All ${data.total_products} products loaded</p>
                        </div>
                    `}
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = sectionHTML;
    
    // Initialize lazy loading for new images
    if (window.lazyLoader) {
        const newImages = container.querySelectorAll('img[data-src]:not(.loaded)');
        window.lazyLoader.addElements(Array.from(newImages));
    }
}

function showCategoryError(categoryId, message) {
    const container = document.getElementById('category-products-container');
    
    container.innerHTML = `
        <div class="load-error">
            <i class="icon-alert-circle"></i>
            <p>Failed to load category: ${message}</p>
            <button class="retry-btn" onclick="retryCategoryLoad('${categoryId}')">Retry</button>
        </div>
    `;
}

// Global functions for template
window.loadMoreCategoryProducts = async function(categoryId, page) {
    const loadingElement = document.getElementById(`category-${categoryId}-loading-more`);
    const loadMoreBtn = document.querySelector(`#category-${categoryId} .load-more-btn`);
    
    if (loadingElement) loadingElement.style.display = 'block';
    if (loadMoreBtn) loadMoreBtn.style.display = 'none';
    
    try {
        const response = await fetch(`/load-category-products/?category_id=${categoryId}&page=${page}`);
        const data = await response.json();
        
        if (data.success) {
            // Append new products
            const grid = document.getElementById(`category-${categoryId}-grid`);
            if (grid) {
                data.products.forEach(product => {
                    const discountBadge = product.discount_percentage > 0 
                        ? `<div class="ps-product__badge">-${product.discount_percentage}%</div>` 
                        : '';
                    
                    const priceHTML = product.discount_price 
                        ? `<p class="ps-product__price sale">${data.currency_symbol}${product.discount_price}<del>${data.currency_symbol}${product.price}</del></p>`
                        : `<p class="ps-product__price">${data.currency_symbol}${product.price}</p>`;
                    
                    const productHTML = `
                        <div class="col-xl-3 col-lg-4 col-md-4 col-sm-6 col-12">
                            <div class="ps-product">
                                <div class="ps-product__thumbnail">
                                    <a href="${product.url}">
                                        <img class="lazy-image" 
                                             data-src="${product.image_url}" 
                                             src="/static/img/placeholder.png"
                                             alt="${product.name}">
                                    </a>
                                    ${discountBadge}
                                </div>
                                <div class="ps-product__container">
                                    ${product.brand_name ? `<a class="ps-product__vendor" href="#">${product.brand_name}</a>` : ''}
                                    <div class="ps-product__content">
                                        <a class="ps-product__title" href="${product.url}">
                                            ${product.name.length > 40 ? product.name.substring(0, 37) + '...' : product.name}
                                        </a>
                                        ${priceHTML}
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    grid.insertAdjacentHTML('beforeend', productHTML);
                });
            }
            
            // Update lazy loader
            if (window.lazyLoader && grid) {
                const newImages = grid.querySelectorAll('img[data-src]:not(.loaded)');
                window.lazyLoader.addElements(Array.from(newImages));
            }
            
            // Update UI
            if (data.has_next) {
                if (loadMoreBtn) {
                    loadMoreBtn.style.display = 'block';
                    loadMoreBtn.setAttribute('onclick', `loadMoreCategoryProducts('${categoryId}', ${data.next_page})`);
                }
            } else {
                // Show end message
                const endHTML = `
                    <div class="end-message" id="category-${categoryId}-end">
                        <i class="icon-check-circle"></i>
                        <p>All ${data.total_products} products loaded</p>
                    </div>
                `;
                
                const contentDiv = document.querySelector(`#category-${categoryId} .ps-section__content`);
                if (contentDiv && loadMoreBtn) {
                    loadMoreBtn.insertAdjacentHTML('afterend', endHTML);
                    loadMoreBtn.style.display = 'none';
                }
            }
        }
    } catch (error) {
        console.error('Error loading more category products:', error);
        
        // Show error
        const errorHTML = `
            <div class="load-error">
                <p>Failed to load more products: ${error.message}</p>
                <button class="retry-btn" onclick="loadMoreCategoryProducts('${categoryId}', ${page})">Retry</button>
            </div>
        `;
        
        if (loadMoreBtn) {
            loadMoreBtn.insertAdjacentHTML('afterend', errorHTML);
        }
    } finally {
        if (loadingElement) loadingElement.style.display = 'none';
    }
};

window.retryCategoryLoad = function(categoryId) {
    // Implement retry logic
    const event = new Event('click');
    const tab = document.querySelector(`.category-tab[data-category-id="${categoryId}"]`);
    if (tab) tab.dispatchEvent(event);
};

// Performance Monitoring
function setupPerformanceMonitoring() {
    // Monitor image loading performance
    document.addEventListener('lazyloaded', function(e) {
        const img = e.target;
        const loadTime = img.dataset.loadStart 
            ? performance.now() - parseFloat(img.dataset.loadStart)
            : 0;
        
        if (loadTime > 1000) {
            console.warn(`Slow image load: ${img.src} took ${loadTime.toFixed(0)}ms`);
        }
    });
    
    // Monitor scroll performance
    let scrollStartTime;
    window.addEventListener('scroll', function() {
        if (!scrollStartTime) {
            scrollStartTime = performance.now();
        }
    }, { passive: true });
    
    // Debounce scroll end detection
    const scrollEndHandler = PerformanceUtils.debounce(function() {
        if (scrollStartTime) {
            const scrollDuration = performance.now() - scrollStartTime;
            if (scrollDuration > 100) {
                console.log(`Scroll duration: ${scrollDuration.toFixed(0)}ms`);
            }
            scrollStartTime = null;
        }
    }, 500);
    
    window.addEventListener('scroll', scrollEndHandler, { passive: true });
    
    // Monitor AJAX request performance
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        const start = performance.now();
        return originalFetch.apply(this, args).then(response => {
            const duration = performance.now() - start;
            if (duration > 1000) {
                console.warn(`Slow fetch: ${args[0]} took ${duration.toFixed(0)}ms`);
            }
            return response;
        });
    };
}