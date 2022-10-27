#!/usr/local/Cluster-Apps/python/3.6.8/bin/python3.6

import os
import subprocess
import re
import sys

sys.path.append('/ddn/home/fzzq22/CODE_AND_SCRIPT/PYTHON_COMMON_MODULE')
import PARAM_FILE

#----------------------------------------------------------------------------------------------------------------------------#
def COUNTING_STATES(STATE_LIST):
	for i in range(len(STATE_LIST)):
		STATE_LIST[i] = int(STATE_LIST[i])
	nmstates 	= 0
	nstates  	= 0
	for multiplicity, i in enumerate(STATE_LIST):
		nmstates 	+= (multiplicity + 1) * i
		nstates 	+= i 
	return nmstates, nstates

# --------------------------- READING THE PARAMETERS ------------------------------------------- #
def READING_PARAMETER_FILE(PARAMETER_FILE_NAME):
	with open(PARAMETER_FILE_NAME, "r") as PARAMETER_FILE:
		CALCULATION             = PARAMETER_FILE.readline()             # SH or NX
		# List containing the number of states for each multiplicity: nsinglets, ndoublets, ntriplets, ...
		STATE_LIST              = PARAMETER_FILE.readline().split()
		rangexmin               = float(PARAMETER_FILE.readline())      # Xmin and Xmax for the plot
		rangexmax               = float(PARAMETER_FILE.readline())
		rangeymin               = float(PARAMETER_FILE.readline())      # We use multiplot. This is the Ymin Ymax for the energy axis
		rangeymax               = float(PARAMETER_FILE.readline())
		rangey2max              = float(PARAMETER_FILE.readline())      # Xmax for the coordinates axis
		outname                 = PARAMETER_FILE.readline().rstrip()    # Name of the plot.png file
		# A string idicate the coordinates that we want to print. They vary depends on the molecule we are studing.
		INPUT_COORD             = PARAMETER_FILE.readline()
		# The time step of the dynamics
		TIMESTEP                = float(PARAMETER_FILE.readline())
		template_geo            = PARAMETER_FILE.readline().rstrip()
		if int( len(template_geo) ) == 0:
			raise ValueError ('The parameter file lacks some records!')
		return (CALCULATION, STATE_LIST, rangexmin, rangexmax, rangeymin, rangeymax, rangey2max,
				 outname, INPUT_COORD, TIMESTEP, template_geo)

#----------------------------------------------------------------------------------------------------------------------------#
def TOT_ENERGY_CHECK(tot_energy_step_1, tot_energy_step_2, INIT_TOT_ENERGY):
	Thresh_EGAP     = 0.05 							# eV
	E_GAP	= abs(tot_energy_step_2 - tot_energy_step_1) 			# Energies are given in eV
# FIRST CONDITION to break:   GAP in total energy LARGER THAN 
	if E_GAP > 0.2:
		BREAKREASON     = "GAP"						# We compare the enrgy between the current and previous step
# SECOND CONDITION to break:  DRIFT LARGER THAN
	elif abs(INIT_TOT_ENERGY - tot_energy_step_2) > 0.3:                  	# Check the drift comparing with the initial total energy
		BREAKREASON     = "DRIFT"
# If there is a small gap with warn the user
	elif E_GAP > Thresh_EGAP:
		BREAKREASON     = "WARNING"
	else:
		BREAKREASON 	= False
	return BREAKREASON, E_GAP

#----------------------------------------------------------------------------------------------------------------------------#
def PRINT_WARNING(warning, E_GAP, time):
	warning += 1
	print(f"{PARAM_FILE.bcolors.WARNING}%5.2f eV discontinuity at time: %5.2f fs{PARAM_FILE.bcolors.ENDC}" %(E_GAP, time))
	return warning

