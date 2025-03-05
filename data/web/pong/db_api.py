from channels.db import database_sync_to_async
from .models import OngoingGame, CompletedGame

class GameDB:
	@staticmethod
	async def create_game(game_id: str, player1_id: str, player2_id: str = None):
		return await database_sync_to_async(OngoingGame.create_game)(
			game_id, player1_id, player2_id
		)

	@staticmethod
	async def update_score(game_id: str, player1_sets: int, player2_sets: int):
		return await database_sync_to_async(OngoingGame.update_score)(game_id, player1_sets, player2_sets)

	@staticmethod
	async def player_in_game(username: str):
		return await database_sync_to_async(OngoingGame.player_in_game)(username)
	
	@staticmethod
	async def delete_game(game_id: str):
		return await database_sync_to_async(OngoingGame.delete_game)(game_id)
	

	@staticmethod
	async def complete_game(game_id: str, winner: str):
		try:
			ongoing = await database_sync_to_async(OngoingGame.objects.get)(game_id=game_id)
			await database_sync_to_async(CompletedGame.create_from_ongoing)(ongoing, winner)
			return True
		except OngoingGame.DoesNotExist:
			return False