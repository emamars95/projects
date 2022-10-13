#!/usr/local/Cluster-Apps/python/3.6.8/bin/python3.6
import config
import write_file

import os
import glob
import re

def TDDFT_extractor():
	for i in range(config.i_point, config.n_point, config.step):
		ex_data = []								
		n_singlets = 0				                             		#Total number of state is conted automatically 
		n_triplets = 0

		FILE_NAME = glob.glob("*_" + str(i) + str(config.typ_keyword))[0]	 	#config.typ_keyword=.log	

		for line in open(FILE_NAME):                  	 		#Look in the file line
			match = re.findall(config.energy_keyword, line)		#Find the record containing the S0 Energy in A.U
			if match:                               		#if match is not null
				config.s0_energy = float(line.split()[4])      	#Take the 4-th record and save it as so ground state energy (always singlet)

				if   (config.usepoint == "Y" and i == config.index_point_to_scale):
					config.scale_energy	= config.s0_energy
					print("S0 energy read used to scale:  ", config.scale_energy, ". It has been read from the ", config.index_point_to_scale, "-th point")

			if   (config.unrestricted_choice == "N"):
				matchs = re.findall(config.s_keyword, line)    		#Excitation energies singlets	
				if matchs:
					n_singlets += 1
					ex_data.append("SINGLET")    			#Keep records: [3] -> spin     [4] ->  eV Energy
					ex_data.append(line.split()[4])

				matcht = re.findall(config.t_keyword, line)    		#Excitation energies triplets
				if (matcht and config.triplet_choice == "Y"):
					n_triplets += 1
					ex_data.append("TRIPLET")
					ex_data.append(line.split()[4])

			elif (config.unrestricted_choice == "Y"):	
				match_ex = re.findall("Excited State", line)		#Due spin contamination there is not a proper well defined spin for each state
				if match_ex:
					multiplicity = float(line.split()[9].split("=")[1]) #<S**2>=3.0 -> ['<S**2>','3.0']
					if multiplicity < 0.5:
						n_singlets += 1
						ex_data.append("SINGLET")
						ex_data.append(line.split()[4])
					if multiplicity > 1.5:
						n_triplets += 1
						ex_data.append("TRIPLET")
						ex_data.append(line.split()[4])	
		if len(ex_data) == 0:		# This can happen in unrestricted calculations. In case the state are too contaminated nor singlet/triplet state can be defined.
			ex_data = ["MISSING"] 
		write_file.write_output(i, ex_data, n_singlets, n_triplets)

def EOM_CCSD_extractor():
	for i in range(config.i_point, config.n_point, config.step):
		ex_data = [];	n_singlets = 0;	n_triplets = 0; FLAG = False
	
		FILE_NAME   = glob.glob("*_" + str(i) + str(config.typ_keyword))[0]

		for line in open(FILE_NAME):
			match_flag = re.findall("EOM-CCSD transition properties", line)
			if match_flag:
				FLAG = True

			match = re.findall(config.energy_keyword, line)         # Find the record containing the S0 Energy in A.U. 
			if match:                                      		# If match is not null 
				config.s0_energy = float(line.split()[3])       # Take the 3-th record and save it as so ground state energy (always singlet)
				if(config.usepoint == "Y" and i == config.index_point_to_scale):
					config.scale_energy     = config.s0_energy

			matchs = re.findall(config.s_keyword, line)         	# Find the record containing the excitation Energy in A.U.
			if matchs and FLAG:
				n_singlets += 1
				ex_data.append("SINGLET")                
				ex_data.append(line.split()[4])

		write_file.write_output(i, ex_data, n_singlets, n_triplets)
