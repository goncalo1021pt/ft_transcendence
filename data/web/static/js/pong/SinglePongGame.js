import { Player, Paddle, Ball, ScoreBoard, GameField } from './PongComponents.js';
import * as THREE from 'three';

export class QuickLobby {
	constructor(parent, view) {
		this.parent = parent;
		this.view = view;
		this.socket = null;
		this.lobbyElement = null;
	}

	createLobbyElement() {
		const lobbyDiv = document.createElement('div');
		const statusText = document.createElement('div');
		const cancelButton = document.createElement('button');
	
		lobbyDiv.classList.add('pong-lobby'); 
		statusText.classList.add('lobby-status');
		cancelButton.classList.add('lobby-button');
	
		statusText.textContent = "Searching for opponent...";
		cancelButton.textContent = "Cancel";
	
		lobbyDiv.appendChild(statusText);
		lobbyDiv.appendChild(cancelButton);
		this.lobbyElement = lobbyDiv;
		this.statusText = statusText;
		this.cancelButton = cancelButton; 
		this.parent.appendChild(lobbyDiv);
	
		cancelButton.addEventListener('click', () => {
			if (this.socket) {
				this.socket.close();
			}
			this.parent.removeChild(lobbyDiv);
			this.refreshView();
		});
	}

	startLobby() {
		this.createLobbyElement();
		this.socket = new WebSocket(`wss://${window.location.host}/wss/mpong/`);
		this.setupSocketHandlers();
	}

	setupSocketHandlers() {
		this.socket.onopen = () => {
			this.socket.send(JSON.stringify({
				action: "connect",
			}));
		};
	
		this.socket.onmessage = (event) => {
			const data = JSON.parse(event.data);
			switch(data.event) {
				case 'player_count':
					this.statusText.textContent = `Players in queue: ${data.state.player_count}`;
					break;
				case 'match_found':
					this.statusText.textContent = 'Match found! Starting game...';
					this.parent.removeChild(this.lobbyElement);
					const game = new MultiPongGame(this.parent, data.state, this.view);
					game.startGame();
					break;
			}
		};

		this.socket.onclose = () => {
			console.log('Lobby Socket closed');
		};

		this.socket.onerror = (error) => {
			console.log('Socket error', error);
		}
	}

	refreshView() {
		// window.location.reload();
		const hash = window.location.hash.substring(2);
		Router.go(hash);
	}
}

export class TournamentLobby extends QuickLobby {
    constructor(parent, view, gameId) {
        super(parent, view);
        this.gameId = gameId;
    }
    
	// createLobbyElement() {
	// 	super.createLobbyElement();
	// 	this.lobbyElement.removeChild(this.cancelButton);
	// }

    startLobby() {
        this.createLobbyElement(); 
        this.socket = new WebSocket(`wss://${window.location.host}/wss/mpong/tournament/${this.gameId}/`);
        this.setupSocketHandlers(); 
    }
}

export class PongGame {
	constructor(container, view) {
		this.container = container;
		this.view = view;
		this.socket = null;
		this.gameField = null;
		this.scoreBoard = null;
		this.ball = null;
		this.paddleLeft = null;
		this.paddleRight = null;
		this.player1 = null;
		this.player2 = null;
		this.view.registerGame(this);
		this.gameDiv = null;
        
        // Three.js components
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.threeContainer = null;
        this.animationFrameId = null;
        
        // Game dimensions for calculations
        this.fieldWidth = 0;
        this.fieldHeight = 0;
	}

	setupSocketHandlers() {
		this.socket.onmessage = (event) => {
			const data = JSON.parse(event.data);
			this.handleGameEvent(data.event, data.state);
		};
		this.socket.onopen = () => console.log("Game socket opened");
		this.socket.onclose = (event) => console.log("Game socket closed");
		this.socket.onerror = (error) => console.log(error);
	}
    
