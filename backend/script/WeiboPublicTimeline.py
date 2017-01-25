# -*- coding: utf-8 -*-
#!/usr/bin/Python2.7
#
#Author:- Anurag Shivaprasad
#Date:- October 2016
'''
=====================
Weibo Public Timeline
=====================
'''
import pandas as pd
from WeiboConnect import WeiboConnect
from api_credentials import creds 
from TF import TF
import os


class WeiboPublicTimeline(WeiboConnect,TF):
	'''Uses the sina weibo API to get posts from the Public Timeline
	Attributes:
	data: JSON object containing all collected posts
	'''
	
	def __init__(self):
		"""Inits weiboPublicTimeline class. Inherited classes WeiboConnect and TF are also initialized"""
		self.credIndex = 0
		if os.path.isfile('weibo_cred_index.txt'):
			with open('weibo_cred_index.txt', 'r') as file:
				string = file.readline().strip()
				try:
					self.credIndex = int(string)
				except ValueError:
					self.credIndex = 0
		WeiboConnect.__init__(self,creds[self.credIndex])
		TF.__init__(self)

	def scrapePublicTimeline(self,count=200):
		"""Gets a specified maximum number of posts using weibo client
		Args:
		count: Number of posts to fetch
		Returns:
		None
		"""
		if count > 200:
			count = 200
		elif count < 1:
			count = 1
		
		startCredential = self.credIndex
		while True:
			try:
				self.data = self.client.get('statuses/public_timeline', count= count)
				break
			except RuntimeError:
				## switch cred
				print 'API Key %d is not working, switching key...' % (self.credIndex,)
				self.credIndex = (self.credIndex + 1) % len(creds)
				if self.credIndex == startCredential:
					raise RuntimeError('Not enough API keys, create more keys')
				else:
					with open('weibo_cred_index.txt', 'w') as file:
						file.write(str(self.credIndex))
					self.setWeiboCredential(creds[self.credIndex])
	
	def extractText(self):	
		"""Extracts text for all posts in the JSON object
		Args:
		None
		Returns:
		None
		"""	
		df_statuses = pd.DataFrame(self.data['statuses'])
		print df_statuses.shape[0]
		print df_statuses.columns
		df_text = pd.DataFrame(df_statuses.text)
		self.df_segmented_text = self.word_segmenter.segmenter(df_text)		

	def getSegmentedText(self,truncated = True,display=False):
		""" Returns dataframe of segmented texts to calling function
		Args:
		truncated: Boolean value setting whether you get truncated view of dataframe or not
		display: Boolean value setting whether method displays dataframe as well.

		Returns:
		df_segmented_text: Pandas DataFrame containing segmented posts with TF.
		"""
		if truncated == False:
			pd.set_option('display.max_colwidth', -1)
		if display == True:
			print self.df_segmented_text
		return self.df_segmented_text

	def getScrapedData(self):
		""" Returns dataframe of raw texts to calling function
		Args:
		None

		Returns:
		Pandas DataFrame containing raw posts.

		"""	

		return pd.DataFrame(self.data['statuses'])

	def getTF(self):
		""" Returns dataframe of TF scores for words to calling function
		Args:
		None

		Returns:
		Pandas dataframe of TF scores for words

		"""			
		self.tf(df=self.df_segmented_text)
		df_tf = pd.DataFrame(pd.Series(self.term_freq))
		df_tf.columns = ["pad"]
		df_tf["post"] = list(df_tf.index)
		return df_tf
