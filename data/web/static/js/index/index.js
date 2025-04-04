import { NavMenu } from '../nav/NavMenu.js';
import { LoginMenu } from '../login/LoginMenu.js';

import { HomeView } from '../home/HomeView.js';
import { PongView } from '../pong/PongView.js';
import { TournamentView } from '../pong/TournamentView.js';
import { ProfileView } from '../profile/ProfileView.js';
import { RegisterView } from '../login/RegisterView.js';
import { LoginView } from '../login/LoginView.js';
import { AuthService } from '../index/AuthService.js';
import { TwofactorView } from '../login/TwoFactorView.js';


Router.subscribe('home', HomeView);
Router.subscribe('profile', ProfileView);
Router.subscribe('pong', PongView);
Router.subscribe('tournament', TournamentView);
Router.subscribe('register', RegisterView);
Router.subscribe('login', LoginView);
Router.subscribe('two-factor', TwofactorView);


await AuthService.init();
Router.init();
