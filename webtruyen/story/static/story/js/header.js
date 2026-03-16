
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

    // Tạm thời tắt transition để tránh bị "chậm" khi đổi chế độ sáng/tối
    html.classList.add("no-transition");

    const isLight = html.classList.toggle("light-mode");
    localStorage.setItem("theme", isLight ? "light" : "dark");
    setThemeIcon(isLight);

    // Bật lại transition sau khi đã đổi xong (sẽ áp dụng cho các thay đổi sau)
    requestAnimationFrame(() => html.classList.remove("no-transition"));
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

 function toggleMobileSearch() {
    const bar = document.getElementById('mobile-search-bar');
    const input = document.getElementById('mobile-search-input');
    const isOpen = bar.style.maxHeight !== '0px' && bar.style.maxHeight !== '';

    if (isOpen) {
      bar.style.maxHeight = '0px';
    } else {
      bar.style.maxHeight = bar.scrollHeight + 'px';
      setTimeout(() => input.focus(), 300);
    }
  }

  // Đóng search bar khi bấm ra ngoài
  document.addEventListener('click', function(e) {
    const bar = document.getElementById('mobile-search-bar');
    const btn = document.getElementById('mobile-search-btn');
    if (bar && btn && !bar.contains(e.target) && !btn.contains(e.target)) {
      bar.style.maxHeight = '0px';
    }
  });