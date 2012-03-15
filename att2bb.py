#!/usr/bin/env python
"""
Convert an iOS Attendance file report to one uploadable to Blackboard.
"""
import sys # file I/O
import csv # to parse the main CSV file

import logging

import argparse
parser = argparse.ArgumentParser(description='convert attendance report to Blackboard upload')
parser.add_argument('--verbose',help='be verbose',action='store_const',const=logging.INFO,dest='debug_level',default=logging.WARNING)
parser.add_argument('--debug',help='show debugging statements',action='store_const',const=logging.DEBUG,dest='debug_level',default=logging.WARNING)
parser.add_argument('file',help='name of the CSV file')
# TODO: write to stdout unless an option is given (--save?)

# the data object: a finite-state machine
# TODO: extend the class?
# TODO: use a member logger rather than the global one?
from fysom import Fysom

def oncourse_record(e):
	logging.debug("entering state: %s", e.dst)
	rec=e.row
	logging.debug("course record: %s",repr(rec))
	course_name=rec.pop(0)
	logging.debug("course=%s",course_name)
	dates=[]
	rec.pop(0) # next field is blank
	for date in rec:
		if(date != ''):
			dates.append('Attendance %s' % date)
		e.fsm.current_course = course_name
		e.fsm.data[course_name] = {}
		e.fsm.data[course_name]['dates'] = dates
		e.fsm.data[course_name]['scores'] = {}
	return data
	
def onstudent_records(e):
	logging.debug("entering state: %s", e.dst)
	
def onstudent_record(e):
	logging.debug("entering state: %s", e.dst)
	row=e.row
	current_course=e.fsm.current_course
	logging.debug("Processing row: %s",repr(row))
	name=row.pop(0) # discard
	netid=row.pop(0)
	logging.debug("NetID=%s",netid)
	scores=[]
	for date in e.fsm.data[current_course]['dates']:
		status=row.pop(0)
		note=row.pop(0)
		score = 1 if (status=='Present') else 0
		score+= len(note)
		logging.debug("score[%s]=%s",date,score)
		scores.append("%.2f" % score)
	e.fsm.data[current_course]['scores'][netid]=scores

def onclass_course_separator(e):
	logging.debug("entering state: %s", e.dst)
	logging.debug('skipping blank line')
	
def onend_row(e):
	logging.debug("entering state: %s", e.dst)

fsm = Fysom({
	'initial' : 'start',
	'events' : [
		{'name': 'row'    , 'src': 'start'                  , 'dst': 'course_record'},
		{'name': 'end_row', 'src': 'course_record'          , 'dst': 'course_record'},
		{'name': 'blank'  , 'src': 'course_record'          , 'dst': 'student_records'},
		{'name': 'row'    , 'src': 'student_records'        , 'dst': 'student_record'},
		{'name': 'end_row', 'src': 'student_record'         , 'dst': 'student_records'},
		{'name': 'blank'  , 'src': 'student_records'        , 'dst': 'class_course_separator'},
		{'name': 'row'    , 'src': 'class_course_separator' , 'dst': 'course_record'}
	],
	'callbacks': {
		'oncourse_record': oncourse_record,
		'onstudent_records': onstudent_records,
		'onstudent_record': onstudent_record,
		'onclass_course_separator': onclass_course_separator,
		'onend_row': onend_row
	}
})

fsm.current_course=''
fsm.data={}



args = parser.parse_args()
logging.basicConfig(level=args.debug_level)

records = csv.reader(open(args.file, 'r'))
logging.info("Reading CSV file.")

# read
for row in records:
	data = {}
	logging.debug("Processing row: %s",repr(row))
	# some rows are blank, and some blank rows are fields of empty strings
	# blank rows do have fields, they're just all empty strings
	if(''.join(row)==''):
		fsm.blank()
	else:
		fsm.row(row=row)
		fsm.end_row()
logging.debug("FSM data: %s",fsm.data)

# output
logging.info("Writing CSV file(s).")
for coursename, classdata in fsm.data.items():
	dates=classdata['dates']
	student_scores=classdata['scores']
	filebasename="%s_Attendance_bb" % coursename
	filename="%s.csv" % filebasename.replace('.','_').replace(' ','_')
	with open(filename,'w') as f:
		writer=csv.writer(f)
		headers=['Username']
		headers.extend(dates)
		logging.debug('headers=%s',repr(headers))
		writer.writerow(headers)
		for NetID, scores in student_scores.items():
			row=[NetID] + scores
			writer.writerow(row)
		f.close()
	logging.info("Wrote %s" % filename)
logging.info("Done!")
	
	
	