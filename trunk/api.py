#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#




import wsgiref.handlers


from google.appengine.ext import webapp
from django.utils import simplejson
from google.appengine.ext import db

import models
import helpers


def get_json(messages):
	messageset = []
	for message in messages:
		messageset.append({
		'id': message.messageid,
		'message': message.message,
		'username': message.username,
		'user_id': message.user,
		'user_imageurl': message.imgurl,
		'datetime': str(message.message_date),
		'live': message.live,
		'moderated': message.moderated,
		})
	return simplejson.dumps(messageset)


class AllHandler(webapp.RequestHandler):
  def get(self):
	self.response.out.write(get_json(models.MessageCache.all().order('-messageid')))


class UserHandler(webapp.RequestHandler):
  def get(self, username):
	query = db.Query(models.MessageCache)
	query.filter('lusername =', username)
	query.order('-messageid')
	messages = query.fetch(1000)
	self.response.out.write(get_json(messages))


class UserIDHandler(webapp.RequestHandler):
  def get(self, userid):
	query = db.Query(models.MessageCache)
	query.filter('user =', int(userid))
	query.order('-messageid')
	messages = query.fetch(1000)
	self.response.out.write(get_json(messages))


class APIHandler(webapp.RequestHandler):
  def get(self, requested):
	query = db.Query(models.MessageCache)
	if requested == "approved":
		query.filter('live =', True)
		query.filter('moderated =', True)
	if requested == "blocked":
		query.filter('live =', False)
		query.filter('moderated =', True)
	if requested == "moderated":
		query.filter('moderated =', True)
	if requested == "unmoderated":
		query.filter('moderated =', False)
	query.order('-messageid')
	messages = query.fetch(1000)
	self.response.out.write(get_json(messages))



def main():
  application = webapp.WSGIApplication([
	('/api', APIDocHandler),
	('/api/', APIDocHandler),
	('/api/all', AllHandler),
	('/api/user/(.*)', UserHandler),
	('/api/userid/(.*)', UserIDHandler),
	('/api/status/(approved)', APIHandler),
	('/api/status/(blocked)', APIHandler),
	('/api/status/(moderated)', APIHandler),
	('/api/status/(unmoderated)', APIHandler),
	], debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
