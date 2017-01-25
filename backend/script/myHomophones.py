#!/usr/bin/python
# -*- coding: utf-8 -*-
from fetch_pinyin import fetchPinyin
import re

def _connectDb(db, dbHost='localhost'):
	import psycopg2
	try:
		conn = psycopg2.connect("dbname='%s' user='postgres' password='uYa1w5ol!' host='%s'" % (db, dbHost) )
	except:
		print 'Unable to connect to database'
		conn = None

	#conn.set_client_encoding("utf-8")
	return conn

def _decomposeAndRemovePinyinTones(string, type='diacritics'):
	if string is None:
		return None
	if not isinstance(string, unicode):
		string = unicode(string, 'utf-8')
		# print "isinstance of unique: " + keyword
	from cjklib.reading import ReadingFactory
	rf = ReadingFactory()
	readings = rf.decompose(string, 'Pinyin')
	readings = [rf.convert(string, 'Pinyin', 'Pinyin', 
		sourceOptions={'toneMarkType': type},
		targetOptions={'toneMarkType': 'none'}).lower().replace(u'ü', u'v') for string in readings]
	readings = [r for r in readings if r != ' ' and r != "'"]
	return readings
	
def _getCharactersForReadingFromDb(reading, exclude=None):
	conn = _connectDb('chinese_character')
	if conn is None:
		return None
	
	cur = conn.cursor()
	sql = "SELECT distinct f.id, f.character, f.pinyin, c.rank_percentile FROM freq_list f, char_sound c WHERE f.id=c.char_id AND c.pinyin_root=%s"
	param = (reading, )
	if not exclude is None:
		sql += " AND f.character!=%s"
		param += (exclude,)
	
	cur.execute(sql, param)
	results = []
	for result in cur:
		
		result = {
			'id': result[0],
			'character': result[1],
			'pinyin': result[2],
			'rank': result[3]
		}
		result['score'] = result['rank']/len(result['pinyin'].split('/'))
		results.append(result)
	return results	

def _generateAlternativeFromWord(word, pinyin):
	conn = _connectDb('chinese_character')
	if conn is None:
		return
	
	print pinyin
	if type(pinyin) is list:
		readings = pinyin
	else:
		readings = _decomposeAndRemovePinyinTones(pinyin)
	
	alt_words = [{'word': '', 'score': 0}]
	
	cur = conn.cursor()
	cur.execute("SELECT hanzi FROM alt_word WHERE pinyin=%s AND hanzi!=%s", (' '.join(readings), word))
	results = cur.fetchall()
	if len(results) > 0:
	   # already processed this keyword, return existing results
	   cur.close()
	   conn.close()
	   return results
   
	for index, r in enumerate(readings):
		alt_char = _getCharactersForReadingFromDb(r)

		#print r, alt_char, len(alt_char)
		concat_words = []
		for aw in alt_words:
		   for ac in alt_char:
			   nw = {
				   'word': aw['word'] + ac['character'],
				   'score': aw['score'] + ac['score']
			   }
			   concat_words.append(nw)
		   
		alt_words = concat_words
		alt_words = sorted(alt_words, key=lambda x: x['score'], reverse=True)
	
	#for aw in alt_words:
	for i in range(min(100, len(alt_words))):
		aw = alt_words[i]
		cur.execute("INSERT INTO alt_word (pinyin, hanzi, score) VALUES (%s, %s, %s)", (' '.join(readings), aw['word'], aw['score']))

	conn.commit()
	cur.close()
	conn.close()

def getAlternativeForWord(keyword, pinyin=None, scorerange=None, maxresults=20, recursive=False):
	re_chinese = re.compile(ur"[\u4E00-\u9FA5]+", re.U)
	if not re_chinese.match(keyword):
		return []
	# print "Hello"
	if not isinstance(keyword, unicode):
		keyword = unicode(keyword, 'utf-8')
	
	print len(keyword)
	if len(keyword) > 3:
		try:
			print "length > 3" + keyword
		except UnicodeEncodeError:
			try:
				print "length > 3" + keyword.encode('utf-8')
			except UnicodeEncodeError:
				print "length > 3"

		import math
		ks = [(keyword[0:2], keyword[2:])]
		if len(keyword[3:]) > 1:
			ks.append((keyword[0:3], keyword[3:]))
		rs = []
		for k in ks:
			n = max(int(math.ceil(math.sqrt(maxresults))), 2)
			r1s = getAlternativeForWord(k[0], maxresults=n, recursive=True)
			r2s = getAlternativeForWord(k[1], maxresults=n, recursive=True)
			range1 = r1s[0]['score'] - r1s[-1]['score']
			range2 = r2s[0]['score'] - r2s[-1]['score']
			#print n, len(r1s), len(r2s), range1, range2
			if range1 > range2:
				r2s = getAlternativeForWord(k[1], scorerange=range1, recursive=True)
			elif range2 > range1:
				r1s = getAlternativeForWord(k[0], scorerange=range2, recursive=True)
			#print n, len(r1s), len(r2s)
			r = []
			for r1 in r1s:
				for r2 in r2s:
					result = {
						'word': r1['word'] + r2['word'],
						'score': r1['score'] + r2['score']
					}
					r.append(result)
			r = sorted(r, key=lambda x: x['score'], reverse=True)
			if len(r) > maxresults:
				r = r[0:maxresults]
			rs.append(r)
		
		results = [r for r in rs[0] if r['word']!=keyword]
		result_words = [r['word'] for r in results]
		if len(rs) > 1:
			for r in rs[1]:
				if r['word'] not in result_words and r['word']!=keyword:
					results.append(r)
					result_words.append(r['word'])
			results = sorted(results, key=lambda x: x['score'], reverse=True)
			if len(results) > maxresults:
				results = results[0:maxresults]
		print "results"
		print results
		return results
	else:
		cn_conn = _connectDb('chinese_character')
		if cn_conn is None:
			print "cn_conn is None"
			return []

		if pinyin is None:
			pinyin = fetchPinyin(keyword)

		readings = _decomposeAndRemovePinyinTones(pinyin)
	
		cn_cur = cn_conn.cursor()
		
		sql = "SELECT hanzi, score FROM alt_word WHERE pinyin=%s"
		readings_string = ' '.join(readings)
		param = (readings_string, )
		
		if not recursive:
			sql += " AND hanzi!=%s"
			param += (keyword, )	
		if scorerange is not None:
			cn_cur.execute("SELECT MAX(score) FROM alt_word WHERE pinyin=%s", (readings_string,))
			max_score = cn_cur.fetchone()[0]
			min_score = max_score - scorerange
			sql += " AND score >= %s"
			param += (min_score,)
			
		sql += " ORDER BY score DESC"
		if scorerange is None:
			sql += " LIMIT %s"
			param += (maxresults,)
		
		cn_cur.execute(sql, param)
		dbResults = cn_cur.fetchall()
		
		if len(dbResults) == 0:
			_generateAlternativeFromWord(keyword, readings)
			cn_cur.execute(sql, param)
			dbResults = cn_cur.fetchall()
	
		results = []
		for r in dbResults:
			result = {
				'word': unicode(r[0], 'utf-8'),
				'score': r[1]
			}
			results.append(result)
	
		cn_cur.close()
		return results

if __name__ == '__main__':
	import sys
	#arg = sys.argv[1]
	arg = u'法同'
	if not isinstance(arg, unicode):
		arg = unicode(arg, 'utf-8')
	results = getAlternativeForWord(arg) #sys.argv[1])#
	for r in results:
		print r['word'], r['score']
