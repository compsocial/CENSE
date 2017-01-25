# -*- coding: utf-8 -*-
#!/usr/bin/Python2.7
#
#Author:- Anurag Shivaprasad
#Date:- October 2016
#Objective:- To fetch posts from weibo using the weibo API and store word and their Term Frequency in mongoDB across all collected posts

from WeiboPublicTimeline import WeiboPublicTimeline
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


print now(), "SINA WEIBO FLOW BEGINNING..."
wpt = WeiboPublicTimeline()
wpt.scrapePublicTimeline(200)
wpt.extractText()
w_df = wpt.getSegmentedText(display=False,truncated = False)
w_df_tf = wpt.getTF()
w_df_tf.apply(lambda line: toMongo(line,mongoconnect,'TF',stamp),axis = 1)
print now(), "SINA WEIBO FLOW COMPLETE"

endTime = datetime.now()
print now(), 'Running time', (endTime - startTime).total_seconds(), 'seconds'
print '\n'