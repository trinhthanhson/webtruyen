
    (function () {
            const html = document.documentElement;
            html.classList.add("no-transition");
            html.style.scrollbarGutter = "stable"; // Chống giật trái phải như đã xử lý
            try {
                const theme = localStorage.getItem("theme");
                if (theme === "light") html.classList.add("light-mode");
            } catch (e) { }
        })();

    tailwind.config = {
        theme: {
            extend: {
                colors: {
                    primary: "#EAB308",
                    bodybg: "#121212",
                },
                fontFamily: {
                    logo: ['"Dancing Script"', "cursive"],
                    sans: ["Inter", "ui-sans-serif", "system-ui"],
                },
            },
        },
    };