def PRINT_BREAK(E_GAP, TIME, BREAKREASON):
	print (f"{PARAM_FILE.bcolors.FAIL}%5.2f eV discontinuity. Dynamics stoped at: %5.2f fs due %s {PARAM_FILE.bcolors.ENDC}" %(E_GAP, TIME, BREAKREASON))
	os.system("touch %s" %(PARAM_FILE.error_dyn))
	return

def CHECK_BREAK(tot_energy_step_1, tot_energy_step_2, INIT_TOT_ENERGY, warning, TIME, BREAKREASON):
	if BREAKREASON == "SWITCH":							tobreak = True;
	else:
		BREAKREASON, E_GAP      = TOT_ENERGY_CHECK(tot_energy_step_1, tot_energy_step_2, INIT_TOT_ENERGY)
		if not BREAKREASON:					# If there is no gap we update the i-1 record
			tot_energy_step_1       = tot_energy_step_2; 			tobreak	= False
		elif (BREAKREASON == "WARNING"):
			warning 	= PRINT_WARNING(warning, E_GAP, TIME)
			if warning >= 5: 
				PRINT_BREAK(E_GAP, TIME, BREAKREASON);			tobreak = True
			else: 
				tot_energy_step_1 = tot_energy_step_2;			tobreak = False
		else: 
			PRINT_BREAK(E_GAP, TIME, BREAKREASON); 				tobreak = True; 
	return tot_energy_step_1, tot_energy_step_2, warning, TIME, BREAKREASON, tobreak

#----------------------------------------------------------------------------------------------------------------------------#
def TRAJECTORY_BREAK_SH(EnergyFile, nmstates, TIMESTEP):
	INIT_TOT_ENERGY         = 0.0;	tot_energy_step_1       = 0.0;	tot_energy_step_2       = 0.0; 	warning			= 0
	with open(EnergyFile, "r") as fp:
		for i, lisline in enumerate(fp):
			BREAKREASON = False
			lisline = lisline.split()
			if i == 5: 					#Line six is the first point of the dynamics t = 0 fs
				tot_energy_step_1	= float(lisline[6])		# Energy in eV.
				INIT_TOT_ENERGY		= tot_energy_step_1		# We save the initial energy to check drifts
			if (i > 5) and (lisline[0] != "#"):		# '#' occurs in out file when the traj HOPs. We want skip that line
				TIME = float(lisline[1])
				tot_energy_step_2	= float(lisline[6])		# Energy in eV.
				(tot_energy_step_1, tot_energy_step_2, warning, TIME, BREAKREASON,
					tobreak) = CHECK_BREAK(tot_energy_step_1, tot_energy_step_2, INIT_TOT_ENERGY, warning, TIME, BREAKREASON)
				if tobreak: break
	return TIME, BREAKREASON

#----------------------------------------------------------------------------------------------------------------------------#
def TRAJECTORY_BREAK_NX(EnergyFile, nmstates, TIMESTEP):
	INIT_TOT_ENERGY		= 0.0; 	tot_energy_step_1	= 0.0;	tot_energy_step_2	= 0.0;  warning                 = 0
	with open(EnergyFile,"r") as fp:
		for i, lisline in enumerate(fp):
			BREAKREASON = False
			lisline	= lisline.split(); TIME = float(lisline[0])
			if i == 0: 					# Line 0 is the first point of the dynamics t = 0 fs
				# Here we multiply for the conversion factor to get the energies in eV
				# nmstates+2 line with total energy, consider the array in python start from 0
				tot_energy_step_1	= float(lisline[nmstates + 2]) * PARAM_FILE.ev_au_conv
				INIT_TOT_ENERGY		= tot_energy_step_1            			# We save the total energy at the beginning
				INIT_S0_ENERGY		= float(lisline[1]) * PARAM_FILE.ev_au_conv   	# NX save energy in a.u and not scaled respect the intial point
			if (i > 0):
				# The total energy for the actual line is saved in the variable
				tot_energy_step_2 	= float(lisline[nmstates + 2]) * PARAM_FILE.ev_au_conv
				# Here we check the energy discontinuities and if there are some drift with trajectories
				BREAKREASON, E_GAP 	= TOT_ENERGY_CHECK(tot_energy_step_1, tot_energy_step_2, INIT_TOT_ENERGY) 
