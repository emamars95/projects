#!/usr/local/Cluster-Apps/python/3.6.8/bin/python3.6

#########################################################################################
#This program in python extract and convert energies from the most common 3rd party QC	#
#and give in output a file containing, along the column, singlets and triplets states 	#
#energies and, along the row, the LIIC poits. 						#
######################################################################################### 

import config
import init_subrutine


###########################################################################################################

init_subrutine.menu()
init_subrutine.set_up()

config.O_FILE      = open(config.OUTPUT_FILE, "w")

if (config.program     == "G09"):
	print("G09 interface will be used\n")
	import G09_interface
	config.typ_keyword  = ".log" 			#.log correspond to the output of G09
	if (config.calc_choice == "M06-2X" or config.calc_choice == "PBE0"):
		config.energy_keyword    = "SCF Done:" 	#Keyword to grep S0 energy 
		if(config.unrestricted_choice == "N"):
			config.s_keyword = "Singlet-"  #Keyword to extract singlets energy 
			config.t_keyword = "Triplet-"
			print("Keyword used to search for singlets '", config.s_keyword, "' and triplets '", config.t_keyword, "'")
			print("They are consistent with a restricted calculation using g09\n")
		if(config.unrestricted_choice == "Y"):
			print("Try to grep the electronic energy using their spin, in case values are missed check spin-contaminations for the missing states.")
			print("Treshold to assign singlet state S**2<0.5 and triplet states S**2>1.5" )
		G09_interface.TDDFT_extractor()
	if(config.calc_choice == "EOM-CCSD"):
		config.energy_keyword   = "E\(CORR\)="        #Keyword to grep S0 energy
		config.s_keyword = 'Singlet-A'
		config.t_keyword = 'Triplet-A'
		print("EOM-CCSD calculation chosen\n")
		print("Keyword used to search for singlets '", config.s_keyword, "' and triplets '", config.t_keyword, "'")
		G09_interface.EOM_CCSD_extractor()
	
elif (config.program     == "TURBOMOLE"):
	print("Turbomole interface will be used\n")

	import TurboMole_interface

	if   (config.calc_choice == "ADC2" or config.calc_choice == "CC2" or config.calc_choice == "CIS" or config.calc_choice == "CIS(D)" or config.calc_choice == "MP4"):
		config.typ_keyword	= "ricc2.out"			# Output file
		config.s_keyword        = "Energy:"                     # Excited state energy keyword

		if config.calc_choice   == "ADC2":
			config.energy_keyword   = "Final MP2 energy"    # MP2 energy keyword
			print("ADC(2) calculation chosen\n")
			TurboMole_interface.TURBO_extractor(record_s0 = 5, record_ex = 3, ex_table_flag = "")
		elif config.calc_choice == "CC2":
			config.energy_keyword   = "Final CC2 energy"    # CC2 energy keyword
			print("CC(2)  calculation chosen\n")
			TurboMole_interface.TURBO_extractor(record_s0 = 5, record_ex = 3, ex_table_flag = "CC2 excitation energies")
		elif config.calc_choice == "CIS":
			config.energy_keyword   = "Energy of reference wave function is"    # CIS energy keyword
			print("CIS/CCS calculation chosen\n")
			TurboMole_interface.TURBO_extractor(record_s0 = 6, record_ex = 3, ex_table_flag = "")
		elif config.calc_choice == "CIS(D)":
			config.energy_keyword   = "Final MP2 energy"    # MP2 energy keyword
			print("CIS(D)  calculation chosen\n")
			TurboMole_interface.TURBO_extractor(record_s0 = 5, record_ex = 9, ex_table_flag = "CIS\(D\) excitation energies")
		elif config.calc_choice == "MP4":
			config.energy_keyword   = "Final MP4 energy"    # MP4 energy keyword
			print("MP4 calculation chosen\n")
			TurboMole_interface.TURBO_extractor(record_s0 = 5, record_ex = None, ex_table_flag = "")

	elif (config.calc_choice == "PBE0TURBO"):
		config.typ_keyword      = "escf.out"                   	# Output file
		config.energy_keyword   = "Total energy:"    		# DTF energy keyword
		config.s_keyword        = "Excitation energy / eV"	# Excited state energy keyword
		print("TDA-DFT calculation chosen\n")
		TurboMole_interface.TURBO_extractor(record_s0 = 2, record_ex = 4, ex_table_flag = "")

if (config.program     == "BAGEL" or config.program     == "MOLPRO"):
	print("Bagel and Molpro interface will be used")
	import BAGELandMOLPRO_interface
	BAGELandMOLPRO_interface.energies()	 

config.O_FILE.close

