#!/usr/bin/env python3

import sys
import os
from os.path import isfile

import TRAJECTORY_MODULES
import PARAM_FILE
from TOOLS import GET_DATA_FROM_STRING, GET_DATA

original_stdout = sys.stdout 										# Save a reference to the original standard output
pwd_directory = os.path.basename(os.path.normpath(os.getcwd()))   	# Get the current directory name. If it is part of 

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def NX_CHECK_TIME():
	time_dyn = GET_DATA_FROM_STRING("dyn.out", "STEP    ", 9)
	if not isfile("dyn.xyz"): 
		os.system(". load-NX.sh && $NX/dynout2xyz.pl")
		time_xyz = 0.0
	else:
		time_xyz = GET_DATA_FROM_STRING("dyn.xyz", "Time =", 2)
		if time_dyn > time_xyz:
			os.system(". load-NX.sh && $NX/dynout2xyz.pl")
	return time_dyn, time_xyz

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def SH_CHECK_TIME():
	os.system(". load-SHARCH.sh && $SARCH/data_extractor.x output.dat")
	time_dyn = GET_DATA("output.lis", 1)
	if not isfile(PARAM_FILE.coordinate_file):
		time_xyz = 0.0
	else:
		time_xyz = GET_DATA("COORDINATES.out", 0)
	return time_dyn, time_xyz

def CHECK_RESTART(rangexmin):
	# a restart, it will contain the following indication: (i) method used, (ii) time at which the dynamics is restarted separated by _
	if isfile("../RESULTS/DONT_ANALYZE") and "*RESTART*" in pwd_directory:
		METHOD_USED, time_restart = pwd_directory.split("_")
	# We grep at which time the primary dynamics is finished.
		timebreak = timebreak + time_restart
		rangexmin = time_restart
		gnuplot_time_label = f"($1 + {str(time_restart)})"        	# Time written in the file + the one at which the traj is restarted
		restart	= True												# For now only NX -> restarted with SHARC is implemented
																	# SHARC restarted with NX is not yet implemented
	else:
		restart	= False												# If it is not a restart
		time_restart = 0.0
		gnuplot_time_label = "1"									# Time aways written in the first column
	return restart, time_restart, gnuplot_time_label, rangexmin

