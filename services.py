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

import helpers
import twitter
import models



class SearchHandler(webapp.RequestHandler):
	def get(self, term):
		searches = None
		searchthis = False
		returns = False
		if term == "activate09":
			term = "activate09"
			searchthis = True
		if searchthis:
			results, url = twitter.get_search(term)
			searches = results['results']
			messages, hasurl = twitter.handle_searches(searches, term)
		template_values = {
			'returns': searches,
			'returntype': "searches",
			'url': url,
			'hasurl': hasurl,
		}
		helpers.render_uncacheable_template(self, "webviews/data.html", template_values)


class InitialiseAdminHandler(webapp.RequestHandler):
	def get(self):
		users = models.get_user_count()
		if users > 0:
			template_values = {
				'users': True,
			}
		else:
			template_values = {
				'users': False,
			}
		helpers.render_uncacheable_template(self, "adminviews/createfirstuser.html", template_values)
	def post(self):
		email = self.request.get("email")
		password = self.request.get("password")
		if len(email) == 0 or len(password) == 0:
			template_values = {
				'users': False,
			}
		else:
			user = models.User.get_or_insert(email, email=email, password=password)
			user.put()
			template_values = {
				'user': user,
				}
		helpers.render_uncacheable_template(self, "adminviews/createfirstuser.html", template_values)



def main():
	application = webapp.WSGIApplication([
		('/services/search/(.*)', SearchHandler),
		('/services/initialiseadmin', InitialiseAdminHandler),
		],debug=True)
	wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()	
