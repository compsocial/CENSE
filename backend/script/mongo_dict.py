# -*- coding: utf-8 -*-
#!/usr/bin/Python2.7
#
#Author:- Anurag Shivaprasad
#Date:- October 2016
#Objective:- Dictionary mapping simple mathematical binary and unary operators to mongo equivalents

mongo_dict={
			"<": "$lt",
			">": "$gt",
			"<=": "$lte",
			">=": "$gte",
			"!=": "$ne",
			"==": "$eq",
			"in": "$in",
			"not in": "$nin",
			"or": "$or",
			"and":"$and",
			"not" : "$not",
			"where" : "$where"			
}