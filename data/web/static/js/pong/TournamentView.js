import { AuthService } from '../index/AuthService.js';
import { MultiPongGame, TournamentLobby } from './SinglePongGame.js';

export class TournamentView extends BaseComponent { // could extend pongview ?
	constructor() {
		super('/tournament-view/');
		this.activeGames = new Set();
	}

	async onIni() {
		await this.contentLoaded;
		this.element = this.getElementById("tournament-view");
		if (!this.element) return;
		
		const menu = new TournamentMenu(this.element, this);
		await menu.initialize();
		this.pollInterval = setInterval(() => menu.poll(), 5000);
		// beforeunload event to clean up games ?
	}

	registerGame(game) {
		this.activeGames.add(game);
	}

	unregisterGame(game) {
		this.activeGames.delete(game);
	}

	insertBackButton() {
		const backButton = document.createElement('button');
		backButton.textContent = "Back to Tournament";
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
		clearInterval(this.pollInterval);
		for (const game of this.activeGames) {
			game.cleanup();
		}
		this.activeGames.clear();
	}
}

class TournamentMenu {
	constructor(parent, view) {
		this.parent = parent;
		this.view = view;
		this.errorDiv = null;
		this.menuDiv = null;
	}

	async initialize() {
		this.menuDiv = this.parent.querySelector('.container-fluid');
		this.errorDiv = this.parent.querySelector('#tournament-errors');
		this.setupEventListeners();
		await this.poll();
	}

	async poll() {
		await this.fetchTournamentHistory();
		await this.fetchTournaments();
	}

	setupEventListeners() {
		const createBtn = this.parent.querySelector("#create-tournament");
		const joinBtn = this.parent.querySelector("#join-tournament");
		const leaveBtn = this.parent.querySelector("#leave-tournament");

		createBtn?.addEventListener('click', () => this.createTournament());
		joinBtn?.addEventListener('click', () => this.joinTournament());
		leaveBtn?.addEventListener('click', () => this.leaveTournament());
	}

	async fetchTournaments() {
		const response = await fetch('/tournament-view/list/', {
			method: 'GET',
		});
		const data = await response.json();
		this.updateTournamentState(data);
		this.updateTournamentsList(data.tournaments);
	}

	updateTournamentState(data) {
		const stateDiv = this.parent.querySelector("#tournament-state");
		if (!stateDiv) return;

		if (data.in_tournament && data.current_tournament) {
			const t = data.current_tournament;
			let stateHTML = `
				<div class="mb-2">Tournament ID: <span class="badge bg-secondary">${data.current_tournament_id}</span></div>
				<div class="mb-2">Status: <span class="badge bg-secondary">${t.status}</span></div>
				${t.status === 'IN_PROGRESS' ? `<div class="mb-2">Round: <span class="badge bg-success">${t.current_round + 1}</span></div>` : ''}
				<div class="mb-3">Players: ${t.players.join(', ')}</div>
			`;

			if (t.status === 'IN_PROGRESS' && t.rounds.length > 0 && t.current_round < t.rounds.length) {
				const currentRoundMatches = t.rounds[t.current_round];
				stateHTML += this.renderCurrentRoundMatches(currentRoundMatches);
			}

			stateDiv.innerHTML = stateHTML;
			this.setupMatchButtons();
			
			const leaveBtn = this.parent.querySelector("#leave-tournament");
			if (leaveBtn) 
				leaveBtn.classList.remove('d-none');
		} else {
			stateDiv.innerHTML = '<div class="text-secondary">Not in tournament</div>';
			

			const leaveBtn = this.parent.querySelector("#leave-tournament");
			if (leaveBtn) 
				leaveBtn.classList.add('d-none');
		}
	}

	async fetchTournamentHistory() {
		const response = await fetch('/tournament-view/history/', {
			method: 'GET',
		});
		const data = await response.json();
		this.updateTournamentHistory(data);
	}
	
	updateTournamentHistory(data) {
		const historyDiv = this.parent.querySelector("#last-tournament");
		if (!historyDiv) return;
	
		if (!data.has_history) {
			historyDiv.innerHTML = '<div class="text-secondary">No tournament history</div>';
			return;
		}
	
		const t = data.tournament;
		const userStatus = t.elimination_round 
			? `Eliminated in round ${t.elimination_round} of ${t.total_rounds}`
			: '🏆 Tournament Winner!';
	
		historyDiv.innerHTML = `
			<div class="card bg-dark bg-opacity-25 border-secondary">
				<div class="card-body p-3">
					<div class="d-flex justify-content-between mb-2">
						<span>ID: <span class="badge bg-secondary">${t.id}</span></span>
						<span>Winner: <span class="badge bg-success">${t.winner}</span></span>
					</div>
					<div class="text-center">
						<span class="${t.elimination_round ? 'text-warning' : 'text-success'}">${userStatus}</span>
					</div>
				</div>
			</div>
		`;
	}

