# -*- coding: utf-8 -*-
#!/usr/bin/Python2.7
#
#Author:- Chaya Hiruncharoenvate
#Date:- December 2016
#Objective:- Retrieved generated censored keywords from mongo database

from MongoConnect import MongoConnect
import json
from bson.json_util import dumps
import pandas as pd


mongoconnect = MongoConnect('freeweibo')
keywords = json.loads(dumps(mongoconnect.getDocuments(collection='keywords', all_docs=True)))
dt = pd.DataFrame(keywords)

dt['_id'].tolist()