# -*- coding: utf-8 -*-
#!/usr/bin/Python2.7
#
#Author:- Anurag Shivaprasad
#Date:- October 2016
'''
==================
MongoConnect Class
==================

'''

from pymongo import MongoClient
from mongo_dict import mongo_dict
from exceptions import ValueError

class MongoConnect:
	'''
	This class is used to establish a connection to mongoConnect by creating a mongo client.
	With the created connection, this class provides functionality to add, remove and update
	documents from the database.

	Attributes:
	client: A mongo Client object to connect to the database.
	db: the database Object created from the client.

	'''
	def __init__(self,db=''):
		''' Initializes MongoConnect with a client and a connection to the specified database
		Args:
		db: String specifying the database name for the client connection.
		Returns:
		None
		Raises:
			ValueError if unable to connect to db.
		'''
		self.client = MongoClient()
		try:
			self.db = self.client[db]
		except:
			raise ValueError("Unable to connect to %s. Check if mongoDB is running and is %s is a valid database." % db)

	def Writer(self,collection,document):
		'''Writes a given document to specified collection in db.
		Args:
		collection: String containing name of collection in db
		document: JSON object of document to be inserted.

		Return:
		None
		'''
		result=self.db[collection].insert_one(document)

	def isPresent(self,collection,data):
		'''Checks if a document is present in a given collection
		Args:
		collection: String containing name of collection in db
		data: contains id of a document to be checked in collection.

		Return:
		boolean value indicating if id is present or not.
		'''
		ispresent=self.db[collection].find({"_id": data}).limit(1).count()
		if ispresent == 0:
			return False
		else:
			return True

	def Updater(self,collection,document):
		'''Updaters a given document in a specified collection in db.
		Args:
		collection: String containing name of collection in db
		document: JSON object of document to be updated.

		Return:
		None
		'''
		self.db[collection].update({'_id':document["_id"]}, {"$set": document}, upsert=False)

	def findByID(self,collection,id):
		'''Finds a document in a given collection
		Args:
		collection: String containing name of collection in db
		id: id of a document to be checked in collection.

		Return:
		mongo cursor containing document
		'''
		return self.db[collection].find({"_id": id}).limit(1)

	def getDocuments(self,collection,query="",all_docs=False,snapshot=False):
		'''Returns documents in a given collection according to the specified query
		Args:
		collection: String containing name of collection in db
		query: String containing simple query
		all_docs: Boolean value to set whether all documents are required are not. If true, 
		method will retrieve all documents in the given collection.

		Return:
		mongo cursor containing documents
		'''		
		query_split = query.split(" ")
		if all_docs == False:
			if len(query_split) == 3:
				attribute = query_split[0]
				equality = mongo_dict[query_split[1]]
				try:
					value = float(query_split[2])
				except ValueError:
					value = query_split[2]
				return self.db[collection].find({attribute:{equality : value}}, modifiers = {'$snapshot': snapshot})
		
		else:
			return self.db[collection].find(modifiers = {'$snapshot': snapshot})
	
	def deleteDocuments(self,collection,query=""):
		'''Deletes Documents according to given constraints
		Args:
		collection: String containing name of collection in db
		query: String containing simple query

		Return:
		Count of documents deleted according to the given query
		'''		
		query_split = query.split(" ")
		attribute = query_split[0]
		equality = mongo_dict[query_split[1]]
		try:
			value = float(query_split[2])
		except ValueError:
			value = query_split[2]
		result=self.db[collection].delete_many({attribute:{equality : value}})
		return result.deleted_count
