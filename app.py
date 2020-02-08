#!/usr/bin/env python2.7
import os
import const
import errno
import subprocess
import pymongo
import datetime
import re
from flask import Flask, request, flash, redirect, url_for, render_template, send_from_directory, current_app
from flask_login import login_user, login_required, logout_user, current_user
from extensions import userdb, login_manager
from user_model import User
from werkzeug.utils import secure_filename
from celery import Celery
from data_check import at_check, fh_check
from make_table import submit_information, score_total, score_details, reid_details, personal_scores


UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['txt', 'csv'])

app = Flask(__name__)
app.secret_key = 'B3Yr7dqj/3X R~GIN!mNn]LWX/,?SA'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./db/user.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


'''             common functions             '''
@celery.task
def anony_scoring(cur_user, curuser_dir, filename, sfname, now_time):
	output = subprocess.check_output(['sh ./static/sh/drill2.sh ./static/pwsdata {} {} {}'.format(curuser_dir, filename, sfname)],
								stderr=subprocess.STDOUT,
								shell=True)
	output = output.split('\n')
	score = {'username': cur_user, 'filename': filename, 'submit_time': now_time, 'S_name': sfname}
	for i, o in enumerate(output):
		if i < 7:
			sc, ut = o.split(',')
			score[ut] = float(sc)
		else:
			if o != '':
				if o[0] == 'S':
					if '_' in o:
						pre, pos = o.split('_')
					else:
						pre, pos = o.split('.')
					for j in range(1, 5):
						score[pre + '_T' + str(j*25)] = float(output[i+j])
	#print score
	client = pymongo.MongoClient("localhost", 27017)
	db = client.restdb
	anonys = db.anony
	anonys.insert(score)
	client.close()

def reid_scoring(cur_user, curuser_dir, tgtuser_dir, sfname):
	output = subprocess.check_output(['sh ./static/sh/drill3.sh ./static/pwsdata {} {} {}'.format(curuser_dir, tgtuser_dir, sfname)],
								stderr=subprocess.STDOUT,
								shell=True)
	output = output.split('\n')
	re_score = {'username': cur_user, 'tgtusername': sfname.split('_')[0], 'sfname': sfname}
	for i in range(1,5):
		re_score['Fh{}'.format(i*25)] = output[i]
	return re_score


def configure_ext(app):
	login_manager.init_app(app)

	userdb.init_app(app)
	userdb.app = app
	userdb.create_all()

def list_file(path):
	filelist = [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]
	return filelist

def dir_check(path):
	try:
		os.makedirs(path)
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise
def dir_clear(path):
	filelist = list_file(path)
	for f in filelist:
		os.remove(os.path.join(path, f))

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_lastupname(username):
	client = pymongo.MongoClient("localhost", 27017)
	db = client.restdb
	at_rec = db.at_records
	try:
		at_filename = at_rec.find({'username': username}).sort("upload_time", pymongo.DESCENDING)[0]['at_filename']
		client.close()
		return at_filename
	except:
		client.close()
		return ''


'''             index page             '''
@app.route('/')
def index():
	return render_template("index.html")

'''             score page             '''
@app.route('/score')
def score():
	return render_template("score.html", table=score_total())

@app.route('/score_detail/<path:_id>')
def score_detail(_id):
	return render_template("score_detail.html", table=score_details(_id))

@app.route('/reid_detail/<path:sname>')
def reid_detail(sname):
	return render_template("score_detail.html", table=reid_details(sname))

@app.route('/personal')
def personal():
	return render_template("personal.html", table=personal_scores(current_user.username))



'''             Login functions             '''
@login_manager.user_loader
def load_user(username):
	return User.query.filter_by(username = username).first()

from forms import SignupForm
@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = SignupForm()
	if request.method == 'GET':
		return render_template('signup.html', form = form)
	elif request.method == 'POST':
		if form.validate_on_submit():
			if User.query.filter_by(username=form.username.data).first():
				flash("This username already exists", "warning")
				return redirect(url_for('signup'))
			else:
				newuser = User(form.username.data, form.password.data)
				userdb.session.add(newuser)
				userdb.session.commit()
				flash("User created!!!", "success")
				return redirect(url_for('login'))
		else:
			flash("Form didn't validate", "danger")
			return redirect(url_for('signup'))

