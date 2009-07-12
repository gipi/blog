#!/usr/bin/env python
import os

PYTHON_DEPENDENCIES = ['pygments', 'docutils', 'windmill']
PROGRAM_DEPENDENCIES = ['tex',]

for dep in PYTHON_DEPENDENCIES:
	print 'check \'' + dep + '\'',
	try:
		__import__(dep)
		print 'ok'
	except:
		print 'failed'

for dep in PROGRAM_DEPENDENCIES:
	print 'check \'' + dep + '\''
	os.system('echo | ' + dep + ' 2>&1 > /dev/null')
