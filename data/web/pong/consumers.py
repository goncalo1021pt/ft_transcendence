from channels.generic.websocket import AsyncWebsocketConsumer
from .pong import PongGame, MultiPongGame, AiPongGame
from .pong_components import Player
from multiprocessing import Process
from .ai.pong_ai_components import AITraining
from .db_api import GameDB
import json, os, neat, logging


logger = logging.getLogger('pong')

class SinglePongConsumer(AsyncWebsocketConsumer):
	active_games = {}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.mode = 'vs'
		self.id = None
		self.game : PongGame = None
	
	def get_username(self):
		return self.scope["user"].username if self.scope["user"].is_authenticated else None
	
	def get_user_id(self):
		return self.scope["user"].uuid if self.scope["user"].is_authenticated else None


	async def connect(self):
		if not self.scope["user"].is_authenticated:
			await self.close()
			return
		# self.id = self.get_username()
		self.id = self.get_user_id()
		if self.id in self.active_games:
			await self.close()
			return
		await self.accept()


	async def disconnect(self, close_code):
		if self.id in self.active_games:
			if not self.game:
				return
			self.game.remove_consumer(self)
			del self.active_games[self.id]


	async def receive(self, text_data):
		data = json.loads(text_data)
		if 'action' not in data:
			return
		match data['action']:
			case 'connect':
				if self.id not in self.active_games:
					self.active_games[self.id] = self.id
				
				mode = 'ai' if data.get('mode') == 'ai' else 'vs'
				self.game = PongGame(mode)
				self.game.add_consumer(self)
				await self.game.init_game_components()
				await self.game.start()
				

			case 'paddle_move_start':
					paddle = self.game.paddleLeft if data.get('side') == 'left' else self.game.paddleRight
					paddle.direction = -1 if data.get('direction') == 'up' else 1
			case 'paddle_move_stop':
					paddle = self.game.paddleLeft if data.get('side') == 'left' else self.game.paddleRight
					paddle.direction = 0


	async def broadcast(self, message):
		try:
			await self.send(json.dumps(message))
		except Exception as e:
			logger.error(f"Error sending message: {e}")

	async def broadcast_game_start(self, game):
		await self.broadcast({
			'event': 'game_start',
			'state': game.get_start_data()
		})

	async def broadcast_game_state(self, game):
		await self.broadcast({
			'event': 'game_state',
			'state': {
				'l_paddle_y': game.paddleLeft.y,
				'r_paddle_y': game.paddleRight.y,
				'ball_x': game.ball.x,
				'ball_y': game.ball.y,
			}
		})

	async def broadcast_game_end(self, winner: Player):
		await self.broadcast({
			'event': 'game_end',
			'state': {
				'winner': winner.player_id
			}
		})

	async def broadcast_game_score(self, score_data: dict):
		await self.broadcast(score_data)