@app.route('/login', methods=['GET','POST'])
def login():
	form = SignupForm()
	if request.method == 'GET':
		return render_template('login.html', form=form)
	elif request.method == 'POST':
		if form.validate_on_submit():
			user = User.query.filter_by(username=form.username.data).first()
			if user:
				if user.password == form.password.data:
					login_user(user)
					return redirect(url_for('index'))
				else:
					flash("user doesn't exist or wrong password", "danger")
					return redirect(url_for('login'))
			else:
				flash("user doesn't exist or wrong password", "danger")
				return redirect(url_for('login'))
		else:
			flash("Form didn't validate", "danger")
			return redirect(url_for('login'))

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

'''             anonyUpload functions             '''
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
	curuser_dir = UPLOAD_FOLDER + '/' + current_user.username
	dir_check(curuser_dir)
	dir_check(curuser_dir + '/AT_file')
	dir_check(curuser_dir + '/S_file')
	dir_check(curuser_dir + '/F_file')
	dir_check(curuser_dir + '/Fh_file')

	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part', 'danger')
			return redirect(request.url)
		file = request.files['file']
		# if user does not select file, browser also
		# submit a empty part without filename
		if file.filename == '':
			flash('No selected file', 'danger')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			at_filename = secure_filename(file.filename)
			if at_filename[0:3] != 'AT_':
				flash('Wrong filename format.', 'danger')
				return redirect(request.url)
			else:
				file.save(os.path.join(app.config['UPLOAD_FOLDER']+ '/' + current_user.username + '/AT_file/', at_filename))
				client = pymongo.MongoClient("localhost", 27017)
				db = client.restdb
				at_rec = db.at_records
				at_rec.insert({'username': current_user.username, 'upload_time': str(datetime.datetime.now()), 'at_filename': at_filename})
				client.close()
				
	return render_template("upload.html")


'''             reidUpload functions             '''
@app.route('/upload2', methods=['GET', 'POST'])
@login_required
def upload2():
	curuser_dir = UPLOAD_FOLDER + '/' + current_user.username
	dir_check(curuser_dir)
	dir_check(curuser_dir + '/AT_file')
	dir_check(curuser_dir + '/S_file')
	dir_check(curuser_dir + '/F_file')
	dir_check(curuser_dir + '/Fh_file')

	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part', 'danger')
			return redirect(request.url)
		files = request.files.getlist('file')
		# if user does not select file, browser also
		# submit a empty part without filename
		if len(files) == 0:
			flash('No selected file', 'danger')
			return redirect(request.url)
		for f in files:
			if f and allowed_file(f.filename):
				fh_filename = secure_filename(f.filename)
				if re.match(r'^Fh(25|50|75|100)_[\w-]+_[\w-]+$', fh_filename[:-4]):
					f.save(os.path.join(app.config['UPLOAD_FOLDER']+ '/' + current_user.username + '/Fh_file/', fh_filename))
				else:
					flash('Wrong filename format.', 'danger')
					return redirect(request.url)
	else:
		dir_clear(curuser_dir + '/Fh_file')
		#return redirect(url_for('upload', filename=filename))
	return render_template("upload2.html")

'''             Compute functions             '''
@app.route('/anony_check', methods=['GET', 'POST'])
@login_required
def anony_check():
	at_filename = get_lastupname(current_user.username)

	if at_filename != '':
		curuser_dir = UPLOAD_FOLDER + '/' + current_user.username
		at_filepath = curuser_dir + '/AT_file/' + at_filename
		t_filepath = './static/pwsdata/given_data/T.csv'

		msg = at_check(at_filepath, t_filepath)
		if msg != 'OK':
			flash(msg, 'danger')
			return redirect(url_for('upload'))
		else:
			now_time = datetime.datetime.now()
			now_time_str = now_time.strftime("%Y%m%d%H%M%S%f")
			sfname = current_user.username+'_'+now_time_str
			subprocess.call(['sh ./static/sh/drill.sh ./static/pwsdata {} {} {}'.format(curuser_dir, at_filename[3:-4], sfname)],
								stderr=subprocess.STDOUT,
								shell=True)
			info = [('User', current_user.username), ('Submit Time', now_time), ('S file name', 'S_'+sfname+'.txt')]
			str(now_time)
			return render_template("check.html", sfname=sfname+'#'+str(now_time).replace(' ', '@'), table=submit_information(info))

	else:
		flash('Cannot find your file, upload again.', 'danger')
		return redirect(url_for('upload'))

