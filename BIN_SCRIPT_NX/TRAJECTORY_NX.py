#!/usr/bin/env python3

import os
from os.path import isfile
import glob
import sys
import subprocess

sys.path.append('/ddn/home/fzzq22/CODE_AND_SCRIPT/PYTHON_COMMON_MODULE')

from NX_MODULES 	import GET_EXCITATION_ENERGY, SUBMIT_TRAJECTORIES, LABEL_TRAJ, GET_TIME_BASED_ON_D1
from TOOLS      	import sorted_nicely, GET_DATA
from TRAJECTORY_MODULES import GET_MOLECULE_LABEL, READING_PARAMETER_FILE
import PARAM_FILE

PWD 	= os.getcwd()

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def COPY_FILE(TRAJ_NAME, RESULT_FOLDER, FILE_TO_COPY, TIME_TRAJ_IS):
	os.system("cp " + PWD + "/" + FILE_TO_COPY + "  " + RESULT_FOLDER)				# Copy INPUT file for PLOT_TRAJ.py
	os.system("sed -i 's/traj1/" + TRAJ_NAME + "/' "  + RESULT_FOLDER + FILE_TO_COPY)		# We update the INPUT files with
	if "zoom" in FILE_TO_COPY:									# If it is the zoom INPUT we also modify the maxxrange and
