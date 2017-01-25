# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import csv
import requests
import bs4
import sys
import os
from fetch_pinyin import fetchPinyin
import mongoConnect
import time
import myHomophones as mh

def createJSON(keyword,mongoconnect):
	if not(mongoconnect.isPresent('keywords',keyword.words)):
		stamp=time.localtime(time.time())
		pinyin_word = keyword.pinyin
		homophone=mh.getAlternativeForWord(keyword.words, pinyin=pinyin_word)
		insertDocument = {
				"_id":keyword.words , 
				"pinyin": pinyin_word,
				"added_on":time.time(),
				"searched": 0,
				 "homophones": homophone}
		mongoconnect.Writer('keywords',insertDocument)

	return 0
		
def isAllChineseChar(string):
	return all(((u'\u4e00' <= char) and (char <= u'\u9fff')) for char in string)

def checkWord(keyword):
	if isAllChineseChar(keyword.decode("unicode-escape")):	return keyword.decode("unicode-escape")
	else:	return np.nan
	
baseUrl = 'https://freeweibo.com/en'
response = requests.get(baseUrl)
soup = bs4.BeautifulSoup(response.text,"html.parser")
lis = soup.select('div#right ol li a')
lis1 = pd.DataFrame(lis,columns=["words"])
keywords = pd.DataFrame()
keywords["words"] = lis1.words.apply(lambda x: x.getText().encode("unicode-escape"))
keywords.words = keywords.words.apply(lambda x: checkWord(x))
keywords = keywords.dropna()
keywords.words = keywords.words.apply(lambda x: x.encode('utf-8'))
fetchPinyin(keywords)
print keywords
mongoconnect = mongoConnect.mongoConnect('freeweibo')

keywords.apply(lambda line: createJSON(line,mongoconnect),axis = 1)