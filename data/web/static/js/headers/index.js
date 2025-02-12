import { NavMenu } from '../nav/NavMenu.js';
import { LoginMenu } from '../login/LoginMenu.js';
import { HomeView } from '../home/HomeView.js';
import { PongView } from '../pong/PongView.js';
import { ProfileView } from '../profile/ProfileView.js';

//Router.subscribe('', NavMenu);
//customElements.define('nav-menu', NavMenu);
Router.subscribe('home', HomeView);
Router.subscribe('pong', PongView);
Router.subscribe('profile', ProfileView);

Router.init();
