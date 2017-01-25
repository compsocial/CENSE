# -*- coding: utf-8 -*-
#!/usr/bin/Python2.7
#
#Author:- Anurag Shivaprasad
#Date:- October 2016
'''
=====================
Weibo Connect Class
=====================
'''
from weibo import Client

class WeiboConnect:

	token = dict()
	client = None

	def __init__(self,credentials):
		self.setWeiboCredential(credentials)
		print "Successfully Connected to Weibo!"

	def setWeiboCredential(self, credentials):
		self.token[u'access_token'] = credentials[u'access_token']
		self.token[u'remind_in'] = credentials[u'remind_in']
		self.token[u'uid'] = credentials[u'uid']
		self.token[u'expires_at'] = credentials[u'expires_at']
		self.client = Client(credentials[u'API_KEY'],credentials[u'API_SECRET'],credentials[u'REDIRECT_URI'],self.token)
