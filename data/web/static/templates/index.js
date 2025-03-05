import { NavMenu } from '../js/nav/NavMenu.js';
import { HomeView } from '../js/home/HomeView.js';
import { PongView } from '../js/pong/PongView.js';

//Router.subscribe('', NavMenu);
//customElements.define('nav-menu', NavMenu);
Router.subscribe('home', HomeView);
Router.subscribe('pong', PongView);

Router.init();
