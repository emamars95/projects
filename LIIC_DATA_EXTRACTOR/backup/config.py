#!/usr/bin/env python3

#DEFAULT VALUES FOR INPUT CHOICEs
calc_choice	= "B"		#TYPE OF CALCULATION
fc_choice 	= "Y"		#0TH POINT IS FC (USED TO PLOT)
triplet_choice	= "N"		#IN THE CALCULATION ARE PRESENT TRIPLETS? Needed to fix keyword for extracting data

n_point          = 34           #TOTAL NUMBER OF POINTS present in the LIIC (starting from zero)
singlet_to_print = 3            #NUMBER OF STATES THAT HAVE TO BE PRINTED AMONG ALL THOSE PRESENT
triplet_to_print = 3

OUTPUT_FILE     = "plotEnergy"  #OUTPUT FILE WITH ALL STATES
O_FILE          = open(OUTPUT_FILE, "w")
REF_FILE        = "FCenergy"    #FC S0 ENERGY. IF fc_choice = "N" THE FILE MUST BE PRESENT

ev_conversion	= float(27.2114)#CONVERSION CONSTANTS

################################################

#DEFAUL VALUES

fc_energy 	= 0.0		
typ_keyword	= ".log"	#keyword for output file, g09 .log, Bagel-MOLPRO .out
s0_energy 	= 0.0
energy_keyword 	= "SCF Done:"	#DEFAULT OF G09
s_keyword 	= "Singlet-A"	#DEFAULT OF G09
t_keyword 	= ""		
unrestricted_choice = "N"