class MultiPongConsumer(SinglePongConsumer):
	active_games = {}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
	
	async def connect(self):
		if not self.scope["user"].is_authenticated:
			await self.close()
			return
		self.game_id = self.scope['url_route']['kwargs']['game_id']
		#self.player_id = self.get_username()
		self.player_id = self.get_user_id()
		await self.accept()


	async def receive(self, text_data):
		data = json.loads(text_data)
		if 'action' not in data:
			return
			
		match data['action']:
			case 'connect':
				if self.game_id not in self.active_games:
					await self.create_game()
				elif self.is_full():
					await self.close()
				elif self.is_rejoin():
					await self.rejoin_game()
				else:
					await self.join_game()
					await self.active_games[self.game_id]['game'].start()
			
			case 'paddle_move_start':
				if paddle := self.get_player_paddle():
					paddle.direction = -1 if data.get('direction') == 'up' else 1
			
			case 'paddle_move_stop':
				if paddle := self.get_player_paddle():
					paddle.direction = 0


	async def disconnect(self, close_code):
		if not self.game:
			return

		if self.game_id in self.active_games:
			game_entry = self.active_games[self.game_id]
			if game_entry:
				# consumer removes himself from game_entry reference
				side = ('left' if game_entry['left'] and game_entry['left']['socket'] == self 
					else 'right' if game_entry['right'] and game_entry['right']['socket'] == self 
					else None)
				if side:
					game_entry[side]['socket'] = None
					game_entry['game'].remove_consumer(self)

				# only remove game if both consumers are gone
				if not game_entry['left']['socket'] and not game_entry['right']['socket']:
					if (winner := game_entry['game'].scoreBoard.end_match()):
						await GameDB.complete_game(game_entry['game'].game_id, winner.player_id)
					else:
						#await GameDB.complete_game(game_entry['game'].game_id, self.player_id)
						await GameDB.complete_game(game_entry['game'].game_id, self.scope["user"].username)
					await GameDB.delete_game(self.game_id)
					del self.active_games[self.game_id]


	def get_player_paddle(self):
		game = self.active_games.get(self.game_id)
		if not game:
			return None
		return (game['game'].paddleLeft if self.player_id == game['left']['id'] 
				else game['game'].paddleRight if self.player_id == game['right']['id'] 
				else None)
	

	async def create_game(self):
		self.active_games[self.game_id] = {
			'left': {'id': self.player_id, 'socket': self},
			'right': None,
			'game': MultiPongGame(self.game_id)
		}
		self.game = self.active_games[self.game_id]['game']
		self.active_games[self.game_id]['game'].add_consumer(self)


	async def join_game(self):
		game_entry = self.active_games[self.game_id]
		game_entry['right'] = {'id': self.player_id, 'socket': self}
		game = game_entry['game']
		self.game = game
		game.add_consumer(self)
		await game.init_game_components()
		await GameDB.create_game(self.game_id, game_entry['left']['id'], self.player_id)


	async def rejoin_game(self):
		game_entry = self.active_games[self.game_id]
		side = 'left' if (game_entry['left'] and game_entry['left']['id'] == self.player_id) else 'right'
		game_entry[side]['socket'] = self
		self.game = game_entry['game']
		self.game.add_consumer(self)
		await self.broadcast_game_start(self.game)


	def is_rejoin(self) -> bool:
		game_entry = self.active_games.get(self.game_id)
		if not game_entry:
			return False
		# if game is not full and our id is already in game, we are rejoining :)
		return ((game_entry['left'] and self.player_id == game_entry['left']['id']) or 
				(game_entry['right'] and self.player_id == game_entry['right']['id']))
	
	def is_full(self) -> bool:
		game_entry = self.active_games.get(self.game_id)
		if not game_entry:
			return False
		# game is full if both consumers are present
		return (game_entry['left'] and game_entry['left']['socket'] and 
				game_entry['right'] and game_entry['right']['socket'])
	
	
	async def broadcast_game_score(self, score_data: dict):
		await super().broadcast_game_score(score_data)
		await GameDB.update_score(self.game_id, score_data['state']['player1_sets'], score_data['state']['player2_sets'])

class AIConsumer(SinglePongConsumer):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		local_dir = os.path.dirname(__file__)
		config_path = os.path.join(local_dir, "ai/config.txt")
		self.config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
								neat.DefaultSpeciesSet, neat.DefaultStagnation,
								config_path)
		self.training_mode = False


	async def connect(self):

		if self.training_mode == True:
			process = Process(target=AITraining, args=(self.config,))
			process.start()
			return
		else:
			if not self.scope["user"].is_authenticated:
				await self.close()
				return

			# self.id = self.get_username()
			self.id = self.get_user_id()
			if self.id in self.active_games:
				await self.close()
				return

			if self.id not in self.active_games:
				self.active_games[self.id] = self.id
			else:
				await self.close()
				return
			await self.accept()


	async def disconnect(self, close_code):
		if self.id in self.active_games:
			if not self.game:
				return
			self.game.remove_consumer(self)
			del self.active_games[self.id]

	async def receive(self, text_data):
		data = json.loads(text_data)
		if 'action' not in data:
			return
		match data['action']:
			case 'connect':
				self.game = AiPongGame()
				self.game.add_consumer(self)
				await self.game.init_game_components()
				await self.game.start()

			case 'paddle_move_start':
				paddle = self.game.paddleLeft
				paddle.direction = -1 if data.get('direction') == 'up' else 1
			case 'paddle_move_stop':
				paddle = self.game.paddleLeft
				paddle.direction = 0

