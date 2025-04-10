from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver, Signal
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from .models import FriendshipRequest, User, Ladderboard
from .consumers import LoginMenuConsumer
import logging

logger = logging.getLogger('pong')

@receiver(post_delete, sender=FriendshipRequest)
@receiver(post_save, sender=FriendshipRequest)
def friendship_updated(sender, instance, **kwargs):
	if instance:
		receiver = instance.receiver
		receiver_id = receiver.id
	
		for consumer in LoginMenuConsumer.instances:
			if consumer.user.id == receiver_id:
				async_to_sync(consumer.broadcast_notification)()
				break

		for consumer in LoginMenuConsumer.instances:
			if consumer.user.id == instance.sender.id:
				async_to_sync(consumer.broadcast_notification)()
				break


profile_updated_signal = Signal()

@receiver(profile_updated_signal)
async def profile_updated(sender, **kwargs):
	user : User = kwargs.get('user')
	for consumer in LoginMenuConsumer.instances:
		if consumer.user == user:
			await consumer.broadcast_notification()
			break


tournament_started_signal = Signal()
tournament_updated_signal = Signal()

@receiver(tournament_started_signal)
@receiver(tournament_updated_signal)
async def tournament_updated(sender, instance, **kwargs):
	if instance: 
		users = [await database_sync_to_async(User.objects.get)(username=username) for username in instance.players]
		for user in users:
			for consumer in LoginMenuConsumer.instances:
				if consumer.user == user:
					await consumer.broadcast({'event': 'tournament',})
					break


@receiver(post_save, sender=User)
def update_ladderboard(sender, instance, created, **kwargs):
	logger.debug(f"User {instance.username} saved with rank {instance.rank}")
	ladderboard_entry, created = Ladderboard.objects.get_or_create(
		user=instance,
		defaults={'rank_value': instance.rank}
	)
	
	if not created and ladderboard_entry.rank_value != instance.rank:
		ladderboard_entry.rank_value = instance.rank
		ladderboard_entry.save()