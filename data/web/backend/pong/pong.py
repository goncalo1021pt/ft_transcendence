from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
import random

# import logging
# import os

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# LOG_FILE = os.path.join(BASE_DIR, 'pong_debug.log')

# logging.basicConfig(
#     filename=LOG_FILE,
#     level=logging.DEBUG,
#     format='%(asctime)s - %(message)s'
# )

GAME_SETTINGS = {
	'field': {
		'width': 1024,
		'height': 768,
	},
	'paddle': {
		'width': 15,
		'height': 100,
		'velo': 22.2 # 1000px / 45fps
	},
	'l_paddle': {
		'start_y': 334, #field height / 2 - paddle height / 2
		'start_x': 40,
	},
	'r_paddle': {
		'start_y': 334, #field height / 2 - paddle height / 2
		'start_x': 969, #field width - 40 - paddle width
	},
	'ball': {
		'size': 15,
		'start_x': 512,
		'start_y': 384,
		'velo_x': 5, # actually direction vector not speed
		'velo_y': 3
	},
	'match': {
		'win_points': 2, # 5 points to win a set
		'win_sets': 2 # 2 sets to win a match
	},
	'display': {
		'fps': 60 # packet update rate
	},
}

class Player:
	def __init__(self, session_key, paddle):
		self.player_id = session_key
		self.paddle = paddle
		self.score = 0
		self.sets = 0

	def score_point(self):
		self.score += 1
		
	def win_set(self):
		self.sets += 1
		
class GameField:
	def __init__(self):
		self.width = GAME_SETTINGS['field']['width']
		self.height = GAME_SETTINGS['field']['height']

class ScoreBoard:
	def __init__(self, instance, left_player: Player, right_player: Player):
		self.instance = instance
		self.left_player = left_player
		self.right_player = right_player
		self.last_scored = None

	def update(self, last_scored: Player = None):
		self.last_scored = last_scored
		if last_scored:
			asyncio.create_task(self.send())

	def new_set(self, winner : Player):
		winner.win_set()
		#if self.end_match() is None:
		self.left_player.score = self.right_player.score = 0


	def end_match(self):
		if self.left_player.sets >= GAME_SETTINGS['match']['win_sets']:
			return self.left_player
		elif self.right_player.sets >= GAME_SETTINGS['match']['win_sets']:
			return self.right_player
		return None

	async def send(self):
		await self.instance.send(json.dumps({
			'event': 'score_update',
			'state': {
				'player1_score': self.left_player.score,
				'player2_score': self.right_player.score,
				'player1_sets': self.left_player.sets,
				'player2_sets': self.right_player.sets,
			}
		}))
class Paddle:
	def __init__(self, x=0, y=0):
		self.x = self.start_x = x
		self.y = self.start_y = y
		self.width = GAME_SETTINGS['paddle']['width']
		self.height = GAME_SETTINGS['paddle']['height']
		self.velo = GAME_SETTINGS['paddle']['velo']

	def reset(self):
		self.x = self.start_x
		self.y = self.start_y
	
	def move(self, y):
		self.y = max(0, min(GAME_SETTINGS['field']['height'] - GAME_SETTINGS['paddle']['height'], y))

