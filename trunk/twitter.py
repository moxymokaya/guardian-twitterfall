import base64

from google.appengine.api import urlfetch
from django.utils import simplejson

import models


def get_twitter_credentials():
	username='your_username'
	password='your_password'
	return username, password


def get_from_twitter(url):
	username, password = get_twitter_credentials()
	base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
	headers = {'Authorization': "Basic %s" % base64string} 
	result = urlfetch.fetch(url, method=urlfetch.GET, headers=headers)
	json = simplejson.loads(result.content)
	return json


def get_search(query):
	key = "search_" + query
	since_id = models.get_from_keystore(key)
	if not since_id:
		since_id = "1"
	url = "http://search.twitter.com/search.json?q=" + query + "&rpp=100&since_id=" + since_id
	messages = get_from_twitter(url)
	return messages, url


def handle_searches(messages, searchtag):
	i = 0
	searchtag = "search_" + searchtag
	since_id = models.get_from_keystore(searchtag)
	hasurl = False
	highest_message_id = 0
	for message in messages:
		if i == 0:
			highest_message_id = str(message['id'])
			i = 1
		if int(message['id']) > int(since_id):
			if "http://" in message['text'].lower():
				messageelements = message['text'].split(" ")
				newmessageelements = []
				for messageelement in messageelements:
					if messageelement[0:7].lower() == "http://":
						newmessageelements.append("<a href='"+ messageelement +"' target='_new'>"+ messageelement +"</a>")
					else:
						newmessageelements.append(messageelement)
				markedupmessage = " ".join(newmessageelements)
			else:
				markedupmessage = message['text']
			if "@" in markedupmessage:
				messageelements = markedupmessage.split(" ")
				newmessageelements = []
				for messageelement in messageelements:
					if messageelement[0:1].lower() == "@":
						if len(messageelement) > 1:
							newmessageelements.append("<a href='http://twitter.com/"+ messageelement[1: len(messageelement)] +"' target='_new'>"+ messageelement +"</a>")
					else:
						newmessageelements.append(messageelement)
				markedupmessage = " ".join(newmessageelements)
			if "#" in markedupmessage:
				messageelements = markedupmessage.split(" ")
				newmessageelements = []
				for messageelement in messageelements:
					if messageelement[0:1].lower() == "#":
						if len(messageelement) > 1:
							newmessageelements.append("<span class='hashtag' id='"+ messageelement[1: len(messageelement)] +"'>"+ messageelement +"</span>")
					else:
						newmessageelements.append(messageelement)
				markedupmessage = " ".join(newmessageelements)
			models.cache_message(message['profile_image_url'], "searches", message['id'], message['from_user_id'], message['from_user'], markedupmessage, message['created_at'], message_tag=searchtag)
	if highest_message_id > 0:
		models.add_to_keystore(searchtag, highest_message_id)
	return messages, hasurl


