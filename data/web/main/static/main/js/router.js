document.addEventListener('DOMContentLoaded', () => {
    const content = document.getElementById('content');
    
    function loadContent(page) {
        switch(page) {
            case 'home':
                content.innerHTML = '<h1>Welcome to Transcendence</h1>';
                break;
            case 'users':
                content.innerHTML = '<h1>Users List</h1>';
                break;
            case 'profile':
                content.innerHTML = '<h1>Profile Page</h1>';
                break;
        }
    }

    // Handle navigation
    window.addEventListener('hashchange', () => {
        const page = window.location.hash.slice(1) || 'home';
        loadContent(page);
    });

    // Load initial content
    loadContent('home');
});