# It is necessary for TDDFT and ADC(2) dynamics when we can have a swap of S0 and S1 excited state. Clearly the dynamics beyond is not valid anymore.
# THIRD CONDITION: (S0 energy - S1 energy) > 0.0 ==> S1 and S0 cross 
				if float(lisline[1]) - float(lisline[2]) > 0:   BREAKREASON	= "SWITCH"; 	
				(tot_energy_step_1, tot_energy_step_2, warning, TIME, BREAKREASON,
					 tobreak) = CHECK_BREAK(tot_energy_step_1, tot_energy_step_2, INIT_TOT_ENERGY, warning, TIME, BREAKREASON)
				if tobreak: break
	return TIME, BREAKREASON, INIT_S0_ENERGY/27.2114

#----------------------------------------------------------------------------------------------------------------------------#
def GET_MOLECULE_label(template_geo):
	if   "HPP" 	in template_geo:
		label = "HPP" 
	elif "HPAC" 	in template_geo:
		label = "HPAC"
	elif "PYRONE" 	in template_geo:
		label = "PYRONE"
	elif "FORMALDEHYDE" in template_geo:
		label = "FORMALDEHYDE"
	elif "ACROLEIN" in template_geo:
		label = "ACROLEIN"
	elif "BH3NH3" 	in template_geo:
		label = "BH3NH3"
		class_molecule = PARAM_FILE.BH3NH3 
	elif "Pyridine" in template_geo:
		label = "Pyridine"
	elif "Nucleic_Acid" in template_geo:
		label = "Nucleic_Acid"
	else:
		print(label)
		raise ValueError ('label not recognized')
	return label, class_molecule

#----------------------------------------------------------------------------------------------------------------------------#	
def MAKE_GEOMETRICAL_COORDINATES(TIMESTEP, template_geo, label_MOLECULE):
    TMP_COORDINATES_FILE_NAME	= "COORDINATES.out"
    os.system("cp -f dyn.xyz output.xyz")						# Python script read the file output.xyz
    programgeo                  = '/nobackup/zcxn55/SOFTWARE/SHARC-2.1-corr-edc/bin/geo.py'
    cmd = "python2 $SHARC/%s -t %5.2f < %s > %s" %(programgeo, TIMESTEP, template_geo, TMP_COORDINATES_FILE_NAME )
    os.system(cmd)								# The tmp coordinate file is created

    if label_MOLECULE == "HPP" or label_MOLECULE == "HPAC":
        label		= "   time\t\tO-O\t\t\tO-H\t\t\tO--H\t\tC-C\t\t\tC=0\t\tC=O pyramid\t\tC-O\t\td 3 1 4 10\t\td 2 1 4 10\t\tC1--O11"
    elif label_MOLECULE == "PYRONE":
        label           = "   time\t\tC=0"
    elif label_MOLECULE == "FORMALDEHYDE":
        label           = "   time\t\tC=0"
    elif label_MOLECULE == "ACROLEIN":
        label           = "   time\t\tC=0"
    elif label_MOLECULE == "BH3NH3":
        label           = "   time\t\t\tB-N\t\t\tN-H\t\tN-H\t\t\tN-H\t\tB-H\t\t\tB-H\t\tB-H\t\tNH3 pyramid\t\tBH3 pyramid"
    elif label_MOLECULE == "Pyridine":
        label           = "   time\t\t\tB-N\t\t\tB-H\t\t\tB-H\t\tB-H\t\tBH3 pyramid"
    elif label_MOLECULE == "Nucleic_Acid":
        label           = "   time\t\tC-O\t\t\tC-C"
    os.system("sed -i '1d' %s" 		%(TMP_COORDINATES_FILE_NAME))
    os.system('sed -i "s/time.*/%s/g" ' %(TMP_COORDINATES_FILE_NAME))
    return

