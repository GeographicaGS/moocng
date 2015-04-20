from django.db import models
from django.core.urlresolvers import reverse
from django.utils.html import urlize, escape

import pymongo
import re
from dateutil import tz
from datetime import date, datetime

from moocng.mongodb import get_db
from bson.objectid import ObjectId

class CommunityShareBase(object):
	def __init__(self, prefix='share'):
		self.col_prefix=prefix
		self.col_post = '%s_post' % self.col_prefix

	def get_posts(self, case, id, user, page):
	    postCollection = get_db().get_collection(self.col_post)
	    idsUsers=[{"id_user": id}]
	    if(case == 0 and user):
	        for following in user["following"]:
	                idsUsers.append({"id_user": following})
	        
	    posts = postCollection.find({"$and": [{"$or": idsUsers, }, {"$or": [ {"is_child": {"$exists": False} }, {"is_child": False} ] } ] })[page:page+10].sort("date",pymongo.DESCENDING)
	    posts_list = []
	    for post in posts:
	        if len(post['children']) > 0:
	            self._proccess_post_children(post)
	        posts_list.append(post)

	    return self._processPostList(posts_list)

	def search_posts(self, query, page):
	    postCollection = get_db().get_collection(self.col_post)
	    mongoQuery = {'$regex': '.*%s.*' % (query)}

	    posts = postCollection.find({'text': mongoQuery})[page:page+10].sort("date",pymongo.DESCENDING)

	    return self._processPostList(posts)

	def insert_post(self, post):
		return get_db().get_collection(self.col_post).insert(post)

	def count_posts(self, id):
	    return get_db().get_collection(self.col_post).find({'id_user': id}).count()

	def _hashtag_to_link(self, matchobj):
	    hashtag = matchobj.group(0)
	    hashtagUrl = reverse('profile_posts_hashtag', args=[hashtag[1:]])
	    return '<a href="%s">%s</a>' % (hashtagUrl, hashtag)

	def _proccess_hashtags(self, text):
	    hashtagged = re.sub(r'(?:(?<=\s)|^)#(\w*[A-Za-z_]+\w*)', self._hashtag_to_link, text)
	    return hashtagged

	def _processPost(post, from_zone, to_zone):
	    post["date"] = datetime.strptime(post.get("date"), "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=from_zone).astimezone(to_zone).strftime('%d %b %Y').upper()
	    if("original_date" in post):
	        post["original_date"] = datetime.strptime(post.get("original_date"), "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=from_zone).astimezone(to_zone).strftime('%d %b %Y').upper()
	    post["id"] = post.pop("_id")
	    post["text"] = _proccess_hashtags(post["text"])
	    listPost.append(post)

	def _processPostList(self, posts):
	    listPost = []
	    from_zone = tz.tzutc()
	    to_zone = tz.tzlocal()

	    for post in posts:
	        post["date"] = datetime.strptime(post.get("date"), "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=from_zone).astimezone(to_zone).strftime('%d %b %Y').upper()
	        if("original_date" in post):
	            post["original_date"] = datetime.strptime(post.get("original_date"), "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=from_zone).astimezone(to_zone).strftime('%d %b %Y').upper()
	        post["id"] = post.pop("_id")
	        post["text"] = self._proccess_hashtags(post["text"])
	        listPost.append(post)

	    return listPost

	def _proccess_post_children(self, post):
	    postCollection = get_db().get_collection(self.col_post)
	    from_zone = tz.tzutc()
	    to_zone = tz.tzlocal()
	    post['replies'] = []
	    for child in post['children']:
	        post_child = postCollection.find({'_id': child}).limit(1)[0]
	        if post_child and len(post_child['children']) > 0:
	            self._proccess_post_children(post_child)

	        post_child["date"] = datetime.strptime(post_child.get("date"), "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=from_zone).astimezone(to_zone).strftime('%d %b %Y').upper()
	        if("original_date" in post_child):
	            post_child["original_date"] = datetime.strptime(post_child.get("original_date"), "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=from_zone).astimezone(to_zone).strftime('%d %b %Y').upper()
	        post_child["id"] = post_child.pop("_id")
	        post_child["text"] = self._proccess_hashtags(post_child["text"])

	        post['replies'].append(post_child)

class Microblog(CommunityShareBase):
	def __init__(self):
		super(Microblog,self).__init__('microblog')
		self.col_user = '%s_user' % self.col_prefix

	def get_blog_user(self, id):
	    return get_db().get_collection(self.col_user).find_one({'id_user': id})

	def insert_blog_user(self, user_id):
		user = {
			"id_user": user_id, 
			"following": [id]
		}
		get_db().get_collection(self.col_user).insert(user)

	def get_num_followers(self, id):
	    return get_db().get_collection(self.col_user).find({"following": {"$eq" : id}}).count()

	def update_following_blog_user(self, id, following):
	    get_db().get_collection(self.col_user).update({"id_user": id}, {"$set": {"following": following}})

	def insert_post(self, id_user, first_name, last_name, username, avatar, postText):
		post = { 
			"id_user": id_user,
			"first_name": first_name,
			"last_name":last_name,
			"username": "@%s" % (username),
			"avatar": avatar,
			"date": datetime.utcnow().isoformat(),
			"text": urlize(escape(postText)),
			"children": [],
			"favourite": [],
			"shared": 0,
		}
		#get_db().get_collection(self.col_post).insert(post)
		super(Microblog,self).insert_post(post)

	def save_retweet(self, post_id, user_id, username):
	    postCollection = get_db().get_collection(self.col_post)
	    post = postCollection.find_one({"$and": [{"id_user":user_id},{"id_original_post":ObjectId(post_id)}]})

	    if(not post):
	        postCollection.update({"$or": [{"_id": ObjectId(post_id)}, {"id_original_post": ObjectId(post_id)}]}, {"$inc": {"shared":  1}}, multi=True)
	        post = postCollection.find_one({"_id": ObjectId(post_id)})
	        post["id_author"] = post["id_user"]
	        post["id_user"] = user_id
	        post["id_original_post"] = post["_id"]
	        post["original_date"] = post["date"]
	        post["date"] = datetime.utcnow().isoformat()
	        post["shared_by"] = "@%s" % (username)
	        del post["_id"]
	        #get_db().get_collection(self.col_post).insert(post)
	        super(Microblog,self).insert_post(post)
	        return True
	    else:
	        return False

	def save_reply(self, post_id, user_id, first_name, last_name, username, avatar, postText):
	    postCollection = get_db().get_collection(self.col_post)
	    post_orig = postCollection.find_one({"_id":ObjectId(post_id)})
	    if post_orig:
	    	post = {
						"id_user": user_id, 
						"first_name": first_name,
						"last_name": last_name,
						"username": "@%s" % (username),
						"avatar": avatar,
						"date": datetime.utcnow().isoformat(),
						"text": urlize(escape(postText)),
						"children": [],
						"favourite": [],
						"shared": 0,
						"is_child": True,

					}
	        reply_id = postCollection.insert(post)
	        post_orig["children"].append(reply_id)
	        postCollection.update({'_id': ObjectId(post_id)}, {"$set": {"children": post_orig["children"]}})
	        return True
	    else:
	        return False


class Blog(CommunityShareBase):
	def __init__(self):
		super('blog')


class Forum(CommunityShareBase):
	def __init__(self):
		super(Forum,self).__init__('forum')
		self.col_category = '%s_category' % self.col_prefix

	def get_forum_category(self, slug):
		return get_db().get_collection(self.col_category).find_one({'slug': slug})

	def insert_forum_category(self, name, slug):
		category = {
			"name": name,
			"slug": slug
		}
		get_db().get_collection(self.col_category).insert(category)

	def insert_post(self, category_slug, id_user, first_name, last_name, username, avatar, postText):
		post = { 
			"category_slug": category_slug,
			"id_user": id_user,
			"first_name": first_name,
			"last_name":last_name,
			"username": "@%s" % (username),
			"avatar": avatar,
			"date": datetime.utcnow().isoformat(),
			"text": urlize(escape(postText)),
			"children": [],
			"favourite": [],
			"shared": 0,
		}
		#get_db().get_collection(self.col_post).insert(post)
		super(Forum,self).insert_post(post)