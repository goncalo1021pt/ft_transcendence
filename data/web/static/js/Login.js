export  class LoginPage extends BaseComponent {

	constructor() {
		super('static/html/login.html');
	}

	async onIni() {
		const element = this.getElementById("login");
		if (element) {
			element.innerHTML = "Hello, this is the login page!";
		}
	}

	onDestroy(){
	
	}

	

}

customElements.define('login-page', LoginPage);