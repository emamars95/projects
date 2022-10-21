#!/usr/bin/env python3

from os import path
import sys
import config as config
import glob
import re

sys.path.append('/ddn/home/fzzq22/CODE_AND_SCRIPT/PYTHON_COMMON_MODULE')
from TOOLS      import sorted_nicely



def parsing(parameterfile):
    list = {}
    with open(parameterfile) as f:
        for line in f:
            (key, val) = line.split()[':']
            list[str(key)] = val
    return 

# Main menu #
def menu():
    print("\n\n   ************ MAIN MENU ************** \n")
    choice_p   = input('''
    A 
    
    ''')



 
 
      choice = input("""
   A: M06-2X   G09     calculation
   B: PBE0     G09     calculation
   C: EOM-CCSD G09     calculation
   D: CASSCF   BAGEL   calculation
   E: CASPT2   BAGEL   calculation
   F: XMSPT2   BAGEL   calculation
   G: CASSCF   MOLPRO  calculation
   H: XMSPT2   MOLPRO  calculation
   I: MRCI     MOLPRO  calculation
   L: ADC(2)   TURBO   calculation
   M: CC2      TURBO   calculation
   N: CIS/CCS  TURBO   calculation
   O: CIS(D)   TURBO   calculation
   P: MP4      TURBO   calculation
   R: TDA-PBE0 TURBO   calculation
   HF:HF       BAGEL   calculation
   Q: Quit  

   Please enter your choice: """)

      if  choice.upper() == "A":
          config.calc_choice = "M06-2X"
          config.program     = "G09"
      elif choice.upper() == "B":
          config.calc_choice = "PBE0"
          config.program     = "G09"
      elif choice.upper() == "C":
          config.calc_choice = "EOM-CCSD"
          config.program     = "G09"
      elif choice.upper() == "HF":
          config.calc_choice = "HF"
          config.program     = "BAGEL"
      elif choice.upper() == "D":
          config.singlets = int(input("Insert the number of singlet computed at CASSCF level of theory:   "))
          config.calc_choice = "CASSCF"
          config.program     = "BAGEL"
      elif choice.upper() == "E":
          config.calc_choice = "CASPT2"
          config.program     = "BAGEL"
      elif choice.upper() == "F":
          config.calc_choice = "XMSPT2"
          config.program     = "BAGEL"
      elif choice.upper() == "G":
          config.calc_choice = "CASSCF_MOLPRO"
          config.program     = "MOLPRO"
      elif choice.upper() == "H":
          config.calc_choice = "XMSPT2_MOLPRO"
          config.program     = "MOLPRO"
      elif choice.upper() == "I":
          config.calc_choice = "MRCI_MOLPRO"
          config.program     = "MOLPRO"
      elif choice.upper() == "L":
          config.calc_choice = "ADC2"
          config.program     = "TURBOMOLE"
      elif choice.upper() == "M":
          config.calc_choice = "CC2"
          config.program     = "TURBOMOLE"
      elif choice.upper() == "N":
          config.calc_choice = "CIS"
          config.program     = "TURBOMOLE"
      elif choice.upper() == "O":
          config.calc_choice = 'CIS(D)' 
          config.program     = "TURBOMOLE"
      elif choice.upper() == "P":
          config.calc_choice = 'MP4'
          config.program     = "TURBOMOLE"
      elif choice.upper() == "R":
          config.calc_choice = "PBE0TURBO"
          config.program     = "TURBOMOLE"
      elif choice.upper() =="Q":
          sys.exit()
      else:
          print("You must only select either A, B, C, D, E, F, G, H, I, L, M, N, O, P, R or Q.")
          print("Please try again")
          menu()
      return()

#########################################################################################################
def init_point():
	try:
		ALLNAME         = sorted_nicely(glob.glob("geom_*"))
		config.i_point  = int(re.sub("[^0-9]", "", ALLNAME[0]))
	except:
		config.i_point  = 0
		print("First point is set to ", config.i_point)
	config.index_point_to_scale = config.i_point
	return

#########################################################################################################
def set_up():
	init_point()
	n_point = input ("\n\tHow many point you have you your LIIC?\t\t\t\t\t")
	if n_point:
		config.n_point = int(n_point) + config.i_point + 1
	else:
		print  ("\n\tIt is mandatory to provide the number of points for the LIIC\n\n")
		set_up()

	step 	= input("\n\tStep between two consecutive points?\t\t\t\t\t")
	if step:
		config.step    	= int(step)
	else:
		config.step	= 1
		print  ("\tThe step between two consecutive points will be\t\t\t\t", config.step)

	usepoint	= input ("\n\tDo you want use a point of the LIIC to scale the enegies (Y/N)?\t\t")
	if usepoint.upper() == "Y":
		index_point_to_scale	= input ("\tWhich point do you want to use to scale the energies along the LIIC?\t")
		if index_point_to_scale:
			config.index_point_to_scale	= int(index_point_to_scale)
		print("\tThe S0 energy of the ", config.index_point_to_scale, "-th point will be used" )
		config.usepoint	= "Y"
	elif usepoint.upper() == "N":
		try:
			R_FILE 			= open(config.REF_FILE, "r")		#Open file containing FCenergy for scailing
			config.scale_energy 	= float(R_FILE.readline())		#Read the S0 energy of the reference
			R_FILE.close()
			print("\tThe scale energy is ", config.scale_energy, " read from the file ", config.REF_FILE)
		except IOError:
        		print("Could not open file! Check if the file ", config.REF_FILE, " exists in the current folder")
		config.usepoint = "N"
	else :
		print ("\tI will read the S0 energy from point " + str(config.index_point_to_scale) + " as default choice")


	triplet_choice = input("\n\tIs the calculation include triplet(Y/N)?\t\t\t\t")
	if   triplet_choice.upper() == "Y":
        	config.triplet_choice = "Y"
	elif triplet_choice.upper() == "N":
        	config.triplet_choice = "N"
	else:
		print ("\tI will use the " + str(config.triplet_choice) + " as default choice")

	if (config.calc_choice == "M06-2X" or config.calc_choice == "PBE0"):
		unrestricted_choice = input("\n\tIs the wavefunction unrestricted?  ")
		if   unrestricted_choice.upper() == "Y":
			config.unrestricted_choice = "Y"
		elif unrestricted_choice.upper() == "N":
			config.unrestricted_choice = "N"
		else:
			print ("\tI will use the " + str(config.unrestricted_choice) + " as default choice\n")

	if (config.program     == "TURBOMOLE" and not config.calc_choice == 'MP4'):
		n_singlets =  input("\n\tHow many SINGLET EXCITED states do you have computed?\t\t\t")
		config.n_singlets = int(n_singlets)
	print("\n   ************ END  MENU ************** \n")

	return()

#########################################################################################################	


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
