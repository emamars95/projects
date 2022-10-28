#!/usr/bin/env python3

import os
import subprocess
from json import loads

from TOOLS import GET_DATA
import PARAM_FILE
from BH3NH3 import BH3NH3

#----------------------------------------------------------------------------------------------------------------------------#
def COUNTING_STATES(state_list):
	for i in range(len(state_list.split())):
		state_list[i] = int(state_list[i])
	nmstates 	= 0
	nstates  	= 0
	for multiplicity, i in enumerate(state_list):
		nmstates 	+= (multiplicity + 1) * i
		nstates 	+= i 
	return nmstates, nstates

#----------------------------------------------------------------------------------------------------------------------------#
def READING_PARAMETER_FILE(parameter_file_name):
	with open(parameter_file_name, "r") as parameter_file:
		data = parameter_file.read()
	dictionary = loads(data)
	return dictionary
			
#----------------------------------------------------------------------------------------------------------------------------#
def TOT_ENERGY_CHECK(tot_energy_step_1, tot_energy_step_2, INIT_TOT_ENERGY):
	Thresh_EGAP     = 0.05 							# eV
	e_gap	= abs(tot_energy_step_2 - tot_energy_step_1) 			# Energies are given in eV
# FIRST CONDITION to break:   GAP in total energy LARGER THAN 
	if e_gap > 0.2:
		break_reason     = "GAP"						# We compare the enrgy between the current and previous step
# SECOND CONDITION to break:  DRIFT LARGER THAN
	elif abs(INIT_TOT_ENERGY - tot_energy_step_2) > 0.3:                  	# Check the drift comparing with the initial total energy
		break_reason     = "DRIFT"
# If there is a small gap with warn the user
	elif e_gap > Thresh_EGAP:
		break_reason     = "WARNING"
	else:
		break_reason 	= False
	return break_reason, e_gap

#----------------------------------------------------------------------------------------------------------------------------#
def PRINT_WARNING(warning, e_gap, time):
	warning += 1
	print(f"{PARAM_FILE.bcolors.WARNING}%5.2f eV discontinuity at time: %5.2f fs{PARAM_FILE.bcolors.ENDC}" %(e_gap, time))
	return warning

def PRINT_BREAK(e_gap, time, break_reason):
	print (f"{PARAM_FILE.bcolors.FAIL}%5.2f eV discontinuity. Dynamics stoped at: %5.2f fs due %s {PARAM_FILE.bcolors.ENDC}" %(e_gap, time, break_reason))
	with open(PARAM_FILE.error_dyn, 'w') as fp:
		fp.write(f'{time} fs\t{e_gap:5.2f} eV')
	return

def CHECK_BREAK(tot_energy_step_1, tot_energy_step_2, INIT_TOT_ENERGY, warning, time, break_reason):
	if break_reason == "SWITCH":							tobreak = True;
	else:
		break_reason, e_gap      = TOT_ENERGY_CHECK(tot_energy_step_1, tot_energy_step_2, INIT_TOT_ENERGY)
		if not break_reason:					# If there is no gap we update the i-1 record
			tot_energy_step_1       = tot_energy_step_2; 			tobreak	= False
		elif (break_reason == "WARNING"):
			warning 	= PRINT_WARNING(warning, e_gap, time)
			if warning >= 5: 
				PRINT_BREAK(e_gap, time, break_reason);			tobreak = True
			else: 
				tot_energy_step_1 = tot_energy_step_2;			tobreak = False
		else: 
			PRINT_BREAK(e_gap, time, break_reason); 				tobreak = True; 
	return tot_energy_step_1, tot_energy_step_2, warning, time, break_reason, tobreak

#----------------------------------------------------------------------------------------------------------------------------#
def TRAJECTORY_BREAK_SH(EnergyFile, nmstates, timestep):
	INIT_TOT_ENERGY         = 0.0;	tot_energy_step_1       = 0.0;	tot_energy_step_2       = 0.0; 	warning			= 0
	with open(EnergyFile, "r") as fp:
		for i, lisline in enumerate(fp):
			break_reason = False
			lisline = lisline.split()
			if i == 5: 					#Line six is the first point of the dynamics t = 0 fs
				tot_energy_step_1	= float(lisline[6])		# Energy in eV.
				INIT_TOT_ENERGY		= tot_energy_step_1		# We save the initial energy to check drifts
			if (i > 5) and (lisline[0] != "#"):		# '#' occurs in out file when the traj HOPs. We want skip that line
				time = float(lisline[1])
				tot_energy_step_2	= float(lisline[6])		# Energy in eV.
				(tot_energy_step_1, tot_energy_step_2, warning, time, break_reason,
					tobreak) = CHECK_BREAK(tot_energy_step_1, tot_energy_step_2, INIT_TOT_ENERGY, warning, time, break_reason)
				if tobreak: break
	return time, break_reason