# the minxrange. They will be maxxrange = TIME_TRAJ_IS and minxrange = TIME_TRAJ_IS - 100.0 to have a very nice plots. 
		if TIME_TRAJ_IS < 100:
			TIMEMIN	= 0.0
		else:
			TIMEMIN = TIME_TRAJ_IS - 100.0	
		os.system("sed -i '3s/0/" + str(TIMEMIN)      + "/' " + RESULT_FOLDER + FILE_TO_COPY)	# We update the INPUT files with minxrange.
		os.system("sed -i '4s/0/" + str(TIME_TRAJ_IS) + "/' " + RESULT_FOLDER + FILE_TO_COPY)   # We update the INPUT files with maxxrange.
	return

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def CHECK_RESTARTED_DYNAMICS_HPP(XMS_RESTART_FOLDER_NAME, SUMMARY_STRING):
	METHOD_USED, TIME_RESTART	= os.path.basename(os.path.normpath(XMS_RESTART_FOLDER_NAME)).split("_")[0], float(os.path.basename(os.path.normpath(XMS_RESTART_FOLDER_NAME)).split("_")[1])
	D1_FILE				= "/d1_" + str(TIME_RESTART) + "fs.tmp"
	D1_TIME_RESTART			= GET_DATA(XMS_RESTART_FOLDER_NAME + D1_FILE, 4)  # Extract the d1 value at the restart time
	SUMMARY_STRING			+= "\t RESTARTED AT : %8.2f fs with d1 : %s" %(TIME_RESTART, D1_TIME_RESTART)
	return SUMMARY_STRING

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def CHECK_REACTIVITY_HPP(RESULT_FOLDER, XMS_RESTART_FOLDER_NAME, SUMMARY_STRING, DATA_STRING):
	coordinate_file		= RESULT_FOLDER + '/' + PARAM_FILE.coordinate_file
	O_H_INTER_DISTANCE      = GET_DATA(coordinate_file, 3)	# Collect O--H distance
	C_O_DOUBLE_BOND         = GET_DATA(coordinate_file, 5)	# Collect C=O bond distance
	O_O_PEROXIDE_BOND	= GET_DATA(coordinate_file, 1)       # Collect O-O bond distance
	C_O_SINGLE_BOND         = GET_DATA(coordinate_file, 7)       # Collect C-O bond distance
	 
	if float(O_H_INTER_DISTANCE) > 1.8  and float(C_O_DOUBLE_BOND) > 1.6:		# Condition to observe non-radiative CI 
		SUMMARY_STRING 	+= "\t> NON-RADIATIVE CI <"
		DATA_STRING	+= "NRCI"
	elif float(O_O_PEROXIDE_BOND) > 1.8 and float(O_H_INTER_DISTANCE) >= 2.0:	# Condition to observe OH release
		SUMMARY_STRING 	+= "\t# OH DISSOCIATION  #"
		DATA_STRING     += "OHDISS"
	elif float(C_O_SINGLE_BOND) > 1.8   and float(O_H_INTER_DISTANCE)  < 2.0: 	# Condition to O2 release
		SUMMARY_STRING 	+= "\t# O2 DISSOCIATION  #"
		DATA_STRING     += "O2DISS"
	elif float(C_O_SINGLE_BOND) > 1.8   and float(O_H_INTER_DISTANCE) >= 2.0: 	# Condition to O2H release
		SUMMARY_STRING  += "\t# O2H DISSOCIATION #"
		DATA_STRING     += "O2HDISS"	
	elif float(O_H_INTER_DISTANCE) < 1.6 :                                		# Condition to have 1,5-Hshift
		SUMMARY_STRING  += "\t*   1,5 - Hshift   *"
		if not XMS_RESTART_FOLDER_NAME:
			print  ("*****  Remember to RESTART the ground state dynamics *****\n")
	return SUMMARY_STRING, DATA_STRING

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def CHECK_REACTIVITY_NRMECI(RESULT_FOLDER, SUMMARY_STRING, DATA_STRING):
	coordinate_file		= RESULT_FOLDER + '/' + PARAM_FILE.coordinate_file
	C_O_DOUBLE_BOND         = GET_DATA(coordinate_file, 1)       # Collect C=O bond distance
	if float(C_O_DOUBLE_BOND) > 1.6:          					# Condition to observe non-radiative CI
		SUMMARY_STRING  += "\t> NON-RADIATIVE CI <"
		DATA_STRING     += "NRCI"

	return SUMMARY_STRING, DATA_STRING

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def CHECK_REACTIVITY_BH3NH3(RESULT_FOLDER, SUMMARY_STRING, DATA_STRING):
	coordinate_file		= RESULT_FOLDER + '/' + PARAM_FILE.coordinate_file_to_use
	B_N_BOND         	= GET_DATA(coordinate_file, 1)       # Collect B-N bond distance
	if float(B_N_BOND) > 2.0:                                               
		SUMMARY_STRING  += "\t> B-N DISS < (%3.3f)" %(B_N_BOND)
		DATA_STRING     += "BNDISS"
	if not "BNDISS" in DATA_STRING: SUMMARY_STRING  += "\t\t\t"
	# We collect all 3 B-H and N-H bonds in two arrays
	LONGER_N_H_BOND		= 0;
	for index in range(2,5):
		N_H_BOND	= float(GET_DATA(coordinate_file, index))
		if N_H_BOND > LONGER_N_H_BOND: LONGER_N_H_BOND = N_H_BOND
		if N_H_BOND > 1.45:							# N-H bond for diss
			SUMMARY_STRING  += "\t> N-H DISS < (%3.3f)" %(N_H_BOND)  
			DATA_STRING     += "NHDISS"
	if not "NHDISS" in DATA_STRING:	SUMMARY_STRING	+= "\t\t\t"
	for index in range(2,5):
		B_H_BOND        = float(GET_DATA(coordinate_file, index + 3))
		if B_H_BOND > 1.50:							# B-H bond for diss
			SUMMARY_STRING  += "\t> B-H DISS < (%3.3f)" %(B_H_BOND)
			DATA_STRING     += "BHDISS"
	return SUMMARY_STRING, DATA_STRING

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def CHECK_RESTARTED_DYNAMICS_BH3NH3(RESTART_FOLDER_NAME, "", ""):
    METHOD_USED, TIME_RESTART       = os.path.basename(os.path.normpath(RESTART_FOLDER_NAME)).split("_")[0], float(os.path.basename(os.path.normpath(RESTART_FOLDER_NAME)).split("_")[1])
    CHECK_REACTIVITY_BH3NH3         
