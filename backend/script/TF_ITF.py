# -*- coding: utf-8 -*-
#!/usr/bin/Python2.7
#
#Author:- Anurag Shivaprasad
#Date:- October 2016
'''
============
TF-ITF Class
============
'''
from MongoConnect import MongoConnect
import time
import json
import pandas as pd
import numpy as np
from bson.json_util import dumps

class TF_ITF:
	'''This class computes the TF-ITF for words

		Attributes:
		mongoconnect: MongoConnect object to access words in mongo
		current_time: int epoch time of current time
		time_to_live: int in seconds. This specifies how much time a word should have been in the database before TF-ITF calculation (maturation period).
		batch_val: Integer. This is the epoch timestamp before which words which have not been computed for TF-ITF should be used.
		threshold: Integer setting threshold for TF-ITF score.
	'''
	def __init__(self,hours_to_live,threshold=2.0):
		"""Inits TF_ITF class
		Args:
		hours_to_live: int in hours- specifies how much time a word should have been in the database before TF-ITF calculation
		threshold: Integer setting threshold for TF-ITF score

		Returns:
		None
		"""
		self.mongoconnect = MongoConnect(db="freeweibo")
		self.current_time = time.time()
		self.time_to_live = float(hours_to_live*3600)
		self.batch_val = self.current_time - self.time_to_live
		self.threshold = threshold

	def changeTimetoLive(self,hours_to_live):
		"""Resets time_to_live during runtime for experiment purposes
		Args:
		hours_to_live: int in hours- specifies how much time a word should have been in the database before TF-ITF calculation

		Returns:
		None
		"""
		self.time_to_live = hours_to_live

	def getPosts(self):
		'''Gets weibo and weiboscope words from mongo older than a threshold value.
		Args:
		None

		Returns
		None
		'''
		self.dict_weibo = dict()
		# json_weibo = json.loads(dumps(self.mongoconnect.getDocuments('TF',"added_on <= " + str(self.batch_val))))
		json_weibo = json.loads(dumps(self.mongoconnect.getDocuments('TF', all_docs = True)))
		for tup in json_weibo:
			self.dict_weibo[tup["_id"]] = tup["count"]

		# self.df_scope = pd.DataFrame(json.loads(dumps(self.mongoconnect.getDocuments('scopewords',"added_on <= " + str(self.batch_val))))).fillna(0)
		self.df_scope = pd.DataFrame(json.loads(dumps(self.mongoconnect.getDocuments('scopewords', all_docs = True)))).fillna(0)
		print self.df_scope.count()
		

	def tf_itfHelper(self,line):
		''' Performs TF-ITF calculation
		Args:
		line: dataframe row with word and count

		Returns:
		dataframe row with word and TF-ITF value.
		'''
		word = line["_id"]
		line["_id"] = line["_id"].encode("utf-8")
		## the word has to appear in the combined censored and uncensored corpus for at least 100 times
		if word in self.dict_weibo.keys() and (line['count'] + self.dict_weibo[word] >= 100):
			line['count'] = line["count"] / float(self.dict_weibo[word])
			return line
		else:
			line['count'] = np.nan
			return line
	
	def tf_itf(self):
		'''TF-ITF Driver method filters out words by threshold and removes words from mongo
		Args:
		None
		Returns:
		None
		'''
		self.df_tf_itf = self.df_scope.apply(self.tf_itfHelper,axis=1)
		# self.df_tf_itf = self.df_tf_itf.drop(["searched"],1)
		self.df_tf_itf = self.df_tf_itf[['_id', 'count']]
		self.df_tf_itf.columns = ["word","tf-itf"]
		self.df_tf_itf = self.df_tf_itf.dropna()
		print self.df_tf_itf
		self.df_tf_itf_final = self.df_tf_itf.loc[self.df_tf_itf["tf-itf"] > self.threshold].sort(["tf-itf"],ascending = False)
	#	self.mongoconnect.deleteDocuments('scopewords',"added_on <= " + str(self.batch_val))
	#	self.mongoconnect.deleteDocuments('TF',"added_on <= " + str(self.batch_val))

	def get_keywords(self):
		'''Returns DataFrame to calling function
		Args:
		None

		Returns:
		pandas DataFrame
		'''

		return self.df_tf_itf_final
