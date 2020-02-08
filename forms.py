#!/usr/bin/env python2.7

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Email, DataRequired

class SignupForm(FlaskForm):
    username = StringField('username', 
                validators=[DataRequired()])
    password = PasswordField(
                'password', 
                validators=[DataRequired()])
    submit = SubmitField("Sign In")