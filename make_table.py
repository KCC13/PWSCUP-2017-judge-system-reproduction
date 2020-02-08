#!/usr/bin/env python2.7

from flask_table import Table, Col, LinkCol
import pymongo
import pandas as pd
import numpy as np
from bson.objectid import ObjectId
from collections import Counter


"""Lets suppose that we have a class that we get an iterable of from
somewhere, such as a database. We can declare a table that pulls out
the relevant entries, escapes them and displays them.
"""


class Item(object):
	def __init__(self, name, description):
		self.name = name
		self.description = description

class ItemTable(Table):
	classes = ['table', 'table-bordered', 'thead-inverse']

	name = Col('Name')
	description = Col('Description')

def submit_information(info):
	items = []
	for p in info:
		items.append(Item(p[0], p[1]))
	table = ItemTable(items)
	return table.__html__()


class ItemTable2(Table):
	classes = ['table', 'table-bordered', 'thead-inverse']

	username = LinkCol('Username', 'reid_detail',
					url_kwargs=dict(sname='sname'), attr='username')
	filename = LinkCol('Filename', 'score_detail',
					url_kwargs=dict(_id='_id'), attr='filename')
	utility = Col('UTL')
	security = Col('SEC')
	average = Col('AVG')
	attack = LinkCol('ATK', 's_download',
					url_kwargs=dict(sinfo='sinfo'), attr='attack')

class Item2(object):
	""" a little fake database """
	def __init__(self, _id, sname, sinfo, username, filename, utility, security, average, attack):
		self._id = _id
		self.sname = sname
		self.sinfo = sinfo
		self.username = username
		self.filename = filename
		self.utility = utility
		self.security = security
		self.average = average
		self.attack = attack

	@classmethod
	def get_elements(self, df):
		items = []
		for index, row in df.iterrows():
			sinfo = row['username'] + '&S_' + row['sname'] + '.txt'
			items.append(Item2(row['_id'], row['sname'], sinfo, row['username'], row['filename'], row['utility'], row['security'], row['average'], 'LINK'))
		return items

def fh_score(sname):
	client = pymongo.MongoClient("localhost", 27017)
	db = client.restdb
	reids = db.reid
	df_reid = pd.DataFrame(list(reids.find({'sfname': sname})))
	client.close()

	worst_sc = 0.0
	if len(df_reid) != 0:
		for i in range(1,5):
			worst_sc += max(df_reid['Fh{}'.format(i*25)].astype(float))
		worst_sc /= 4.0
	return worst_sc

def score_total():
	ut_score = ['ut-ItemCF-supply', 'ut-ItemCF-retail', 'topk_list_difference', 'similarity_distance', 'ut_date', 'ut_price',
				'nrow']
	sc_score = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']

	client = pymongo.MongoClient("localhost", 27017)
	db = client.restdb
	anonys = db.anony
	df_total = pd.DataFrame(list(anonys.find()))
	client.close()

	if len(df_total) != 0:
		df_total['submit_time'] = pd.to_datetime(df_total['submit_time'])

		s_name = ['datenum', 'itemprice', 'itemnum', 'itemdate', 'item2pricenum', 'item2datenum']
		for i, sn in enumerate(s_name):
			tmp = pd.Series(np.zeros(len(df_total)))
			
			for j in range(1, 5):
				tmp += df_total['S{}-{}_T{}'.format(i+1, sn, j*25)]
			
			df_total['S{}'.format(i+1)] = tmp/4.0

		user_list = list(set(df_total['username']))

		scoreboard = []
		for user in user_list:
			df_user = df_total[df_total['username']==user].sort_values(by='submit_time', ascending=False).head(3)
			for index, row in df_user.iterrows():
				sname = row['S_name']
				reid_sc = fh_score(sname)

				_id = row['_id']
				sname = row['S_name']
				username = row['username']
				filename = row['filename']
				worst_ut = max(row[ut_score])
				worst_sc = max(row[sc_score])

				if worst_sc < reid_sc:
					worst_sc = reid_sc 
				
				scoreboard.append({'_id': _id, 'sname': sname, 'username': username, 'filename': filename, 'utility': '%.6f' % worst_ut, 'security': '%.6f' % worst_sc, 'average': '%.6f' % ((worst_ut+worst_sc)/2)})
		scoreboard = pd.DataFrame(scoreboard).sort_values(by='average')
		
		
		items = Item2.get_elements(scoreboard)
		table = ItemTable2(items)
		return table.__html__()
	
	else:
		return ''

