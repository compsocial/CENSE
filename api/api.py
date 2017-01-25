# -*- coding: utf-8 -*-

from flask import Flask, make_response, request, jsonify
import json
from bson.json_util import dumps
import pandas as pd
from MongoConnect import MongoConnect
import random

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route("/")
def hello():
	return "<h1 style='color:blue'>Hello World!</h1>"

# get censored keywords
@app.route("/keywords")
def getKeywords():
	mongoconnect = MongoConnect('freeweibo')
	keywords = json.loads(dumps(mongoconnect.getDocuments(collection='keywords', all_docs=True)))
	dt = pd.DataFrame(keywords)
	return make_response(dumps(dt['_id'].tolist(), ensure_ascii=False).encode('utf-8'))

# get homophone suggestion for a given keyword
@app.route("/homophone")
def getRandomHomophone():
	keyword = request.args.get('keyword', '').encode('utf8')
	if len(keyword) < 1:
		return ''
	else:
		mongoconnect = MongoConnect('freeweibo')
		keywords = keyword.split(',')
		retVal = []
		for keyword in keywords:
			try:
				homophones = json.loads(dumps(mongoconnect.getDocuments(collection='keywords', query='_id == ' + keyword)))[0]
			except IndexError:
				homophones = {}
			if 'homophones' in homophones:
				hphones = homophones['homophones']
				homophone = random.choice(hphones)
				# print homophone['word'].encode('utf-8')
				retVal.append(homophone['word'])
			else:
				retVal.append(keyword.decode('utf-8'))
	return jsonify(retVal)

if __name__ == '__main__':
	app.run(host='0.0.0.0')
