import { AuthService } from "../index/AuthService.js";

export class ProfileView extends BaseComponent {
	constructor(username = null) {
		super(username ? `/profile-view/${encodeURIComponent(username)}/` : '/profile-view/');
		this.requestedUsername = username;
	}

	async onIni() {
		await this.contentLoaded;
		const element = this.getElementById("profile-view");
		if (!element) return;
		this.friendTab = new FriendTab(this);
		this.accountTab = new AccountTab(this);
		this.setupAccountButtons();
		this.setupFriendButtons();
	}

	setupFriendButtons() {
		this.setupButton('friend-button', (e) => this.friendTab.handleFriendRequest(e));
		this.setupButton('accept-friend-button', (e) => this.friendTab.handleFriendRequest(e));
		this.setupButton('reject-friend-button', (e) => this.friendTab.handleFriendRequest(e));
		this.setupButton('cancel-friend-button', (e) => this.friendTab.handleFriendRequest(e));
		this.setupButton('remove-friend-button', (e) => this.friendTab.handleFriendRequest(e));
	}

	setupAccountButtons() {
		this.setupButton('edit-profile-btn', () => this.accountTab.enableEditMode());
		this.setupButton('save-profile-btn', () => this.accountTab.saveProfile('save-profile-btn'));
		this.setupButton('cancel-edit-btn', () => this.accountTab.reloadElements());
		this.setupButton('change-picture-btn', () => this.accountTab.toggleElement('profile-pic-options'));
		this.setupButton('change-password-btn', () => this.accountTab.showChangePasswordFields());
		this.setupButton('confirm-password-btn', () => this.accountTab.changePassword());
		this.setupButton('cancel-password-btn', () => this.accountTab.hideChangePasswordFields());

		this.accountTab.setupSecurityButton();
	}

	setupButton(id, callback) {
		const buttons = document.querySelectorAll(`#${id}`);
		
		if (buttons.length > 1) {
			buttons.forEach(button => {
				button.addEventListener('click', callback);
			});
		} 
		else if (buttons.length === 1) {
			buttons[0].addEventListener('click', callback);
		}
	}

}


class FriendTab {
	constructor(profileView) {
		this.profileView = profileView;
		this.requestedUsername = profileView.requestedUsername;
		this.searchfield = null;
		this.setupSearchAutocomplete();		
	}

	async handleFriendRequest(e) {
		if (e.target.closest('a')) {
			e.preventDefault();
			e.stopPropagation();
		}
		
		const action = e.target.getAttribute('data-action');
		const username = e.target.getAttribute('data-request-id') ;
		const response = await fetch(`/friends/${action}/`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': AuthService.getCsrfToken(),
			},
			body: JSON.stringify({ username: username })
		});
		if (response.ok) {
			await this.reloadElements();
		}
	}

	async reloadElements() {
		const newView = await fetch(this.requestedUsername ? `/profile-view/${encodeURIComponent(this.requestedUsername)}/` : '/profile-view/');
		if (newView.ok) {
			const html = await newView.text();

			const tempDiv = document.createElement('div');
			tempDiv.innerHTML = html;

			const newFriendsList = tempDiv.querySelector('#friends');
			if (newFriendsList) {
				const currentFriendsTab = document.getElementById('friends');
				if (currentFriendsTab) {
					currentFriendsTab.innerHTML = newFriendsList.innerHTML;
				}
			}

			const newFriendsTab = tempDiv.querySelector('#friends-tab');
			if (newFriendsTab) {
				const currentFriendsTabBtn = document.getElementById('friends-tab');
				if (currentFriendsTabBtn) {
					currentFriendsTabBtn.innerHTML = newFriendsTab.innerHTML;
				}
			}

			const newProfileLeftContainer = tempDiv.querySelector('#profile-left-container .mt-3');
			if (newProfileLeftContainer) {
				const currentProfileLeftContainer = document.querySelector('#profile-left-container .mt-3');
				if (currentProfileLeftContainer) {
					currentProfileLeftContainer.innerHTML = newProfileLeftContainer.innerHTML;
				}
			}
		
			this.profileView.setupFriendButtons();
			// this.profileView.setupAccountButtons();
			this.setupSearchAutocomplete();
		}
	}


	setupSearchAutocomplete() {
		this.searchfield = document.getElementById('friend-search-field');
		if (!this.searchfield) return;
		
		this.dropdownContainer = document.createElement('div');
		this.dropdownContainer.className = 'position-absolute bg-dark border rounded-bottom shadow-sm w-25  d-none';
		this.dropdownContainer.id = 'friend-search-dropdown';

		const searchContainer = this.searchfield.parentNode;
		searchContainer.style.position = 'relative';
		searchContainer.appendChild(this.dropdownContainer);
		
		let debounceTimer;
		this.searchfield.oninput = () => {
			clearTimeout(debounceTimer);
			
			if (this.searchfield.value.trim().length < 2) {
				this.dropdownContainer.classList.add('d-none');
				return;
			}
			
			debounceTimer = setTimeout(() => {
				this.fetchUserSuggestions();
			}, 300);
		};
		
		document.addEventListener('click', (e) => {
			if (!this.searchfield.contains(e.target) ) {
				this.dropdownContainer.classList.add('d-none');
			}
		});
	}

	async fetchUserSuggestions() {
		const query = this.searchfield.value.trim();
		if (query.length < 2) {
			this.dropdownContainer.classList.add('d-none');
			return;
		}
		console.log('fetching user suggestions');
		const response = await fetch(`/friends/find-user/?q=${encodeURIComponent(query)}`);
		if (!response.ok) throw new Error('Search request failed');
		
		const data = await response.json();
		this.renderSuggestions(data.results);

	}

	renderSuggestions(results) {
		this.dropdownContainer.innerHTML = '';
		
		if (results.length === 0) {
			this.dropdownContainer.classList.add('d-none');
			return;
		}
		
		results.forEach(user => {
			const item = document.createElement('div');
			item.className = 'p-2 border-bottom d-flex align-items-center';
			item.id = `friend-search-item`;
			item.style.cursor = 'pointer';
			
			item.innerHTML = `
				<img src="${user.profile_pic}" alt="${user.username}" 
					 class="rounded-circle me-2" style="width: 24px; height: 24px;">
				<span>${user.username}</span>
			`;

			item.addEventListener('click', () => {
				window.location.hash = `#/profile/${user.username}/`;

			});
			
			this.dropdownContainer.appendChild(item);

		});
		
		this.dropdownContainer.classList.remove('d-none');
	}

}


