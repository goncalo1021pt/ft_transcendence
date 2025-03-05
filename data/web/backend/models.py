from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):  # Inherits all these fields:
	# Username
	# First name
	# Last name
	# Email
	# Password
	# Groups
	# User permissions
	# Is staff
	# Is active
	# Is superuser
	# Last login
	# Date joined
<<<<<<< HEAD
=======
	is_42_user = models.BooleanField(default=False)
	id_42 = models.IntegerField(default=0)
>>>>>>> refs/remotes/origin/goncalo
	uuid : models.UUIDField = None
	pass