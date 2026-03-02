
    (function () {
        const html = document.documentElement;
        html.classList.add("no-transition");
        try {
            const theme = localStorage.getItem("theme");
            if (theme === "light") {
                html.classList.add("light-mode");
            }
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
                    sans: ["Inter", "sans-serif"],
                },
            },
        },
    };
