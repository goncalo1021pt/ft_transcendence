from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
from .pong_components import Paddle, Ball, Player, AIPlayer, ScoreBoard, GameField, GAME_SETTINGS

class PongGameConsumer(AsyncWebsocketConsumer):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.running : bool = False
		self.paddleLeft : Paddle = None
		self.paddleRight : Paddle = None
		self.player1 : Player = None 
		self.player2 : Player = None
		self.ball : Ball = None
		self.scoreBoard : ScoreBoard = None
		self.gamefield : GameField = None

	async def init_game_components(self):
		self.paddleLeft = Paddle(GAME_SETTINGS['l_paddle']['start_x'], GAME_SETTINGS['l_paddle']['start_y'])
		self.paddleRight = Paddle(GAME_SETTINGS['r_paddle']['start_x'], GAME_SETTINGS['r_paddle']['start_y'])
		self.ball = Ball()
		self.gamefield = GameField()
		await self.setup_players()  # Abstract method
		self.scoreBoard = ScoreBoard(self, self.player1, self.player2)
		self.running = True
		await self.broadcast_game_start()

	def get_start_data(self):
		return {
			'player1_id': self.player1.player_id,
			'player2_id': self.player2.player_id,
			'player1_score': self.player1.score,
			'player2_score': self.player2.score,
			'player1_sets': self.player1.sets,
			'player2_sets': self.player2.sets,
			'field_width': self.gamefield.width,
			'field_height': self.gamefield.height,
			'l_paddle_y': self.paddleLeft.y,
			'l_paddle_x': self.paddleLeft.x,
			'r_paddle_y': self.paddleRight.y,
			'r_paddle_x': self.paddleRight.x,
			'paddle_width': GAME_SETTINGS['paddle']['width'],
			'paddle_height': GAME_SETTINGS['paddle']['height'],
			'ball_size': self.ball.size,
		}

	async def broadcast_game_start(self):
		await self.send(json.dumps({
			'event': 'game_start',
			'state': self.get_start_data()
		}))

	async def game_loop(self):
		await self.init_game_components()
		self.ball.reset(self.scoreBoard, self.player1, self.player2)
		while self.running:
			await asyncio.sleep(1 / GAME_SETTINGS['display']['fps'])
			self.paddleLeft.update()
			self.paddleRight.update()
			self.ball.update(self.scoreBoard, self.player1, self.player2)
			await self.broadcast_game_state()
			if (winner := self.scoreBoard.end_match()):
				await self.broadcast_game_end(winner)
				break
		await self.disconnect(1000)

	async def setup_players(self):
		raise NotImplementedError()

	async def broadcast_game_state(self):
		raise NotImplementedError()

	async def broadcast_game_end(self, winner):
		raise NotImplementedError()
	
	async def broadcast_game_score(self, score_data : dict):
		await self.send(json.dumps(score_data))

	def get_session_key(self):
		session = self.scope.get("session", {})
		return session.session_key[:6] if session else None

class SinglePongConsumer(PongGameConsumer):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.mode = 'vs'


	async def setup_players(self):
		self.player1 = Player(self.get_session_key(), self.paddleLeft)
		self.player2 = Player(self.get_session_key() + " (2)", self.paddleRight) if self.mode == 'vs' else AIPlayer('Marvin', self.paddleRight)


	async def broadcast_game_state(self):
		if self.mode == 'ai':
			self.player2.update(self.ball)
		await self.send(json.dumps({
			'event': 'game_state',
			'state': {
				'l_paddle_y': self.paddleLeft.y,
				'r_paddle_y': self.paddleRight.y,
				'ball_x': self.ball.x,
				'ball_y': self.ball.y,
			}
		}))


	async def broadcast_game_end(self, winner : Player):
		await self.scoreBoard.send()
		await self.send(json.dumps({
			'event': 'game_end',
			'state': {
				'winner': winner.player_id
			}
		}))


	async def connect(self):
		await self.accept()


	async def disconnect(self, close_code):
		self.running = False


	async def receive(self, text_data):
		data = json.loads(text_data)
		if 'action' not in data:
			return
		match data['action']:
			case 'connect':
				self.mode = 'ai' if data.get('mode') == 'ai' else 'vs'
				asyncio.create_task(self.game_loop())
			case 'paddle_move_start':
				paddle = self.paddleLeft if data.get('side') == 'left' else self.paddleRight
				paddle.direction = -1 if data.get('direction') == 'up' else 1
			case 'paddle_move_stop':
				paddle = self.paddleLeft if data.get('side') == 'left' else self.paddleRight
				paddle.direction = 0


