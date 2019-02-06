#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 10:31:10 2019

@author: lass
"""

import sys

version = sys.argv[1]

# update to new version in setup.py
with open('setup.py') as f:
	lines = f.readlines()
	writeLines = ''
	for l in lines:
		if l.find("    version='")!=-1:
			l ="    version='"+version+"',\n"
		writeLines+=l
			
with open('setup.py','w') as f:
	f.write(writeLines)



with open('docs/conf.py') as f:
	lines = f.readlines()
	writeLines = ''
	for l in lines:
		if l.find("version = u'")!=-1:
			l = "version = u'"+version+"'\n"
		elif l.find("release = u'")!=-1:
			l = "release = u'"+version+"'\n"
		writeLines+=l
			
with open('docs/conf.py','w') as f:
	f.write(writeLines)



with open('docs/index.rst') as f:
	lines = f.readlines()
	writeLines = ''
	for l in lines:
		if l.find("branch='")!=-1:
			idx = l.find('branch=')
			l = l[:idx] + version+"'\n"
		writeLines+=l
        
with open('docs/index.rst','w') as f:
	f.write(writeLines)