class Item3(object):
	def __init__(self, program, partial_knowledge, value):
		self.program = program
		self.partial_knowledge = partial_knowledge
		self.value = value

class ItemTable3(Table):
	classes = ['table', 'table-bordered', 'thead-inverse', 'table-fixed']

	program = Col('Program')
	partial_knowledge = Col('Partial Knowledge')
	value = Col('Value')

def fh_details(sname):
	client = pymongo.MongoClient("localhost", 27017)
	db = client.restdb
	reids = db.reid
	df_reid = pd.DataFrame(list(reids.find({'sfname': sname})))
	client.close()

	worst_sc = []
	if len(df_reid) != 0:
		for i in range(1,5):
			pos = np.argmax(df_reid['Fh{}'.format(i*25)].astype(float))
			maxsc = df_reid['Fh{}'.format(i*25)].astype(float)[pos]
			username = df_reid['username'][pos]
			worst_sc.append((username, maxsc))
	return worst_sc

def score_details(_id):
	client = pymongo.MongoClient("localhost", 27017)
	db = client.restdb
	anonys = db.anony
	detail = anonys.find_one({'_id': ObjectId(_id)})
	client.close()


	sc_order = ['ut-ItemCF-supply', 'ut-ItemCF-retail', 'topk_list_difference', 'similarity_distance', 'ut_date', 'ut_price',
				'nrow', 'S1-datenum_T25', 'S1-datenum_T50', 'S1-datenum_T75', 'S1-datenum_T100',
				'S2-itemprice_T25', 'S2-itemprice_T50', 'S2-itemprice_T75', 'S2-itemprice_T100',
				'S3-itemnum_T25', 'S3-itemnum_T50', 'S3-itemnum_T75', 'S3-itemnum_T100',
				'S4-itemdate_T25', 'S4-itemdate_T50', 'S4-itemdate_T75', 'S4-itemdate_T100',
				'S5-item2pricenum_T25', 'S5-item2pricenum_T50', 'S5-item2pricenum_T75', 'S5-item2pricenum_T100',
				'S6-item2datenum_T25', 'S6-item2datenum_T50', 'S6-item2datenum_T75', 'S6-item2datenum_T100']

	programs = ['E1-ItemCF-s', 'E2-ItemCF-r', 'E3-topk', 'E4-diff-date', 'E5-diff-price', 'E6-nrow', 'S1-datenum',
				'S2-itemprice', 'S3-itemnum', 'S4-itemdate', 'S5-item2pricenum', 'S6-item2datenum']

	items = []
	for i, pg in enumerate(programs):
		if i < 6:
			if i < 2:
				items.append(Item3(pg, '', '%.6f' % detail[sc_order[i]]))
			elif i == 2:
				items.append(Item3(pg, sc_order[i], '%.6f' % detail[sc_order[i]]))
				items.append(Item3(pg, sc_order[i+1], '%.6f' % detail[sc_order[i+1]]))
			else:
				items.append(Item3(pg, '', '%.6f' % detail[sc_order[i+1]]))
		else:
			for j in range(1,5):
				items.append(Item3(pg, '{}%'.format(j*25), '%.6f' % detail[pg+'_T{}'.format(j*25)]))

	reid_sc = fh_details(detail['S_name'])
	if len(reid_sc) != 0:
		for i in range(4):
			items.append(Item3(reid_sc[i][0], '{}%'.format((i+1)*25), '%.6f' % reid_sc[i][1]))

	table = ItemTable3(items)
	return table.__html__()


class Item4(object):
	def __init__(self, username, reid_cnt, max_t25, max_t50, max_t75, max_t100, max_avg):
		self.username = username
		self.reid_cnt = reid_cnt
		self.max_t25 = max_t25
		self.max_t50 = max_t50
		self.max_t75 = max_t75
		self.max_t100 = max_t100
		self.max_avg = max_avg

