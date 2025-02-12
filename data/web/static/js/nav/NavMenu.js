export class NavMenu extends BaseComponent {
    constructor() {
        super('static/html/nav-menu.html');
    }

    async onIni() {
        const menu = this.querySelector('.nav-menu');
        if (!menu) return;

        
        // Add menu button class
        menu.classList.add('nav-menu-button');

        // Create navigation buttons container
        const buttonContainer = document.createElement('div');
        buttonContainer.classList.add('nav-buttons');

        
        // Create navigation buttons
        const homeButton = document.createElement('div');
        const pongButton = document.createElement('div');

        // Set up buttons
        [homeButton, pongButton].forEach(button => {
            button.classList.add('nav-button');
        });

        homeButton.textContent = "HOME";
        pongButton.textContent = "PONG";

        // Add navigation handlers
        homeButton.addEventListener('click', () => {
            window.location.hash = '#/home';
            menu.classList.remove('expanded');
        });

        pongButton.addEventListener('click', () => {
            window.location.hash = '#/pong';
            menu.classList.remove('expanded');
        });

        // Add buttons to container
        buttonContainer.appendChild(homeButton);
        buttonContainer.appendChild(pongButton);

        // Add container to menu
        menu.appendChild(buttonContainer);

        // Toggle menu expansion
        menu.addEventListener('click', (e) => {
            e.stopPropagation();
            menu.classList.toggle('expanded');
        });

        // Close menu when clicking outside
        document.addEventListener('click', () => {
            menu.classList.remove('expanded');
        });
    }
}

customElements.define('nav-menu', NavMenu);