class AccountTab {
	constructor(profileView) {
		this.profileView = profileView;
	}

	async saveProfile(id) {
		try {
			const formData = {
				username: this.profileView.getElementById('username').value,
				email: this.profileView.getElementById('email').value,
				about_me: this.profileView.getElementById('about').value
			};

			const selectedPic = this.profileView.querySelector('input[name="profile-pic"]:checked');
			if (selectedPic) {
				formData.profile_pic = selectedPic.value;
			}

			const response = await fetch('/profile/update/', {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': AuthService.getCsrfToken(),
				},
				body: JSON.stringify(formData)
			});

			const data = await response.json();

			if (response.ok) {
				this.showMessage('success', data.message);
				const saveBtn = this.profileView.getElementById(id);
				saveBtn.classList.add('d-none');
				this.reloadElements();
			} else {
				this.showMessage('error', data.error);
			}
		} catch (error) {
			this.showMessage('error', error);
		}
	}

	async toggle2FA(enabled) {
		const toggle = this.profileView.getElementById('twoFactorToggle');
		const badge = toggle.nextElementSibling.querySelector('.badge');
		const originalState = !enabled;

		badge.textContent = '...';
		badge.classList.add('bg-secondary');
		badge.classList.remove('bg-success');

		try {
			const response = await AuthService.toggle2fa(enabled);
			const data = await response.json();

			if (response.ok && data.success) {
				badge.textContent = enabled ? 'ON' : 'OFF';
				badge.classList.toggle('bg-secondary', !enabled);
				badge.classList.toggle('bg-success', enabled);

				this.showMessage('success', data.message);
			} else {
				toggle.checked = originalState;
				this.showMessage('error', data.error);
			}
		} catch (error) {
			toggle.checked = originalState;
			this.showMessage('error', error);
		}
	}

	async changePassword() {
		const currentPassword = this.profileView.getElementById('current-password').value;
		const newPassword = this.profileView.getElementById('new-password').value;

		try {
			const confirmButton = this.profileView.getElementById('confirm-password-btn');
			const originalText = confirmButton.textContent;
			confirmButton.disabled = true;
			confirmButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Verifying...';

			const response = await AuthService.change_password(currentPassword, newPassword); 
			const data = await response.json();

			confirmButton.disabled = false;
			confirmButton.textContent = originalText;

			if (response.ok && data.success) {
				this.showMessage('success', data.message);
				this.hideChangePasswordFields();
			} else {
				this.showMessage('error', data.error);
			}
		} catch (error) {
			this.showMessage('error', error);
		}
	}

	showMessage(type, message) {
		const existingAlerts = document.querySelectorAll('#profile-right-container .alert');
		if (existingAlerts.length >= 2) {
			existingAlerts[existingAlerts.length - 1].remove();
		}
	
		const alertDiv = document.createElement('div');
		alertDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
		alertDiv.role = 'alert';
		alertDiv.innerHTML = `
			${message}
			<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
		`;
	
		const tabContent = document.querySelector('.tab-content');
		tabContent.insertBefore(alertDiv, tabContent.firstChild);
	
		setTimeout(() => {
			alertDiv.classList.remove('show');
			setTimeout(() => alertDiv.remove(), 300);
		}, 5000);
	}

	async reloadElements() {
		const newView = await fetch(`/profile-view/`);
		if (newView.ok) {
			const html = await newView.text();
	
			const tempDiv = document.createElement('div');
			tempDiv.innerHTML = html;
	
			const newAccountTab = tempDiv.querySelector('#account');
			if (newAccountTab) {
				const currentAccountTab = document.getElementById('account');
				if (currentAccountTab) {
					currentAccountTab.innerHTML = newAccountTab.innerHTML;
				}
			}
	
			const newLeftContainer = tempDiv.querySelector('#profile-left-container');
			if (newLeftContainer) {
				const currentLeftContainer = document.querySelector('#profile-left-container');
				if (currentLeftContainer) {
					currentLeftContainer.innerHTML = newLeftContainer.innerHTML;
				}
			}
			this.profileView.setupAccountButtons();
			// this.profileView.setupFriendButtons();
		}
	}

	setupSecurityButton() {
		const securityBtn = this.profileView.getElementById('security-btn');
		if (securityBtn) {
			securityBtn.addEventListener('click', () => this.toggleSecurityOptions());
	
			// Setup 2FA toggle
			const twoFactorToggle = this.profileView.getElementById('twoFactorToggle');
	
			if (twoFactorToggle) {
				twoFactorToggle.addEventListener('change', (e) => {
					if (e.target.checked) {
						window.location.href = '#/two-factor';
					} else {
						this.toggle2FA(e.target.checked);
					}
				});
			}
		}
	}

	toggleElement(elementId) {
		const element = this.profileView.getElementById(elementId);
		if (element) {
			element.classList.toggle('d-none');
		}
	}

	toggleSecurityOptions() {
		const securityOptions = this.profileView.getElementById('security-options');
		const securityBtn = this.profileView.getElementById('security-btn');
		const caretIcon = securityBtn.querySelector('i');

		if (securityOptions.classList.contains('d-none')) {
			// Show options
			securityOptions.classList.remove('d-none');
			caretIcon.classList.replace('fa-caret-down', 'fa-caret-up');
			securityBtn.classList.add('active');

			// Animation
			securityOptions.style.opacity = '0';
			securityOptions.style.transform = 'translateY(-10px)';
			securityOptions.style.transition = 'opacity 0.3s, transform 0.3s';
			securityOptions.offsetHeight; // Trigger repaint
			securityOptions.style.opacity = '1';
			securityOptions.style.transform = 'translateY(0)';
		} else {
			// Hide with animation
			securityOptions.style.opacity = '0';
			securityOptions.style.transform = 'translateY(-10px)';
			securityBtn.classList.remove('active');
			caretIcon.classList.replace('fa-caret-up', 'fa-caret-down');

			setTimeout(() => securityOptions.classList.add('d-none'), 300);
		}
	}

	showChangePasswordFields() {
		const changePasswordBtn = this.profileView.getElementById('change-password-btn');
		const passwordFields = this.profileView.getElementById('password-fields');
		const securityCards = this.profileView.querySelectorAll('#security-options .card .card-body');

		securityCards.forEach(card => card.style.minHeight = '240px');

		changePasswordBtn.classList.add('d-none');
		passwordFields.classList.remove('d-none');

		this.profileView.getElementById('current-password').focus();
	}

	hideChangePasswordFields() {
		const securityCards = this.profileView.querySelectorAll('#security-options .card .card-body');
		securityCards.forEach(card => card.style.minHeight = '');

		this.profileView.getElementById('current-password').value = '';
		this.profileView.getElementById('new-password').value = '';
		this.profileView.getElementById('change-password-btn').classList.remove('d-none');
		this.profileView.getElementById('password-fields').classList.add('d-none');
	}

	enableEditMode() {
		// Toggle button visibility
		this.profileView.getElementById('edit-profile-btn').classList.add('d-none');
		this.profileView.getElementById('save-profile-btn').classList.remove('d-none');
		this.profileView.getElementById('cancel-edit-btn').classList.remove('d-none');

		// Enable form fields
		this.profileView.querySelectorAll('.profile-field').forEach(field => field.disabled = false);

		// Show profile picture section
		this.profileView.getElementById('profile-pic-section').classList.remove('d-none');

		// Hide security elements
		const securityBtn = this.profileView.getElementById('security-btn');
		if (securityBtn) securityBtn.classList.add('d-none');

		const securityOptions = this.profileView.getElementById('security-options');
		if (securityOptions && !securityOptions.classList.contains('d-none')) {
			securityOptions.classList.add('d-none');
		}
	}

}

customElements.define('profile-view', ProfileView);
