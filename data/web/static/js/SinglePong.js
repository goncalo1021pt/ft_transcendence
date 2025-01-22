export class SinglePongPage extends BaseComponent {
	constructor() {
		super('static/html/singlepong.html');
	}

	async onIni() {
		const element = this.getElementById("game-container");
		if (element) {
			this.paddle = this.getElementById("paddle");
			this.gameField = this.getElementById("game-field");
			this.scoreElement = this.getElementById("score");
			this.currentPaddleY = 250;

			const socket = new WebSocket(`ws://${window.location.host}/ws/pong/`);
			
			socket.onopen = () => {
				socket.send(JSON.stringify({
					action: "connect"
				}));
			};

			socket.onclose = (event) => {
				
			};

			socket.onerror = (error) => {
				
			};

			socket.onmessage = (event) => {
				// console.log('Message received:', event.data);
				const data = JSON.parse(event.data);
				if (data.event === "game_state") {
					const state = data.state;
					this.currentPaddleY = state.paddle_y;
					this.paddle.style.top = `${state.paddle_y}px`;
				}
			};
			
			this.socket = socket;
			this.currentPaddleY = 250;
			
			window.addEventListener("keydown", (e) => {
				e.preventDefault();
				if (e.key === "ArrowUp") {
					this.currentPaddleY = Math.max(0, this.currentPaddleY - 10);
					socket.send(JSON.stringify({
						action: "move_paddle",
						paddle_y: this.currentPaddleY
					}));
				} else if (e.key === "ArrowDown") {
					this.currentPaddleY = Math.min(500, this.currentPaddleY + 10);
					socket.send(JSON.stringify({
						action: "move_paddle",
						paddle_y: this.currentPaddleY
					}));
				}
			});
		}
	}

	onDestroy() {
		if (this.socket) {
			this.socket.close();
		}
	}
}

customElements.define('singlepong-page', SinglePongPage);


// this.heartbeatInterval = setInterval(() => {
// 	if (socket.readyState === WebSocket.OPEN) {
// 		socket.send(JSON.stringify({
// 			action: "heartbeat"
// 		}));
// 	}
// }, 30000); // Send heartbeat every 30 seconds

// socket.onclose = (event) => {
// 	console.log("WebSocket closed:", event);
// 	clearInterval(this.heartbeatInterval);
// };