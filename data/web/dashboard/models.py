from django.db import models
from django.db.models import Q, Count
from backend.models import User, FriendshipRequest
from pong.models import CompletedGame
from tournaments.models import Tournament

import logging

logger = logging.getLogger('pong')

def get_user(username):
	try:
		user = User.objects.get(username=username)
		return user
	except User.DoesNotExist:
		return None

# redundant function, can call user.profile_pic directly
def user_picture(user): 
	if not user:
		return None
	return user.profile_pic

# redundant function, can call user.rank directly
def user_rank(user):
	return user.rank if user else 0

def user_status(user):
	if not user:
		return "offline"
	return "online" if user.status else "offline"

def user_about(user):
	if not user:
		return {"first_joined": "", "last_seen": ""}

	return {
		"uuid": str(user.uuid),
		"first_joined": user.date_joined.strftime("%Y-%m-%d %H:%M:%S") if user.date_joined else "",
		"last_seen": user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else ""
	}


def user_stats(username):
	if not username:
		return {"total": 0, "total_w": 0, "total_l": 0}

	user = get_user(username)
	if not user:
		return {"total": 0, "total_w": 0, "total_l": 0}
	
	uuid_str = str(user.uuid)
	completed_games = CompletedGame.objects.filter(player_ids__has_key=uuid_str)
	total_games = completed_games.count()
	wins = CompletedGame.objects.filter(winner_id=uuid_str).count()

	return {
		"total": total_games,
		"total_w": wins,
		"total_l": total_games - wins
	}


def user_matches(username, limit=5):
	if not username:
		return {"p1_games": [], "p2_games": []}

	user = get_user(username)
	if not user:
		return {"p1_games": [], "p2_games": []}
		
	uuid_str = str(user.uuid)
	user_games = CompletedGame.objects.filter(
		player_ids__has_key=uuid_str
	).order_by('-completed_at')[:limit*2]  

	player1_history = []
	player2_history = []
	
	for game in user_games:
		is_player1 = False
		opponent_uuid = None
		
		for game_uuid, game_username in game.player_ids.items():
			if game_uuid == uuid_str:
				if game.player1_username == game_username:
					is_player1 = True
				continue
			opponent_uuid = game_uuid
		opponent_username = User.objects.get(uuid=opponent_uuid).username
		
		is_winner = game.winner_id == uuid_str
		
		game_info = {
			"game_id": game.game_id,
			"opponent": opponent_username,
			"opponent_pic": user_picture(get_user(opponent_username)),
			"result": "win" if is_winner else "loss",
			"date": game.completed_at.strftime("%Y-%m-%d %H:%M:%S")
		}
		
		if is_player1:
			game_info["score"] = f"{game.player1_sets}-{game.player2_sets}"
			player1_history.append(game_info)
		else:
			game_info["score"] = f"{game.player2_sets}-{game.player1_sets}"
			player2_history.append(game_info)

	player1_history = sorted(player1_history, key=lambda x: x["date"], reverse=True)[:limit]
	player2_history = sorted(player2_history, key=lambda x: x["date"], reverse=True)[:limit]

	return {
		"p1_games": player1_history,
		"p2_games": player2_history
	}


def format_matches(matches_data):
    all_games = []

    for game in matches_data['p1_games']:
        game_cp = game.copy() 
        game_cp['position'] = 'p1'
        all_games.append(game_cp)
    
    for game in matches_data['p2_games']:
        game_cp = game.copy() 
        game_cp['position'] = 'p2'
        all_games.append(game_cp)
    
    from datetime import datetime
    def parse_date(date_str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M')
        except (ValueError, TypeError):
            try:
                return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                return datetime.min

    sorted_games = sorted(all_games, key=lambda x: parse_date(x['date']), reverse=True)
    return sorted_games


def user_friends(user: User):
	if not user:
		return {"list": []}
	
	friends_queryset = user.friends
	
	friends_list = []
	for friend in friends_queryset:
		friends_list.append({
			"uuid": str(friend.uuid),
			"profile_pic": user_picture(friend),
			"username": friend.username,
			"rank": user_rank(friend),
			"status": user_status(friend)
		})
	
	return {
		"list": friends_list,
		"count": len(friends_list)
	}

def user_pending_received(user: User):
	if not user:
		return {"list": []}
	
	pending_requests = user.pending_received_requests
	
	requests_list = []
	for request in pending_requests:
		sender = request.sender
		requests_list.append({
			"request_id": request.id,
			"uuid": str(sender.uuid),
			"username": sender.username,
			"profile_pic": user_picture(sender),
			"rank": user_rank(sender),
			"status": user_status(sender),
			"created_at": request.created_at.strftime("%Y-%m-%d %H:%M:%S")
		})
	
	return {
		"list": requests_list,
	}

def user_pending_sent(user: User):
	if not user:
		return {"list": []}
	
	pending_requests = user.pending_sent_requests
	
	requests_list = []
	for request in pending_requests:
		receiver = request.receiver
		requests_list.append({
			"request_id": request.id,
			"uuid": str(receiver.uuid),
			"username": receiver.username,
			"profile_pic": user_picture(receiver),
			"rank": user_rank(receiver),
			"status": user_status(receiver),
			"created_at": request.created_at.strftime("%Y-%m-%d %H:%M:%S")
		})
	
	return {
		"list": requests_list,
	}

def friendship_status(user : User, target_user : User):

	if not user or not target_user or user is target_user:
		return 'none'
	
	friend_request = FriendshipRequest.objects.filter(
		(Q(sender=user, receiver=target_user) | 
		Q(sender=target_user, receiver=user)),
		status='accepted'
	).first()
	if friend_request:
		return 'friends'
	
	sent_request = FriendshipRequest.objects.filter(
		sender=user,
		receiver=target_user,
		status='pending'
	).exists()
	if sent_request:
		return 'pending_sent'

	received_request = FriendshipRequest.objects.filter(
		sender=target_user,
		receiver=user,
		status='pending'
	).exists()
	if received_request:
		return 'pending_received'

	return 'none'
