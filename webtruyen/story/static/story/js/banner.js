// banner.js - Banner slider functionality
class BannerSlider {
    constructor() {
        this.slides = document.querySelectorAll('.slide');
        this.dots = document.querySelectorAll('.dot');
        this.prevArrow = document.querySelector('.prev-arrow');
        this.nextArrow = document.querySelector('.next-arrow');
        this.currentSlide = 0; 
        this.slideInterval = null;
        this.autoSlideDelay = 3000; 

        if (this.slides.length > 0) {
            this.init();
        }
    }

    init() {
        console.log('BannerSlider initialized with', this.slides.length, 'slides');
        
        // 🌟 SỬA LỖI: Buộc xóa class active từ HTML để JS quản lý trạng thái
        this.slides.forEach(slide => slide.classList.remove('active'));
        this.dots.forEach(dot => dot.classList.remove('active'));

        // Thêm event listeners (giữ nguyên)
        if (this.prevArrow) {
            this.prevArrow.addEventListener('click', () => this.prevSlide());
        }
        if (this.nextArrow) {
            this.nextArrow.addEventListener('click', () => this.nextSlide());
        }

        // Add dot click events (giữ nguyên)
        this.dots.forEach(dot => {
            dot.addEventListener('click', (e) => {
                const slideIndex = parseInt(e.target.getAttribute('data-slide'));
                this.goToSlide(slideIndex);
            });
        });

        // 🌟 KÍCH HOẠT LẠI SLIDE ĐẦU TIÊN để đảm bảo hiển thị ngay
        this.showSlide(this.currentSlide); 
        
        this.startAutoSlide();

        // Pause auto-slide on hover (giữ nguyên)
        const bannerSection = document.querySelector('.banner-section');
        if (bannerSection) {
            bannerSection.addEventListener('mouseenter', () => this.stopAutoSlide());
            bannerSection.addEventListener('mouseleave', () => this.startAutoSlide());
        }

        this.addTouchEvents();
    }

    showSlide(index) {
        console.log('Showing slide:', index); 
        
        this.slides.forEach(slide => slide.classList.remove('active'));
        this.dots.forEach(dot => dot.classList.remove('active'));
        
        this.slides[index].classList.add('active');
        this.dots[index].classList.add('active');
        
        console.log('Active slides:', document.querySelectorAll('.slide.active').length); 
        
        this.currentSlide = index;
    }
    
    // ... (Các hàm khác: nextSlide, prevSlide, goToSlide, startAutoSlide, stopAutoSlide, restartAutoSlide, addTouchEvents, handleSwipe - GIỮ NGUYÊN)
    nextSlide() {
        const nextIndex = (this.currentSlide + 1) % this.slides.length;
        this.showSlide(nextIndex);
        this.restartAutoSlide();
    }

    prevSlide() {
        const prevIndex = (this.currentSlide - 1 + this.slides.length) % this.slides.length;
        this.showSlide(prevIndex);
        this.restartAutoSlide();
    }

    goToSlide(index) {
        if (index >= 0 && index < this.slides.length) {
            this.showSlide(index);
            this.restartAutoSlide();
        }
    }

    startAutoSlide() {
        this.stopAutoSlide(); 
        this.slideInterval = setInterval(() => {
            this.nextSlide();
        }, this.autoSlideDelay);
    }

    stopAutoSlide() {
        if (this.slideInterval) {
            clearInterval(this.slideInterval);
            this.slideInterval = null;
        }
    }

    restartAutoSlide() {
        this.stopAutoSlide();
        this.startAutoSlide();
    }

    addTouchEvents() {
        let startX = 0;
        let endX = 0;
        const slider = document.querySelector('.banner-slider');

        if (slider) {
            slider.addEventListener('touchstart', (e) => {
                startX = e.touches[0].clientX;
            });

            slider.addEventListener('touchend', (e) => {
                endX = e.changedTouches[0].clientX;
                this.handleSwipe(startX, endX);
            });
        }
    }

    handleSwipe(startX, endX) {
        const swipeThreshold = 50;
        const diff = startX - endX;

        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                this.nextSlide(); 
            } else {
                this.prevSlide(); 
            }
        }
    }
}

// Khởi tạo banner slider khi DOM ready
function initBannerSlider() {
    const slides = document.querySelectorAll('.slide');
    if (slides.length > 0) {
        new BannerSlider();
        console.log('Banner slider initialized successfully!');
    } else {
        console.log('No slides found for banner slider');
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initBannerSlider);
} else {
    initBannerSlider();
}