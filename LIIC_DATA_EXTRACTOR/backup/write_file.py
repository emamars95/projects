import config

def write_output(i,n_state,ex_data):
#If the first point is the FC write its energy in REF.FILE 
	if config.fc_choice == "Y": 
		R_FILE = open(config.REF_FILE, "w")
		R_FILE.write(str(config.fc_energy))	

	difference_au = config.s0_energy - config.fc_energy	#S0 - FC_S0 energy in Hartree
	difference_eV = difference_au * config.ev_conversion		#Conversion in eV
	config.O_FILE.write("%i \t %9.5f    " %(i, difference_eV))     #write in the position 1,1 of the table state-LIIC point, in position 1,2 the difference in S0 and FC point

	s = 0
	t = 0
	for j in range (0, n_state):                  #Firstly are printed the singlet (ground state already printed)       
		state_spin      = str(  ex_data[j * 2])
		value_eV        = float(ex_data[j * 2 + 1])
		if (state_spin == config.s_keyword and s < config.singlet_to_print - 1):    #The first singlet state is the ground state therefore -1 S state
			scaledenergy_eV = value_eV + difference_eV
			config.O_FILE.write("%9.5f    " %(scaledenergy_eV))
			s = s + 1

	if config.triplet_choice == "Y":
        #Secondly, if present, are printed the triplet. If state_spin is not present in the ex_data no state will be printed.
		for j in range (0, n_state):
			state_spin      = str(ex_data[j * 2 ])
			value_eV        = float(ex_data[j * 2 + 1 ])
			if (state_spin == config.t_keyword and t < config.triplet_to_print):
				scaledenergy_eV = value_eV + difference_eV
				config.O_FILE.write("%9.5f    " %(scaledenergy_eV))
				t = t + 1
	config.O_FILE.write("\n")

