const titleEl = document.getElementById("active-title");
const descEl = document.getElementById("active-description");
const bgBlurEl = document.getElementById("global-bg-blur");
// 1. Kiểm tra thiết bị ngay từ đầu
const isMobile = window.innerWidth < 768;

const swiper = new Swiper(".mySwiper", {
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

    if (typeof titleEl !== 'undefined') titleEl.textContent = data.title;
    if (typeof descEl !== 'undefined') descEl.textContent = data.desc;

    const url = data.url;
    const titleLink = document.getElementById("active-title-link");
    const readMoreLink = document.getElementById("active-readmore-link");

    if (titleLink) titleLink.href = url;
    if (readMoreLink) readMoreLink.href = url;
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