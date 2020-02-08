#!/usr/bin/env python2.7

from extensions import userdb

class User(userdb.Model):
	__tablename__ = 'user'
	username = userdb.Column(userdb.String(80), primary_key=True, unique=True, nullable=False)
	password = userdb.Column(userdb.String(80), nullable=False)
	def __init__(self, username, password):
		self.username = username
		self.password = password
	def __repr__(self):
		return '<User %r>' % self.username
	def is_authenticated(self):
		return True
	def is_active(self):
		return True
	def is_anonymous(self):
		return False
	def get_id(self):
		return str(self.username)
		