#----------------------------------------------------------------------------------------------------------------------------#
def TRAJECTORY_BREAK_NX(EnergyFile, nmstates, timestep):
	INIT_TOT_ENERGY		= 0.0; 	tot_energy_step_1	= 0.0;	tot_energy_step_2	= 0.0;  warning                 = 0
	with open(EnergyFile,"r") as fp:
		for i, lisline in enumerate(fp):
			break_reason = False
			lisline	= lisline.split(); time = float(lisline[0])
			if i == 0: 					# Line 0 is the first point of the dynamics t = 0 fs
				# Here we multiply for the conversion factor to get the energies in eV
				# nmstates+2 line with total energy, consider the array in python start from 0
				tot_energy_step_1	= float(lisline[nmstates + 2]) * PARAM_FILE.ev_au_conv
				INIT_TOT_ENERGY		= tot_energy_step_1            			# We save the total energy at the beginning
				s0_ene		= float(lisline[1]) * PARAM_FILE.ev_au_conv   	# NX save energy in a.u and not scaled respect the intial point
			if (i > 0):
				# The total energy for the actual line is saved in the variable
				tot_energy_step_2 	= float(lisline[nmstates + 2]) * PARAM_FILE.ev_au_conv
				# Here we check the energy discontinuities and if there are some drift with trajectories
				break_reason, e_gap 	= TOT_ENERGY_CHECK(tot_energy_step_1, tot_energy_step_2, INIT_TOT_ENERGY) 
# It is necessary for TDDFT and ADC(2) dynamics when we can have a swap of S0 and S1 excited state. Clearly the dynamics beyond is not valid anymore.
# THIRD CONDITION: (S0 energy - S1 energy) > 0.0 ==> S1 and S0 cross 
				if float(lisline[1]) - float(lisline[2]) > 0:   break_reason	= "SWITCH"; 	
				(tot_energy_step_1, tot_energy_step_2, warning, time, break_reason,
					 tobreak) = CHECK_BREAK(tot_energy_step_1, tot_energy_step_2, INIT_TOT_ENERGY, warning, time, break_reason)
				if tobreak: break
	return time, break_reason, s0_ene/PARAM_FILE.ev_au_conv

#----------------------------------------------------------------------------------------------------------------------------#
def GET_MOLECULE_LABEL(template_geo):
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
		class_molecule = BH3NH3
	elif "Pyridine" in template_geo:
		label = "Pyridine"
	elif "Nucleic_Acid" in template_geo:
		label = "Nucleic_Acid"
	else:
		print(label)
		raise ValueError ('label not recognized')
	return label, class_molecule

#----------------------------------------------------------------------------------------------------------------------------#	
def MAKE_GEOMETRICAL_COORDINATES(timestep, template_geo, label_molecule):
    os.system("cp -f dyn.xyz output.xyz")						# Python script read the file output.xyz
    programgeo = '/nobackup/zcxn55/SOFTWARE/SHARC-2.1-corr-edc/bin/geo.py'
    cmd = "python2 $SHARC/%s -t %5.2f < %s > %s" %(programgeo, timestep, template_geo, PARAM_FILE.coordinate_file)
    os.system(cmd)								# The tmp coordinate file is created
    if label_molecule == "HPP" or label_molecule == "HPAC":
        label = "   time\t\tO-O\t\t\tO-H\t\t\tO--H\t\tC-C\t\t\tC=0\t\tC=O pyramid\t\tC-O\t\td 3 1 4 10\t\td 2 1 4 10\t\tC1--O11"
    elif label_molecule == "PYRONE":
        label = "   time\t\tC=0"
    elif label_molecule == "FORMALDEHYDE":
        label = "   time\t\tC=0"
    elif label_molecule == "ACROLEIN":
        label = "   time\t\tC=0"
    elif label_molecule == "BH3NH3":
        label = "   time\t\t\tB-N\t\t\tN-H\t\tN-H\t\t\tN-H\t\tB-H\t\t\tB-H\t\tB-H\t\tNH3 pyramid\t\tBH3 pyramid"
    elif label_molecule == "Pyridine":
        label = "   time\t\t\tB-N\t\t\tB-H\t\t\tB-H\t\tB-H\t\tBH3 pyramid"
    elif label_molecule == "Nucleic_Acid":
        label = "   time\t\tC-O\t\t\tC-C"
    os.system("sed -i '1d' %s" 		%(PARAM_FILE.coordinate_file))
    os.system('sed -i "s/time.*/%s/g" ' %(PARAM_FILE.coordinate_file))
    return

