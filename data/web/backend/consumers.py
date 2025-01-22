from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging

class PongGameConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.paddle_y = 250
		await self.accept()


	async def disconnect(self, close_code):
		pass

	async def receive(self, text_data):
		data = json.loads(text_data)
		# if data['action'] == 'heartbeat':
		# 	await self.send(json.dumps({
		# 		'event': 'heartbeat'
		# 	}))
		if data['action'] == 'move_paddle':
			self.paddle_y = data['paddle_y']
			await self.send(json.dumps({
				'event': 'game_state',
				'state': {
					'paddle_y': self.paddle_y
				}
			}))
