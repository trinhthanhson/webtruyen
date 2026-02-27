const container = document.getElementById('font-control-container');
const toggleBtn = document.getElementById('font-toggle-btn');
const toggleIcon = document.getElementById('toggle-icon');
let isMenuOpen = false;

// Xử lý đóng mở
toggleBtn.addEventListener('click', () => {
    isMenuOpen = !isMenuOpen;
    if (isMenuOpen) {
        container.style.transform = 'translateY(-50%) translateX(0)';
        toggleIcon.style.transform = 'rotate(180deg)';
    } else {
        container.style.transform = 'translateY(-50%) translateX(calc(100% - 12px))';
        toggleIcon.style.transform = 'rotate(0deg)';
    }
});

// Code xử lý tăng giảm chữ (giữ lại từ bản trước)
let currentFontSize = parseInt(localStorage.getItem('user-font-size')) || 18;
const contentArea = document.querySelector('.chapter-content');
const sizeDisplay = document.getElementById('current-size-display');

function updateFontSize() {
    if (contentArea) {
        contentArea.style.fontSize = currentFontSize + 'px';
        sizeDisplay.innerText = currentFontSize;
        localStorage.setItem('user-font-size', currentFontSize);
    }
}

function changeFontSize(delta) {
    currentFontSize += delta;
    if (currentFontSize < 12) currentFontSize = 12;
    if (currentFontSize > 40) currentFontSize = 40;
    updateFontSize();
}

function resetFontSize() {
    currentFontSize = 18;
    updateFontSize();
}

document.addEventListener("DOMContentLoaded", updateFontSize);
// Xóa class no-transition sau khi load xong
document.addEventListener("DOMContentLoaded", () => {
    setTimeout(() => {
        document.documentElement.classList.remove("no-transition");
    }, 100);
});
