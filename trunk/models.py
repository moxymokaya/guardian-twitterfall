import random
import datetime

from google.appengine.ext import db
from google.appengine.api import memcache

import helpers

class User(db.Model):
	email = db.StringProperty(required=True)
	password = db.StringProperty(required=True)
	live = db.BooleanProperty(default=True)
	last_login = db.DateTimeProperty(auto_now=True)


def get_user_count():
	query = db.Query(User)
	return query.count()


def do_login(email, password, self):
	query = db.Query(User)
	query.filter('email =', email)
	query.filter('password =', password)
	user = query.get()
	if not user:
		user = ""
	else:
		user.put()
		helpers.set_cookie(self, 'ukey', str(user.key()))
	return user


def do_logout(self):
	userkey = helpers.get_user_cookie(self)
	if len(userkey) >0:
		user = db.get(db.Key(userkey))
		if user:
			user.put()
	else:
		user = False
	helpers.destroy_user_cookie(self)	
		
def get_current_user(self):
	userkey = helpers.get_user_cookie(self)
	if len(userkey) >0:
		user = db.get(db.Key(userkey))
		if user:
			user.put()
	else:
		user = False
	return user



class MessageCache(db.Model):
	messageid = db.IntegerProperty(required=True)
	messagetype = db.StringProperty(required=True)
	user = db.IntegerProperty(required=True)
	username = db.StringProperty(required=True)
	lusername = db.StringProperty()
	message = db.TextProperty(required=True)
	imgurl = db.TextProperty(required=True)
	message_date = db.DateTimeProperty(required=True)
	message_tag = db.StringProperty()
	live = db.BooleanProperty(default=False)
	moderated = db.BooleanProperty(default=False)
	cached_at = db.DateTimeProperty(auto_now_add=True)


def cache_message(imgurl, messagetype, messageid, user, username, message, message_date, message_tag):
	key = "id_" + str(messageid)
	increment_counter("alltweets")
	messagecache = MessageCache.get_or_insert(key, imgurl=imgurl, messagetype=messagetype, user=user, username=username, lusername=username.lower(),  message=message, messageid=messageid, message_date=helpers.convert_twitter_datetime(message_date), message_tag=message_tag)


def get_latest_messages(number):
	key = "messageset_" + str(number)
	messages = memcache.get(key)
	if not messages:
		query = db.Query(MessageCache)
		query.filter('live =', True)
		query.filter('moderated =', True)
		query.order('-messageid')
		messages = query.fetch(number)
		memcache.add(key, messages, 10)
	return messages


def get_message_by_status(status):
	if status == "approve":
		live = True
	else:
		live = False
	query = db.Query(MessageCache)
	query.filter('live =', live)
	query.filter('moderated =', True)
	query.order('-messageid')
	messages = query.fetch(1000)
	return messages


def get_unmoderated_count():
	query = db.Query(MessageCache)
	query.filter('moderated =', False)
	query.order('messageid')
	count = query.count()
	return count


def get_unmoderated_messages(number):
	query = db.Query(MessageCache)
	query.filter('moderated =', False)
	query.order('messageid')
	messages = query.fetch(number)
	return messages


def update_message_status(action, messageid):
	if action == "approve":
		live = True
	else:
		live = False
	query = db.Query(MessageCache)
	query.filter('messageid =', int(messageid))
	message = query.get()
	message.live = live
	message.moderated = True
	message.put()
	if action == "approve":
		increment_counter("livetweets")
	else:
		decrement_counter("livetweets")
	return message
	
		

class KeyStore(db.Model):
	name = db.StringProperty(required=True)
	value = db.StringProperty()


def add_to_keystore(name, value):
	keystore = KeyStore.get_or_insert(name, name=name)
	keystore.value = value
	keystore.put()



def get_from_keystore(name):
	keystore = KeyStore.get_by_key_name(name)
	if keystore:
		return keystore.value
	else:
		return False


# elements for sharded counter
	
class CounterConfig(db.Model):
	name = db.StringProperty(required=True)
	num_shards = db.IntegerProperty(required=True, default=1)

class Counter(db.Model):
	name = db.StringProperty(required=True)
	count = db.IntegerProperty(required=True, default=0)


def get_next_id(name):
	increment_counter(name)
	return get_counter(name)


def get_counter(name):
	total = 0
	for counter in Counter.gql('WHERE name = :1', name):
		total += counter.count
	return total


def increment_counter(name):
	config = CounterConfig.get_or_insert(name, name=name)
	def txn():
		index = random.randint(0, config.num_shards - 1)
		shard_name = name + str(index)
		counter = Counter.get_by_key_name(shard_name)
		if counter is None:
			counter = Counter(key_name=shard_name, name=name)
		counter.count += 1
		counter.put()
	db.run_in_transaction(txn)



def decrement_counter(name):
	config = CounterConfig.get_or_insert(name, name=name)
	def txn():
		index = random.randint(0, config.num_shards - 1)
		shard_name = name + str(index)
		counter = Counter.get_by_key_name(shard_name)
		if counter is None:
			counter = Counter(key_name=shard_name, name=name)
		counter.count -= 1
		counter.put()
	db.run_in_transaction(txn)
	