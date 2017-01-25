# -*- coding: utf-8 -*-
#!/usr/bin/Python2.7
#
#Author:- Anurag Shivaprasad
#Date:- October 2016
#Objective:- Obtain pinyin for given word.

from xpinyin import Pinyin
import pandas as pd

#roman_gs = goslate.Goslate(writing=goslate.WRITING_ROMAN)

def fetchPinyin(keyword):
	'''Fetches pinyin for the given word using xpinyin module
	Args:
	keyword: unicode chinese character word.

	Returns:
	pinyin of given keyword
	'''

	p = Pinyin()
	return p.get_pinyin(keyword,' ')