#!/usr/local/Cluster-Apps/python/3.6.8/bin/python3.6

import re
import subprocess
import sys

# Sort the data alphanumerically
def sorted_nicely(ARRAY):
        convert = lambda text: int(text) if text.isdigit() else text
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
        return sorted(ARRAY, key = alphanum_key)

# Get the data from the last line of file = FILE and column = RECORD  
def GET_DATA(FILE, RECORD):
	try:
		DATA    = float(subprocess.check_output(['tail', '-1', FILE]).split()[RECORD])
	except:
		DATA    = "None"
	return DATA

def GET_DATA_FROM_STRING(FILE, STRING, RECORD):
	try:
		DATA    = float(subprocess.check_output('grep "%s" %s | tail -1' % (STRING, FILE), shell = True).decode('ascii').split()[RECORD])
	except:
		DATA	= "None"
	return DATA

# Discrete gradient at the 4th order 
def GRADIENT(ARRAY, i):
	grad    = ARRAY[i-2]/12 - 2*ARRAY[i-1]/3 + 2*ARRAY[i+1]/3 - ARRAY[i+2]/12
	return grad
# Discrete Hessian at the 4th order
def CURVATURE(ARRAY,i):	
	hess	= -ARRAY[i-2]/12 + 4*ARRAY[i-1]/3 - 5*ARRAY[i]/2 + 4*ARRAY[i+1]/3 - ARRAY[i+2]/12
	return hess
