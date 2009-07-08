import datetime
import os

from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from google.appengine.api import users

import models

def render_cacheable_template(self, end_point, template_values, key, cachelength):
	cachedresponse = memcache.get(key)
	if not cachedresponse:
		cachedresponse = render_template(self, end_point, template_values)
		memcache.add(key, cachedresponse, cachelength)
	render_response(self, cachedresponse)

		
def render_uncacheable_template(self, end_point, template_values):
	render_response(self, render_template(self, end_point, template_values))


def render_admin_template(self, end_point, template_values):
	user = models.get_current_user(self)
	template_values['user'] = user
	if not user:
		template_values['title'] = "log in now please"
		render_response(self, render_template(self, "adminviews/notpermitted.html", template_values))
	else:
		render_response(self, render_template(self, end_point, template_values))


def render_response(self, thisresponse):
	self.response.out.write(thisresponse)


def render_template(self, end_point, template_values):
	path = os.path.join(os.path.dirname(__file__), "templates/" + end_point)
	thisresponse = template.render(path, template_values)
	return thisresponse


def set_cookie(self, name, value):
	self.response.headers.add_header(
		'Set-Cookie', 
		'%s=%s; path=/; expires=Fri, 31-Dec-2020 23:59:59 GMT' % (name.encode(),  value.encode()))


def destroy_cookie(self, name, username):
	self.response.headers.add_header(
		'Set-Cookie', 
		'%s=%s; path=/; expires=-1' % (name.encode(),  username.encode()))


def get_cookie(self, name):
	cookievalue = self.request.cookies.get(name, '')
	return cookievalue


def get_user_cookie(self):
	return get_cookie(self, "ukey")


def destroy_user_cookie(self):
	destroy_cookie(self, "ukey", "")


def monthname_to_month(monthname):
	if monthname == "Jan":
		month = 1
	if monthname == "Feb":
		month = 2
	if monthname == "Mar":
		month = 3
	if monthname == "Apr":
		month = 4
	if monthname == "May":
		month = 5
	if monthname == "Jun":
		month = 6
	if monthname == "Jul":
		month = 7
	if monthname == "Aug":
		month = 8
	if monthname == "Sep":
		month = 9
	if monthname == "Oct":
		month = 10
	if monthname == "Nov":
		month = 11
	if monthname == "Dec":
		month = 12
	return month

def convert_twitter_datetime(theirdatetime):
	thisdatetime = datetime.datetime(int(theirdatetime[12: 16]), monthname_to_month(theirdatetime[8: 11]), int(theirdatetime[5: 7]), int(theirdatetime[17: 19]), int(theirdatetime[20: 22]), int(theirdatetime[23: 25]))
	return thisdatetime