class Ball:
	def __init__(self):
		self.x = GAME_SETTINGS['ball']['start_x']
		self.y = GAME_SETTINGS['ball']['start_y']
		self.size = GAME_SETTINGS['ball']['size']
		self.dx = GAME_SETTINGS['ball']['velo_x']
		self.dy = GAME_SETTINGS['ball']['velo_y']
		self.wait_time = None
		self.is_waiting = False
	
	async def countdown(self, duration):
		await asyncio.sleep(duration)
		self.is_waiting = False

	def coin_toss(self):
		self.dx = GAME_SETTINGS['ball']['velo_x'] * (1 if random.random() > 0.5 else -1)
		self.dy = GAME_SETTINGS['ball']['velo_y'] * (1 if random.random() > 0.5 else -1)

	def reset(self, scoreBoard : ScoreBoard, leftPlayer : Player, rightPlayer : Player):
		self.x = GAME_SETTINGS['ball']['start_x']
		self.y = GAME_SETTINGS['ball']['start_y']
		if scoreBoard.last_scored is None:
			self.coin_toss()
		elif scoreBoard.last_scored: # Set direction towards scoring player, maybe swap ?
			self.dx = abs(self.dx) if scoreBoard.last_scored == rightPlayer else -abs(self.dx)
			self.dy = GAME_SETTINGS['ball']['velo_y'] * (1 if random.random() > 0.5 else -1)
			
		self.is_waiting = True
		leftPlayer.paddle.reset()
		rightPlayer.paddle.reset()
		asyncio.create_task(self.countdown(3))

	def update(self, scoreBoard: ScoreBoard, leftPlayer: Player, rightPlayer: Player):
		if self.is_waiting:
			return
			
		# Position update
		self.x += self.dx
		self.y += self.dy

		# Collision with top and bottom walls
		if self.y <= 0 or self.y >= GAME_SETTINGS['field']['height'] - self.size:
			self.dy *= -1

		# Collision with left paddle
		if (self.x <= leftPlayer.paddle.x + leftPlayer.paddle.width and
			self.x + self.size >= leftPlayer.paddle.x and
			self.y + self.size >= leftPlayer.paddle.y and
			self.y <= leftPlayer.paddle.y + leftPlayer.paddle.height):
			self.dx *= -1
			self.x = leftPlayer.paddle.x + leftPlayer.paddle.width

		# Collision with right paddle
		if (self.x + self.size >= rightPlayer.paddle.x and
			self.y + self.size >= rightPlayer.paddle.y and
			self.y <= rightPlayer.paddle.y + rightPlayer.paddle.height):
			self.dx *= -1
			self.x = rightPlayer.paddle.x - self.size

		# Scoring and reset conditions
		if self.x <= 0:  
			rightPlayer.score_point()
			if rightPlayer.score >= GAME_SETTINGS['match']['win_points']:
				scoreBoard.update(rightPlayer)
				scoreBoard.new_set(rightPlayer)
			else:
				scoreBoard.update(rightPlayer)
			self.reset(scoreBoard, leftPlayer, rightPlayer)
		elif self.x >= GAME_SETTINGS['field']['width']: 
			leftPlayer.score_point()
			if leftPlayer.score >= GAME_SETTINGS['match']['win_points']:
				scoreBoard.update(leftPlayer)
				scoreBoard.new_set(leftPlayer)
			else:
				scoreBoard.update(leftPlayer)
			self.reset(scoreBoard, leftPlayer, rightPlayer)
		scoreBoard.update()
		
class PongGameConsumer(AsyncWebsocketConsumer):

	def get_session_key(self):
		session = self.scope.get("session", {})
		return session.session_key[:6] if session else None

	async def connect(self):
		await self.accept()
		self.paddleLeft = Paddle(GAME_SETTINGS['l_paddle']['start_x'], GAME_SETTINGS['l_paddle']['start_y'])
		self.paddleRight = Paddle(GAME_SETTINGS['r_paddle']['start_x'], GAME_SETTINGS['r_paddle']['start_y'])
		self.player1 = Player(self.get_session_key(), self.paddleLeft)
		self.player2 = Player("Marvin", self.paddleRight)
		self.scoreBoard = ScoreBoard(self, self.player1, self.player2)
		self.gamefield = GameField()
		self.ball = Ball()
		self.running = True
		#asyncio.create_task(self.game_loop())

	async def game_loop(self):
		# send first message with static components
		await self.send(json.dumps({
			'event': 'game_start',
			'state': {
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
				'paddle_velo': GAME_SETTINGS['paddle']['velo'],
				'ball_size': self.ball.size,
			}
		}))

		self.ball.reset(self.scoreBoard, self.player1, self.player2)

		while self.running: # send data for dynamic components only
			await asyncio.sleep(1 / GAME_SETTINGS['display']['fps'])
			self.ball.update(self.scoreBoard, self.player1, self.player2)
			await self.send(json.dumps({
				'event': 'game_state',
				'state': {
					# 'player1_score': self.player1.score,
					# 'player2_score': self.player2.score,
					# 'player1_sets': self.player1.sets,
					# 'player2_sets': self.player2.sets,
					'l_paddle_y': self.paddleLeft.y,
					'r_paddle_y': self.paddleRight.y,
					'ball_x': self.ball.x,
					'ball_y': self.ball.y,
				}
			}))

			if (winner := self.scoreBoard.end_match()):
				await self.scoreBoard.send()
				await self.send(json.dumps({
					'event': 'game_end',
					'state': {
						'winner': winner.player_id
					}
				}))
				break

		await self.disconnect(1000)
	


	async def disconnect(self, close_code):
		self.running = False

	async def receive(self, text_data):
		data = json.loads(text_data)

		if 'action' not in data:
			return

		match data['action']: # in a mp game side should be tracked with the user id or session key (uuid while we dont have users)
			case 'connect':
				asyncio.create_task(self.game_loop())
			case 'move_paddle_up':
				paddle = self.paddleLeft if data.get('side') == 'left' else self.paddleRight
				paddle.move(paddle.y - 10)
			case 'move_paddle_down':
				paddle = self.paddleLeft if data.get('side') == 'left' else self.paddleRight
				paddle.move(paddle.y + 10)



