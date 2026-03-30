
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

    // Tạm thời tắt transition để tránh bị "chậm" khi đổi chế độ sáng/tối
    html.classList.add("no-transition");

    const isLight = html.classList.toggle("light-mode");
    localStorage.setItem("theme", isLight ? "light" : "dark");
    setThemeIcon(isLight);

    requestAnimationFrame(() => html.classList.remove("no-transition"));
}

function init() {
    const isLight = document.documentElement.classList.contains("light-mode");
    setThemeIcon(isLight);

    document.documentElement.classList.remove("no-transition");

    initHeaderScroll();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
} else {
    init();
}

let header;
let ticking = false;

function updateHeaderScroll() {
    if (!header) return;
    header.classList.toggle("header-scrolled", window.scrollY > 30);
}

function initHeaderScroll() {
    header = document.getElementById("main-header");
    updateHeaderScroll();

    window.addEventListener("scroll", () => {
        if (!ticking) {
            window.requestAnimationFrame(() => {
                updateHeaderScroll();
                ticking = false;
            });
            ticking = true;
        }
    }, { passive: true });
}
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

  document.addEventListener('click', function(e) {
    const bar = document.getElementById('mobile-search-bar');
    const btn = document.getElementById('mobile-search-btn');
    if (bar && btn && !bar.contains(e.target) && !btn.contains(e.target)) {
      bar.style.maxHeight = '0px';
    }
  });