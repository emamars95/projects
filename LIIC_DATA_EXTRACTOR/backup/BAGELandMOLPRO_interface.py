#!/usr/bin/env python3

import config
import write_file

import glob
import re
import os


def energies():
	cmd_make = ""
	for i in range(0, config.n_point):
		if (config.calc_choice == "C"):
			cmd_make = "sed '/ci vector, state   0/q' *liic*_" + str(i) + ".out | tail -" + str(config.singlet_to_print + 2) + "| head -" + str(config.singlet_to_print) + "| awk '{print $4}' > " + str(i) + ".out_tmp"
		if (config.calc_choice == "D"):
			cmd_make = "grep 'CASPT2 energy : state' *liic*_" + str(i) + ".out | awk '{print $7}' > " + str(i) + ".out_tmp"
		if (config.calc_choice == "E"):
			cmd_make = "grep 'MS-CASPT2 energy : state' *liic*_" + str(i) + ".out | awk '{print $7}' > " + str(i) + ".out_tmp"
		if (config.calc_choice == "F"):
			cmd_make = "grep 'MCSCF STATE' *liic*_" + str(i) + ".out  | grep 'Energy' | awk '{print $5}' > " + str(i) + ".out_tmp"
		if (config.calc_choice == "G"):
			cmd_make = "grep 'RSPT2 STATE' *liic*_" + str(i) + ".out  | grep 'Energy' | awk '{print $5}' > " + str(i) + ".out_tmp"

		os.system(cmd_make)					
		n_state = 0
		ex_data = []

		for FILE_NAME in glob.glob(str(i) + ".out_tmp"):		#FILE are the tmp file containing the energy in AU of all states
			FILE    = open(FILE_NAME, "r")       
			for line in FILE:
				ex_data.append( str(config.s_keyword))
				ex_data.append( float(line))        
				n_state = n_state + 1 

			if   (config.fc_choice == "Y" and i == 0):	
				config.fc_energy = ex_data[1]
			elif (config.fc_choice == "N" and i == 0):
				R_FILE    = open(config.REF_FILE, "r")       	 	#Open file containing FC energy for scailing
				config.fc_energy = float(R_FILE.readline())	#Read the energy asociated with the FC reference
				R_FILE.close()
		config.s0_energy = ex_data[1]
		
		for k in range(0, n_state):
			ex_data[k * 2 + 1] = (ex_data[k * 2 + 1] - config.s0_energy) * config.ev_conversion
		ex_data = ex_data[2 : n_state * 2 ]	
		#Keep only the excitation energies in Ev and discard the first two records associated with 'Singlet-A' and S0 energy 
		#write the file collected, n_state -1 (we exclude the ground state). In G09 we will give to the subroutine only the excitation energies.
		write_file.write_output(i, n_state - 1 ,ex_data)
		cmd_rm = "rm -rf " + str(i) + ".out_tmp"
		os.system(cmd_rm)
	return()
