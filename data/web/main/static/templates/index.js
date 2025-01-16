import { UserPage } from '../js/UserPage.js'
import { HomePage } from '../js/HomePage.js'
import { ProfilePage } from '../js/ProfilePage.js'

// Register routes
Router.subscribe('home', HomePage)
Router.subscribe('users', UserPage)
Router.subscribe('profile', ProfilePage)


Router.init()