@app.route('/reid_check', methods=['GET', 'POST'])
@login_required
def reid_check():
	curuser_dir = UPLOAD_FOLDER + '/' + current_user.username
	fh_dirpath = curuser_dir + '/Fh_file'
	fh_filenames = [f for f in os.listdir(fh_dirpath) if os.path.isfile(os.path.join(fh_dirpath, f))]
	t_filepath = './static/pwsdata/given_data/T.csv'
	msg = fh_check(fh_dirpath, fh_filenames, t_filepath)
	if msg != 'OK':
		flash(msg, 'danger')
		return redirect(url_for('upload2'))
	else:
		info = []
		info.append(('Username', current_user.username))
		sfname = fh_filenames[0].split('_')[1]+'_'+fh_filenames[0].split('_')[2]
		target = 'S_'+sfname
		info.append(('Target', target))
		for fh in fh_filenames:
			if fh[4] == '_':
				info.append((fh[:4], fh))
			elif fh[5] == '_':
				info.append((fh[:5], fh))
		info.append(('Submit Time', str(datetime.datetime.now())))
		return render_template("check2.html", sfname=sfname, table=submit_information(info))

'''             Compute functions             '''
@app.route('/compute', methods=['GET', 'POST'])
@login_required
def compute():
	if request.method == 'POST':
		sfname = request.form['pass_sf']
		sfname, now_time = sfname.split('#')
		now_time = now_time.replace('@', ' ')
		print now_time
		
		curuser_dir = UPLOAD_FOLDER + '/' + current_user.username
		
		at_name = get_lastupname(current_user.username)[3:-4]
		anony_scoring.delay(current_user.username, curuser_dir, at_name, sfname, now_time)
	return render_template("compute.html")

@app.route('/compute2', methods=['GET', 'POST'])
@login_required
def compute2():
	if request.method == 'POST':
		sfname = request.form['pass_sf']
		tgt_usr = sfname.split('_')[0]
		tgtusr_dir = UPLOAD_FOLDER + '/' + tgt_usr
		curuser_dir = UPLOAD_FOLDER + '/' + current_user.username
		re_score = reid_scoring(current_user.username, curuser_dir, tgtusr_dir, sfname[:-4])
		
		client = pymongo.MongoClient("localhost", 27017)
		db = client.restdb
		reids = db.reid
		reids.insert(re_score)
		client.close()

		info = [('Target', 'S_' + sfname)]
		for i in range(1, 5):
			fh = 'Fh{}'.format(i*25)
			info.append((fh, re_score[fh]))

	return render_template("compute2.html", table=submit_information(info))


'''             Material functions             '''
@app.route('/material', defaults={'filename':''}, methods=['GET', 'POST'])
@app.route('/material/<path:filename>')
def material(filename):
	mtpath = "./materials"
	mtfiles = [f for f in os.listdir(mtpath) if os.path.isfile(os.path.join(mtpath, f))]
	if filename not in mtfiles:
		return render_template("material.html", mtfiles = mtfiles)
	else:
		return send_from_directory(directory="./materials", filename=filename)

@app.route('/s_download/<path:sinfo>')
def s_download(sinfo):
	user_dir, sname = sinfo.split('&')
	return send_from_directory(directory="./uploads/" + user_dir + '/S_file', filename=sname, as_attachment=True)
	

if __name__ == '__main__':
	configure_ext(app)
	dir_check(UPLOAD_FOLDER)
	app.run( 
		host=const.HOST,
		port=const.PORT,
		debug=True,
		threaded=True
	)