#----------------------------------------------------------------------------------------------------------------------------#
def WRITE_HEAD_GP(outname, rangexmin, rangexmax, rangeymin, rangeymax, positionlabel1):
    GNUPLOT_HEAD    =  'set terminal pngcairo enhanced dashed font "Helvetica,28.0" size 1300,1200\nset encoding iso_8859_1\n'
    GNUPLOT_HEAD    += 'set output "%s"\n\n' 						% (outname)
    GNUPLOT_HEAD    += 'set dashtype 11 (10,9)\nset dashtype 12 (5,8)\n\n'
    GNUPLOT_HEAD    += 'set lmargin at screen 0.11\nset rmargin at screen 0.86\n'
    GNUPLOT_HEAD    += 'set xrange[%i:%i]\nset xlabel "Time (fs)"\n' 			% (rangexmin, rangexmax)
    GNUPLOT_HEAD    += 'set title offset 0,-0.8\n'
    GNUPLOT_HEAD    += 'set multiplot\n  set ytics nomirror\n  set key at %s\n  set ylabel "Relative Energy(eV)"\n  set yrange[%s:%s]\n'  %(positionlabel1, rangeymin, rangeymax)

    return GNUPLOT_HEAD

#----------------------------------------------------------------------------------------------------------------------------#					
def WRITE_GEOMETRICAL_CORDINATES_HPP_GP(INPUT_COORD, GNUPLOT_TIME_label):
#This subrouting will create a GNUPLOT_COORD for gnuplot. The GNUPLOT_COORD, depending on the INPUT, will plot different coordinates such as O-H, O-O...
#Notice that you need to modify Geo_new.out file in case the geometrical paramenter changes.  
	GNUPLOT_COORD 	= ''
	index		= []
	if ( "A" in INPUT_COORD ):
		GNUPLOT_COORD += '  plot "COORDINATES.out" using %s:2 w l lw 5 dt 11 lc rgbcolor "#FF4500" title "O-O bond" axes x1y2'	% (GNUPLOT_TIME_label) 	#Orange for O-O
		y2label = '"Bond Length ({\\305})"'
		index.append(2)
	if ( "B" in INPUT_COORD ):
		GNUPLOT_COORD += ', \\\n  "" using %s:4 w l lw 5 dt 11 lc rgbcolor "#660033" title "O--H bond" axes x1y2'		% (GNUPLOT_TIME_label)	#Purple for O--H
		index.append(4)
	if ( "C" in INPUT_COORD ):
		GNUPLOT_COORD += ', \\\n  "" using %s:5 w l lw 5 dt 11 lc rgbcolor "#800000" title "C-C bond" axes x1y2'			% (GNUPLOT_TIME_label)	#Maroon 
		index.append(5)
	if ( "D" in INPUT_COORD ):
		GNUPLOT_COORD += ', \\\n  "" using %s:6 w l lw 5 dt 11 lc rgbcolor "#FFD700" title "C=O bond" axes x1y2'			% (GNUPLOT_TIME_label)	#Yellow
		index.append(6)
	if ( "F" in INPUT_COORD ):
		GNUPLOT_COORD += ', \\\n  "" using %s:3 w l lw 5 dt 11 lc rgbcolor "#FF0000" title "O-H bond" axes x1y2'			% (GNUPLOT_TIME_label)	#Red
		index.append(3)
	if ( "G" in INPUT_COORD ):
		GNUPLOT_COORD += ', \\\n  "" using %s:8 w l lw 5 dt 11 lc rgbcolor "#21908d" title "C-O bond" axes x1y2'			% (GNUPLOT_TIME_label)	#Teal
		index.append(8)
	if ( "E" in INPUT_COORD ):
		GNUPLOT_COORD += ', \\\n  "" using %s:($7/10) w l lw 5 dt 11 lc rgbcolor "#aadc32" title "Pyramidalization" axes x1y2'	% (GNUPLOT_TIME_label)	#Lime Green
		index.append(7)
		y2label = '"Bond Length ({\\305}) / Angle (10^-^1)"'
