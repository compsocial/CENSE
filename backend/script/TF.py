#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import path
import os
import sys
from multiprocessing import Pool
from TextSegmenter import TextSegmenter 

class TF():

	def __init__(self):
		print "Initializing TF Calculator..."
		self.term_freq = dict()
		self.word_segmenter = TextSegmenter()


	def tfHelper(self,row):
		post_count = row.pad
		status = row.textseg.split(" ")
		for word in status:
			if not word in self.term_freq.keys():
				self.term_freq[word] = post_count
			else:
				self.term_freq[word] += post_count

	def tf(self,input_dataframe=True,filename=None,df=None):
		if input_dataframe == False:
			#f = open('censored_terms.txt', 'r')
			words = { }
			f = filename

			print 'Start reading'
			for line in f:
				word = line.decode('utf-8').replace('\n', '')
				if word not in words:
					words[word] = 1
				else:
					words[word] += 1
			f.close()

			print 'Done reading'

			print 'Start writing'
			f = open('censored_tf.txt', 'w')
			words = sorted(words.items(), key=lambda x: x[1], reverse=True)

			for w in words:
				if w[1] > 1:
					f.write(w[0].encode('utf-8') + ' ' + str(w[1]) + '\n')
			f.close()
			print 'Done writing'

		elif input_dataframe == True:
			self.term_freq = dict()
			df.apply(self.tfHelper,axis=1)

	def getTF(self):
		return self.term_freq

