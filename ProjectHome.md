A simple application to allow you to create a curated/moderated updating twitter display at conferences or wherever you choose. The application is designed for pre-moderation only.

There are 4 parts to the app.

## 1. Front end ##

The display of the tweets which refresh over AJAX at 10 second intervals. The data for this view is cached in memcache for 10 seconds to harden the service a tiny bit if it's needed to exist on several screens. Maximum delay between a tweet being approved and being onscreen is just under 20 seconds.

## 2. Services ##

There is one main service which collects the latest 150 tweets for a search term. This service is hit once a minute via a cron job. It's unlikely unless you're doing something against a very fast moving hashtag that you'll go over 150 tweets per minute.

## 3. Admin ##

There is a very simple admin interface.

/admin/ - gives you the 5 earliest unmoderated tweets to moderate (it's a FIFO queue), approving/blocking them marks them as moderated and hitting the next five button will produce the next 5 in the queue

/admin/allblocked - gives you all blocked messages reverse chronologically and allows you to approve messages
/admin/allapproved - does the converse

/admin/backlog - is for experienced moderators only and allows you to pick off the backlog of messages

## 4. APIs ##

There is also a JSON GET API to the data... it's methods are described at /api/

This is very experimental and has not yet been used, but is provided so people can perform some secondary analysis and reuse the data.


# Dependencies #

The code is a complete Google App Engine instance, you will need an AppEngine account and the SDK.

# How to use #

There are a few parameters you will need to change to make it work for your needs.

**twitter.py**

You'll need to add your username and password

```
	username='your_username'
	password='your_password'
```

**app.yaml**

You'll need to change the application name to one suitable for your purpose

```
application: guardian-twitterfall
```

**cron.yaml**

You'll need to change the URL for the search service to your search.

```
cron:
- description: activate search
  url: /services/search/activate09
  schedule: every 1 minutes
```

**services.py**

Within the **SearchHandler** you'll need to change the term. This basically is the trailing element of the URL and is there to protect from anyone from adding a spurious term to your indexing.

```
		if term == "activate09":
			searchthis = True
```

Obviously you'll need to change the styles and templates to suit your event, we've left the Activate ones in so you can see the output. Let us know what yours looks like, we've created a Flickr Pool (http://www.flickr.com/groups/1141284@N20/)

On first deploy you'll need to create a user. You do this by hitting the /services/initialiseadmin service and entering an e-mail address and password. Passwords are stored in the clear in the datastore.

# Caveats #

This was built pretty quickly to solve a need so the code isn't the cleanest and best. There are some duplications of template elements for instance which we'll try to tidy away and someone way better at CSS will probably want to have at the stylesheets and same for the Javascript and probably the Python too. It's provided as is and we cannot make any warranty for loss of data or the application not working.

