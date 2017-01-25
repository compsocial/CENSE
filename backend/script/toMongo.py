# -*- coding: utf-8 -*-
#!/usr/bin/Python2.7
#
#Author:- Anurag Shivaprasad
#Date:- October 2016
#Objective:- To Write to and update documents in mongodb.

import pandas as pd
from bson.json_util import dumps
import json
from datetime import datetime

def toMongo(keyword,mongoconnect,collection,timestamp):
	'''Given a row from a dataframe containing keyword and it's information, constructs a dict object and inserts this into specified mongo db and collection.
	Args:
	keyword: Pandas dataframe row containing keyword and its information
	mongoconnect: MongoConnect Object
	collection: String containing name of collection into which to insert document.
	timestamp: datetime object
	'''

	dateString = timestamp.strftime('%Y-%m-%d')

	if not(mongoconnect.isPresent(collection,keyword.post)):
		# insertDocument = {
		# 		"_id":keyword.post, 
		# 		"added_on":timestamp,
		# 		"count": keyword.pad,
		# 		"searched": 0}
		insertDocument = {
			'_id': keyword.post,
			'count': keyword.pad,
			dateString: keyword.pad,
			'searched': 0
		}
		mongoconnect.Writer(collection,insertDocument)
		
	elif mongoconnect.isPresent(collection,keyword.post):
		prev = json.loads(dumps(mongoconnect.findByID(collection,keyword.post)))[0]
		updateDocument = {
			'_id': keyword.post,
			'searched': prev['searched'],
			'count': prev['count'] + keyword.pad
		}
		if dateString in prev:
			updateDocument[dateString] = prev[dateString] + keyword.pad
		else:
			updateDocument[dateString] = keyword.pad
		# updateDocument = {
		# 		"_id":keyword.post, 
		# 		"added_on":prev[u'added_on'],
		# 		"count": prev['count'] + keyword.pad,
		# 		"searched": prev['searched']}
		mongoconnect.Updater(collection,updateDocument)
	return 0