#----------------------------------------------------------------------------------------------------------------------------#
def WRITE_HEAD_GP(outname, rangexmin, rangexmax, rangeymin, rangeymax, positionlabel1):
    gnuplot_head    =  'set terminal pngcairo enhanced dashed font "Helvetica,28.0" size 1300,1200\nset encoding iso_8859_1\n'
    gnuplot_head    += 'set output "%s"\n\n' 						% (outname)
    gnuplot_head    += 'set dashtype 11 (10,9)\nset dashtype 12 (5,8)\n\n'
    gnuplot_head    += 'set lmargin at screen 0.11\nset rmargin at screen 0.86\n'
    gnuplot_head    += 'set xrange[%i:%i]\nset xlabel "time (fs)"\n' 			% (rangexmin, rangexmax)
    gnuplot_head    += 'set title offset 0,-0.8\n'
    gnuplot_head    += 'set multiplot\n  set ytics nomirror\n  set key at %s\n  set ylabel "Relative Energy(eV)"\n  set yrange[%s:%s]\n'  %(positionlabel1, rangeymin, rangeymax)

    return gnuplot_head

#----------------------------------------------------------------------------------------------------------------------------#					
def WRITE_GEOMETRICAL_CORDINATES_HPP_GP(input_coord, gnuplot_time_label):
#This subrouting will create a gnuplot_coord for gnuplot. The gnuplot_coord, depending on the INPUT, will plot different coordinates such as O-H, O-O...
#Notice that you need to modify Geo_new.out file in case the geometrical paramenter changes.  
	gnuplot_coord 	= ''
	index		= []
	if ( "A" in input_coord ):
		gnuplot_coord += '  plot "COORDINATES.out" using %s:2 w l lw 5 dt 11 lc rgbcolor "#FF4500" title "O-O bond" axes x1y2'	% (gnuplot_time_label) 	#Orange for O-O
		y2label = '"Bond Length ({\\305})"'
		index.append(2)
	if ( "B" in input_coord ):
		gnuplot_coord += ', \\\n  "" using %s:4 w l lw 5 dt 11 lc rgbcolor "#660033" title "O--H bond" axes x1y2'		% (gnuplot_time_label)	#Purple for O--H
		index.append(4)
	if ( "C" in input_coord ):
		gnuplot_coord += ', \\\n  "" using %s:5 w l lw 5 dt 11 lc rgbcolor "#800000" title "C-C bond" axes x1y2'			% (gnuplot_time_label)	#Maroon 
		index.append(5)
	if ( "D" in input_coord ):
		gnuplot_coord += ', \\\n  "" using %s:6 w l lw 5 dt 11 lc rgbcolor "#FFD700" title "C=O bond" axes x1y2'			% (gnuplot_time_label)	#Yellow
		index.append(6)
	if ( "F" in input_coord ):
		gnuplot_coord += ', \\\n  "" using %s:3 w l lw 5 dt 11 lc rgbcolor "#FF0000" title "O-H bond" axes x1y2'			% (gnuplot_time_label)	#Red
		index.append(3)
	if ( "G" in input_coord ):
		gnuplot_coord += ', \\\n  "" using %s:8 w l lw 5 dt 11 lc rgbcolor "#21908d" title "C-O bond" axes x1y2'			% (gnuplot_time_label)	#Teal
		index.append(8)
	if ( "E" in input_coord ):
		gnuplot_coord += ', \\\n  "" using %s:($7/10) w l lw 5 dt 11 lc rgbcolor "#aadc32" title "Pyramidalization" axes x1y2'	% (gnuplot_time_label)	#Lime Green
		index.append(7)
		y2label = '"Bond Length ({\\305}) / Angle (10^-^1)"'
#y2label is the label associated with the second plot of multiplot. Depending on which coordinate you chose it can change.
	return gnuplot_coord, y2label, index

