#!/usr/bin/env python3

#########################################################################################
#This program in python extract and convert energies from the most common 3rd party QC	#
#and give in output a file containing, along the column, singlets and triplets states 	#
#energies and, along the row, the LIIC poits. 						#
######################################################################################### 

import config
import init_subrutine


###########################################################################################################

init_subrutine.menu()
init_subrutine.choice()

config.O_FILE      = open(config.OUTPUT_FILE, "w")

if (config.calc_choice == "A" or config.calc_choice == "B" or config.calc_choice == "H" or config.calc_choice == "I"):
	print("G09 and ADC(2) interface will be used")
	import G09andADC2_interface
	
	if (config.calc_choice == "A" or config.calc_choice == "B" or config.calc_choice == "I"):
		config.typ_keyword  = ".log" #.log correspond to the output of G09
		if (config.calc_choice == "A" or config.calc_choice == "B"):
			config.energy_keyword   = "SCF Done:"   #Keyword to grep S0 energy 
			if(config.unrestricted_choice == "N"):
				config.s_keyword = "Singlet-A" 
				config.t_keyword = "Triplet-A"
			else:
				config.s_keyword = "1.000-A" 
				config.t_keyword = "3.000-A"
		if(config.calc_choice == "I"):
			config.s_keyword = 'Singlet-?Sym'
			config.t_keyword = 'Triplet-?Sym'
	
	elif (config.calc_choice == "H"):
		config.typ_keyword	= "ricc2.out"	#Outfile for adc(2)	
		config.energy_keyword	= "Final MP2 energy"	#MP2 energy keyword
		config.s_keyword = "Energy:"
	G09andADC2_interface.G09andADC2_energies()		

if (config.calc_choice == "C" or config.calc_choice == "D" or config.calc_choice == "E" or config.calc_choice == "F" or config.calc_choice == "G"):
	print("Bagel and Molpro interface will be used")
	import BAGELandMOLPRO_interface
	BAGELandMOLPRO_interface.energies()	 

config.O_FILE.close