    setupThreeJS() {
        this.scene = new THREE.Scene();
        this.scene.background = null;
		// const aspectRatio = this.fieldWidth / this.fieldHeight;
		const aspectRatio = 1280 / 720;
		this.camera = new THREE.PerspectiveCamera(60, aspectRatio, 0.1, 2000);
		this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true});
		// this.renderer.setSize(this.fieldWidth, this.fieldHeight);
		this.renderer.setSize(1280, 720);

		this.renderer.setPixelRatio(window.devicePixelRatio > 1 ? 2 : 1);
		this.renderer.powerPreference = "high-performance";
		this.renderer.physicallyCorrectLights = false;

		this.gameDiv.appendChild(this.renderer.domElement);
		// const light = new THREE.AmbientLight(0xffffff, 2);
		// this.scene.add(light);
        this.startAnimationLoop();
    }
    
	cameraSetup(playerSide) {
		const fieldCenterX = this.fieldWidth / 2;
		const fieldCenterY = this.fieldHeight / 2;

		if (playerSide === 'left') {
			const leftPaddleX = 0;
			const leftPaddleY = fieldCenterY;
			this.camera.position.set(leftPaddleX - 230, -leftPaddleY, 500);
			this.camera.lookAt(fieldCenterX - 150, -fieldCenterY, 0);
			this.camera.rotation.z = -Math.PI / 2;
		} else if (playerSide === 'right') {
			const rightPaddleX = this.fieldWidth;
			const rightPaddleY = fieldCenterY;
			this.camera.position.set(rightPaddleX + 230, -rightPaddleY, 500);
			this.camera.lookAt(fieldCenterX + 150, -fieldCenterY, 0);
			this.camera.rotation.z = Math.PI / 2;
		} else {
			this.camera.position.set(fieldCenterX, -fieldCenterY - 100, 900);
			this.camera.lookAt(fieldCenterX, -fieldCenterY, 0);
		}
	}

	startAnimationLoop() {
		const animate = () => {
			this.animationFrameId = requestAnimationFrame(animate);
			this.renderer.render(this.scene, this.camera);
		};
		animate();
	}

	createGameElements() {
		const gameDiv = document.createElement('div');
		gameDiv.classList.add('game-container');
        const scoreBoardElement = document.createElement('div');
		this.scoreBoard = new ScoreBoard(scoreBoardElement);
        this.gameField = new GameField();
        this.paddleLeft = new Paddle();
        this.paddleRight = new Paddle();
        this.ball = new Ball();
		gameDiv.appendChild(scoreBoardElement);
		this.container.appendChild(gameDiv);
		this.gameDiv = gameDiv;
	}

	handleGameEvent(event, state) {
		switch(event) {
			case "game_state":
				this.updateGameState(state);
				break;
			case "score_update":
				this.updateScore(state);
				break;
			case "game_start":
				this.handleGameStart(state);
				break;
			case "game_end":
				this.updateGameState(state);
				this.scoreBoard.showWinner(state.winner);
				if (this.player1) this.player1.remove();
				if (this.player2) this.player2.remove();
				this.view.insertBackButton();
				break;
		}
	}

	updateGameState(state) {
		this.paddleLeft.update(state.l_paddle_y);
		this.paddleRight.update(state.r_paddle_y);
		this.ball.update(state.ball_x, state.ball_y);
	}

	updateScore(state) {
		this.scoreBoard.update(
			state.player1_score,
			state.player2_score,
			state.player1_sets,
			state.player2_sets
		);
	}

	handleGameStart(state) {
		this.createGameElements();
		this.fieldWidth = state.field_width;
		this.fieldHeight = state.field_height;
		this.setupThreeJS();
		this.gameField.createMesh(this.scene, state.field_width, state.field_height);
		this.paddleLeft.update(state.l_paddle_y, state.l_paddle_x, state.paddle_width, state.paddle_height);
		this.paddleRight.update(state.r_paddle_y, state.r_paddle_x, state.paddle_width, state.paddle_height);
		this.paddleLeft.createMesh(this.scene, state.l_paddle_x, state.l_paddle_y, state.paddle_width, state.paddle_height, 20, 0x0000ff);
		this.paddleRight.createMesh(this.scene, state.r_paddle_x, state.r_paddle_y, state.paddle_width, state.paddle_height, 20, 0xff0000);
		this.ball.update(state.ball_x, state.ball_y, state.ball_size, this.scene);
		this.ball.createMesh(this.scene, state.ball_x, state.ball_y, state.ball_size, 0xffffff);
		this.scoreBoard.update(
			state.player1_score, 
			state.player2_score, 
			state.player1_sets, 
			state.player2_sets,
			state.player1_id,
			state.player2_id
		);
		this.scoreBoard.createUi(state.win_points, state.win_sets);
		
		// state.win_points, for ui
		// state.set_points

		this.setupPlayers(state);
		console.log("Game started!");
	}

	setupPlayers(state) {
		throw new Error("Method 'setupPlayers' must be implemented");
	}

	cleanup() {
		if (this.socket) this.socket.close();
		if (this.player1) this.player1.remove();
		if (this.player2) this.player2.remove();

        if (this.gameField) this.gameField.remove();
        if (this.paddleLeft) this.paddleLeft.remove();
        if (this.paddleRight) this.paddleRight.remove();
        if (this.ball) this.ball.remove();

        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
        }
        
        if (this.renderer) {
            this.renderer.dispose();
        }
        
		this.view.unregisterGame(this);
		if (this.gameDiv && this.gameDiv.parentNode) {
			this.gameDiv.parentNode.removeChild(this.gameDiv);
		}
	}
}

