# -*- coding: utf-8 -*-
#!/usr/bin/Python2.7
#
#Author:- Anurag Shivaprasad
#Date:- October 2016
'''
====================
Text Segmenter Class
====================
'''

import re
import json
import jieba
import os
import enchant
import numpy as np
import pandas as pd
import jieba.posseg as pseg
from nltk.corpus import stopwords
from nltk.tokenize.stanford_segmenter import StanfordSegmenter


class TextSegmenter:
	'''This class segments a given chinese text into words with a variety of segmentation algorithms in existing modules

	Attributes:
	english_dict: dict obtained from enchant containing englsih words
	chinese_stopwords: dict containing chinese_stopwords
	english_stopwords: dict containing chinese_stopwords
	'''
	jieba.enable_parallel()

	def __init__(self):
		"""Inits TextSegmenter with stopword attributes and dictionary attributes as specified above."""

		self.english_dict = enchant.Dict("en_US")
		with open(os.path.dirname(os.path.abspath(__file__))+'/zh_stopwords.json') as data_file:    
			self.chinese_stopwords = json.load(data_file)
		self.english_stopwords = stopwords.words('english')

	def isAllChineseChar(self,string):
		"""Checks if a given word contains only chinese characters
		Args:
		string: text string cotaining word to be checked

		Returns:
		Boolean value indicating whether all character in the string are chinese characters
		"""
		return all(((u'\u4e00' <= char) and (char <= u'\u9fff')) for char in string)

	def checkWord(self,keyword):
		"""Checks if a given keyword is suitable to be stored: 

		Args:
		keyword: String containing word to be checked

		Return:
		Boolean value indicating whether word is all chinese or not
		"""
		if self.isAllChineseChar(keyword):	
			return True

		else:
			return False

	def prepSegmentation(self,df_text):
		'''This method prepares the given dataframe for segmentation by counting the number of instances of every unique post.
		Args:
		df_text: Dataframe containing posts

		Return:
		Dataframe containing unique posts with their counts
		'''
		df_text["pad"] = np.ones((df_text.shape[0],1))
		# f = {'pad': {'pad': 'count'}, 'timestamp': {'timestamp': 'max'}}
		df_text_new = pd.DataFrame(df_text.groupby("text")["pad"].count()).sort(columns="pad",ascending=False) 
		# df_text_new = df_text.groupby('text').agg(f)
		# df_text_new.columns = df_text_new.columns.droplevel(0)
		df_text_new["textseg"] = list(df_text_new.index)
		return df_text_new

	def segmenterHelper(self,line,method='Jieba',ngram=None):

		'''Segments a given post and drops irrelevant words. Checks for the following conditions:
		
		1. Not a stopword in english or chinese
		2. Not a mention of a user or tweet
		3. Not a number
		4. Not a single english character

		Args:
		line: String containing post
		method: Used to specify algorithm to be used for censorship (Jieba or Stanford or ngram)
		ngram: Parameter for ngram method, specifying the values for 'n'

		Returns:
		String containing segmented post
		'''
		line = re.sub(r"http\S+", "", line)
		past1 = ''
		word_list = []

		if method == 'Stanford':
			new_line = segmenter.segment(line)
			#Punctuation and emoji removal not coded for Stanford

		elif method == 'Jieba':
			words = pseg.cut(line)
			for i, w in enumerate(words):
				word = w.word
				#print word
				# word_list.append(word)
				flag = w.flag
				
			 	if past1 == '@':
				# skip username
			 		past1 = ''
			 		continue
			 	if past1 == '[' and word != ']':
			 		continue
			 	elif past1 == '[' and word == ']':
			 		past1 = ''

			 	if flag == 'x':
			 		# skip punctuation
			 		if word == '@' or word == '[':
			 			past1 = word
			 		continue

			 	if word in self.chinese_stopwords or word in self.english_stopwords:
			 		continue

			 	if word == " " or "." in word or word.isdigit():
					continue

				elif not self.checkWord(word):
					if not (self.english_dict.check(word) and len(word)>1):
						continue

			 	word_list.append(word)
			word_list = list(set(word_list))
			new_line =  u' '.join(word_list)
		elif method == 'ngram':
			defaultNgram = [2,3]

			## check if the parameter of ngram is a single number
			if isinstance(ngram, (int, long)):
				ngram = [ngram]
			## if it's a list, all items must be integers
			elif isinstance(ngram, list):
				ngram = [x for x in ngram if isinstance(x, (int, long))]
				if len(ngram) == 0:
					ngram = defaultNgram
			else:
				ngram = defaultNgram

			re_han, re_skip = re.compile(ur"([\u4E00-\u9FA5a-zA-Z0-9]+)", re.U), re.compile(ur"([#&\._]|\r\n|\s)", re.U)
			re_chinese = re.compile(ur"[\u4E00-\u9FA5]+", re.U)
			blocks = re_han.split(line)
			past = ''
			past1 = ''
			for blk in blocks:
				if not blk:
					continue

				if past1 == '@':
				# skip username
			 		past1 = ''
			 		continue
			 	if past1 == '[' and blk != ']':
			 		continue
			 	elif past1 == '[' and blk == ']':
			 		past1 = ''

				if blk == '@' or blk == '[':
					past1 = blk
					continue
				else:
					for n in ngram:
						for i in range(len(blk) - n + 1):
							word = blk[i:i+n]
							if len(word) == 0:
								continue
							if word in self.chinese_stopwords or word in self.english_stopwords:
			 					continue
							if word == " " or "." in word or word.isdigit():
								continue
							if not re_chinese.match(word):
								continue
							word_list.append(word)
			word_list = list(set(word_list))
			new_line =  u' '.join(word_list)
		else:
			raise ValueError("Invalid segmentation method!")		
		return new_line

	def segmenter(self,df,method='Jieba',ngram=None):
		'''Driver function to segment incoming posts
		Args:
		df: Dataframe containing posts

		Returns:
		Dataframe containing segmented posts
		'''
		df = self.prepSegmentation(df)
		df["textseg"] = df["textseg"].apply(self.segmenterHelper, args=(method,ngram))
	
		return df