def TEST_DICTIONARY_KEY(key):
	if key:
		key = float(key)
	return key
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def main():
	if sys.argv[1]:
		parameter_file_name = str(sys.argv[1])
	else:
		parameter_file_name	= PARAM_FILE.input_for_traj
	# --------------------------- READING THE PARAMETERS ------------------------------------------- #
	dictionary = TRAJECTORY_MODULES.READING_PARAMETER_FILE(parameter_file_name)

	calculation             = dictionary.get('method')             		# SH or NX
	state_list              = dictionary.get('states').split()
	rangexmin               = TEST_DICTIONARY_KEY(dictionary.get('rangexmin'))      	# Xmin and Xmax for
	rangexmax               = TEST_DICTIONARY_KEY(dictionary.get('rangexmax'))
	rangeymin               = TEST_DICTIONARY_KEY(dictionary.get('rangeymin'))      	# We use multiplot. 
	rangeymax               = TEST_DICTIONARY_KEY(dictionary.get('rangeymax'))
	rangey2min              = TEST_DICTIONARY_KEY(dictionary.get('rangey2min'))      	
	rangey2max              = TEST_DICTIONARY_KEY(dictionary.get('rangey2max'))      	
	outname                 = dictionary.get('output').rstrip()    		# Name of the plot.p
	input_coord             = dictionary.get('coordinates')
	timestep                = TEST_DICTIONARY_KEY(dictionary.get('time_step'))
	template_geo            = dictionary.get('template_geo').rstrip()
	# --------------------------- END OF READING THE PARAMETERS ------------------------------------ #
	print(state_list)
	if calculation.upper() == "NX":		# NX
		time_dyn, time_xyz = NX_CHECK_TIME()
	elif calculation.upper() == "SH": 	# SH
		time_dyn, time_xyz = SH_CHECK_TIME()		
	else:
		sys.exit("Exit the program since the input has not been recognized")	
	# ---------------------------------------------------------------------------------------------- #
	# Compute the total number of state, state are given in the format nsinglets, ndoublets, ntriplets, ... 
	nmstates, nstates = TRAJECTORY_MODULES.COUNTING_STATES(state_list)
	# Compute the time at which the dynamics is not anymore valid, total energy discontinuity ... 
	# print("\n Computing the time at which the trajecotry is not valid anymore\n")
	if calculation == "NX":
		timebreak, breakreason, scaling = TRAJECTORY_MODULES.TRAJECTORY_BREAK_NX("en.dat", 	nstates, timestep)
	if calculation == "SH":
		timebreak, breakreason = TRAJECTORY_MODULES.TRAJECTORY_BREAK_SH("output.lis", nmstates, timestep)
	# ---------------------------------------------------------------------------------------------- #
	if "zoom" in parameter_file_name and rangexmax == 0.0 and timebreak > 100.0:
		rangexmax	= timebreak - 100.00					# Zoom over the last 100 fs of the dynamics
	# ---------------------------------------------------------------------------------------------- #
	restart, time_restart, gnuplot_time_label, rangexmin = CHECK_RESTART(rangexmin)		
	# ---------------------------------------------------------------------------------------------- #
	label_molecule, class_molecule  = TRAJECTORY_MODULES.GET_MOLECULE_LABEL(template_geo)
	if time_dyn > time_xyz or not isfile(PARAM_FILE.coordinate_file):									# The dynamics is saved in dyn.xyz, however otput xyz was necessary to extract coordinates
		TRAJECTORY_MODULES.MAKE_GEOMETRICAL_COORDINATES(timestep, template_geo, label_molecule) 		# Recoupute the COORDINATES.out file
	# ---------------------------------------------------------------------------------------------- #
	if rangexmax == 0.0:																				# If a not particular time is given in input
		rangexmax = timebreak + 5	# + (2.0 * timebreak / 100) #Use the time. The extra lenght is only for nice plots not ending with the end of the dynamics.
	# Adjust the position of the label 1 (electronic states) and label 2 (coordinates)
	positionlabel1 = "%5.3f,%i"   %(rangexmax - (rangexmax - rangexmin) / 1.6  , rangeymax)
	positionlabel2 = "%5.3f,%i"   %(rangexmax - (rangexmax - rangexmin) / 10.0 , rangey2max)
	# ---------------------------------------------------------------------------------------------- #
	#Initialize the string 
	gnuplot_script = ''
	#We write the fist part of the gnuplot script
	gnuplot_script += TRAJECTORY_MODULES.WRITE_HEAD_GP(outname, rangexmin, rangexmax, rangeymin, rangeymax, positionlabel1)
	#We write the second part, containing the information to plot the electronic states
	if calculation == "NX":
		gnuplot_script += TRAJECTORY_MODULES.WRITE_NX_STATE_GP(nstates,  state_list, scaling, gnuplot_time_label, "en.dat"                   , time_restart, restart)
	if calculation == "SH":
		gnuplot_script += TRAJECTORY_MODULES.WRITE_SH_STATE_GP(nmstates, state_list,          gnuplot_time_label, "output_data/expec_MCH.out", time_restart, restart)
	#We write the last part containing the geometrical coordinates and the breakline at time = timebreak
	gnuplot_script += TRAJECTORY_MODULES.WRITE_COORDS_AND_BREAKLINE(rangeymax, rangey2min, rangey2max, positionlabel2, timebreak, breakreason, input_coord, gnuplot_time_label, label_molecule)
	#We write the string into the file (that will remain in the folder)
	with open(PARAM_FILE.gnuplot_file_traj, 'w') as gnuplot_script_FILE:
		sys.stdout = gnuplot_script_FILE	# Change the standard output to the file we created.
		print(gnuplot_script)
	# ---------------------------------------------------------------------------------------------- #
	sys.stdout = original_stdout 				# Reset the standard output to its original value
	os.system("gnuplot " + PARAM_FILE.gnuplot_file_traj)	# Write the png file running the gnuplot script


if __name__ == "__main__": 
	main()