return SUMMARY_STRING


#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def TAIL_COORDINATES_FILE(RESULT_FOLDER, LINE):
	coord_file		= RESULT_FOLDER + "/" + PARAM_FILE.coordinate_file
	coord_file_to_use	= RESULT_FOLDER + "/" + PARAM_FILE.coordinate_file_to_use
	os.system("head -%i %s > %s" %(LINE, coord_file, coord_file_to_use))

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def CHECK_REACTIVITY(RESULT_FOLDER, TIME_TRAJ_IS, SUMMARY_STRING, DATA_STRING):
        # Here we have to check at which molecule we are dealing with. Depending on the molecule the geometrical coordinates can be     #
        # different and therefore, we have to adopt different procedure.                                                                #
        (binx, binx, binx, binx, binx, binx, binx, binx, binx, binx, TEMPLATE_GEO) = READING_PARAMETER_FILE("%s/%s" %(RESULT_FOLDER, PARAM_FILE.input_for_traj))
        WHICH_MOLECULE  = GET_MOLECULE_LABEL(TEMPLATE_GEO)
        # Now in WHICH_MOLECULE we have the label of the molecule we are dealing with. 
        if   WHICH_MOLECULE == "HPP":
                SUMMARY_STRING, DATA_STRING     = CHECK_REACTIVITY_HPP(RESULT_FOLDER, XMS_RESTART_FOLDER_NAME, SUMMARY_STRING, DATA_STRING)
                XMS_RESTART_FOLDER_NAME         = glob.glob(TRAJ_FOLDER  + "XMS-RESTART-12-9*")[0]      # Name in which the trajectory was restarted for HPP
                SUMMARY_STRING                  = CHECK_RESTARTED_DYNAMICS_HPP(XMS_RESTART_FOLDER_NAME, SUMMARY_STRING)
        elif WHICH_MOLECULE == "PYRONE":
                SUMMARY_STRING, DATA_STRING     = CHECK_REACTIVITY_NRMECI(RESULT_FOLDER, SUMMARY_STRING, DATA_STRING)
        elif WHICH_MOLECULE == "FORMALDEHYDE":
                SUMMARY_STRING, DATA_STRING     = CHECK_REACTIVITY_NRMECI(RESULT_FOLDER, SUMMARY_STRING, DATA_STRING)
        elif WHICH_MOLECULE == "ACROLEIN":
                SUMMARY_STRING, DATA_STRING     = CHECK_REACTIVITY_NRMECI(RESULT_FOLDER, SUMMARY_STRING, DATA_STRING)
        elif WHICH_MOLECULE == "OXALYL_fluoride":
                SUMMARY_STRING, DATA_STRING     = CHECK_REACTIVITY_NRMECI(RESULT_FOLDER, SUMMARY_STRING, DATA_STRING)
        elif WHICH_MOLECULE == "BH3NH3":
                TIME_D1,        D1              = GET_TIME_BASED_ON_D1(RESULT_FOLDER, MIN_TIME=0, MAX_TIME=TIME_TRAJ_IS)
                TAIL_COORDINATES_FILE(RESULT_FOLDER, TIME_D1 / 0.5 + 2)                 # 1 is the title 1 is time =0
                SUMMARY_STRING                  += "\tD1 %5.4f at TIME %5.1f fs" %(D1, TIME_D1)
                SUMMARY_STRING, DATA_STRING     = CHECK_REACTIVITY_BH3NH3(RESULT_FOLDER, SUMMARY_STRING, DATA_STRING)
        else: raise ValueError ('Value not recognized in %s' %(TEMPLATE_GEO))
        return SUMMARY_STRING, DATA_STRING

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def CHECK_TRAJECOTRY(TRAJ_NAME, TRAJ_FOLDER, RESULT_FOLDER):
	# The two string are initialized with the name of the trajectory.
	print  		(f"{PARAM_FILE.bcolors.OKBLUE}*****  The dynamics of %s is checked         *****\n{PARAM_FILE.bcolors.ENDC}" %(TRAJ_NAME.ljust(10))) 		# ljust add some empty spaces
	SUMMARY_STRING 	= str(TRAJ_NAME) + "\t"							# We add the name of the trajectory at the first column
	DATA_STRING	= str(TRAJ_NAME) + "\t"

	DATA_STRING	+= GET_EXCITATION_ENERGY(PWD + "/makedir.log", TRAJ_NAME) + "\t"	# We collect the excitation energy from the makedir.log file
	TIME_TRAJ_IS	 = GET_DATA(RESULT_FOLDER + "/en.dat", 0)				# Collect TRAJ time (record 0) from the en.dat file

