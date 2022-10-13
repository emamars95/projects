#!/usr/local/Cluster-Apps/python/3.6.8/bin/python3.6

import config

# ---------------------------------------------------------------------------------------------------------- #
def WRITE_LABELS(n_singlets, n_triplets):
	print("There will be written ", n_singlets, " singlet and ", n_triplets, " triplet excited states")
	config.O_FILE.write("LIIC point  ")                     # Print the header label
	for j in range(0, n_singlets + 1):
		config.O_FILE.write("S%i\t\t" %(j))
	if (n_triplets > 0):
		for j in range(1, n_triplets + 1):
			config.O_FILE.write("T%i\t\t" %(j))
	config.O_FILE.write("\n")
	return

# ---------------------------------------------------------------------------------------------------------- #
def SAVE_REF_ENERGY():
	R_FILE = open(config.REF_FILE, "w")
	R_FILE.write(str(config.scale_energy))
	R_FILE.close()						# Save the reference energy used in a permanent file
	return

# ---------------------------------------------------------------------------------------------------------- #
def WRITE_EXCITATIONS(n_state, ex_data, difference_eV):
	for j in range (0, n_state):                            # Firstly are printed the singlet ex. states (S0 already printed)
		if str(ex_data[j * 2]) == "SINGLET":		# Where the spin is stored
				scaledenergy_eV = difference_eV + float(ex_data[j * 2 + 1]) 	# Where the state energy is stored
				config.O_FILE.write("%9.5f\t" %(scaledenergy_eV))		# We write in the file the energy scaled in eV
	#Secondly, if present, are printed the triplet. If state_spin is not present in the ex_data no state will be printed.
	if config.triplet_choice == "Y":
		for j in range (0, n_state):
			if str(ex_data[j * 2]) == "TRIPLET":
				scaledenergy_eV = difference_eV + float(ex_data[j * 2 + 1])
				config.O_FILE.write("%9.5f\t" %(scaledenergy_eV))
	return 

# ---------------------------------------------------------------------------------------------------------- #
def write_output(i, ex_data, n_singlets, n_triplets):
	n_state = n_singlets + n_triplets

	#If the first point is the FC write its energy in REF.FILE 
	if (i == config.i_point):
		WRITE_LABELS(n_singlets, n_triplets)
		SAVE_REF_ENERGY()
	if config.s0_energy == "MISSING":				# The values for such point is not found (problem in convercence!)
		print("Warning! Point ", i, "has not output. Check the calculation!\n") # And we print a error message	
		config.O_FILE.write("\n")				# We skip the line 

	else:								# The value is found correctly

		difference_au = config.s0_energy - config.scale_energy	# S0 - S0 energy (of the point) in Hartree
		difference_eV = difference_au * config.ev_conversion	# Conversion in eV

		config.O_FILE.write("%i\t%9.5f\t" %(i, difference_eV))      

		if n_state > 0:
			WRITE_EXCITATIONS(n_state, ex_data, difference_eV)
		else:
			print("Warning! Point ", i, "has not the excitation enegies. No problem in case of GS calculations.")
		config.O_FILE.write("\n")
