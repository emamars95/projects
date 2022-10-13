#!/usr/local/Cluster-Apps/python/3.6.8/bin/python3.6

import config
import write_file

import os
import glob
import re
import warnings

def Initialization():
	# In ESCF the same keyword grep also the total energy of excited states so it is necessary to take only the fist instance. We add GOT_s0.
	ex_data 	= []; n_singlets 	= 0; n_triplets 	= 0; GOT_s0 	= False; ex_table 	= False
	return ex_data, n_singlets, n_triplets, GOT_s0, ex_table

def D1_diagnostic(i, FILE_NAME):
	# Get the d1 diagnostic. In case of cc2 in the output file 2 instances are found. The first is associated with MP2 d1 diagnostic (discarded) while the second one is associated with the cc2 d1 diagnostic (saved in the file d1_values).
	cmd = 'grep "D1 diagnostic" \'' + str(FILE_NAME) + '\' | tail -1 | awk \'{print ' + str(i) + ',  $5}\' >> d1_values ' 
	os.system(cmd)

def READ_S0(FILE_NAME, record_s0):
	# We open the output file and we look at the S0 energy and then at the excitation energies.
	with open(FILE_NAME, 'r') as FILE:
		for line in FILE:		                                    	# Look in the file line by line
			match 		= re.findall(config.energy_keyword, line)	# Find the record containing the S0 Energy in A.U
			if match:
				s0_energy 	= float(line.split()[record_s0])       	# Take the record_s0-th record and save it as so ground state energy (always singlet)	
				break
	return s0_energy

def FIND_ENERGY_TO_SCALE(record_s0):
	# config.typ_keyword=ricc2.out or escf.out depending on the calculation chosen
	FILE_NAME 		= glob.glob( "*_%s/%s" %(config.index_point_to_scale, str(config.typ_keyword)) )[0]
	config.scale_energy	= READ_S0(FILE_NAME, record_s0)
	print("S0 energy read used to scale:  ", config.scale_energy, ". It has been read from the ", config.index_point_to_scale, "-th point")
	return

def TURBO_extractor(record_s0, record_ex, ex_table_flag): 			# to get ground  state energy and excited state energies
	os.system("rm -f d1_values")						# Remouve the file if it exist to create a fresh one
	FIND_ENERGY_TO_SCALE(record_s0)

	for i in range(config.i_point, config.n_point, config.step):
		# Initialization of the variables at each point of the LIIC
		ex_data , n_singlets, n_triplets , GOT_s0, ex_table = Initialization()
		# Take the name of the output file using the index of the LIIC point i
		FILE_NAME = glob.glob("*_" + str(i) + "/" + str(config.typ_keyword))[0]  	# config.typ_keyword=ricc2.out or escf.out depending on the calculation chosen       
		# Take D1 diagnostic. 
		if (config.calc_choice == "ADC2" or config.calc_choice == "CC2" or config.calc_choice == "CIS(D)"):   	
			D1_diagnostic(i, FILE_NAME)
		# We open the output file and we look at the S0 energy and then at the excitation energies. 
		FILE	= open(FILE_NAME, 'r')
		for line in FILE:   	                                	# Look in the file line by line
			match = re.findall(config.energy_keyword, line)        	# Find the record containing the S0 Energy in A.U
			# Look for S0 energy. Each calculation has a different record and pattern to look for the S0 energy. 
			if match and not GOT_s0:                               	# If match is not null and not found before in the file 
				GOT_s0 		 = True				# We do not look at S0 energy anymore in the file
				config.s0_energy = float(line.split()[record_s0])	# Take the record_s0-th record and save it as so ground state energy (always singlet)
			elif match and GOT_s0: warnings.warn("Founded two instance matching S0 values in the same file. Modify script if necessary.")
			# Turbo mole usually print a table with the summary of the excitation energy 
			tablematch = re.findall(ex_table_flag, line)            # Find the table containing the excitation energy
			# print(tablematch,ex_table_flag)
			if tablematch: ex_table	= True				# We found the table paring line by line the file
			# Look for the excitation energy for all calculations but CIS(D) and MP4 (in the last calculation we do not have excitation energies)
			if not config.calc_choice == "CIS(D)" and not config.calc_choice == "MP4":
				matchs = re.findall(config.s_keyword, line)   	# Excitation energies
				if matchs and n_singlets < config.n_singlets:	# Before we take the singlets
					n_singlets += 1 
					ex_data.append("SINGLET")
					ex_data.append(line.split()[record_ex])	# Extract record_ex
				# If we have to get the excitation of other spin state they will be printed after in the turbomole file
				elif (matchs and n_singlets >= config.n_singlets and config.triplet_choice == "Y") :
					n_triplets += 1				# And then the triplets
					ex_data.append("TRIPLET")
					ex_data.append(line.split()[record_ex])
			# Look for the excitation energy for CIS(D) calculation
			elif config.calc_choice == "CIS(D)" and ex_table:
				try:								# not all line has record 3 aviable there try before
					if line.split()[3] == "1":		   		# Record 3 is the multiplicity
						n_singlets += 1
						ex_data.append("SINGLET")
						ex_data.append(line.split()[record_ex])         # Extract record_ex
					if line.split()[3] == "3":
						n_triplets += 1
						ex_data.append("TRIPLET")
						ex_data.append(line.split()[record_ex])
				except:	
					pass							# Pass if it rises an error
		FILE.close()
		# print (ex_data)
		write_file.write_output(i, ex_data, n_singlets, n_triplets)
	return
