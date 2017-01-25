# -*- coding: utf-8 -*-
#!/usr/bin/Python2.7
#
#Author:- Anurag Shivaprasad
#Date:- October 2016
#Objective:- To remove all keywords that are older than the set amount of time from the current date
import pandas as pd
import numpy as np
from MongoConnect import MongoConnect
import time
from datetime import date, datetime, timedelta

def now():
	return str(datetime.now()) + '\t'

startTime = datetime.now()

daysToLive_censored = 180
daysToLive_uncensored = 30

mongoconnect = MongoConnect(db="freeweibo")

## remove extracted censored keywords
earlierthan_30=time.time()-2592000
count = mongoconnect.deleteDocuments(collection="keywords",query="added_on < %d" % earlierthan_30)
print now(), 'Censored keywords removed', count


currentDatetime = date.today()
## remove expired words from censored corpus
update = 0
delete = 0
oldestDate = currentDatetime - timedelta(days = daysToLive_censored)
cur = mongoconnect.getDocuments(collection = "scopewords", all_docs = True, snapshot = True)
for row in cur:
	if '_id' in row and len(row['_id']) < 1:
		mongoconnect.deleteDocuments(collection='scopewords', query='_id == %s' % row['_id'])
	else:
		rowUpdate = False
		for key in row.keys():
			try:
				keyDate = datetime.strptime(key, '%Y-%m-%d').date()
				if keyDate < oldestDate:
					row['count'] -= row.pop(key, 0)
					rowUpdate = True
			except ValueError:
				continue
		if rowUpdate and row['count'] > 0:
			mongoconnect.Updater('scopewords', row)
			update += 1
		elif rowUpdate:
			delete += mongoconnect.deleteDocuments(collection='scopewords', query='_id == %s' % row['_id'])
print now(), 'Censored corpus updated', update
print now(), 'Censored corpus deleted', delete

## remove expired words from uncensored corpus
update = 0
delete = 0
oldestDate = currentDatetime - timedelta(days = daysToLive_uncensored)
cur = mongoconnect.getDocuments(collection = "TF", all_docs = True, snapshot = True)
for row in cur:
	if '_id' in row and len(row['_id']) < 1:
		mongoconnect.deleteDocuments(collection='TF', query='_id == %s' % row['_id'])
	else:
		rowUpdate = False
		for key in row.keys():
			try:
				keyDate = datetime.strptime(key, '%Y-%m-%d').date()
				if keyDate < oldestDate:
					row['count'] -= row.pop(key, 0)
					rowUpdate = True
			except ValueError:
				continue
		if rowUpdate and row['count'] > 0:
			mongoconnect.Updater('TF', row)
			update += 1
		elif rowUpdate:
			delete += mongoconnect.deleteDocuments(collection='TF', query='_id == %s' % row['_id'])
print now(), 'Uncensored corpus updated', update
print now(), 'Uncensored corpus deleted', delete

endTime = datetime.now()
print now(), 'Running time', (endTime - startTime).total_seconds(), 'seconds'
print '\n'