	async joinTournamentMatch(gameId) {
		this.parent.innerHTML = '';
		
		const wrapper = document.createElement('div');
		wrapper.classList.add('tournament-game-wrapper', 'h-100', 'd-flex', 'flex-column');
		this.parent.appendChild(wrapper);
		
		const gameContainer = document.createElement('div');
		gameContainer.classList.add('tournament-game-container', 'flex-grow-1', 'mb-3');
		wrapper.appendChild(gameContainer);
		
		// const backButton = document.createElement('button');
		// backButton.textContent = "Back to Tournament";
		// backButton.classList.add('btn', 'btn-outline-light', 'tournament-back-button'); 
		// wrapper.appendChild(backButton);
		
		// backButton.addEventListener('click', () => {
		// 	this.view.activeGames.forEach(game => game.cleanup());
		// 	this.view.activeGames.clear();  
		// 	// window.location.reload();
		// 	const hash = window.location.hash.substring(2);
		// 	Router.go(hash);
		// });
		
		const tournamentLobby = new TournamentLobby(gameContainer, this.view, gameId);
		tournamentLobby.startLobby();
	}

	renderCurrentRoundMatches(matches) {
		return `
			<h5 class="border-bottom pb-2 mb-3">Current Round Matches</h5>
			<div class="tournament-matches">
				${matches.map(match => this.renderMatch(match)).join('')}
			</div>
		`;
	}

	renderMatch(match) {
		let statusClass = "bg-secondary";
		if (match.status === "COMPLETED") statusClass = "bg-success";
		if (match.status === "IN_PROGRESS") statusClass = "bg-primary";
		return `
			<div class="card bg-dark bg-opacity-25 border-secondary mb-2">
				<div class="card-body p-3">
					<div class="d-flex justify-content-between align-items-center mb-2">
						<div class="match-players">${match.player1 || 'TBD'} vs ${match.player2 || 'TBD'}</div>
						<span class="badge ${statusClass}">${match.status}</span>
					</div>
					${match.winner ? `<div class="text-success mb-2">Winner: ${match.winner}</div>` : ''}
					${match.is_player_match && match.status === 'PENDING' ? `
						<button class="join-match-button btn btn-sm btn-outline-light w-100 tournament-join-btn" 
								data-game-id="${match.game_id}">
							Join Match
						</button>
					` : ''}
				</div>
			</div>
		`;
	}

	setupMatchButtons() {
		this.parent.querySelectorAll('.join-match-button').forEach(button => {
			button.addEventListener('click', () => {
				const gameId = button.dataset.gameId;
				this.joinTournamentMatch(gameId);
			});
		});
	}

	updateTournamentsList(tournaments) {
		const container = this.parent.querySelector("#tournaments-container");
		if (!container) return;

		if (tournaments?.length) {
			container.innerHTML = tournaments.map(t => `
				<div class="list-group-item tournament-item bg-dark bg-opacity-50 border-0" data-tournament-id="${t.tournament_id}">
					<div class="d-flex justify-content-between align-items-center">
						<span>ID: <span class="badge bg-secondary">${t.tournament_id}</span></span>
						<span class="badge ${t.status === 'WAITING' ? 'bg-warning' : t.status === 'IN_PROGRESS' ? 'bg-primary' : 'bg-success'}">${t.status}</span>
						<span>Players: <span class="badge bg-info">${t.player_count}/${t.max_players}</span></span>
					</div>
				</div>
			`).join('');
		} else {
			container.innerHTML = '<div class="list-group-item bg-dark bg-opacity-50 border-0 text-secondary">No active tournaments</div>';
		}

		container.querySelectorAll('.tournament-item').forEach(item => {
			item.addEventListener('click', () => {
	
				container.querySelectorAll('.tournament-item').forEach(el => 
					el.classList.remove('active'));
	
				item.classList.add('active');
			});
		});
	}

	async createTournament() {
		this.clearError();
		const response = await fetch('tournament-view/create/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': AuthService.getCsrfToken(),
			},
			body: JSON.stringify({ action: 'create' })
		});
		
		const data = await response.json();
		if (!this.handleError(response, data)) {
			await this.fetchTournaments();
		}
	}

	async joinTournament() {
		this.clearError();
		const selectedRow = this.parent.querySelector('.active');
		if (!selectedRow) return;

		const tournamentId = selectedRow.dataset.tournamentId;
		const response = await fetch('tournament-view/join/', {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': AuthService.getCsrfToken(),
			},
			body: JSON.stringify({ tournament_id: tournamentId })
		});
		
		const data = await response.json();
		if (!this.handleError(response, data)) {
			await this.fetchTournaments();
		}
	}

	async leaveTournament() {
		this.clearError();
		const response = await fetch('tournament-view/leave/', {
			method: 'DELETE',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': AuthService.getCsrfToken(),
			}
		});
		
		const data = await response.json();
		if (!this.handleError(response, data)) {
			await this.fetchTournaments();
		}
	}

	clearError() {
		if (this.errorDiv) {
			this.errorDiv.textContent = '';
		}
	}

	handleError(response, data) {
		if (!response.ok && this.errorDiv) {
			this.errorDiv.textContent = data.message;
			return true;
		}
		return false;
	}
}

customElements.define('tournament-view', TournamentView);