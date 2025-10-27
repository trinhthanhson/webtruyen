// main.js - Load all components
document.addEventListener('DOMContentLoaded', function() {
    loadComponents();
});

async function loadComponents() {
    try {
        // Load header
        await loadComponent('header.html', 'afterbegin');
        
        // Load banner
        await loadComponent('banner.html', 'afterend');
        
        // Load footer
        await loadComponent('footer.html', 'beforeend');
        
        // Load banner CSS
        loadCSS('banner.css');
        
        // Load banner JS
        loadJS('banner.js');
        
    } catch (error) {
        console.error('Error loading components:', error);
    }
}

function loadComponent(url, position) {
    return fetch(url)
        .then(response => {
            if (!response.ok) throw new Error(`Failed to load ${url}`);
            return response.text();
        })
        .then(data => {
            const header = document.querySelector('header');
            if (header && position === 'afterend') {
                header.insertAdjacentHTML(position, data);
            } else {
                document.body.insertAdjacentHTML(position, data);
            }
        });
}

function loadCSS(url) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = url;
    document.head.appendChild(link);
}

function loadJS(url) {
    const script = document.createElement('script');
    script.src = url;
    script.defer = true;
    document.body.appendChild(script);
}