#----------------------------------------------------------------------------------------------------------------------------#                                  
def WRITE_GEOMETRICAL_CORDINATES_BH3NH3_GP(input_coord, gnuplot_time_label):
	gnuplot_coord   = '';	index           = []
	if ( "A" in input_coord ):
		gnuplot_coord 	+= '  plot "COORDINATES.out" using %s:2 w l lw 5 dt 11 lc rgbcolor "#FF4500" title "N-B bond" axes x1y2'   % (gnuplot_time_label)  # Orange
		y2label 	=  '"Bond Length ({\\305})"'
		index.append(2)
	if ( "B" in input_coord ):
		gnuplot_coord += ', \\\n  "" using %s:3 w l lw 5 dt 11 lc rgbcolor "#660033" title "N-H bonds" axes x1y2'   	% (gnuplot_time_label)  # Purple
		gnuplot_coord += ', \\\n  "" using %s:4 w l lw 5 dt 11 lc rgbcolor "#660033" notitle axes x1y2'   		% (gnuplot_time_label)  
		gnuplot_coord += ', \\\n  "" using %s:5 w l lw 5 dt 11 lc rgbcolor "#660033" notitle axes x1y2'   		% (gnuplot_time_label)  	
		index.append(3); index.append(4); index.append(5)
	if ( "C" in input_coord ):
		gnuplot_coord += ', \\\n  "" using %s:6 w l lw 5 dt 11 lc rgbcolor "#FFD700" title "B-H bonds" axes x1y2'        % (gnuplot_time_label)  
		gnuplot_coord += ', \\\n  "" using %s:7 w l lw 5 dt 11 lc rgbcolor "#FFD700" notitle axes x1y2'                  % (gnuplot_time_label)
		gnuplot_coord += ', \\\n  "" using %s:8 w l lw 5 dt 11 lc rgbcolor "#FFD700" notitle axes x1y2'                  % (gnuplot_time_label)
		index.append(6); index.append(7); index.append(8)

	return gnuplot_coord, y2label, index

#----------------------------------------------------------------------------------------------------------------------------#                                  
def WRITE_GEOMETRICAL_CORDINATES_Pyridine_GP(input_coord, gnuplot_time_label):
    gnuplot_coord   = '';   index           = []
    if ( "A" in input_coord ):
            gnuplot_coord   += '  plot "COORDINATES.out" using %s:2 w l lw 5 dt 11 lc rgbcolor "#FF4500" title "N-B bond" axes x1y2'   % (gnuplot_time_label)  # Orange
            y2label         =  '"Bond Length ({\\305})"'
            index.append(2)
    if ( "B" in input_coord ):
            gnuplot_coord += ', \\\n  "" using %s:3 w l lw 5 dt 11 lc rgbcolor "#FFD700" title "B-H bonds" axes x1y2'        % (gnuplot_time_label)
            gnuplot_coord += ', \\\n  "" using %s:4 w l lw 5 dt 11 lc rgbcolor "#FFD700" notitle axes x1y2'                  % (gnuplot_time_label)
            gnuplot_coord += ', \\\n  "" using %s:5 w l lw 5 dt 11 lc rgbcolor "#FFD700" notitle axes x1y2'                  % (gnuplot_time_label)
            index.append(3); index.append(4); index.append(5)
    return gnuplot_coord, y2label, index

#----------------------------------------------------------------------------------------------------------------------------#
def WRITE_GEOMETRICAL_CORDINATES_Nucleic_Acid_GP(input_coord, gnuplot_time_label):
    gnuplot_coord   = '';   index           = []
    if ( "A" in input_coord ):
            gnuplot_coord   += '  plot "COORDINATES.out" using %s:2 w l lw 5 dt 11 lc rgbcolor "#FF4500" title "C-O bond" axes x1y2'   % (gnuplot_time_label)  # Orange
            y2label         =  '"Bond Length ({\\305})"'
            index.append(2)
    if ( "B" in input_coord ):
            gnuplot_coord += ', \\\n  "" using %s:3 w l lw 5 dt 11 lc rgbcolor "#FFD700" title "C-C bonds" axes x1y2'        % (gnuplot_time_label)
            index.append(3); 

    return gnuplot_coord, y2label, index

