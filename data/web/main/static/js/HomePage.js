export  class HomePage extends BaseComponent {

	constructor() {
		super('static/html/home.html');
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