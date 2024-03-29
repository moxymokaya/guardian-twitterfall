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


class MainHandler(webapp.RequestHandler):
  def get(self):
	template_values = {
	}
	helpers.render_uncacheable_template(self, "webviews/home.html", template_values)


class MessageListHandler(webapp.RequestHandler):
  def get(self):
	template_values = {
		'messages' : models.get_latest_messages(20),
	}
	helpers.render_uncacheable_template(self, "webviews/messagelist.html", template_values)


def main():
  application = webapp.WSGIApplication([
	('/', MainHandler),
	('/messages', MessageListHandler),
	], debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
