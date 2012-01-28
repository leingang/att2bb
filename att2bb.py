#!/usr/bin/env python
"""
Convert an iOS attendance file report to one uploadable to Blackboard.
"""
import sys # file I/O
import csv # to parse the main CSV file

import logging

import argparse
parser = argparse.ArgumentParser(description='convert attendance report to Blackboard upload')
parser.add_argument('--verbose',help='be verbose',action='store_const',const=logging.INFO,dest='debug_level',default=logging.WARNING)
parser.add_argument('--debug',help='show debugging statements',action='store_const',const=logging.DEBUG,dest='debug_level',default=logging.WARNING)
parser.add_argument('file',help='name of the CSV file')
args = parser.parse_args()


logging.basicConfig(level=args.debug_level)


records = csv.reader(open(args.file, 'r'))

# first row has course name and date
# TODO: allow for multiple dates
rec=next(records)
logging.debug("first record: %s",repr(rec))
course=rec[0]
date=rec[2]
logging.debug("course=%s date=%s" % (course,date))

# second row is blank
next(records)

# rest of the rows are student records
report=[]
for row in records:
	logging.debug("Processing row: %s",repr(row))
	(name,netid,status,note)=row
	logging.debug("NetID=%s; status=%s; note=%s",netid,status,note)
	reportrow=[netid]
	score = 1 if (status=='Present') else 0
	score+= len(note)
	logging.debug("score=%s",score)
	reportrow.append("%f" % score)
	report.append(reportrow)
	
# output
writer=csv.writer(sys.stdout)
writer.writerow(['Username','Attendance %s' % date])
for row in report:
	writer.writerow(row)
	
	