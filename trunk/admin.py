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

import models
import helpers

class LoginHandler(webapp.RequestHandler):
	def post(self):
		user = models.do_login(self.request.get("email"), self.request.get("password"), self)
		if user:
			self.redirect("/admin/")
		else:
			template_values = {}
			helpers.render_admin_template(self, "adminviews/home.html", template_values)
			

class LogoutHandler(webapp.RequestHandler):
	def get(self):
		models.do_logout(self)
		self.redirect("/admin/")
		

class MainAdminHandler(webapp.RequestHandler):
  def get(self):
	messages = models.get_unmoderated_messages(5)
	messageset = ""
	for message in messages:
		messageset = messageset + "," + str(message.messageid)
	if len(messageset) == 0:
		messageset = False
	else:
		messageset = messageset[1:len(messageset)]
	template_values = {
		'messages' : messages,
		'messageset' : messageset,
	}
	helpers.render_admin_template(self, "adminviews/home.html", template_values)



class ListHandler(webapp.RequestHandler):
  def get(self, status):
	messages = models.get_message_by_status(status)
	template_values = {
		'messages' : messages,
		'status' : status,
	}
	helpers.render_admin_template(self, "adminviews/list.html", template_values)


class ViewBacklogHandler(webapp.RequestHandler):
  def get(self):
	count = models.get_unmoderated_count()
	messages = models.get_unmoderated_messages(500)
	template_values = {
		'messages' : messages,
		'count' : count,
	}
	helpers.render_admin_template(self, "adminviews/backlog.html", template_values)


class ApproveSetHandler(webapp.RequestHandler):
  def post(self):
	messageids = self.request.get("messageset").split(",")
	for messageid in messageids:
		models.update_message_status("approve", messageid)
	self.redirect("/admin/")


class SingleHandler(webapp.RequestHandler):
  def get(self, action, messageid):
	message = models.update_message_status(action, messageid)
	if action == "approve": 
		actiontext = "approved"
	else:
		actiontext = "blocked"
	template_values = {
		'message' : message,
		'actiontext' : actiontext,
	}
	helpers.render_admin_template(self, "adminviews/messageaction.html", template_values)




def main():
	application = webapp.WSGIApplication([
	('/admin/', MainAdminHandler),
	('/admin/login', LoginHandler),
	('/admin/logout', LogoutHandler),
	('/admin/all(block)ed', ListHandler),
	('/admin/all(approve)d', ListHandler),
	('/admin/approveset', ApproveSetHandler),
	('/admin/(approve)single/(.*)', SingleHandler),
	('/admin/(block)single/(.*)', SingleHandler),
	('/admin/backlog', ViewBacklogHandler),
	], debug=True)
	wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
