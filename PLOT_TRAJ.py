#!/usr/bin/env python3

import sys
import os
import subprocess
sys.path.append('/ddn/home/fzzq22/CODE_AND_SCRIPT/PYTHON_COMMON_MODULE')

import TRAJECTORY_MODULES
import PARAM_FILE

original_stdout = sys.stdout 			# Save a reference to the original standard output

PARAMETER_FILE_NAME 	= str(sys.argv[1])
# --------------------------- READING THE PARAMETERS ------------------------------------------- #
(CALCULATION, STATE_LIST, rangexmin, rangexmax, rangeymin, rangeymax, rangey2max,
	outname, INPUT_COORD, TIMESTEP, TEMPLATE_GEO) = TRAJECTORY_MODULES.READING_PARAMETER_FILE(PARAMETER_FILE_NAME)
# --------------------------- END OF READING THE PARAMETERS ------------------------------------ #

if   "N" in CALCULATION.upper():		# NX
	CALCULATION = "NX"
	time_dyn        = float(subprocess.check_output('grep "STEP    " dyn.out | tail -1' , shell = True).decode('ascii').split()[9])
	if not os.path.isfile("dyn.xyz"): 
		os.system("run-NX.sh dynout2xyz.pl")
		time_xyz	= 0.0
	else:
		time_xyz	= float(subprocess.check_output('grep "Time ="   dyn.xyz | tail -1' , shell = True).decode('ascii').split()[2])
		if time_dyn > time_xyz:
			os.system("run-NX.sh dynout2xyz.pl")
elif "S" in CALCULATION.upper(): 		# SH
	CALCULATION = "SH"
	os.system("/nobackup/zcxn55/SOFTWARE/SHARC-2.1-corr-edc/bin/data_extractor.x output.dat")
	time_dyn        = float(subprocess.check_output('tail -1 output.lis', shell = True).decode('ascii').split()[1])
	if not os.path.isfile("COORDINATES.out"):
		time_xyz        = 0.0
	else:
		time_xyz	= float(subprocess.check_output('tail -1 COORDINATES.out', shell = True).decode('ascii').split()[0])
else:
	sys.exit("Exit the program since the input has not been recognized")	
# ---------------------------------------------------------------------------------------------- #

# Compute the total number of state, state are given in the format nsinglets, ndoublets, ntriplets, ... 
nmstates, nstates	= TRAJECTORY_MODULES.COUNTING_STATES(STATE_LIST)

# Compute the time at which the dynamics is not anymore valid, total energy discontinuity ... 
# print("\n Computing the time at which the trajecotry is not valid anymore\n")
if CALCULATION == "NX":
	timebreak, breakreason, scaling  = TRAJECTORY_MODULES.TRAJECTORY_BREAK_NX("en.dat", 	nstates, TIMESTEP)
if CALCULATION == "SH":
	timebreak, breakreason		 = TRAJECTORY_MODULES.TRAJECTORY_BREAK_SH("output.lis", nmstates, TIMESTEP)
# ---------------------------------------------------------------------------------------------- #

if "zoom" in PARAMETER_FILE_NAME and rangexmin == 0.0 and timebreak > 100.0:
	#print(rangexmin, timebreak)
	rangexmin	= timebreak - 100.00					# Zoom over the last 100 fs of the dynamics
# ---------------------------------------------------------------------------------------------- #

CURRENT_DIRECTORY       = os.path.basename(os.path.normpath(os.getcwd()))   	# Get the current directory name. If it is part of 
# a restart, it will contain the following indication: (i) method used, (ii) time at which the dynamics is restarted separated by _  
if os.path.isfile("../RESULTS/DONT_ANALYZE") and "XMS-RESTART-12-9-3s" in CURRENT_DIRECTORY:
	METHOD_USED, TIME_RESTART       = CURRENT_DIRECTORY.split("_")[0], float(CURRENT_DIRECTORY.split("_")[1])
# We grep at which time the primary dynamics is finished.
	rangexmin       	= TIME_RESTART
	timebreak       	= timebreak + TIME_RESTART
	GNUPLOT_TIME_LABEL 	= "($1 + " + str(TIME_RESTART) + " )"        	# Time written in the file + the one at which the traj is restarted
	RESTART			= True						# For now only NX -> restarted with SHARC is implemented
										# SHARC restarted with NX is not yet implemented
