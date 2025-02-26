import { AuthService } from '../index/AuthService.js';

export class LoginView extends BaseComponent {
	constructor() {
		super('/login-view/');
	}

	async onIni() {
		if (AuthService.isAuthenticated) {
			window.location.hash = '#/home';
			return;
		}

		const form = this.getElementById('login-form');
		const errorDiv = this.getElementById('form-errors');
		const login42Button = this.getElementById('login_42');

		form?.addEventListener('submit', async (e) => {
			e.preventDefault();
			errorDiv.textContent = '';
			
			try {
				const formData = new FormData(form);
				await AuthService.login(
					formData.get('username'),
					formData.get('password')
				);
				window.location.hash = '#/home';
			} catch (error) {
				errorDiv.textContent = error.message;			
			}
		});

		login42Button?.addEventListener('click', async () => {
			window.location.href = 'https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-f8562a1795538b5f2a9185781d374e1152c6466501442d50530025b059fe92ad&redirect_uri=https%3A%2F%2Flocalhost%3A8080%2Foauth_callback%2F&response_type=code';
			
		});
	}
}

customElements.define('login-view', LoginView);