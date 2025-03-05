from channels.generic.websocket import AsyncWebsocketConsumer
from .db_api import GameDB
import json, time, secrets

class QuickLobby(AsyncWebsocketConsumer):
	queued_players = {}

	def generate_game_id(self) -> str:
		timestamp = int(time.time())
		token = secrets.token_hex(4)
		return f"{timestamp}:{token}"
	
	def get_username(self):
		return self.scope["user"].username if self.scope["user"].is_authenticated else None

	async def broadcast_player_count(self):
		for player in self.queued_players.values():
			await player.send(json.dumps({
				'event': 'player_count',
				'state': {
					'player_count': len(self.queued_players)
				}
			}))

	async def connect(self):
		if not self.scope["user"].is_authenticated:
			await self.close()
			return
		self.player_id = self.get_username()

		if ongoing_game := await GameDB.player_in_game(self.player_id):
			
			reconnect_data = {
				'event': 'match_found',
				'state': {
					'game_id': ongoing_game,
					'game_url': f'wss/mpong/game/{ongoing_game}/',
				}
			}
			await self.accept()
			await self.send(json.dumps(reconnect_data))
			await self.close()
			return

		await self.accept()
		
		self.queued_players[self.player_id] = self
		await self.broadcast_player_count()
		await self.try_match_players()


	async def disconnect(self, close_code):
		if hasattr(self, 'player_id') and self.player_id in self.queued_players:
			del self.queued_players[self.player_id]
			await self.broadcast_player_count()


	async def receive(self, text_data):
		data = json.loads(text_data)
		if 'action' not in data:
			return


	async def try_match_players(self):
		if len(self.queued_players) >= 2:
			players = list(self.queued_players.keys())[:2]
			game_id = f"{self.generate_game_id()}"
			
			# send match data before removing from queue
			match_data = {
				'event': 'match_found',
				'state': {
					'game_id': game_id,
					'game_url': f'wss/mpong/game/{game_id}/',
					'player1_id': players[0],
					'player2_id': players[1]
				}
			}
			
			# send match data and close connections
			player1 = self.queued_players[players[0]]
			player2 = self.queued_players[players[1]]
			
			await player1.send(json.dumps(match_data))
			await player2.send(json.dumps(match_data))
			
			# remove from queue and close lobby connections
			del self.queued_players[players[0]]
			del self.queued_players[players[1]]
			await player1.close()
			await player2.close()


