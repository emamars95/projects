#!/usr/local/Cluster-Apps/python/3.6.8/bin/python3.6

#DEFAULT VALUES FOR INPUT CHOICEs
program		= ""		# MAIN PROGRAM
calc_choice	= ""		# TYPE OF CALCULATION
usepoint	= "Y"
triplet_choice	= "N"		# IN THE CALCULATION ARE PRESENT TRIPLETS?

i_point		= 0
n_point         = 20            # LAST point of the LIIC (we start from zero)
step		= 1

OUTPUT_FILE     = "plotEnergy"  # OUTPUT FILE WITH ALL STATES
REF_FILE        = "FCenergy"    # FC S0 ENERGY. IF fc_choice = "N" THE FILE MUST BE PRESENT

ev_conversion	= float(27.2114)# CONVERSION CONSTANTS from ev to au

################################################

#DEFAUL VALUES

scale_energy 	= 0.0
index_point_to_scale = 0		
typ_keyword	= ""		
s0_energy 	= 0.0
energy_keyword 	= ""	
s_keyword 	= ""	
t_keyword 	= ""		
unrestricted_choice = "N"
singlets	= 0
