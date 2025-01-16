document.addEventListener('DOMContentLoaded', () => {

});

class BaseComponent extends HTMLElement {
	constructor(template) {
		super();
		fetch(template).then(async (response) => {
			if (response.ok) {
				const html = await response.text()
				this.innerHTML = html
				this.onIni();
			}
			else
				console.error('Failed to fetch users')
		})	
	}

	getElementById(id){
		return this.querySelector("#"+id)
	}


	onIni(){
		console.log("onIni")
	}

	disconnectedCallback() {
		this.onDestroy();
	}

	onDestroy(){
		console.log("onDestroy")
	}

}

customElements.define('base-component', BaseComponent);

class Router {
    static routes = {};

    static subscribe(url, component) {
        this.routes[url] = component;
    }

    static go(url) {
        const component = this.routes[url];
        if (component) {
            const content = document.getElementById('content');
            if (content) {
                content.innerHTML = "";
                content.append(new component());
            } else {
                console.error('Content element not found');
            }
        } else {
            console.error(`No component found for route: ${url}`);
        }
    }

    static init() {
        const defaultRoute = 'home';  // Set the default route
        window.addEventListener('hashchange', () => {
            const page = window.location.hash.slice(1) || defaultRoute;
            this.go(page);
        });
        this.go(defaultRoute);  // Load the default route on page load
    }
}

Router.init();

