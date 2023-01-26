#!/usr/local/Cluster-Apps/python/3.6.8/bin/python3.6

import config
import write_file

import glob
import re
import os

def WRITE_FILES(TMP_FILE_NAME, OUT_FILE_NAME):
	if (config.calc_choice == "HF"):
		cmd_make = "sed '/SCF iteration converged/q' " + OUT_FILE_NAME + " | tail -3 | head -1 | awk '{print $2}' > " + TMP_FILE_NAME
	if (config.calc_choice == "CASSCF"):
		cmd_make = "sed '/ci vector, state   0/q' "   + OUT_FILE_NAME + " | tail -" + str(config.singlets + 2) + "| head -" + str(config.singlets) + "| awk '{print $4}' > " + TMP_FILE_NAME
	if (config.calc_choice == "CASPT2"):
		cmd_make = "grep ' CASPT2 energy : state' "   + OUT_FILE_NAME + " | awk '{print $7}' > " + TMP_FILE_NAME
	if (config.calc_choice == "XMSPT2"):
		cmd_make = "grep 'MS-CASPT2 energy : state' " + OUT_FILE_NAME + " | awk '{print $7}' > " + TMP_FILE_NAME
	if (config.calc_choice == "CASSCF_MOLPRO"):
		cmd_make = "grep 'MCSCF STATE ' "              + OUT_FILE_NAME + " | grep 'Energy' | awk '{print $5}' > " + TMP_FILE_NAME
		# If we have more than 9 states molpro write the nstate all togheter with the string to find.
		cmd_make += " && grep 'MCSCF STATE1' "         + OUT_FILE_NAME + " | grep 'Energy' | awk '{print $4}' >> " + TMP_FILE_NAME 
	if (config.calc_choice == "XMSPT2_MOLPRO"):
		cmd_make = "grep 'RSPT2 STATE' "              + OUT_FILE_NAME + " | grep 'Energy' | awk '{print $5}' > " + TMP_FILE_NAME
	if (config.calc_choice == "MRCI_MOLPRO"):
		cmd_make = "grep 'MRCI STATE' "               + OUT_FILE_NAME + " | grep 'Energy' | awk '{print $5}' > " + TMP_FILE_NAME
	# TMP file is created for each point i of the LIIC
	os.system(cmd_make)
	return

def READ_FILES(TMP_FILE_NAME):
	n_singlets  	= 0;        n_triplets  = 0;        ex_data = []
	FILE 		= open(TMP_FILE_NAME, "r")
	for line in FILE:
		ex_data.append("SINGLET")                       # We write the states
		ex_data.append(float(line))                     # We gather the energy of each state
		n_singlets += 1
	FILE.close()
	return n_singlets, n_triplets, ex_data

def FIND_ENERGY_TO_SCALE():
	TMP_FILE_NAME = "scale_file.out_tmp"; OUT_FILE_NAME = "*_%s.out" %(str(config.index_point_to_scale))
	WRITE_FILES(TMP_FILE_NAME, OUT_FILE_NAME)
	n_singlets, n_triplets, ex_data 	= READ_FILES(TMP_FILE_NAME)
	config.scale_energy			= ex_data[1]
	print("S0 energy read used to scale:  ", config.scale_energy, ". It has been read from the ", config.index_point_to_scale, "-th point")	
	return 

def energies():
	FIND_ENERGY_TO_SCALE()
	for i in range(config.i_point, config.n_point, config.step):
		TMP_FILE_NAME = str(i) + ".out_tmp";	OUT_FILE_NAME = "*_" + str(i) + ".out"
		#OUT_FILE_NAME = "*out.1_" + str(i); 	#OUT_FILE_NAME = "*.out"

		WRITE_FILES(TMP_FILE_NAME, OUT_FILE_NAME)	
	
		if (os.stat(TMP_FILE_NAME).st_size == 0):			# Check if the file is empty (calculation did not converge properly)
			config.s0_energy = "MISSING"				# Send an error to the program
		else:								# If the file is not empty (the point converged)
			n_singlets, n_triplets, ex_data	= READ_FILES(TMP_FILE_NAME)
			config.s0_energy = ex_data[1]
			for k in range(0, n_singlets):
				# The excitation energy are converted
				ex_data[k * 2 + 1] = (ex_data[k * 2 + 1] - config.s0_energy) * config.ev_conversion
			ex_data = ex_data[2 : n_singlets * 2 ]
# -----------------------------------------------------------------------------------------------------	#
# Keep only the excitation energies in Ev and discard the first two records associated with 'Singlet-A'	# 
# and S0 energy write the file collected, n_state -1 (we exclude the ground state). In G09 we will give	#
# to the subroutine only the excitation energies.							#
# ----------------------------------------------------------------------------------------------------- #
		write_file.write_output(i, ex_data, n_singlets - 1, n_triplets)
		cmd_rm = "rm -rf " + TMP_FILE_NAME; os.system(cmd_rm)   #Remove tmp file
	return
