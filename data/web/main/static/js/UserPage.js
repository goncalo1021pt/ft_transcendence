export  class UserPage extends BaseComponent {

	constructor() {
		super('static/html/user.html');
	}

	async onIni() {
		const element = this.getElementById("user");
		if (element) {
			//
		}
	}

	onDestroy(){
	
	}

}

customElements.define('user-page', UserPage);