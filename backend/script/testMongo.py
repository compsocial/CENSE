from MongoConnect import MongoConnect
import time
import json
import pandas

class TF_ITF:

	def __init__(self,hours_to_live):
		self.mongoconnect = MongoConnect(db="freeweibo")
		self.current_time = time.time()
		self.time_to_live = float(hours_to_live*3600)
		self.batch_val = current_time - time_to_live

	def changeTimetoLive(self,hours_to_live):
		self.time_to_live = hours_to_live

	def getPosts(self):
		#Get sinaweiboposts
		self.df_weibo = pd.DataFrame(json.loads(dumps(self.mongoconnect.getDocuments('TF',"added_on >=" + self.batch_val))))
		self.df_scope = pd.DataFrame(json.loads(dumps(self.mongoconnect.getDocuments('scopewords',"added_on >=" + self.batch_val))))

	def displayCursors(self):
		print self.df_scope
		print self.df_weibo
		


