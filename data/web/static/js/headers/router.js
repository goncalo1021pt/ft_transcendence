document.addEventListener('DOMContentLoaded', () => {

});

class BaseComponent extends HTMLElement {
	constructor(template) {
		super();
		this.contentLoaded = this.loadTemplate(template);
	}

	getElementById(id){
		return this.querySelector("#" + id)
	}

	onIni(){
		// overriden in child classes
	}

	disconnectedCallback() {
		this.onDestroy();
	}

	onDestroy(){
		// overriden in child classes
	}

	async loadTemplate(template) {
		try {
			const response = await fetch(template);
			if (!response.ok) {
				throw new Error('Failed to fetch template');
			}
			const html = await response.text();
			this.innerHTML = html;
			this.onIni();
		} catch (error) {
			console.error('Template loading failed:', error);
		}
	}

}

customElements.define('base-component', BaseComponent);

class Router {
	static routes = {};

	static subscribe(url, component) {
		// Remove leading slash if present to normalize routes
		url = url.replace(/^\//, '');
		this.routes[url] = component;
	}

	static go(url) {
		// Remove leading slash if present
		url = url.replace(/^\//, '');
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
		const defaultRoute = 'home';
		window.addEventListener('hashchange', () => {
			// Extract page name after #/ and remove leading slash
			const page = window.location.hash.slice(2).replace(/^\//, '') || defaultRoute;
			this.go(page);
		});
		const currentHash = window.location.hash.slice(2).replace(/^\//, '');
		this.go(currentHash || defaultRoute);
	}
}



