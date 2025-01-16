export  class ProfilePage extends BaseComponent {

	constructor() {
		super('static/main/html/profile.html');
	}

	async onIni() {
		const element = this.getElementById("profile");
		if (element) {
			//
		}
	}

	onDestroy(){
	
	}

}

customElements.define('profile-page', ProfilePage);