#y2label is the label associated with the second plot of multiplot. Depending on which coordinate you chose it can change.
	return GNUPLOT_COORD, y2label, index

#----------------------------------------------------------------------------------------------------------------------------#                                  
def WRITE_GEOMETRICAL_CORDINATES_BH3NH3_GP(INPUT_COORD, GNUPLOT_TIME_label):
	GNUPLOT_COORD   = '';	index           = []
	if ( "A" in INPUT_COORD ):
		GNUPLOT_COORD 	+= '  plot "COORDINATES.out" using %s:2 w l lw 5 dt 11 lc rgbcolor "#FF4500" title "N-B bond" axes x1y2'   % (GNUPLOT_TIME_label)  # Orange
		y2label 	=  '"Bond Length ({\\305})"'
		index.append(2)
	if ( "B" in INPUT_COORD ):
		GNUPLOT_COORD += ', \\\n  "" using %s:3 w l lw 5 dt 11 lc rgbcolor "#660033" title "N-H bonds" axes x1y2'   	% (GNUPLOT_TIME_label)  # Purple
		GNUPLOT_COORD += ', \\\n  "" using %s:4 w l lw 5 dt 11 lc rgbcolor "#660033" notitle axes x1y2'   		% (GNUPLOT_TIME_label)  
		GNUPLOT_COORD += ', \\\n  "" using %s:5 w l lw 5 dt 11 lc rgbcolor "#660033" notitle axes x1y2'   		% (GNUPLOT_TIME_label)  	
		index.append(3); index.append(4); index.append(5)
	if ( "C" in INPUT_COORD ):
		GNUPLOT_COORD += ', \\\n  "" using %s:6 w l lw 5 dt 11 lc rgbcolor "#FFD700" title "B-H bonds" axes x1y2'        % (GNUPLOT_TIME_label)  
		GNUPLOT_COORD += ', \\\n  "" using %s:7 w l lw 5 dt 11 lc rgbcolor "#FFD700" notitle axes x1y2'                  % (GNUPLOT_TIME_label)
		GNUPLOT_COORD += ', \\\n  "" using %s:8 w l lw 5 dt 11 lc rgbcolor "#FFD700" notitle axes x1y2'                  % (GNUPLOT_TIME_label)
		index.append(6); index.append(7); index.append(8)

	return GNUPLOT_COORD, y2label, index

#----------------------------------------------------------------------------------------------------------------------------#                                  
def WRITE_GEOMETRICAL_CORDINATES_Pyridine_GP(INPUT_COORD, GNUPLOT_TIME_label):
        GNUPLOT_COORD   = '';   index           = []
        if ( "A" in INPUT_COORD ):
                GNUPLOT_COORD   += '  plot "COORDINATES.out" using %s:2 w l lw 5 dt 11 lc rgbcolor "#FF4500" title "N-B bond" axes x1y2'   % (GNUPLOT_TIME_label)  # Orange
                y2label         =  '"Bond Length ({\\305})"'
                index.append(2)
        if ( "B" in INPUT_COORD ):
                GNUPLOT_COORD += ', \\\n  "" using %s:3 w l lw 5 dt 11 lc rgbcolor "#FFD700" title "B-H bonds" axes x1y2'        % (GNUPLOT_TIME_label)
                GNUPLOT_COORD += ', \\\n  "" using %s:4 w l lw 5 dt 11 lc rgbcolor "#FFD700" notitle axes x1y2'                  % (GNUPLOT_TIME_label)
                GNUPLOT_COORD += ', \\\n  "" using %s:5 w l lw 5 dt 11 lc rgbcolor "#FFD700" notitle axes x1y2'                  % (GNUPLOT_TIME_label)
                index.append(3); index.append(4); index.append(5)

        return GNUPLOT_COORD, y2label, index