else:
	RESTART			= False						# If it is not a restart
	TIME_RESTART		= 0.0
	TIME_END_OF_DYN		= 0.0
	GNUPLOT_TIME_LABEL 	= "1"						# Time aways written in the first column
# ---------------------------------------------------------------------------------------------- #

LABEL_MOLECULE  = TRAJECTORY_MODULES.GET_MOLECULE_LABEL(TEMPLATE_GEO)

if CALCULATION == "NX" and time_dyn > time_xyz or not os.path.isfile(PARAM_FILE.coordinate_file):	# The dynamics is saved in dyn.xyz, however otput xyz was necessary to extract coordinates
	TRAJECTORY_MODULES.MAKE_GEOMETRICAL_COORDINATES(TIMESTEP, TEMPLATE_GEO, LABEL_MOLECULE) 	# Recoupute the COORDINATES.out file
	#os.system("rm -f output.xyz")
elif CALCULATION == "SH" and time_dyn > time_xyz or not os.path.isfile(PARAM_FILE.coordinate_file):							
	TRAJECTORY_MODULES.MAKE_GEOMETRICAL_COORDINATES(TIMESTEP, TEMPLATE_GEO, LABEL_MOLECULE)		# Recoupute the COORDINATES.out file

# ---------------------------------------------------------------------------------------------- #

if rangexmax == 0.0:					#If a not particular time is given in input
	rangexmax = timebreak + 5# + (2.0 * timebreak / 100) #Use the time. The extra lenght is only for nice plots not ending with the end of the dynamics.
#Adjust the position of the label 1 (electronic states) and label 2 (coordinates)
positionlabel1 = "%5.3f,%i"   %(rangexmax - (rangexmax - rangexmin) / 1.6  , rangeymax)
positionlabel2 = "%5.3f,%i"   %(rangexmax - (rangexmax - rangexmin) / 10.0 , rangey2max)
# ---------------------------------------------------------------------------------------------- #

#Initialize the string 
GNUPLOT_SCRIPT = ''
#We write the fist part of the gnuplot script
GNUPLOT_SCRIPT += TRAJECTORY_MODULES.WRITE_HEAD_GP(outname, rangexmin, rangexmax, rangeymin, rangeymax, positionlabel1)

shadeofblue     = ["#084594","#2171B5","#9ECAE1","#C6DBEF"]
shadeofgreen    = ["#005A32","#238B45","#A1D99B","#C7E9C0"]

#We write the second part, containing the information to plot the electronic states
if CALCULATION == "NX":
	GNUPLOT_SCRIPT += TRAJECTORY_MODULES.WRITE_NX_STATE_GP(nstates,  STATE_LIST, scaling, GNUPLOT_TIME_LABEL, shadeofblue, shadeofgreen, "en.dat"                   , TIME_RESTART, RESTART)
if CALCULATION == "SH":
	GNUPLOT_SCRIPT += TRAJECTORY_MODULES.WRITE_SH_STATE_GP(nmstates, STATE_LIST,          GNUPLOT_TIME_LABEL, shadeofblue, shadeofgreen, "output_data/expec_MCH.out", TIME_RESTART, RESTART)

#We write the last part containing the geometrical coordinates and the breakline at time = timebreak
GNUPLOT_SCRIPT += TRAJECTORY_MODULES.WRITE_COORDS_AND_BREAKLINE(rangeymax, rangey2max, positionlabel2, timebreak, breakreason, INPUT_COORD, GNUPLOT_TIME_LABEL, LABEL_MOLECULE)
#We write the string into the file (that will remain in the folder)
with open(PARAM_FILE.gnuplot_file_traj, 'w') as GNUPLOT_SCRIPT_FILE:
	sys.stdout = GNUPLOT_SCRIPT_FILE	# Change the standard output to the file we created.
	print(GNUPLOT_SCRIPT)
# ---------------------------------------------------------------------------------------------- #
sys.stdout = original_stdout 				# Reset the standard output to its original value
os.system("gnuplot " + PARAM_FILE.gnuplot_file_traj)	# Write the png file running the gnuplot script