# This section is dedicated in case the file DONT_ANALYZE is found in the RESULT folder. This file is created after that plots are generated	#
# and the excited state dynamics is fully stopped. In such cases, we do not want to plot them again. However, maybe we want restart the ground	#
# state dynamics. It will be suggested only in case a NON-RADIATIVE CI pattern is found at the end of the excited state output files.		# 

	if os.path.isfile(RESULT_FOLDER + '/' + PARAM_FILE.dont_analyze_file):			# If the file is present in the folder
		SUMMARY_STRING	+= "FINISHED AT %6.1f fs" %(float(TIME_TRAJ_IS)) 		# The plots will be not generated again
		if os.path.isfile(RESULT_FOLDER + '/' + PARAM_FILE.error_dyn):                 	# If the error file (due energy disc) is present in the folder
			SUMMARY_STRING	+= "\t ENERGY DISCONTINUITY"
			DATA_STRING 	+= "ENERGY_DISCONTINUITY"
		else:	SUMMARY_STRING, DATA_STRING = CHECK_REACTIVITY(RESULT_FOLDER, TIME_TRAJ_IS, SUMMARY_STRING, DATA_STRING)

# This section is dedicated in case the file DONT_ANALYZE is NOT found in the result folder. In this cases the dynamics is not stopped yet	#
# or at least it is just finished. In this last case, the file DONT_ANALYZE will be created, warning that is not necessary to analyze 		#
# the data anymore. In case the plot has never been generated, the input files are also copied in the REUSULT folder.				#		

	else:
		ERROR_SIGNAL		= False; STOP_SIGNAL		= False	# Logical varaibles to indicate if an error is find in the NX dynamics
		# Read from moldyn.log if there is an error
		try: 	ERROR_SIGNAL	= subprocess.check_output('grep "::ERROR::" %s/moldyn.log ' % (TRAJ_FOLDER), shell = True).decode('ascii')
		except:	pass
		# Read from moldyn.log if the dynamics is finished without errors
		try:	STOP_SIGNAL	= subprocess.check_output('grep "moldyn.pl: End of dynamics" %s/moldyn.log ' % (TRAJ_FOLDER), shell = True).decode('ascii')
		except:	pass
	        # IF THERE IS AN ERROR IN A TRAJECOTRY NOT ALREADY CHECKED
		if ERROR_SIGNAL:
			SUMMARY_STRING  += "*  ::ERROR::  *\t"
			DATA_STRING     += "ERROR"
		# JUST FINISHED TRAJECTORY! IT HAS TO BE PLOTTED AND ANALYZED
		elif STOP_SIGNAL:									# If the dynamics is just finished!
			print(TRAJ_NAME + "\t is just finished. It will be fully analyzed automatically.\n")
			COPY_FILE(TRAJ_NAME, RESULT_FOLDER, PARAM_FILE.input_for_traj, TIME_TRAJ_IS)	# We modify the two file changing name of the trajectories and the time
			COPY_FILE(TRAJ_NAME, RESULT_FOLDER, PARAM_FILE.input_for_zoom, TIME_TRAJ_IS)
			os.system("touch %s/%s" %(RESULT_FOLDER, PARAM_FILE.dont_analyze_file))		# We write the file to not analyze the folder again
			SUMMARY_STRING	+= "* JUST FINISHED *\t%8.2f fs"			%(float(TIME_TRAJ_IS))	
			os.chdir(RESULT_FOLDER)								# Enter in TRAJ*/RESULT FOLDER.
			os.system("%s %s" %(PARAM_FILE.plot_traj_script, PARAM_FILE.input_for_traj))	# RUN our script to generate trajectory plots.
			os.system("%s %s &>/dev/null" %(PARAM_FILE.plot_traj_script, PARAM_FILE.input_for_zoom))	# RUN our script to generate the trajectory of the last part of the dynamics.
			os.system('grep "D1 diagnostic for MP2:" ' + TRAJ_FOLDER + '/moldyn.log | awk \'{printf "%9.2f\\t%s\\n", counter/2, $5; counter++}\' > d1_values')
		# STILL RUNNING.
		else:										# Otherwise the dynamics is still running
			SUMMARY_STRING  += "   RUNNING   \t%8.2f fs"				%(float(TIME_TRAJ_IS))
			DATA_STRING     += "RUNNING"	
	return SUMMARY_STRING, DATA_STRING

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def main():
	
	print ("\n\n")
	CHOICE	= input("Do you want submit DYNAMICS? (Y or N)                            ")  

	if   CHOICE.upper() == "Y":
		if not isfile(PARAM_FILE.to_submit_file):					# If this file does not exist ww ask we want label the trajectory to submit
			# Labeling means to chose a subgroup of trajectory to submit based on random number generator
			labeling  = input("Do you want label the trajectory to submit ? (Y or N)            ")
			# If the user want to label trajectories then we ask the the variable to compute the probability: wanted_traj/total_traj
			# Higher is this probability (0 < p < 1) higher is the proportion sumitted vs not submitted
			if labeling.upper() == "Y":
				default_traj	= 10 
				wanted_traj	= input("How many trajectory you want? (%5.0f default) " %(default_traj) )
				if not wanted_traj: wanted_traj = 10		# Default value
				default_traj 	= 20+1
				total_traj	= input("How many trajectory in total? (%5.0f default) " %(default_traj) )
				if not total_traj:  total_traj  = default_traj		
				print ("Number of traj requested: " + str(wanted_traj) + " and number of total trajectories: " + str(total_traj))
				LABEL_TRAJ(PWD, wanted_traj, total_traj)
		SUBMIT_TRAJECTORIES(PWD)

	elif CHOICE.upper() == "N":
		print  ("*****************************************************************\n")
		print  ("*****             The dynamics will be checked		     *****\n")
		print  ("*****************************************************************\n")

		ALLNAME	= sorted_nicely(glob.glob("TRAJ*"))

		SUMMARY_FILE 	= open( PARAM_FILE.summury_file  , "w")
		DATA_FILE	= open( PARAM_FILE.traj_file, "w")
            D
		
		for TRAJ_NAME in ALLNAME:
			TRAJ_FOLDER	= PWD + "/" + TRAJ_NAME + "/" 
			RESULT_FOLDER	= TRAJ_FOLDER + "RESULTS/"
			if os.path.isdir(RESULT_FOLDER):				# If the result folder exist the trajectory had been submitted
				os.chdir(TRAJ_FOLDER)

				SUMMARY_STRING, DATA_STRING = CHECK_TRAJECOTRY(TRAJ_NAME, TRAJ_FOLDER, RESULT_FOLDER)

				SUMMARY_FILE.write(SUMMARY_STRING + "\n")
				DATA_FILE.write(DATA_STRING       + "\n")

		SUMMARY_FILE.close()
		DATA_FILE.close()      
	
	else:
		print  (" Chose Y or N, lower characters are accepted                     \n")
		main()


#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#

print ("*****************************************************************  ")
print (" This script allows you to submit the dynamics in NX or to check   ")
print (" the evolution of the trajectories. The program will automatically ")
print (" plots and summary of the dynamics                                 ")
print ("*****************************************************************  ")

main() 

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#          
