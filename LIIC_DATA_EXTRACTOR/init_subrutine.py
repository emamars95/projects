#!/usr/local/Cluster-Apps/python/3.6.8/bin/python3.6

from os import path
import sys
import config
import glob
import re

sys.path.append('/ddn/home/fzzq22/CODE_AND_SCRIPT/PYTHON_COMMON_MODULE')
from TOOLS      import sorted_nicely


#########################################################################################################

#Main menu to questioning about probram and electronic structure method used. 
def menu():
      print("\n\n   ************ MAIN MENU ************** \n")
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