#----------------------------------------------------------------------------------------------------------------------------#
def WRITE_NX_STATE_GP(nstates, state_list, s0_ene, t_label, datafile):
	singlets = 0; triplets = 1;
	lw_1 = 3.0;	lw_2 = 6.0;
	gnuplot_state = f' plot "{datafile}" u {t_label}:((${nstates+3} - {s0_ene:9.5f})*{PARAM_FILE.ev_au_conv}) title "Total Energy" lw {lw_1:3.1f} lc rgbcolor "#000000" w l, \\\n'
	for i in range(state_list[0]):
		if singlets < 4:						# The first 4 singlets are displyed in blue
			gnuplot_state += f'  "" u {t_label}:((${i+2} - {s0_ene:9.5f})*{PARAM_FILE.ev_au_conv}) title "S_{i}" lw {lw_2:3.1f} lt 1 lc rgb "{PARAM_FILE.shadeofblue[singlets]}" w l, \\\n'
		else:									# The remaining are simply in grey without label
			gnuplot_state += f'  "" u {t_label}:((${i+2} - {s0_ene:9.5f})*{PARAM_FILE.ev_au_conv}) notitle lw {lw_2:3.1f} lt 1 lc rgb "grey" w l, \\\n'
		singlets += 1
	for i in range(triplets, state_list[2] + 1):
		if triplets < 4: 
			gnuplot_state += f'  "" u {t_label}:((${i+2} - {s0_ene:9.5f})*{PARAM_FILE.ev_au_conv}) title "T_{i}" lw {lw_2:3.1f} lt 1 lc rgb "{PARAM_FILE.shadeofgreen[triplets]}" w l, \\\n'
		else:
			gnuplot_state += f'  "" u {t_label}:((${i+2} - {s0_ene:9.5f})*{PARAM_FILE.ev_au_conv}) notitle lw {lw_2:3.1f} lt 1 lc rgb "grey" w l, \\\n'
		triplets	+=1
	# Plot the running trajecotry in back empty circles
	gnuplot_state += f' "" u {t_label}:((${nstates+2} - {s0_ene:9.5f})*{PARAM_FILE.ev_au_conv}) notitle lw {lw_1:3.1f} lc rgbcolor "#000000" pt 6 ps 2.0 w p\n\n'
	return gnuplot_state

#----------------------------------------------------------------------------------------------------------------------------#
def WRITE_SH_STATE_GP(nmstates, state_list, t_label, datafile, time_restart, restart):
	singlets  = 0; triplets = 0
	lw_1 = 3.0;	lw_2 = 6.0
	# We assign the spin at each state reading the information from the SHARC out file
	with open(datafile, "r") as FILE_MCH:
		for i, lisline in enumerate(FILE_MCH):
			if i > 2:
				break
	lisline = lisline.split()                                       # The lisline will contain the result at t = 0

	gnuplot_state = f' plot "{datafile}" u {t_label}:4 title "Total Energy" lw {lw_1:6.2f} lc rgbcolor "#000000" w l, \\\n'
	for i in range(nmstates):
		if int(float(lisline[4 + nmstates + i])) == 0 :				# The spin of the i-th state is zero (singlet)
			if singlets < 4:				# The first 4 singlets are displyed in blue 
				gnuplot_state += f'  "" u {t_label}:{5+i} title "S_{singlets}" lw {lw_2:6.2f} lt 1 lc rgb "{PARAM_FILE.shadeofblue[singlets]}" w l	, \\\n'
			else:						# The remaining are simply in grey without label
				gnuplot_state += f'  "" u {t_label}:{5+i} notitle              lw {lw_2:6.2f} lt 1 lc rgb "grey" w l	, \\\n'
			singlets	      += 1

		if int(float(lisline[4 + nmstates + i])) == 2 :				# The spin of the i-th state is two (triplets)
			if (triplets < state_list[2]):							# state_list[2] = Number of triplet states
				gnuplot_state += f'  "" u {t_label}:{5+i} title "T_{triplets + 1}" lw {lw_2:6.2f} lt 1 lc rgb "{PARAM_FILE.shadeofgreen[singlets]}" w l	, \\\n'
			else: 													# Plot the title only for one of the three components of the triplet states
				gnuplot_state += f'  "" u {t_label}:{5+i} notitle                  lw {lw_2:6.2f} lt 1 lc rgb "{PARAM_FILE.shadeofgreen[singlets]}" w l	, \\\n'
			triplets	      += 1