def WRITE_GEOMETRICAL_CORDINATES_Nucleic_Acid_GP(INPUT_COORD, GNUPLOT_TIME_label):
        GNUPLOT_COORD   = '';   index           = []
        if ( "A" in INPUT_COORD ):
                GNUPLOT_COORD   += '  plot "COORDINATES.out" using %s:2 w l lw 5 dt 11 lc rgbcolor "#FF4500" title "C-O bond" axes x1y2'   % (GNUPLOT_TIME_label)  # Orange
                y2label         =  '"Bond Length ({\\305})"'
                index.append(2)
        if ( "B" in INPUT_COORD ):
                GNUPLOT_COORD += ', \\\n  "" using %s:3 w l lw 5 dt 11 lc rgbcolor "#FFD700" title "C-C bonds" axes x1y2'        % (GNUPLOT_TIME_label)
                index.append(3); 

        return GNUPLOT_COORD, y2label, index


#----------------------------------------------------------------------------------------------------------------------------#
def WRITE_NX_STATE_GP(nstates, STATE_LIST, INIT_S0_ENERGY, GNUPLOT_TIME_label, colorS, colorT, DATAFILE, TIME_RESTART, RESTART):
	GNUPLOT_STATE   = ''
	SINGLET_STATES  = 0;	TRIPLET_STATES	= 1;
	LW_1		= 3.0;	LW_2		= 6.0;

	GNUPLOT_STATE 	+= '  plot "%s" u %s:(($%i - %9.5f)*27.2114) title "Total Energy" lw %3.1f lc rgbcolor "#000000" w l, \\\n' % (DATAFILE, GNUPLOT_TIME_label, nstates + 3, INIT_S0_ENERGY, LW_1)
	for i in range(STATE_LIST[0]):
		if SINGLET_STATES < 4:		#The first 4 singlets are displyed in blue
			GNUPLOT_STATE += '  "" u %s:(($%i - %9.5f)*27.2114) title "S_%i" lw %3.1f lt 1 lc rgb "%s" w l, \\\n'	% (GNUPLOT_TIME_label, i + 2, INIT_S0_ENERGY, i, LW_2, colorS[SINGLET_STATES])
		else:				#The remaining are simply in grey without label
			GNUPLOT_STATE += '  "" u %s:(($%i - %9.5f)*27.2114) notitle lw %3.1f lt 1 lc rgb "grey" w l, \\\n'   	% (GNUPLOT_TIME_label, i + 2, INIT_S0_ENERGY,    LW_2)
		SINGLET_STATES   += 1
	for i in range(TRIPLET_STATES, STATE_LIST[2] + 1):
		if TRIPLET_STATES < 4: 
			GNUPLOT_STATE += '  "" u %s:(($%i - %9.5f)*27.2114) title "T_%i" lw %3.1f lt 1 lc rgb "%s" w l, \\\n'   % (GNUPLOT_TIME_label, i + 2, INIT_S0_ENERGY, i, LW_2, colorT[TRIPLET_STATES])
		else:
			GNUPLOT_STATE += '  "" u %s:(($%i - %9.5f)*27.2114) notitle lw %3.1f lt 1 lc rgb "grey" w l, \\\n'      % (GNUPLOT_TIME_label, i + 2, INIT_S0_ENERGY,    LW_2)
		TRIPLET_STATES	+=1

	# Plot the running trajecotry in back empty circles
	GNUPLOT_STATE += '  "" u %s:(($%i - %9.5f)*27.2114) notitle lw %3.1f lc rgbcolor "#000000" pt 6 ps 2.0 w p\n\n'	% (GNUPLOT_TIME_label, nstates + 2, INIT_S0_ENERGY, LW_1)
	return GNUPLOT_STATE

