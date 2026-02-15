const titleEl = document.getElementById("active-title");
const descEl = document.getElementById("active-description");
const bgBlurEl = document.getElementById("global-bg-blur");

var swiper = new Swiper(".mySwiper", {
    effect: "cards",
    grabCursor: true,
    rewind: true,
    speed: 300,
    autoplay: { delay: 4500, disableOnInteraction: true },
    on: {
        init: function () {
            syncBanner(this);
        },
        // Đồng bộ NGAY khi slide đổi
        slideChange: function () {
            syncBanner(this);
        },
    },
});

function syncBanner(s) {
    const slide = s.slides[s.activeIndex];
    if (!slide) return;

    const data = slide.dataset;
    const imgPath = slide.querySelector("img").src;

    // Set tất cả NGAY LẬP TỨC
    bgBlurEl.style.backgroundImage = `url('${imgPath}')`;
    titleEl.textContent = data.title;
    descEl.textContent = data.desc;

    const url = data.url;
    document.getElementById("active-title-link").href = url;
    document.getElementById("active-readmore-link").href = url;
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
    const isLight = html.classList.toggle("light-mode");

    localStorage.setItem("theme", isLight ? "light" : "dark");
    setThemeIcon(isLight);
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
    const menu = document.getElementById("mobile-menu");
    menu.classList.toggle("translate-x-full");
}
function toggleCategory() {
    const list = document.getElementById("mobile-category-list");
    const icon = document.getElementById("cat-icon");

    list.classList.toggle("hidden");
    icon.classList.toggle("rotate-180");
}