export class AIPongGame extends PongGame {
	constructor(container, view) {
		super(container, view);
		this.trainingMode = null;  // Will be set from the server
	}

	async startGame() {
		this.socket = new WebSocket(`wss://${window.location.host}/wss/aipong/`);
		this.setupSocketHandlers();
		this.socket.onopen = () => {
			this.socket.send(JSON.stringify({
				action: "connect",
			}));
		};
	}

	setupPlayers(state) {
		this.player1 = new Player(state.player1_id, this.paddleLeft, this.socket, "left");
		this.player2 = new Player(state.player2_id, this.paddleRight, this.socket, "right");
		// p2 should be ai player ?! doesnt need socket
		this.player1.inputManager('a', 'd');
		this.cameraSetup('left');
	}
}

export class SinglePongGame extends PongGame {
	constructor(container, view) {
		super(container, view);
		this.mode = 'vs';
	}

	async startGame(mode = 'vs') {
		this.mode = mode;
		this.socket = new WebSocket(`wss://${window.location.host}/wss/spong/`);
		this.setupSocketHandlers();
		this.socket.onopen = () => {
			this.socket.send(JSON.stringify({
				action: "connect",
				mode: this.mode
			}));
		};
	}

	setupPlayers(state) {
		this.player1 = new Player(state.player1_id, this.paddleLeft, this.socket, "left");
		this.player2 = new Player(state.player2_id, this.paddleRight, this.socket, "right");
		this.player1.inputManager('w', 's');
		if (this.mode === 'vs') {
			this.player2.inputManager('ArrowUp', 'ArrowDown');
		}
		this.cameraSetup();
	}
}

export class MultiPongGame extends PongGame {
	constructor(container, matchData, view) {
		super(container, view);
		this.game_id = matchData.game_id;
		this.game_url = matchData.game_url;
		this.player_id = matchData.player_id;
	}

	async startGame() {
		this.socket = new WebSocket(`wss://${window.location.host}/${this.game_url}`);
		this.setupSocketHandlers();
		
		this.socket.onopen = () => {
			this.socket.send(JSON.stringify({
				action: "connect"
			}));
		};
	}

	setupPlayers(state) {
		this.selfKeys = ['d', 'a'];
		this.player1 = new Player(state.player1_id, this.paddleLeft, this.socket, "left");
		this.player2 = new Player(state.player2_id, this.paddleRight, this.socket, "right");
		(this.player_id === state.player1_id
			? this.player1.inputManager(this.selfKeys[1], this.selfKeys[0])
			: this.player2.inputManager(this.selfKeys[0], this.selfKeys[1]));
		(this.player_id === state.player1_id
			? this.cameraSetup('left')
			: this.cameraSetup('right'));
	}
}

