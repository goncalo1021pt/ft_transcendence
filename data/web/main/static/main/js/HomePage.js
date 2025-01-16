export  class HomePage extends BaseComponent {

	constructor() {
		super('static/main/html/home.html');
	}

	async onIni() {
		const element = this.getElementById("home");
		if (element) {
			//
		}
	}

	onDestroy(){
	
	}

}

customElements.define('home-page', HomePage);