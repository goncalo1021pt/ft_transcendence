


export  class UserPage extends BaseComponent {

	constructor() {
		super('static/main/html/user.html');
	}

	onIni(){
		document.getElementById("user").style.color = "red"
		console.log("onIni UserPage")
	}

	onDestroy(){
	
	}

}

customElements.define('user-page', UserPage);