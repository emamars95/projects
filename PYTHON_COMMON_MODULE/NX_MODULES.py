#!/usr/bin/env python3
import os
import sys
import subprocess
import glob
from os.path 		import isfile

from TOOLS      	import sorted_nicely
import PARAM_FILE

# This check the file from the last line to the first line 
# In input      min_time : the first time from which you want to look for
#               MAX_TILE : the max time for which you want to look for
def GET_TIME_BASED_ON_D1_REVERSED(result_folder, min_time, max_time, thresh_d1):
	for line in reversed( list( open( "%s/%s" %(result_folder, PARAM_FILE.d1_file), "r") ) ):
		time, D1 = float(line.rstrip().split()[0]), float(line.rstrip().split()[1])
		if time <= max_time:
			if D1 <= thresh_d1:	break
			if time <= min_time:		break
	print("Returning D1: ", D1, " read at time: ", time)
	return time, D1

# This check the file from the first line to the last line 
def GET_TIME_BASED_ON_D1(result_folder, min_time, max_time, thresh_d1):
	for line in open( "%s/%s" %(result_folder, PARAM_FILE.d1_file), "r" ):
		time_tmp, D1_tmp = float(line.rstrip().split()[0]), float(line.rstrip().split()[1])
		if time_tmp >= min_time:
			if    D1_tmp  >= thresh_d1:	break	# We want the previus step, i.e. when D1 is < thresh
			else: D1, time = D1_tmp, time_tmp	
			if time >= max_time:	break
	print("Returning D1: ", D1, " read at time: ", time, "\n")
	return time, D1		
		
def MAKE_GEOM_VELOC_NX(time, time_step, natoms):
# In dyn.out the data relative to time step i are written AFTER the pattern $time(i)
# Therefore we sed between $time(i) and $time(i+1) to get the vale of $time(i)
	file_geom = open('geom', 'w')
	file_veloc = open('veloc', 'w')
	with open('dyn.out', 'r') as fp:
		for line in fp:
			if f'{str(time)}0 fs' in line:
				break									# Find the time requested in dyn.out
		for _ in range(3):								# skip three lines
			fp.readline()
		for _ in range(natoms):							# Write geom file
			file_geom.write(fp.readline())
		for _ in range(2):								# skip two lines
			fp.readline()
		for _ in range(natoms):							# Write veloc
			file_veloc.write(fp.readline())
	file_geom.close()
	file_veloc.close()
	# Convert NX format in xyz format
	os.system(". load-NX.sh && $NX/nx2xyz > geom.xyz")
	return

# Get the excitation energy and the probability of one specific TRAJECTORY. Return a string with the values.  
def GET_EXCITATION_ENERGY(FILE, TRAJ_NAME):
	try:
		f = open(FILE)
		ALL_DATA        = subprocess.check_output('grep -B 1 "%s " %s | head -1' % (TRAJ_NAME, FILE), shell = True).decode('ascii').split()
		EX_ENERGY       = ALL_DATA[2]
		PROB_TRANSITION = ALL_DATA[6]
		f.close
		return str(EX_ENERGY) + "\t" + str(PROB_TRANSITION)
	except IOError:
		print("\n\n" + FILE + " NOT found\n\n")
		sys.exit()
 
