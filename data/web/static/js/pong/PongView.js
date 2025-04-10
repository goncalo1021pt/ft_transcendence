import { QuickLobby, SinglePongGame, AIPongGame } from './SinglePongGame.js';
import { Ball } from './PongComponents.js';
import * as THREE from 'three';

export class PongView extends BaseComponent {
	constructor() {
		super('/pong-view/');  
		this.activeGames = new Set();
		this.element = null;
	}

	async onIni() {
		await this.contentLoaded;
		this.element = this.getElementById("pong-view");
		if (!this.element) return;
		
		const menu = new PongStartMenu(this.element, this);
		menu.init();

		this.gameElement = new GameElementDisplay('3d-pong-asset');
		this.gameElement.init();

		window.addEventListener('beforeunload', () => {
			for (const game of this.activeGames) {
				game.cleanup();
			}
			this.activeGames.clear();
			this.gameElement.cleanup();
		});
	}

	registerGame(game) {
		this.activeGames.add(game);
	}

	unregisterGame(game) {
		this.activeGames.delete(game);
	}

	insertBackButton() {
		const backButton = document.createElement('button');
		backButton.textContent = "Back to Menu";
		backButton.classList.add('btn', 'btn-outline-light', 'tournament-back-button'); 
		this.element.appendChild(backButton);
		
		backButton.addEventListener('click', () => {
			this.activeGames.forEach(game => game.cleanup());
			this.activeGames.clear();  
			const hash = window.location.hash.substring(2);
			Router.go(hash);
		});
		
	}

	onDestroy() {
		if (this.gameElement) { this.gameElement.cleanup(); }
		for (const game of this.activeGames) {
			game.cleanup();
		}
		this.activeGames.clear();
		window.removeEventListener('beforeunload', this.beforeUnloadListener);
	}
}

customElements.define('pong-view', PongView);


export class PongStartMenu {
    constructor(parent, view) {
        this.parent = parent;
        this.view = view;
    }

    init() {
        const menuContainer = this.parent.querySelector('.pong-menu-container');
        const menuDiv = this.parent.querySelector('.pong-menu');
        const startVersus = menuDiv.querySelector('#start-versus');
        const startAi = menuDiv.querySelector('#start-ai');
        const startQuick = menuDiv.querySelector('#start-quick');
        const startTournament = menuDiv.querySelector('#start-tournament');

        startVersus.addEventListener('click', () => {
            this.parent.removeChild(menuContainer);
			this.view.gameElement.cleanup();
            const game = new SinglePongGame(this.parent, this.view);
            game.startGame('vs');
        });

        startAi.addEventListener('click', () => {
            this.parent.removeChild(menuContainer);
			this.view.gameElement.cleanup(); 
            const game = new AIPongGame(this.parent, this.view);
            game.startGame('ai');
        });

        startQuick.addEventListener('click', () => {
            this.parent.removeChild(menuContainer); 
			this.view.gameElement.cleanup();
            const lobby = new QuickLobby(this.parent, this.view);  
            lobby.startLobby();
        });

        startTournament.addEventListener('click', () => {
            this.parent.removeChild(menuContainer); 
            window.location.hash = '#/tournament';
        });
    }
}

export class GameElementDisplay {
    constructor(parent) {
        this.parent = document.getElementById(parent);
        if (!this.parent) {
            console.error(`parent container not found`);
            return;
        }
		this.userInfo = document.getElementById("user-info");
		this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.ball = null;
		this.animationFrameId = null;
	}

	init() {
		this.setupThreeJS();
		this.startAnimationLoop();
	}

	setupThreeJS() {
		this.scene = new THREE.Scene();
		this.scene.background = null;
		const aspectRatio = 200 / 200;
		this.camera = new THREE.PerspectiveCamera(60, aspectRatio, 0.1, 1000);
        this.camera.position.set(0, 0, 100);
        this.camera.lookAt(0, 0, 0);

		this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true});
		this.renderer.setSize(200, 200);
		this.renderer.setPixelRatio(window.devicePixelRatio > 1 ? 2 : 1);
		this.renderer.powerPreference = "high-performance";
		this.renderer.physicallyCorrectLights = false;

		this.parent.appendChild(this.renderer.domElement);

		this.ball = new Ball();
		this.ball.createMesh(this.scene, 0, 0, 30, 0x9D9494);
	}

	startAnimationLoop() {
		let time = 0;
		const oscillationSpeed = 0.01;

		const animate = () => {
			time += oscillationSpeed;
			this.animationFrameId = requestAnimationFrame(animate);
			this.renderer.render(this.scene, this.camera);
			
			const x = Math.sin(time) * 0.4;        
			const y = Math.cos(time * 0.3) * 0.4;  
			
			this.ball.directionIndicator(this.scene, this.ball.direction.x, y);
			this.ball.direction = { x, y };

		};
		animate();
	}



	cleanup() {
        if (this.ball) this.ball.remove();

        if (this.animationFrameId) { cancelAnimationFrame(this.animationFrameId); }

        if (this.renderer) { this.renderer.dispose(); }

		if (this.parent) { this.parent.innerHTML = '';}

		if (this.userInfo) { this.userInfo.innerHTML = ''; }
		
		console.log('GameElementDisplay cleaned up');
	}	
}