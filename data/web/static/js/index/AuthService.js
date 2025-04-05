export class AuthService {
	static isAuthenticated = false;
	static currentUser = null;
	static currentpfp = null;
	static host = null;

	static async init() {		
		try {
			await this.check_auth();
			await this.fetchHost();
		} catch (error) {
			throw error;
		}
		
	}
	
	static async login(username, password) {
		const response = await fetch('/login/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': this.getCsrfToken(),
			},
			body: JSON.stringify({ username, password })
		});

		const data = await response.json();
		if (response.ok) {
			console.log(response);
			if (response.status === 201) {
				console.log('2fa required');
				document.getElementById('login-form').style.display = 'none';
				document.getElementById('2fa-form').style.display = 'block';
	
				// Store the username for the 2FA request
				const storedUsername = username;
	
				// Add event listener for the 2FA form submission
				document.getElementById('2fa-form').onsubmit = async (e) => {
					e.preventDefault();
					const code = document.getElementById('2fa-code').value;
	
					const response = await fetch('/verify_2fa_login/', {
						method: 'POST',
						headers: {
							'Content-Type': 'application/json',
							'X-CSRFToken': this.getCsrfToken(),
						},
						body: JSON.stringify({ username: storedUsername, code }) // Include username in the request
					});
	
					const data = await response.json();
					if (response.ok) {
						this.isAuthenticated = true;
						this.currentUser = data.user;
						window.location.reload();
					} else {
						alert(data.error); // need to change to a modal
					}
				};
			} else {
				this.isAuthenticated = true;
				this.currentUser = data.user;
				window.location.reload();
				// window.location.hash = '#/home';
			}
		} else {
			const error = new Error(data.error);
			error.status = response.status;
			throw error;
		}
	}


	static async login42() {
		const host = this.host;
		const redirectUri = encodeURIComponent(`https://${host}/oauth/callback/`);
		window.location.href = `https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-f8562a1795538b5f2a9185781d374e1152c6466501442d50530025b059fe92ad&redirect_uri=${redirectUri}&response_type=code`;
	}


    static async logout() {
        const response = await fetch('/logout/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': this.getCsrfToken(), 
			},
		});

		if (response.ok) {
			this.isAuthenticated = false;
			this.currentUser = null;
		}
		window.location.reload();
    }


	static async register(userData) {
		const response = await fetch('/register/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': this.getCsrfToken(),
			},
			body: JSON.stringify(userData)
		});

		const data = await response.json();
		if (!response.ok) {
			throw new Error(Object.values(data).join('\n'));
		}
	}

	static async change_password(oldpsw, newpsw) {
		const response = await fetch('/change-password/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': this.getCsrfToken()
			},
			body: JSON.stringify({
				current_password: oldpsw,
				new_password: newpsw
			})
		});
		return response;
	}

	static async toggle2fa(enabled) {
		const response = await fetch('/disable_2fa/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': this.getCsrfToken()
			},
			body: JSON.stringify({ two_factor_enable: enabled })
		});	
		return response;
	}

	static async check_auth() {
		const response = await fetch('/check-auth/', {
			method: 'GET',
		});
		const data = await response.json();
		this.isAuthenticated = data.isAuthenticated;
		if (this.isAuthenticated && data.user) {
			this.currentUser = data.user.username;
			this.currentpfp = data.user.profile_pic;
		} else {
			this.currentUser = null;
			this.currentpfp = null;
		}
	}


	static async fetchHost() {
		const response = await fetch('/get-host/', {
			method: 'GET',
		});
		const data = await response.json();
		this.host = data.host;
	}


	static getCsrfToken() {
		return document.cookie
			.split('; ')
			.find(row => row.startsWith('csrftoken='))
			?.split('=')[1];
	}

}