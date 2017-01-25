from weiboPublicTimeline import weiboPublicTimeline
from weiboscopeLatestPosts import weiboscopeLatestPosts
from TF import TF
from toMongo import toMongo
from MongoConnect import MongoConnect
import pandas as pd
import time
from bson.json_util import dumps
import json

stamp=time.time()
mongoconnect = MongoConnect(db = 'freeweibo')


print "SINA WEIBO FLOW BEGINNING..."
wpt = weiboPublicTimeline()
wpt.scrapePublicTimeline(200)
wpt.extractText()
w_df = wpt.getSegmentedText(display=False,truncated = False)
w_df_tf = wpt.getTF()
w_df_tf.apply(lambda line: toMongo(line,mongoconnect,'TF',stamp),axis = 1)
print "SINA WEIBO FLOW COMPLETE"
#---------------------WEIBOSCOPE--------------->>>
print "WEIBOSCOPE FLOW BEGINNING..."
wsp = weiboscopeLatestPosts()
wsp.fetchPosts()
spam_ratio = wsp.spamRatio()
ws_df = wsp.getSegmentedText(display=False,truncated = False)
ws_df_tf = wsp.getTF()

if not(mongoconnect.isPresent('TF',stamp)):
	insertDocument = {
			"_id":stamp, 
			"spam_ratio" : spam_ratio}
	mongoconnect.Writer('weiboscopeBatchSpam',insertDocument)

ws_df_tf.apply(lambda line: toMongo(line,mongoconnect,'scopewords',stamp),axis = 1)
print "WEIBOSCOPE FLOW COMPLETE"