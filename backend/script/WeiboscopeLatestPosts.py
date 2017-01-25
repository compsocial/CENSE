
# -*- coding: utf-8 -*-
#!/usr/bin/Python2.7
#
#Author:- Anurag Shivaprasad
#Date:- October 2016
'''
=============================
Weiboscope Latest Posts Class
=============================
'''
from bs4 import BeautifulSoup
import pandas as pd
import requests
import jieba
import jieba.posseg as pseg
import sys
from MongoConnect import MongoConnect
from TF import TF
from datetime import datetime
import os


class WeiboscopeLatestPosts(TF):
	'''Class for Weiboscope Scraping
	Attributes:
	url: String containing url of webpage to scrape
	post_df: Pandas dataframe for posts with boolean spam indicator for each post'''
	def __init__(self):
		"""Inits WeiboscopeLatestPosts Class with url and posts_df values.
		Args:
		None
		Returns:
		None
		"""
		TF.__init__(self)
		self.url = 'http://weiboscope.jmsc.hku.hk/wsr/latest.py'
		self.post_df = pd.DataFrame(columns=['text','timestamp','spam_val'])
	
	def handleSPAM(self,line):
		"""assign spam indicator for each post depending on whether post text is marked as SPAM.
		Args:
		line: Pandas dataframe row
		Returns:
		line: Pandas dataframe row with spam value set.
		"""
		if "SPAM " in line.text:
			line.text = line.text.split("SPAM ")[1]
			line.spam_val = 1
			return line
		else:
			line.spam_val = 0
			return line

	def fetchPosts(self):
		"""Scrapes page at url for posts.
		Args:
		None
		Returns:
		None
		"""		
		response = requests.get(self.url)
		text = response.text
		soup = BeautifulSoup(response.text,"html.parser")

		lis = pd.Series(soup.get_text().split("\n")[1:])
		lis = lis.loc[lis.apply(lambda line: "|" in line)]
		print 'before date check', len(lis)

		if os.path.isfile('scope_latest_scraped_post.txt'):
			with open('scope_latest_scraped_post.txt', 'r') as file:
				postTimeString = file.readline().strip()
				postTime = datetime.strptime(postTimeString, '%Y-%m-%d %H:%M:%S')
				postSelection = lis.apply(lambda line: datetime.strptime(line.split('|')[0].strip(), '%Y-%m-%d %H:%M:%S') > postTime)
				lis = lis.loc[postSelection]
		print 'after date check', len(lis)

		if len(lis) > 0:
			latestPostTimeString = lis[0].split('|')[0].strip()
			with open('scope_latest_scraped_post.txt', 'w') as file:
				file.write(latestPostTimeString)
			
			self.post_df["text"] = lis.apply(lambda line: line.split("|")[1])
			self.post_df['timestamp'] = lis.apply(lambda line: datetime.strptime(line.split('|')[0].strip(), '%Y-%m-%d %H:%M:%S'))
			self.post_df = self.post_df.apply(self.handleSPAM,axis=1)

		return len(lis) > 0

	def spamRatio(self):
		"""Computes ratio of spam to non spam posts in the batch of posts
		Args:
		None
		Returns:
		Float ratio of spam to non-spam posts
		"""		
		if self.post_df.shape[0] > 0:
			return float(self.post_df.spam_val.sum())/self.post_df.shape[0]
		else:
			return 0

	def getDataFrame(self):
		"""Returns post Dataframe
		Args: 
		None
		Returns:
		post_df
		"""
		return self.post_df

	def getDocument(self):
		"""Returns posts in posts_df Dataframe as a white spaced document.
		Args: 
		None
		Returns:
		document:String containing all posts whitespaced.
		"""
		posts_list = list(self.post_df["text"])
		document = " ".join(posts_list)
		return document

	def getSegmentedText(self,truncated = True,display=False):
		""" Returns dataframe of segmented texts to calling function
		Args:
		truncated: Boolean value setting whether you get truncated view of dataframe or not
		display: Boolean value setting whether method displays dataframe as well.

		Returns:
		df_segmented_text: Pandas DataFrame containing segmented posts with TF.
		"""
		self.df_segmented_text = self.word_segmenter.segmenter(self.post_df, method = 'ngram', ngram = [2,3])	
		if truncated == False:
			pd.set_option('display.max_colwidth', -1)
		if display == True:
			print self.df_segmented_text
		return self.df_segmented_text

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
