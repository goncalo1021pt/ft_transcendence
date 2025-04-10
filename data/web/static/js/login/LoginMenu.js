import { AuthService } from '../index/AuthService.js';
import { ProfileView } from '../profile/ProfileView.js';

export class LoginMenu extends BaseComponent {
    constructor() {
        super('/login-menu/');
    }

    async onIni() {
		await this.contentLoaded;
		this.menu = this.querySelector('.login-menu');
		this.notificationBadge = document.getElementById('menu-notification-badge');
		const loginClient = new LoginClient(this);

        if (!this.menu) return;
        
        this.menu.addEventListener('click', (e) => {
            e.stopPropagation();
            this.menu.classList.toggle('expanded');
			this.notificationBadge && (this.notificationBadge.style.opacity = this.menu.classList.contains('expanded') ? '0' : '1');
        });

        document.addEventListener('click', () => {
            this.menu.classList.remove('expanded');
			if (this.notificationBadge) {this.notificationBadge.style.opacity = '1';}
        });
        
        const logoutButton = this.querySelector('#logout-button');
        if (logoutButton) {
            logoutButton.addEventListener('click', async () => {
                await AuthService.logout();
            });
        }
    }

	async reloadElements() {
		
		const response = await fetch('/login-menu/');
		if (response.ok) {
			const html = await response.text();
			const tempDiv = document.createElement('div');
			tempDiv.innerHTML = html;
			
			const newMenu = tempDiv.querySelector('.login-menu');
			if (newMenu) {
				if (this.menu) {this.menu.innerHTML = newMenu.innerHTML;}

				const newBadge = tempDiv.querySelector('#menu-notification-badge');
				if (newBadge) {
					if (this.notificationBadge) {
						this.notificationBadge.innerHTML = newBadge.innerHTML;
					}
					else {
						this.notificationBadge = newBadge;
						this.menu.parentNode.insertBefore(this.notificationBadge, this.menu);
					}
					this.notificationBadge.style.opacity = this.menu.classList.contains('expanded') ? '0' : '1';
				}
				else if (!newBadge && this.notificationBadge) {
					this.notificationBadge.remove();
					this.notificationBadge = null;
				}
			}

			const logoutButton = this.querySelector('#logout-button');
			if (logoutButton) {
				logoutButton.addEventListener('click', async () => {
					await AuthService.logout();
				});
			}

			if (Router.activeComponent instanceof ProfileView) {
				if (Router.activeComponent.friendTab) {
					Router.activeComponent.friendTab.reloadElements();
				}
			}
		}
	}

}

class LoginClient {
	constructor(loginView) {
		this.loginView = loginView;
		this.socket = new WebSocket(`wss://${window.location.host}/wss/login-menu/`);
		this.setupSocketHandler();
	}

	setupSocketHandler() {
		this.socket.onopen = () => {
			this.socket.send(JSON.stringify({
				action: "connect",
			}));
			this.pingInterval = setInterval(() => {
				this.sendPing();
			}, 30000);
		};

		this.socket.onmessage = (event) => {
			
			const data = JSON.parse(event.data);
			switch(data.event) {
				case 'pong':
					this.loginView.reloadElements();
					console.log(event.data);
					break;
				case 'notification':
					this.loginView.reloadElements();
					console.log(event.data);
					break;
				case 'tournament':
					this.tournamentAlert();
					console.log(event.data);
					break;
			}
		};

		this.socket.onclose = () => {
			console.log('Login menu socket closed');
            if (this.pingInterval) {
                clearInterval(this.pingInterval);
            }
		};

		this.socket.onerror = (error) => {
			console.log('Login menu socket error', error);
			this.socket.close();
		}
	}

	tournamentAlert() {
		if (this.socket && window.location.hash != '#/tournament') {
			const container = document.getElementById('toastContainer');
			if (!container) return;
	
			const alertDiv = document.createElement('div');
			alertDiv.className = 'alert alert-info alert-dismissible fade show';
			alertDiv.role = 'alert';
			alertDiv.innerHTML = `
			<div class="toast-header">
				<strong class="me-auto">Tournament</strong>
				<small class="text-body-secondary">update</small>
			</div>
			<div class="toast-body" style="cursor: pointer;">
				Tournament Bracket Updated.
			</div>
			`;
			container.appendChild(alertDiv);
			alertDiv.addEventListener('click', function(e) {
				window.location.hash = '#/tournament';
				alertDiv.remove()
			});

			setTimeout(() => {
				alertDiv.remove();
			}, 7000);
		}
	}

    sendPing() {
        if (this.socket) {
            this.socket.send(JSON.stringify({
                action: "ping"
            }));
        }
    }
}


customElements.define('login-menu', LoginMenu);