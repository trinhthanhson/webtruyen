const titleEl = document.getElementById("active-title");
const descEl = document.getElementById("active-description");
const bgBlurEl = document.getElementById("global-bg-blur");
// 1. Kiểm tra thiết bị ngay từ đầu
const isMobile = window.innerWidth < 768;

var swiper = new Swiper(".mySwiper", {
    // Cấu hình dựa trên thiết bị
    effect: isMobile ? "slide" : "cards", // Mobile: trượt phẳng, PC: xếp chồng
    slidesPerView: isMobile ? 1.2 : 1,    // Mobile: hiện 1 ảnh và 1 phần ảnh sau
    centeredSlides: isMobile ? true : false,
    spaceBetween: isMobile ? 20 : 0,
    
    grabCursor: true,
    speed: isMobile ? 600 : 300, // Mobile trượt chậm lại chút cho mượt
    loop: isMobile,              // Mobile nên dùng loop để lướt vô tận
    rewind: !isMobile,           // PC dùng rewind nếu không loop
    
    autoplay: { 
        delay: 4500, 
        disableOnInteraction: false // Để người dùng lướt xong vẫn tự chạy tiếp
    },
    
    pagination: {
        el: ".swiper-pagination",
        clickable: true,
    },

    on: {
        init: function () {
            syncBanner(this);
        },
        slideChange: function () {
            syncBanner(this);
        },
    },
});

function syncBanner(s) {
    const slide = s.slides[s.activeIndex];
    if (!slide) return;

    const data = slide.dataset;
    const img = slide.querySelector("img");
    if (!img) return;
    
    const imgPath = img.src;

    // Cập nhật Background (nếu có phần tử bgBlurEl)
    if (typeof bgBlurEl !== 'undefined') {
        bgBlurEl.style.backgroundImage = `url('${imgPath}')`;
    }

    // Trên Mobile, thường ta sẽ ẩn phần text bên trái để tránh dài trang
    // Nhưng nếu anh vẫn hiện text thì logic này giữ nguyên
    if (typeof titleEl !== 'undefined') titleEl.textContent = data.title;
    if (typeof descEl !== 'undefined') descEl.textContent = data.desc;

    const url = data.url;
    const titleLink = document.getElementById("active-title-link");
    const readMoreLink = document.getElementById("active-readmore-link");

    if (titleLink) titleLink.href = url;
    if (readMoreLink) readMoreLink.href = url;
}
// ===== HEADER SCROLL =====
const header = document.getElementById("main-header");
let ticking = false;

window.addEventListener("scroll", () => {
    if (!ticking) {
        window.requestAnimationFrame(() => {
            if (header) {
                header.classList.toggle("header-scrolled", window.scrollY > 30);
            }
            ticking = false;
        });
        ticking = true;
    }
}, { passive: true });

// ===== THEME TOGGLE =====
function setThemeIcon(isLight) {
    const icon = document.getElementById("mode-icon");
    if (!icon) return;

    if (isLight) {
        icon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m12.728 0l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z"/>`;
    } else {
        icon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>`;
    }
}

function toggleTheme() {
    const html = document.documentElement;

    // Tạm thời tắt transition để ký hiệu màu chữ đổi đồng bộ, không bị "chậm"
    html.classList.add("no-transition");

    const isLight = html.classList.toggle("light-mode");
    localStorage.setItem("theme", isLight ? "light" : "dark");
    setThemeIcon(isLight);

    requestAnimationFrame(() => html.classList.remove("no-transition"));
}

// Khởi tạo theme khi trang load
document.addEventListener("DOMContentLoaded", () => {
    const isLight = document.documentElement.classList.contains("light-mode");
    setThemeIcon(isLight);

    setTimeout(() => {
        document.documentElement.classList.remove("no-transition");
    }, 100);
});

function toggleMobileMenu() {
    const mobileMenu = document.getElementById('mobile-menu');
    const body = document.body;
    
    if (!mobileMenu) return;

    // Kiểm tra menu đang đóng (có class translate-x-full)
    const isOpening = mobileMenu.classList.contains('translate-x-full');

    if (isOpening) {
        // MỞ MENU
        mobileMenu.classList.remove('translate-x-full');
        mobileMenu.classList.add('translate-x-0');
        body.classList.add('menu-open'); // CSS sẽ tự ẩn banner nhờ class này
    } else {
        // ĐÓNG MENU
        mobileMenu.classList.remove('translate-x-0');
        mobileMenu.classList.add('translate-x-full');
        body.classList.remove('menu-open'); // Hiện lại banner
    }
}
function toggleCategory() {
    const list = document.getElementById('mobile-category-list');
    const icon = document.getElementById('cat-icon');
    
    if (list.classList.contains('hidden')) {
        list.classList.remove('hidden');
        icon.style.transform = 'rotate(180deg)';
        // Đảm bảo khi mở ra thì chữ không bị mờ
        list.style.opacity = '1';
    } else {
        list.classList.add('hidden');
        icon.style.transform = 'rotate(0deg)';
    }
}