#!/usr/bin/env python3

import config

#########################################################################################################

#Main menu to questioning about probram and electronic structure method used. 
def menu():
      print("\n\n   ************ MAIN MENU ************** \n")
      choice = input("""
   A: M06-2X         calculation
   B: PBE0           calculation
   C: CASSCF BAGEL   calculation
   D: CASPT2 BAGEL   calculation
   E: XMSPT2 BAGEL   calculation
   F: CASSCF MOLPORO calculation
   G: XMSPT2 MOLPORO calculation
   H: ADC(2) TURBO   calculation 
   I: EOM-CCSD G09   calculation
   Q: Quit  

   Please enter your choice: """)

      if choice == "A" or choice =="a":
          config.calc_choice = "A"
      elif choice == "B" or choice =="b":
          config.calc_choice = "B"
      elif choice == "C" or choice =="c":
          config.calc_choice = "C"
      elif choice == "D" or choice =="d":
          config.calc_choice = "D"
      elif choice == "E" or choice =="e":
          config.calc_choice = "E"
      elif choice == "F" or choice =="f":
          config.calc_choice = "F"
      elif choice == "G" or choice =="g":
          config.calc_choice = "G"
      elif choice == "H" or choice =="H":
          config.calc_choice = "H"
      elif choice == "I" or choice =="I":
          config.calc_choice = "I"
      elif choice=="Q" or choice=="q":
          sys.exit
      else:
          print("You must only select either A, B, C, D, E, F, G, H, I or Q.")
          print("Please try again")
          menu()
      print("\n")
      return()

#########################################################################################################

def choice():
	print("   Is the first point of the LIIC the FC?")
	print("   If Y its energy will be used to scale all the other energies of the LIIC")
	print("   If N it is expected the FCenergy file in the pwd folder")
	fc_choice = input("   Make a choice: Y or N:    ")
	if   (fc_choice == "y" or fc_choice == "Y"):
        	config.fc_choice = "Y"
	elif (fc_choice == "n" or fc_choice == "N"):
        	config.fc_choice = "N"
	else :
		print ("   I will use the " + str(config.fc_choice) + " as default choice")
	print("\n")
	print("   Is the calculation include triplet?")
	triplet_choice = input("   Make a choice: Y or N:  ")
	if   (triplet_choice == "y" or triplet_choice == "Y"):
        	config.triplet_choice = "Y"
	elif (triplet_choice == "n" or triplet_choice == "N"):
        	config.triplet_choice = "N"
	else:
		print ("   I will use the " + str(config.triplet_choice) + " as default choice")
	print("\n")	
	config.singlet_to_print = input("   How many SINGLET States do you want print among those calculated:  ")
	config.singlet_to_print = int(config.singlet_to_print)

	print("\n")

	if   (triplet_choice == "y" or triplet_choice == "Y"):
		config.triplet_to_print = input("   How many TRIPLET States do you want print among those calculated:  ")
		config.triplet_to_print = int(config.triplet_to_print)
	print("\n")

	if (config.calc_choice == "A" or config.calc_choice == "B"):
		unrestricted_choice = input("Is the wavefunction unrestricted?  ")
		if   (unrestricted_choice == "y" or unrestricted_choice == "Y"):
			config.unrestricted_choice = "Y"
		elif (unrestricted_choice == "n" or unrestricted_choice == "N"):
			config.unrestricted_choice = "N"
		else:
			print ("   I will use the " + str(config.unrestricted_choice) + " as default choice")
	print("\n")
	return()
#########################################################################################################	
