from django.contrib.auth.models import AbstractUser
from django.db.models import JSONField
from django.db import models
from django.conf import settings
# from settings import MEDIA_URL
import uuid as uuid_lib

class User(AbstractUser):  # Inherits all these fields:
	# Username
	# First name
	# Last name
	# Email
	# Password
	# Groups
	# User permissions
	# Is staff
	# Is active
	# Is superuser
	# Last login
	# Date joined
	is_42_user = models.BooleanField(default=False)
	profile_pic = models.CharField(default=f'https://{settings.WEB_HOST}{settings.MEDIA_URL}profile-pics/pfp-1.png' ,max_length=255)
	id_42 = models.IntegerField(default=0)
	uuid = models.UUIDField(default=uuid_lib.uuid4, editable=True, null=True)
	rank = models.IntegerField(default=0)
	status = models.BooleanField(default=False)
	two_factor_enable = models.BooleanField(default=False)
	two_factor_secret = models.CharField(max_length=255, blank=True, null=True)
	
	@property
	def friends(self):
		"""Get all accepted friends"""
		sender_friends = FriendshipRequest.objects.filter(
			sender=self,
			status='accepted'
		).values_list('receiver__uuid', flat=True)
		
		receiver_friends = FriendshipRequest.objects.filter(
			receiver=self,
			status='accepted'
		).values_list('sender__uuid', flat=True)
		
		friend_uuids = list(sender_friends) + list(receiver_friends)
		
		return User.objects.filter(uuid__in=friend_uuids)

	@property
	def pending_sent_requests(self):
		"""Get all pending requests sent by the user"""
		return FriendshipRequest.objects.filter(
			sender=self,
			status='pending'
		)

	@property
	def pending_received_requests(self):
		"""Get all pending requests received by the user"""
		return FriendshipRequest.objects.filter(
			receiver=self,
			status='pending'
		)

	def send_friend_request(self, receiver_uuid):
		try:
			receiver = User.objects.get(uuid=receiver_uuid)
			if receiver == self:
				return False, "Cannot send friend request to yourself"
				
			existing_request = FriendshipRequest.objects.filter(
				(models.Q(sender=self, receiver=receiver) | 
				models.Q(sender=receiver, receiver=self))
			).first()
			
			if existing_request:
				if existing_request.status == 'accepted':
					return False, "Already friends"
				elif existing_request.status == 'pending' and existing_request.sender == self:
					return False, "Friend request already sent"
				elif existing_request.status == 'pending' and existing_request.receiver == self:
					existing_request.status = 'accepted'
					existing_request.save()
					return True, "Friend request accepted"
				elif existing_request.status == 'rejected':
					existing_request.delete()
			
			FriendshipRequest.objects.create(sender=self, receiver=receiver)
			return True, "Friend request sent"
		except User.DoesNotExist:
			return False, "User not found"

	def cancel_friend_request(self, receiver_uuid):
		"""Cancel a sent friend request"""
		try:
			receiver = User.objects.get(uuid=receiver_uuid)
			request = FriendshipRequest.objects.filter(
				sender=self, 
				receiver=receiver,
				status='pending'
			).first()
			
			if request:
				request.delete()
				return True, "Friend request canceled"
			return False, "No pending request found"
		except User.DoesNotExist:
			return False, "User not found"

	def accept_friend_request(self, sender_uuid):
		"""Accept a received friend request"""
		try:
			sender = User.objects.get(uuid=sender_uuid)
			request = FriendshipRequest.objects.filter(
				sender=sender,
				receiver=self,
				status='pending'
			).first()
			
			if request:
				request.status = 'accepted'
				request.save()
				return True, "Friend request accepted"
			return False, "No pending request found"
		except User.DoesNotExist:
			return False, "User not found"
			
	def reject_friend_request(self, sender_uuid):
		"""Reject a received friend request"""
		try:
			sender = User.objects.get(uuid=sender_uuid)
			request = FriendshipRequest.objects.filter(
				sender=sender,
				receiver=self,
				status='pending'
			).first()
			
			if request:
				request.status = 'rejected'
				request.save()
				return True, "Friend request rejected"
			return False, "No pending request found"
		except User.DoesNotExist:
			return False, "User not found"

	def remove_friend(self, friend_uuid):
		"""Remove an existing friendship"""
		try:
			friend = User.objects.get(uuid=friend_uuid)
			request = FriendshipRequest.objects.filter(
				(models.Q(sender=self, receiver=friend) | 
				models.Q(sender=friend, receiver=self)),
				status='accepted'
			).first()
			
			if request:
				request.delete()
				return True, "Friend removed"
			return False, "Not friends with this user"
		except User.DoesNotExist:
			return False, "User not found"


class FriendshipRequest(models.Model):
	STATUS_CHOICES = [
		('pending', 'Pending'),
		('accepted', 'Accepted'),
		('rejected', 'Rejected')
	]
	
	sender = models.ForeignKey(
		'User', 
		on_delete=models.CASCADE,
		related_name='sent_requests'
	)
	receiver = models.ForeignKey(
		'User', 
		on_delete=models.CASCADE,
		related_name='received_requests'
	)
	status = models.CharField(
		max_length=10,
		choices=STATUS_CHOICES,
		default='pending'
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
		unique_together = ['sender', 'receiver']
		
	def __str__(self):
		return f"{self.sender.username} → {self.receiver.username}: {self.get_status_display()}"


class Ladderboard(models.Model):
	user = models.OneToOneField(
		'User',
		on_delete=models.CASCADE,
		related_name='rank_entry'
	)
	rank_value = models.IntegerField(default=0)
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
		indexes = [
			models.Index(fields=['-rank_value']), 
		]
		ordering = ['-rank_value']
	
	def __str__(self):
		return f"{self.user.username}: {self.rank_value} points"
	
	@classmethod
	def get_leaderboard(cls, start=0, count=10):
		return cls.objects.select_related('user').all()[start:start+count]
    
	@classmethod
	def initialize_all(cls):
		users = User.objects.all()
		for user in users:
			cls.objects.get_or_create(
				user=user,
				defaults={'rank_value': user.rank}
			)