class ItemTable4(Table):
	classes = ['table', 'table-bordered', 'thead-inverse', 'table-fixed']

	username = Col('Username')
	reid_cnt = Col('Count')
	max_t25 = Col('max(T25)')
	max_t50 = Col('max(T50)')
	max_t75 = Col('max(T75)')
	max_t100 = Col('max(T100)')
	max_avg = Col('Avg(max(Ta))')

def reid_details(sname):
	client = pymongo.MongoClient("localhost", 27017)
	db = client.restdb
	reids = db.reid
	df_reid = pd.DataFrame(list(reids.find({'sfname': sname})))
	client.close()

	items = []
	if len(df_reid) != 0:
		atk_cnt = Counter(df_reid['username'])

		for username in atk_cnt.keys():
			df_tmp = df_reid[df_reid['username']==username]
			t25 = max(df_tmp['Fh25'].astype(float))
			t50 = max(df_tmp['Fh50'].astype(float))
			t75 = max(df_tmp['Fh75'].astype(float))
			t100 = max(df_tmp['Fh100'].astype(float))
			avg = (t25 + t50 + t75 + t100)/4.0
			items.append((username, atk_cnt[username], '%.6f' % t25, '%.6f' % t50, '%.6f' % t75, '%.6f' % t100, '%.6f' % avg))
	items.sort(key=lambda x: x[-1], reverse=True)
	items = [Item4(item[0], item[1], item[2], item[3], item[4], item[5], item[6]) for item in items]

	table = ItemTable4(items)
	return table.__html__()

class ItemTable5(Table):
	classes = ['table', 'table-bordered', 'thead-inverse']
	username = LinkCol('Username', 'reid_detail',
					url_kwargs=dict(sname='sname'), attr='username')
	filename = LinkCol('Filename', 'score_detail',
					url_kwargs=dict(_id='_id'), attr='filename')
	submit_time = Col('Submit time')
	utility = Col('UTL')
	security = Col('SEC')
	average = Col('AVG')

class Item5(object):
	""" a little fake database """
	def __init__(self, _id, sname, username, filename, submit_time, utility, security, average):
		self._id = _id
		self.sname = sname
		self.username = username
		self.filename = filename
		self.submit_time = submit_time
		self.utility = utility
		self.security = security
		self.average = average

	@classmethod
	def get_elements(self, df):
		items = []
		for index, row in df.iterrows():
			items.append(Item5(row['_id'], row['sname'], row['username'], row['filename'], row['submit_time'], row['utility'], row['security'], row['average']))
		return items


def personal_scores(cur_usr):
	ut_score = ['ut-ItemCF-supply', 'ut-ItemCF-retail', 'topk_list_difference', 'similarity_distance', 'ut_date', 'ut_price',
				'nrow']
	sc_score = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']

	client = pymongo.MongoClient("localhost", 27017)
	db = client.restdb
	anonys = db.anony
	df_user = pd.DataFrame(list(anonys.find({'username': cur_usr})))
	client.close()

	if len(df_user) != 0:
		df_user['submit_time'] = pd.to_datetime(df_user['submit_time'])

		s_name = ['datenum', 'itemprice', 'itemnum', 'itemdate', 'item2pricenum', 'item2datenum']
		for i, sn in enumerate(s_name):
			tmp = pd.Series(np.zeros(len(df_user)))
			
			for j in range(1, 5):
				tmp += df_user['S{}-{}_T{}'.format(i+1, sn, j*25)]
			
			df_user['S{}'.format(i+1)] = tmp/4.0

		scoreboard = []
		for index, row in df_user.iterrows():
			sname = row['S_name']
			reid_sc = fh_score(sname)

			_id = row['_id']
			sname = row['S_name']
			submit_time = row['submit_time']
			filename = row['filename']
			worst_ut = max(row[ut_score])
			worst_sc = max(row[sc_score])

			if worst_sc < reid_sc:
				worst_sc = reid_sc 
			
			scoreboard.append({'_id': _id, 'sname': sname, 'username': cur_usr, 'filename': filename, 'submit_time': submit_time, 'utility': '%.6f' % worst_ut, 'security': '%.6f' % worst_sc, 'average': '%.6f' % ((worst_ut+worst_sc)/2)})
		scoreboard = pd.DataFrame(scoreboard).sort_values(by='average')
		
		
		items = Item5.get_elements(scoreboard)
		table = ItemTable5(items)
		return table.__html__()

	else:
		return ''
