export class LadderboardView extends BaseComponent {
	constructor() {
		super('/ladderboard-view/');
	}

	async onIni() {
		const element = this.getElementById("ladderboard-view");
		if (element) {
			// Initialize home view
		}
	}
}

customElements.define('ladderboard-view', LadderboardView);