#----------------------------------------------------------------------------------------------------------------------------#
def WRITE_SH_STATE_GP(nmstates, STATE_LIST, GNUPLOT_TIME_label, colorS, colorT, DATAFILE, TIME_RESTART, RESTART):
	LW_1            = 3.0;	LW_2            = 6.0
	SINGLET_STATES  = 0  ;	TRIPLET_STATES	= 0
	GNUPLOT_STATE	= ''
# We assign the spin at each state reading the information from the SHARC out file
	with open(DATAFILE, "r") as FILE_MCH:
		for i, lisline in enumerate(FILE_MCH):
			if i > 2:
				break
	lisline = lisline.split()                                       # The lisline will contain the result at t = 0

	GNUPLOT_STATE   += '  plot "%s" u %s:%i title "Total Energy" lw %6.2f lc rgbcolor "#000000" w l, \\\n'  	% (DATAFILE, GNUPLOT_TIME_label, 4, LW_1)
	for i in range(nmstates):
		if int(float(lisline[4 + nmstates + i])) == 0 :		# The spin of the i-th state is zero (singlet)
			if SINGLET_STATES < 4:				# The first 4 singlets are displyed in blue 
				GNUPLOT_STATE += '  "" u %s:%i title "S_%i" lw %6.2f lt 1 lc rgb "%s" w l	, \\\n' % (GNUPLOT_TIME_label, 5 + i, SINGLET_STATES, LW_2, colorS[SINGLET_STATES])
			else:						# The remaining are simply in grey without label
				GNUPLOT_STATE += '  "" u %s:%i notitle lw %6.2f lt 1 lc rgb "grey" w l		, \\\n' % (GNUPLOT_TIME_label, 5 + i, 		      LW_2)
			SINGLET_STATES	      += 1

		if int(float(lisline[4 + nmstates + i])) == 2 :		# The spin of the i-th state is two (triplets)
			if (TRIPLET_STATES < STATE_LIST[2]):		# STATE_LIST[2] = Number of triplet states
				GNUPLOT_STATE += '  "" u %s:%i title "T_%i" lw %6.2f lt 1 lc rgb "%s" w l	, \\\n' % (GNUPLOT_TIME_label, 5 + i, triplet + 1, LW_2, colorT[TRIPLET_STATES])
			else: 						# Plot the title only for one of the three components of the triplet states
				GNUPLOT_STATE += '  "" u %s:%i notitle lw %6.2f lt 1 lc rgb "%s" w l		, \\\n'	% (GNUPLOT_TIME_label, 5 + i, 		   LW_2, colorT[TRIPLET_STATES % STATE_LIST[2] ])
			TRIPLET_STATES	      += 1
# After three triplet (0,1,2) we want reinitilize the counters. Triplet are printed T1x, T2x, ..., T1y, T2y, ..., T1z, ...
# After printing the label for the first three we can stop printing title (stoptitle is initialized at 1 at this point and no other title are printed) 
	GNUPLOT_STATE   += '  "" u %s:%i notitle lw %6.2f lc rgbcolor "#000000" pt 6 ps 2.0 w p '			% (GNUPLOT_TIME_label, 3, LW_1)

	# In case you have restarted the dynamics will be added the plot belonging to the last part of the previous dynamics.
	if RESTART == True:                                             # This means that the dynamics with SHarc has been restarted from NX.
		shadeofgrey     = ["#808080","#A9A9A9","#C0C0C0","#DCDCDC", "#F5F5F5"]
		GNUPLOT_STATE   += '       , \\\n'                      # We want write so we need to add ,\
		GNUPLOT_STATE   += WRITE_SH_STATE_GP_RESTARTED_FROM_NX(STATE_LIST, shadeofgrey, TIME_RESTART, lisline)

	GNUPLOT_STATE   += '\n\n'        
	return GNUPLOT_STATE

