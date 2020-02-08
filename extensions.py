#!/usr/bin/env python2.7

# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
userdb = SQLAlchemy()

from flask_login import LoginManager
login_manager = LoginManager()