import { QuickLobby, SinglePongGame, MultiPongGame } from './SinglePongGame.js';
export class PongView extends BaseComponent {
	constructor() {
		super('static/html/pong-view.html');
		this.game = null;
	}

	async onIni() {
		const element = this.getElementById("pong-view");
		if (!element) return;
		
		const menu = new PongStartMenu(element, (game) => {
			if (this.game) {
				this.game.cleanup();
			}
			this.game = game;
		});
		menu.render();
	}

	onDestroy() {
		if (this.game) {
			this.game.cleanup();
		}
	}
}

customElements.define('pong-view', PongView);

export class PongStartMenu {
	constructor(parent, onGameCreated) {
		this.parent = parent;
		this.onGameCreated = onGameCreated;
	}

	render() {
		const menuDiv = document.createElement('div');
		const startVersus = document.createElement('button');
		const startAi = document.createElement('button');
		const startQuick = document.createElement('button');

		menuDiv.classList.add('pong-menu');
		startVersus.textContent = "Start Versus";
		startAi.textContent = "Start AI";
		startQuick.textContent = "Quick Match";

		[startVersus, startAi, startQuick].forEach(button => {
			button.classList.add('pong-menu-button');
			menuDiv.appendChild(button);
		}); 

		startVersus.addEventListener('click', () => {
			this.parent.removeChild(menuDiv);
			const game = new SinglePongGame(this.parent);
			this.onGameCreated(game);
			game.startGame('vs');
		});

		startAi.addEventListener('click', () => {
			this.parent.removeChild(menuDiv);
			const game = new SinglePongGame(this.parent);
			this.onGameCreated(game);
			game.startGame('ai');
		});

		startQuick.addEventListener('click', () => {
			this.parent.removeChild(menuDiv);
			const lobby = new QuickLobby(this.parent, (game) => {
				this.onGameCreated(game);
			});
			lobby.startLobby();
		});
		
		this.parent.appendChild(menuDiv);
	}
}
