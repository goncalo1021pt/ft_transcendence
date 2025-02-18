def read_secret(secret_name):
	try:
		with open('/run/secrets/' + secret_name) as f:
			return f.read().strip()
	except IOError:
		return None

SOCIALACCOUNT_PROVIDERS = {
	'42': {
		'SCOPE': ['public'],
		'AUTH_PARAMS': {'access_type': 'online'},
		'METHOD': 'oauth2',
		'VERIFIED_EMAIL': False,
		'VERSION': 'v2',
		'CLIENT_ID': read_secret('forty_two_client_id'),
		'SECRET': read_secret('forty_two_secret'),
	}
}