# After three triplet (0,1,2) we want reinitilize the counters. Triplet are printed T1x, T2x, ..., T1y, T2y, ..., T1z, ...
# After printing the label for the first three we can stop printing title (stoptitle is initialized at 1 at this point and no other title are printed) 
	gnuplot_state += f' "" u {t_label}:3 notitle lw {lw_1:6.2f} lc rgbcolor "#000000" pt 6 ps 2.0 w p '

	# In case you have restarted the dynamics will be added the plot belonging to the last part of the previous dynamics.
	if restart == True:                                             # This means that the dynamics with SHarc has been restarted from NX.
		gnuplot_state   += '       , \\\n'                      	# We want write so we need to add ,\
		gnuplot_state   += WRITE_SH_STATE_GP_RESTARTED(state_list, time_restart, lisline)
	gnuplot_state   += '\n\n'        
	return gnuplot_state

#----------------------------------------------------------------------------------------------------------------------------#
def WRITE_SH_STATE_GP_RESTARTED(state_list, time_restart, lisline):
	gnuplot_state = ''; singlets = 0;
	lw_1 = 3.0; lw_2 = 5.0;
	datafile = "../RESULTS/en.dat"                   				# For now we assumes that the previus dyn was with NX in the folder ../RESULTS/ This can be modified in the future
	end_dyn = GET_DATA(datafile, 0)
	# The S0 energy of the parent dynamics at the time_restart
	s1_ene = float(subprocess.check_output(['tail', '-' + str(int( (end_dyn - time_restart) * 2 + 1 )), datafile]).split()[2])
	scaling = -(float(lisline[5])/PARAM_FILE.ev_au_conv) + s1_ene                              # the scaling for the parent dynamics will be so that the S1 energies at 
	# time_restart will be exactly the same for both calculation (we will have the line conciding at the same point).
	# print (time_END_OF_DYN, s1_ene, scaling, lisline[5])					# !!5 is the index for energy S1!!
	for i in range(state_list[0]):	# Here the number the singlet but could be a sub set of the number of electronic states in the NX dynamics
		gnuplot_state += f'  "{datafile}" u 1:((${i+2} - {scaling:9.5f})*{PARAM_FILE.ev_au_conv}) notitle lw {lw_2:3.1f} lt 1 lc rgb "{PARAM_FILE.shadeofgrey[singlets]}" w l, \\\n'
		singlets   += 1
	return gnuplot_state

#----------------------------------------------------------------------------------------------------------------------------#
def WRITE_COORDS_AND_BREAKLINE(rangeymax, rangey2min, rangey2max, positionlabel2, time_break, break_reason, input_coord, gnuplot_time_label, label_molecule):
#Plot the second part with multipot
	if 	label_molecule == "HPP":
		gnuplot_coord, y2label, index = WRITE_GEOMETRICAL_CORDINATES_HPP_GP(input_coord, gnuplot_time_label)
	elif 	label_molecule == "BH3NH3":
		gnuplot_coord, y2label, index = WRITE_GEOMETRICAL_CORDINATES_BH3NH3_GP(input_coord, gnuplot_time_label)
	elif	label_molecule == "Pyridine":
		gnuplot_coord, y2label, index = WRITE_GEOMETRICAL_CORDINATES_Pyridine_GP(input_coord, gnuplot_time_label) 
	elif 	label_molecule == "Nucleic_Acid":
		gnuplot_coord, y2label, index = WRITE_GEOMETRICAL_CORDINATES_Nucleic_Acid_GP(input_coord, gnuplot_time_label)
	else:
		print ("\n * Not implemented for molecule * \n", label_molecule)

	gnuplot_final  = ''
	gnuplot_final += '  unset key\n  unset ylabel\n  unset yrange\n  unset ytics\n'
	gnuplot_final += f'  set y2label {y2label}\n  set y2tics\n  set key at {positionlabel2}\n  set y2range[{rangey2min}:{rangey2max}]\n'
	gnuplot_final += gnuplot_coord         								#string is the plot associated with the coordinates analysis
	# Finally we add a vertical line to indicate at which time the dynamics is not valid anymore
	if break_reason != False :
		gnuplot_final += f'\n  set key at 0, {rangey2min} \n'
		gnuplot_final += f'  set parametric\n  plot [t=0:{rangeymax:5.3f}] {time_break:5.3f},t w l lw 2.0 lt 1 lc rgbcolor "#FF0000" title "{break_reason}"'
	gnuplot_final += '\n\nunset multiplot'
	return gnuplot_final