# active_games = {
#     'game_id123': {
#         'left': {
#             'id': 'abc123',         
#             'socket': consumer1     
#         },
#         'right': {
#             'id': 'def456',         
#             'socket': consumer2      
#         }
#		 'components': {
#			 'paddleLeft': Paddle(),
#			 'paddleRight': Paddle(),
#			 'ball': Ball(),
#			 'gamefield': GameField()}
#     }
# }
class MultiPongConsumer(PongGameConsumer):
	active_games = {}

	async def connect(self):
		self.game_id = self.scope['url_route']['kwargs']['game_id']
		self.player_id = self.get_session_key()
		await self.accept()

	async def receive(self, text_data):
		data = json.loads(text_data)
		if 'action' not in data:
			return
			
		match data['action']:
			case 'connect':
				if self.game_id not in self.active_games:
					self.active_games[self.game_id] = {
						'left': {'id': self.player_id, 'socket': self},
						'right': None
					}
				else:
					game = self.active_games[self.game_id]
					game['right'] = {'id': self.player_id, 'socket': self}
					await self.init_game_components()
					await self.init_remote_components()
					asyncio.create_task(self.game_loop())

			case 'paddle_move_start':
				if paddle := self.get_player_paddle():
					paddle.direction = -1 if data.get('direction') == 'up' else 1

			case 'paddle_move_stop':
				if paddle := self.get_player_paddle():
					paddle.direction = 0

	async def disconnect(self, close_code):
		if self.game_id in self.active_games:
			self.active_games[self.game_id]['running'] = False 
			del self.active_games[self.game_id]


	async def broadcast_game_start(self):
		game = self.active_games[self.game_id]
		state = {
			'event': 'game_start',
			'state': self.get_start_data()
		}
		await game['left']['socket'].send(json.dumps(state))
		await game['right']['socket'].send(json.dumps(state))


	async def broadcast_game_state(self):
		game = self.active_games[self.game_id]
		state = {
			'event': 'game_state',
			'state': {
				'l_paddle_y': self.paddleLeft.y,
				'r_paddle_y': self.paddleRight.y,
				'ball_x': self.ball.x,
				'ball_y': self.ball.y,
			}
		}
		await game['left']['socket'].send(json.dumps(state))
		await game['right']['socket'].send(json.dumps(state))


	async def broadcast_game_score(self, score_data: dict):
		if self.game_id not in self.active_games:
			return 
		game = self.active_games[self.game_id]
		await game['left']['socket'].send(json.dumps(score_data))
		await game['right']['socket'].send(json.dumps(score_data))


	async def broadcast_game_end(self, winner: Player):
		game = self.active_games[self.game_id]
		state = {
			'event': 'game_end',
			'state': {
				'winner': winner.player_id
			}
		}
		await game['left']['socket'].send(json.dumps(state))
		await game['right']['socket'].send(json.dumps(state))


	async def setup_players(self):
		game = self.active_games[self.game_id]
		self.player1 = Player(game['left']['id'], self.paddleLeft)
		self.player2 = Player(game['right']['id'], self.paddleRight)


	async def init_remote_components(self):
		game = self.active_games[self.game_id]
		game['components'] = {
			'paddleLeft': self.paddleLeft,
			'paddleRight': self.paddleRight,
			'ball': self.ball,
			'gamefield': self.gamefield
		}
		remote_player = game['left']['socket']
		remote_player.paddleLeft = self.paddleLeft
		remote_player.paddleRight = self.paddleRight
		remote_player.ball = self.ball
		remote_player.gamefield = self.gamefield


	def get_player_paddle(self):
		game = self.active_games.get(self.game_id)
		if not game:
			return None
		return (self.paddleLeft if self.player_id == game['left']['id'] 
		else self.paddleRight if self.player_id == game['right']['id'] 
		else None)


	async def game_loop(self):
		#await self.init_game_components()
		self.ball.reset(self.scoreBoard, self.player1, self.player2)
		while self.game_id in self.active_games:
			await asyncio.sleep(1 / GAME_SETTINGS['display']['fps'])
			self.paddleLeft.update()
			self.paddleRight.update()
			self.ball.update(self.scoreBoard, self.player1, self.player2)	
			if self.game_id in self.active_games:  # Check again after update
				await self.broadcast_game_state()
				await self.scoreBoard.send()
				if (winner := self.scoreBoard.end_match()):
					await self.broadcast_game_end(winner)
					break
		await self.disconnect(1000)


class QuickLobby(AsyncWebsocketConsumer):
	queued_players = {}

	def get_session_key(self):
		session = self.scope.get("session", {})
		return session.session_key[:6] if session else None

	async def broadcast_player_count(self):
		for player in self.queued_players.values():
			await player.send(json.dumps({
				'event': 'player_count',
				'state': {
					'player_count': len(self.queued_players)
				}
			}))

	async def connect(self):
		await self.accept()
		self.player_id = self.get_session_key()
		self.queued_players[self.player_id] = self
		await self.broadcast_player_count()
		await self.try_match_players()

	async def disconnect(self, close_code):
		if self.player_id in self.queued_players:
			del self.queued_players[self.player_id]
			await self.broadcast_player_count()

	async def receive(self, text_data):
		data = json.loads(text_data)
		if 'action' not in data:
			return
		
	async def try_match_players(self):
		if len(self.queued_players) >= 2:
			players = list(self.queued_players.keys())[:2]
			game_id = f"game_{players[0]}_{players[1]}"
			
			# Send match data before removing from queue
			match_data = {
				'event': 'match_found',
				'state': {
					'game_id': game_id,
					'game_url': f'ws/mpong/game/{game_id}/',
					'player1_id': players[0],
					'player2_id': players[1]
				}
			}
			
			# Send match data and close connections
			player1 = self.queued_players[players[0]]
			player2 = self.queued_players[players[1]]
			
			await player1.send(json.dumps(match_data))
			await player2.send(json.dumps(match_data))
			
			# Remove from queue and close lobby connections
			del self.queued_players[players[0]]
			del self.queued_players[players[1]]
			await player1.close()
			await player2.close()
			
			await self.broadcast_player_count()