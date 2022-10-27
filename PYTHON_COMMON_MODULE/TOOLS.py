#!/usr/local/Cluster-Apps/python/3.6.8/bin/python3.6

import re
import subprocess

# Sort the data alphanumerically
def sorted_nicely(array):
        convert = lambda text: int(text) if text.isdigit() else text
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
        return sorted(array, key = alphanum_key)

# Get the data from the last line of file = FILE and column = RECORD  
def GET_data(FILE, RECORD):
	try:
		data    = float(subprocess.check_output(['tail', '-1', FILE]).split()[RECORD])
	except:
		data    = "None"
	return data

def GET_data_FROM_STRING(FILE, STRING, RECORD):
	try:
		data    = float(subprocess.check_output('grep "%s" %s | tail -1' % (STRING, FILE), shell = True).decode('ascii').split()[RECORD])
	except:
		data	= "None"
	return data

# Discrete gradient at the 4th order 
def GRADIENT(array, i):
	grad    = array[i-2]/12 - 2*array[i-1]/3 + 2*array[i+1]/3 - array[i+2]/12
	return grad
# Discrete Hessian at the 4th order
def CURVATURE(array,i):	
	hess	= -array[i-2]/12 + 4*array[i-1]/3 - 5*array[i]/2 + 4*array[i+1]/3 - array[i+2]/12
	return hess
