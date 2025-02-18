from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider	

class FortyTwoProvider(OAuth2Provider):
	id = 'forty-two'
	name = '42'
	package = 'authservice.providers'
	
	def get_default_scope(self):
		return ['public']
	
provider_classes = [FortyTwoProvider]