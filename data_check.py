#!/usr/bin/env python2.7

import pandas as pd
import numpy as np

def regex_check(at_tmp, col_num, regex):
	check = at_tmp[col_num].astype(str).str.match(regex)
	result = []
	if not all(check):
		nc = np.where([not i for i in check])[0]
		result = at_tmp.iloc[[nc[0]]].index
	return result


def at_check(at_filepath, t_filepath):
	t = pd.read_csv(t_filepath, dtype=str, header=None)
	at = pd.read_csv(at_filepath, dtype=str, header=None)
	at_tmp = at[at[0]!='DEL']
	#print at_tmp.head()
	#num check
	if len(at_tmp) < len(at)/2:
		return 'Delete too many records'
	
	#at[0] Custom IDs check
	cic = regex_check(at_tmp, 0, r'^[\w-]+$')
	if len(cic) != 0:
		return 'Custom IDs do not match requirement at row {}...'.format(cic[0])

	#at[1] Inovice numbers check
	inc = regex_check(at_tmp, 1, r'^[\w-]+$')
	if len(inc) != 0:
		return 'Inovice numbers do not match requirement at row {}...'.format(inc[0])

	#at[2] Date check
	#format check
	dc = regex_check(at_tmp, 2, r'^\d{4}\/([1])?\d{1}\/([1-3])?\d{1}$')
	if len(dc) != 0:
		return 'Date format do not match requirement at row {}...'.format(dc[0])
	
	#valid date check
	try:
		at_nd_date = pd.to_datetime(at_tmp[2])
	except:
		return 'Date validation do not match requirement'
	
	#same year and month check
	not_del = at_tmp.index.values
	t_nd_ym = [(d.year, d.month) for d in pd.to_datetime(t.loc[not_del, 2])]
	at_nd_ym = [(d.year, d.month) for d in at_nd_date]
	if t_nd_ym != at_nd_ym:
		return 'Date range do not match requirement'

	#at[3] Time check
	tc = regex_check(at_tmp, 3, r'^\d{1,2}:\d{1,2}$')
	if len(tc) != 0:
		return 'Time format do not match requirement at row {}...'.format(tc[0])
	try:
		pd.to_datetime(at_tmp[3], format= '%H:%M')
	except:
		return 'Time validation do not match requirement'

	#at[4] Stock code check
	if len(set(at_tmp[4]) - set(t[4])) != 0:
		return 'Exists non-valid stock code'

	#at[5] Unite Price check
	upc = regex_check(at_tmp, 5, r'^\d{1,5}(\.\d{1,2})?$')
	if len(upc) != 0:
		return 'Unite Price format do not match requirement at row {}...'.format(upc[0])

	#at[6] Quantity check
	qc = regex_check(at_tmp, 6, r'^\d{1,6}$')
	if len(qc) != 0:
		return 'Quantity format do not match requirement at row {}...'.format(qc[0])

	#PID check
	if len(set(at_tmp[0]).intersection(t[0].astype(str))) != 0:
		return 'Using CID as PID is not allowed'

	at_tmp2 = at_tmp.copy()
	at_tmp2[7] = t.loc[at_tmp.index.values, 0]
	at_tmp2[8] = [d.month for d in pd.to_datetime(at_tmp[2])]
	pc = at_tmp2[[7,8,0]].drop_duplicates()
	if any(pc.duplicated([7,8])):
		return 'Masking a CID to different PID in the same month.'

	return 'OK'

def fh_check(fh_dirpath, fh_filenames, t_filepath):
	t = pd.read_csv(t_filepath, dtype=str, header=None)
	t0_sort = sorted(list(set(t[0].astype(int))))

	targets = [(fh_filename.split('_')[1], fh_filename.split('_')[2]) for fh_filename in fh_filenames]
	print targets
	if len(set(targets)) != 1:
		return 'Attack target not the same.'

	for fh_filename in fh_filenames:
		fh = pd.read_csv(fh_dirpath+'/'+fh_filename, dtype=str, header=None)
		
		if len(fh) != len(set(t[0])):
			return 'Number of CIDs do not match requirement.'

		if len(fh.columns) != 13:
			return 'Number of columns do not match requirement.'
		
		if len(set(fh[0]) - set(t[0])):
			return 'Exists non-valid CID.'

		fh0 = list(fh[0].astype(int))
		if t0_sort != fh0:
			return 'CIDs not sorted.'

		return 'OK'



