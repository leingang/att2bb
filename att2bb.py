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
course=rec.pop(0)
logging.debug("course=%s",course)
dates=[]
rec.pop(0) # next field is blank
for date in rec:
	if(date != ''):
		dates.append('Attendance %s' % date)

logging.debug("dates=%s",dates)

# second row is blank
next(records)

# rest of the rows are student records
report=[]
for row in records:
	logging.debug("Processing row: %s",repr(row))
	name=row.pop(0)
	netid=row.pop(0)
	logging.debug("NetID=%s")
	reportrow=[netid]
	for date in dates:
		status=row.pop(0)
		note=row.pop(0)
		score = 1 if (status=='Present') else 0
		score+= len(note)
		logging.debug("score(%s)=%s",date,score)
		reportrow.append("%.2f" % score)
	report.append(reportrow)

# output
writer=csv.writer(sys.stdout)
headers=['Username']
headers.extend(dates)
logging.debug('headers=%s',repr(headers))
writer.writerow(headers)
for row in report:
	writer.writerow(row)
	
	