from .pong_components import Paddle, Ball, Player, AIPlayer, ScoreBoard, GameField, GAME_SETTINGS
import asyncio, logging

logger = logging.getLogger('pong')
class PongGame():
	def __init__(self, mode='vs'):
		self.consumers = []
		self.mode = mode
		self.running : bool = False
		self.paddleLeft : Paddle = None
		self.paddleRight : Paddle = None
		self.player1 : Player = None 
		self.player2 : Player = None
		self.ball : Ball = None
		self.scoreBoard : ScoreBoard = None
		self.gamefield : GameField = None

	def add_consumer(self, consumer):
		self.consumers.append(consumer)

	def remove_consumer(self, consumer):
		if consumer in self.consumers:
			self.consumers.remove(consumer)


	async def init_game_components(self):
		self.paddleLeft = Paddle(GAME_SETTINGS['l_paddle']['start_x'], GAME_SETTINGS['l_paddle']['start_y'])
		self.paddleRight = Paddle(GAME_SETTINGS['r_paddle']['start_x'], GAME_SETTINGS['r_paddle']['start_y'])
		self.ball = Ball()
		self.gamefield = GameField()
		await self.setup_players()
		self.scoreBoard = ScoreBoard(self, self.player1, self.player2)
		
		
	async def setup_players(self): 
		self.player1 = Player(self.consumers[0].get_username(), self.paddleLeft)
		self.player2 = Player(self.consumers[0].get_username() + " (2)", self.paddleRight) if self.mode == 'vs' else AIPlayer('Marvin', self.paddleRight)


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

	async def game_loop(self):
		self.ball.reset(self.scoreBoard, self.player1, self.player2)
		while self.running:
			await asyncio.sleep(1 / GAME_SETTINGS['display']['fps'])

			if hasattr(self, 'self.game_id'):
				if self.missing_players():
					break
				elif self.player_left():
					continue

			self.paddleLeft.update()
			self.paddleRight.update()
			self.ball.update(self.scoreBoard, self.player1, self.player2)
			await self.broadcast_game_state()

			if self.mode == 'ai':
				self.player2.update(self.ball)

			if (winner := self.scoreBoard.end_match()): # this could be done only when a point is scored
				await self.scoreBoard.send()
				await self.broadcast_game_end(winner)
				await asyncio.sleep(0.1)
				break
			
		await self.end_game()


	async def start(self):
		self.running = True
		await self.broadcast_game_start()
		asyncio.create_task(self.game_loop())


	async def end_game(self):
		self.running = False
		for consumer in self.consumers:
			await consumer.close()

	def missing_players(self): # if we garuantee that we only players are always consumer[0] and consumer[1] we can check only for those positions
		consumer_usernames = [c.get_username() for c in self.consumers]
		if (self.player1.player_id not in consumer_usernames and 
			self.player2.player_id not in consumer_usernames):
			return (self.player1.player_id, self.player2.player_id)
		return None
	
	def player_left(self): 
		consumer_usernames = [c.get_username() for c in self.consumers]
		if self.player1.player_id not in consumer_usernames:
			return self.player1.player_id
		if self.player2.player_id not in consumer_usernames:
			return self.player2.player_id
		return None	


	async def broadcast_game_start(self):
		for consumer in self.consumers:
			await consumer.broadcast_game_start(self)

	async def broadcast_game_state(self):
		for consumer in self.consumers:
			await consumer.broadcast_game_state(self)

	async def broadcast_game_end(self, winner: Player):
		for consumer in self.consumers:
			await consumer.broadcast_game_end(winner)

	async def broadcast_game_score(self, score_data: dict):
		for consumer in self.consumers:
			await consumer.broadcast_game_score(score_data)


class MultiPongGame(PongGame):
	def __init__(self, game_id):
		super().__init__('vs') 
		self.game_id = game_id

	async def setup_players(self):
		self.player1 = Player(self.consumers[0].get_username(), self.paddleLeft)
		self.player2 = Player(self.consumers[1].get_username(), self.paddleRight)



