#!/usr/bin/env python3
import os
import sys
import subprocess
import random 
import glob
from os.path import isfile

sys.path.append('/ddn/home/fzzq22/CODE_AND_SCRIPT/PYTHON_COMMON_MODULE')
from TOOLS      import sorted_nicely
import PARAM_FILE

# This check the file from the last line to the first line 
# In input      min_time : the first time from which you want to look for
#               MAX_TILE : the max time for which you want to look for
def GET_TIME_BASED_ON_D1_REVERSED(result_folder, min_time, max_time):
	for line in reversed( list( open( "%s/%s" %(result_folder, PARAM_FILE.d1_file), "r") ) ):
		time, D1 = float(line.rstrip().split()[0]), float(line.rstrip().split()[1])
		if time <= max_time:
			if D1 <= PARAM_FILE.thresh_d1:	break
			if time <= min_time:		break
	print("Returning D1: ", D1, " read at time: ", time)
	return time, D1

# This check the file from the first line to the last line 
def GET_TIME_BASED_ON_D1(result_folder, min_time, max_time):
	for line in open( "%s/%s" %(result_folder, PARAM_FILE.d1_file), "r" ):
		time_tmp, D1_tmp = float(line.rstrip().split()[0]), float(line.rstrip().split()[1])
		if time_tmp >= min_time:
			if    D1_tmp  >= PARAM_FILE.thresh_d1:	break	# We want the previus step, i.e. when D1 is < thresh
			else: D1, time = D1_tmp, time_tmp	
			if time >= max_time:	break
	print("Returning D1: ", D1, " read at time: ", time, "\n")
	return time, D1		
		
def MAKE_GEOM_VELOC_NX(time, time_step):
# In dyn.out the data relative to time step i are written AFTER the pattern $time(i)
# Therefore we sed between $time(i) and $time(i+1) to get the vale of $time(i)
        # Create the file form dyn.out for the time step before the crossing with d1 diagnostic lower than 0.065
        pattern_1 = " " + str(time) + "0 fs"
        pattern_2 = " " + str(time + time_step) + "0 fs"
        os.system("sed -n '/" + pattern_1 + "/,/" + pattern_2 + "/p' dyn.out > out.tmp")
        # Generate the geom  file from the step we are interested in 
        os.system("sed -n '/New geometry:/,/New velocity:/{//!p;}' out.tmp | awk 'NF' > geom ")
        os.system(". load-NX.sh")
        os.system("$NX/nx2xyz > geom.xyz")
        # Generate the veloc file from the step we are interested in 
        os.system("sed -n '/New velocity:/,/time    Etot         Ekin/{//!p;}' out.tmp | awk 'NF' > veloc ")
        os.system("rm -f out.tmp")
        return

# Chose random trajectories from a bunch s
def LABEL_TRAJ(PWD, wanted_traj, total_traj):
	ALLNAME = sorted_nicely(glob.glob("TRAJ*"))
	prob	= wanted_traj/total_traj; i = 0;
	print("The probability to select one trajectory is:     %10.2f and the total number of trajectories are: %10.2f" %(prob, len(ALLNAME)) )
	print("The expected number of trajectory to submit are: %10.2f" %(prob * len(ALLNAME)) )
	os.system("touch %s/%s" %(PWD, PARAM_FILE.to_submit_file)) 		# Write the file
	for TRAJ_NAME in ALLNAME:
		rd	= random.random()			# Random number between 0 and 1
		# The probability to be selected is the number of trajs we want devided the total number of trajectories we have
		if (prob > rd):					# Select trajectory depending on the random number
			traj_folder	=   "%s/%s/" 		%(PWD, TRAJ_NAME)
			os.system("echo %s >  %s/%s"     	%(str(rd), traj_folder, PARAM_FILE.to_submit_file))	# Write a label file with the random number generated
			os.system("echo %s >> %s/%s" 		%(TRAJ_NAME, PWD, PARAM_FILE.to_submit_file))		# Write a summary file with all selected trajectories
			i = i + 1
	print("The number of submitted trajectory are:          %i" %(i))
	return

def SUBMIT(TRAJ_NAME):
	os.system("nohup $NX/moldyn.pl > moldyn.log &")
	print ("%s submitted" %(TRAJ_NAME))

# Submit the trajectory for NX dynamics
def SUBMIT_TRAJECTORIES(PWD):
	labeling	= False
	if isfile(PWD + "/TO_SUBMIT"): labeling	= True
		
	FIRST_TRAJ      = int(input("Insert first traj to submit   "))		
	LAST_TRAJ       = int(input("Insert last traj to submit    "))
	print("INITIAL CONDITIONS from ", FIRST_TRAJ, " to ", LAST_TRAJ, " will be submitted")
	for i in range(FIRST_TRAJ, LAST_TRAJ + 1):
		TRAJ_NAME = "/TRAJ" + str(i)
		os.chdir(PWD + TRAJ_NAME + "/")				# Eneter in the folder
		if labeling:						# If we have previusly labeled the traj to sumbit
			if (isfile("TO_SUBMIT")): SUBMIT(TRAJ_NAME)	# If the traj is labelled
		else:				  SUBMIT(TRAJ_NAME)     # All traj in the range
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
 
