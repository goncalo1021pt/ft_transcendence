from django.db import models

class Game(models.Model):
	game_id = models.CharField(max_length=100, unique=True)
	player1_username = models.CharField(max_length=150)
	player1_sets = models.IntegerField(default=0)
	player2_username = models.CharField(max_length=150)
	player2_sets = models.IntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		abstract = True

class OngoingGame(Game):
	@classmethod
	def create_game(cls, game_id, username1, username2=None):
		return cls.objects.create(
			game_id=game_id,
			player1_username=username1,
			player2_username=username2
		)

	@classmethod
	def player_in_game(cls, username):
		return cls.objects.filter(
			models.Q(player1_username=username) | 
			models.Q(player2_username=username)
		).values_list('game_id', flat=True).first()

	@classmethod
	def delete_game(cls, game_id):
		cls.objects.filter(game_id=game_id).delete()

	@classmethod
	def update_score(cls, game_id : str, player1_sets : int, player2_sets : int):
		game = cls.objects.get(game_id=game_id)
		if not game:
			return
		game.player1_sets = player1_sets
		game.player2_sets = player2_sets
		game.save()

class CompletedGame(Game):
	winner_username = models.CharField(max_length=150)
	completed_at = models.DateTimeField(auto_now_add=True) # = created_at for self

	@classmethod
	def create_from_ongoing(cls, ongoing_game, winner: str):
		return cls.objects.create(
			game_id=ongoing_game.game_id,
			player1_username=ongoing_game.player1_username,
			player2_username=ongoing_game.player2_username,
			player1_sets=ongoing_game.player1_sets,
			player2_sets=ongoing_game.player2_sets,
			winner_username=winner
		)