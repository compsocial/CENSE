# -*- coding: utf-8 -*-
#!/usr/bin/Python2.7
#
#Author:- Anurag Shivaprasad
#Date:- October 2016
#Objective:- To calculate TF-ITF for words and identify censorship related keywords

from TF_ITF import TF_ITF
from fetch_pinyin import fetchPinyin
from MongoConnect import MongoConnect
import time
import myHomophones as mh
import datetime

def now():
	return str(datetime.datetime.now()) + '\t'

startTime = datetime.datetime.now()

tf_itf = TF_ITF(hours_to_live=24,threshold=2.0)
tf_itf.getPosts()
#tf_itf.displayPosts()
tf_itf.tf_itf()
keywords = tf_itf.get_keywords()
print now(), 'Extracted %d keywords' % (len(keywords),)
print now(), keywords
def createJSON(keyword,mongoconnect):
	if not keyword.word == "":
		if not(mongoconnect.isPresent('keywords',keyword.word)):
			stamp=time.localtime(time.time())
			pinyin_word = keyword.pinyin
			print pinyin_word
			print keyword.word
			homophone=mh.getAlternativeForWord(keyword.word, pinyin=pinyin_word)
			if len(homophone) == 0:
				return -1
			insertDocument = {
					"_id":keyword.word , 
					"pinyin": pinyin_word,
					"added_on":time.time(),
					"searched": 0,
					"homophones": homophone}
			mongoconnect.Writer('keywords',insertDocument)
	return 0

keywords["pinyin"] = keywords["word"].apply(fetchPinyin)
#keywords = keywords.loc[keywords.apply(lambda k: len(k['pinyin']) > 0)]
print now(), keywords
mongoconnect = MongoConnect('freeweibo')

keywords.apply(lambda line: createJSON(line,mongoconnect),axis = 1)

endTime = datetime.datetime.now()
print now(), 'Running time', (endTime - startTime).total_seconds(), 'seconds'
print '\n'