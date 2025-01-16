import { UserPage } from './UserPage.js'
import { HomePage } from './HomePage.js'
import { ProfilePage } from './ProfilePage.js'

// Register routes
Router.subscribe('home', HomePage)
Router.subscribe('users', UserPage)
Router.subscribe('profile', ProfilePage)


Router.init()
