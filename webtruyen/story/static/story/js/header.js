
// 1. Hàm đặt Icon (☀️/🌙)
function setThemeIcon(isLight) {
    const icon = document.getElementById("mode-icon");
    if (!icon) return;

    if (isLight) {
        icon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m12.728 0l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z"/>`;
    } else {
        icon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>`;
    }
}

// 2. Hàm Toggle Theme
function toggleTheme() {
    const html = document.documentElement;
    const isLight = html.classList.toggle("light-mode");

    localStorage.setItem("theme", isLight ? "light" : "dark");
    setThemeIcon(isLight);
}

// 3. Khởi tạo khi DOM sẵn sàng
document.addEventListener("DOMContentLoaded", () => {
    const isLight = document.documentElement.classList.contains("light-mode");
    setThemeIcon(isLight);

    // Xóa class no-transition sau 100ms
    setTimeout(() => {
        document.documentElement.classList.remove("no-transition");
    }, 100);
});

// 4. Xử lý Scroll Header
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

window.addEventListener("load", () => {
    document.documentElement.classList.remove("no-transition");
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
