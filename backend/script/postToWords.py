#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import path
import fnmatch
import os
import sys
import jieba
from textblob import TextBlob as tb
import math
from multiprocessing import Pool
import jieba.posseg as pseg

jieba.enable_parallel()

# censored
f = open('censored.txt', 'r')
content = f.read().decode('utf-8')
f.close()

def generateWords(line):
	print line
	words = pseg.cut(line)
	past1 = ''
	past2 = ''
	word_list = []
	for i, w in enumerate(words):
		word = w.word
		flag = w.flag
		
		if past1 == '@':
			# skip username
			if flag == 'x' and word == u':':
				# end of username
				past1 = ''
			continue
		elif flag == 'x':
			# skip punctuation
			past1 = past2 = ''
			if word == '@':
				past1 = '@'
			continue
		
		if past2 != '' and past1 != '':
			word_list.append(past2 + past1 + word)
		if past1 != '':
			word_list.append(past1 + word)
		word_list.append(word)
		past2 = past1
		past1 = word
	return word_list

print 'Generating all words'
words = generateWords(content)
#words = [item for sublist in words for item in sublist]

print 'Done generating words'
print 'There are', len(words), 'words'
f = open('censored_terms1.txt', 'w')
content = u'\n'.join(words)
f.write(content.encode('utf-8'))
f.close()
'''

f = open('data/freeweibo_censored/censored_tf.txt', 'w')

def tf (word):
	global words, f
	f.write(word.encode('utf-8') + ' ' + str(words.count(word)) +  '\n')
	f.flush()

print 'Start computing tf on multi thread'
pool = Pool(8)
pool.map(tf, words)

print 'Finish computing tf'
print 'Output is at data/freeweibo_censored/censored_tf.txt'
f.close()
'''

'''
words = jieba.cut(content, cut_all=False)
words = '\n'.join(words)
csr_blob = tb(words)

csr_words = csr_blob.words
#csr_blob_len = len(csr_words)
f = open('data/freeweibo_censored/censored_tf.txt', 'w')

def tf (word):
	global csr_words, f
	f.write(word.encode('utf-8') + ' ' + str(csr_words.count(word)) +  '\n')
	f.flush()

print 'Start computing tf on multi thread'
pool = Pool(8)
pool.map(tf, csr_words)

print 'Finish computing tf'
print 'Output is at data/freeweibo_censored/censored_tf.txt'

f.close()
'''
'''
tf_scores = sorted(tf_scores.items(), key=lambda x: x[0], reverse=True)
print 'Sort finished'



for item in tf_scores:
	f.write(item[0].encode('utf-8') + ' ' + item[1])
'''

'''	
public_timeline = ''
for file in files:
	filePath = path.join(directory, file)
	f = open(filePath, 'r')
	
	content = f.read()
	words = jieba.cut(content, cut_all=False)
	words = '\n'.join(words)
	public_timeline += words

pt_blob = tb(public_timeline)


def n_containing (word, bloblist):
	return sum(1 for blob in bloblist if word in blob)
def idf (word, bloblist):
	# should count frequency as well
	return math.log(len(bloblist) / (1 + n_containing(word, bloblist)))
def tfidf (word, blob, bloblist):
	return tf(word, blob) * idf(word, bloblist)

bloblist = [csr_blob, pt_blob]
scores = {word: tfidf(word, blob, bloblist) for word in csr_blob.words}
sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
'''
'''
tags = jieba.analyse.extract_tags(content, 20)
log_f = open('jieba.log', 'w')
log_f.write(",".join(tags).encode('utf-8'))
'''
