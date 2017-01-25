# -*- coding: utf-8 -*-
#!/usr/bin/Python2.7
#
#Author:- Anurag Shivaprasad
#Date:- October 2016
#Objective :- To scrape weiboscope for censored posts and stored words and their Term Frequency across the collected posts
#

from WeiboscopeLatestPosts import WeiboscopeLatestPosts
from toMongo import toMongo
from MongoConnect import MongoConnect
import pandas as pd
from datetime import datetime
from bson.json_util import dumps
import json

def now():
	return str(datetime.now()) + '\t'

startTime = datetime.now()

stamp = datetime.now()
mongoconnect = MongoConnect(db = 'freeweibo')


print now(), "WEIBOSCOPE FLOW BEGINNING..."
wsp = WeiboscopeLatestPosts()
if wsp.fetchPosts():
	spam_ratio = wsp.spamRatio()
	ws_df = wsp.getSegmentedText(display=False,truncated = False)
	ws_df_tf = wsp.getTF()

	if not(mongoconnect.isPresent('TF',stamp)):
		insertDocument = {
				"_id":stamp, 
				"spam_ratio" : spam_ratio}
		mongoconnect.Writer('weiboscopeBatchSpam',insertDocument)

	ws_df_tf.apply(lambda line: toMongo(line,mongoconnect,'scopewords',stamp),axis = 1)

print now(), "WEIBOSCOPE FLOW COMPLETE"

endTime = datetime.now()
print now(), 'Running time', (endTime - startTime).total_seconds(), 'seconds'
print '\n'