#----------------------------------------------------------------------------------------------------------------------------#
def WRITE_SH_STATE_GP_RESTARTED_FROM_NX(STATE_LIST, colorS, TIME_RESTART, lisline):
	GNUPLOT_STATE	= '' ; SINGLET_STATES	= 0;
	LW_1            = 3.0;	LW_2            = 5.0;
 
	DYN_DATAFILE    = "../RESULTS/en.dat"                   # For now we assumes that the previus dyn was with NX in the folder ../RESULTS/ This can be modified in the future
	TIME_END_OF_DYN = float(subprocess.check_output(['tail', '-1', DYN_DATAFILE]).split()[0])       # List time found in DYN_DATAFILE is the point at which the dynamics end
# The S0 energy of the parent dynamics at the TIME_RESTART
	INIT_S1_ENERGY  = float(subprocess.check_output(['tail', '-' + str(int( (TIME_END_OF_DYN - TIME_RESTART) * 2 + 1 )), DYN_DATAFILE]).split()[2])
	scaling         = - (float(lisline[5]) / 27.2114) + INIT_S1_ENERGY                              # the scaling for the parent dynamics will be so that the S1 energies at 
# TIME_RESTART will be exactly the same for both calculation (we will have the line conciding at the same point).
#	print (TIME_END_OF_DYN, INIT_S1_ENERGY, scaling, lisline[5])					# !!5 is the index for energy S1!!
	for i in range(STATE_LIST[0]):	# Here the number the singlet but could be a sub set of the number of electronic states in the NX dynamics
		GNUPLOT_STATE += '  "%s" u 1:(($%i - %9.5f)*27.2114) notitle lw %3.1f lt 1 lc rgb "%s" w l, \\\n'% (DYN_DATAFILE, i + 2, scaling, LW_2, colorS[SINGLET_STATES])
		SINGLET_STATES   += 1
	return GNUPLOT_STATE

#----------------------------------------------------------------------------------------------------------------------------#
def WRITE_COORDS_AND_BREAKLINE(rangeymax, rangey2max, positionlabel2, TIMEBREAK, BREAKREASON, INPUT_COORD, GNUPLOT_TIME_label, label_MOLECULE):
#Plot the second part with multipot
	if 	label_MOLECULE == "HPP":
		GNUPLOT_COORD, y2label, index = WRITE_GEOMETRICAL_CORDINATES_HPP_GP(   INPUT_COORD, GNUPLOT_TIME_label)
	elif 	label_MOLECULE == "BH3NH3":
		GNUPLOT_COORD, y2label, index = WRITE_GEOMETRICAL_CORDINATES_BH3NH3_GP(INPUT_COORD, GNUPLOT_TIME_label)
	elif	label_MOLECULE == "Pyridine":
		GNUPLOT_COORD, y2label, index = WRITE_GEOMETRICAL_CORDINATES_Pyridine_GP(INPUT_COORD, GNUPLOT_TIME_label) 
	elif 	label_MOLECULE == "Nucleic_Acid":
		GNUPLOT_COORD, y2label, index = WRITE_GEOMETRICAL_CORDINATES_Nucleic_Acid_GP(INPUT_COORD, GNUPLOT_TIME_label)
	else:
		print ("\n * Not implemented for molecule * \n", label_MOLECULE)

	GNUPLOT_FINAL  = ''
	GNUPLOT_FINAL += '  unset key\n  unset ylabel\n  unset yrange\n  unset ytics\n'
	GNUPLOT_FINAL += '  set y2label %s\n  set y2tics\n  set key at %s\n  set y2range[0.75:%s]\n' 	% (y2label, positionlabel2, rangey2max)
	GNUPLOT_FINAL += GNUPLOT_COORD         								#string is the plot associated with the coordinates analysis
#Finally we add a vertical line to indicate at which time the dynamics is not valid anymore
	if BREAKREASON != False :
		GNUPLOT_FINAL += '\n  set key bottom \n'
		GNUPLOT_FINAL += '  set parametric\n  plot [t=0:%5.3f] %5.3f,t w l lw 2.0 lt 1 lc rgbcolor "#FF0000" title "%s"' % (rangeymax, TIMEBREAK, BREAKREASON)
	return GNUPLOT_FINAL



