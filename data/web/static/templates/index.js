import { UserPage } from '../js/UserPage.js'
import { HomePage } from '../js/HomePage.js'
import { ProfilePage } from '../js/ProfilePage.js'
import { SinglePongPage } from '../js/SinglePong.js'
import { LoginPage } from '../js/Login.js'

// Register routes
Router.subscribe('home', HomePage)
Router.subscribe('users', UserPage)
Router.subscribe('profile', ProfilePage)
Router.subscribe('pong', SinglePongPage)
Router.subscribe('login', LoginPage)


Router.init()
