#!/usr/local/Cluster-Apps/python/3.6.8/bin/python3.6

import os
import sys
import glob
from math	    import ceil, floor
from os.path 	import isfile
import numpy 	as np
from warnings	import warn

sys.path.append('/ddn/home/fzzq22/CODE_AND_SCRIPT/PYTHON_COMMON_MODULE')
from TOOLS      import GET_DATA, sorted_nicely
from TRAJECTORY_MODULES import  READING_PARAMETER_FILE, GET_MOLECULE_LABEL
import PARAM_FILE
import gnuplot.gnuplot_header

PWD     = os.getcwd()

# ---------------------------------------------------------------------------------------------------------------------------- #
def ANALYSIS_BH3NH3(coord_file, result, color, title, gnuplotstr, TRAJ):
	N_H_BOND        = []; B_H_BOND = [];
	for index in range(2,5):
        	N_H_BOND.append(float(GET_DATA(coord_file, index))    )         # Collect N-H bonds
       		B_H_BOND.append(float(GET_DATA(coord_file, index + 3)))         # Collect B-H bonds
	# Take the numbering of the atom associated with the different bond lenghts. The longer bond is the last one
	index_N_H       = np.argsort(N_H_BOND); index_B_H       = np.argsort(B_H_BOND)
	if   PARAM_FILE.BH3NH3.reactivity[0] 		in result:	lt = 1; TRAJ[0] += 1
	elif PARAM_FILE.BH3NH3.reactivity[1]  		in result:	lt = 2; TRAJ[1] += 1
	elif PARAM_FILE.BH3NH3.reactivity[2]     	in result:      lt = 2; TRAJ[1] += 1
	elif PARAM_FILE.BH3NH3.reactivity[3]            in result:      lt = 3; TRAJ[3] += 1
	elif PARAM_FILE.BH3NH3.reactivity[4] 		in result:	lt = 3; TRAJ[4] += 1
	else: raise ValueError ('Did you have considered all possible pathways?')
	gnuplotstr      += ' "%s" u %i:($6+$7+$8)/3:2 lt %i lw 4 lc rgbcolor "%s" %s, \\\n' %(coord_file, index_N_H[2] + 3, lt, color, title)
	return gnuplotstr, TRAJ

def READ_TRAJFILE(gnuplotstr, PATH, file_traj, w, color, titling, TRAJ):
	(binx, binx, binx, binx, binx,
		binx, binx, binx, binx, binx, TEMPLATE_GEO) = READING_PARAMETER_FILE("%s/%s" %(PATH, PARAM_FILE.input_for_traj))
	WHICH_MOLECULE  = GET_MOLECULE_LABEL(TEMPLATE_GEO)

	with open(file_traj, 'r') as ofile:
		for line in ofile:
			# Write the title as Windons +- 0.5 eV
			if titling:	title = 'title "Window %.1f \\261 0.5 eV"' %(w + 6); titling = False
			else:		title = 'notitle'			# We write no title
			# maybe there is some line in which we have no record for the dynamics outcome
			try:
				traj    = line.split()[0];      outcome = line.split()[3]
				if "RUNNING" in outcome:        outcome	= ''
			# In case we don't we print a warning
			except:	
				print("%10s no outcome! You should check what is happening manually" %(traj))	
				outcome = ''
			if outcome:
				coord_file        = "%s/%s/RESULTS/%s" %(PATH, traj, PARAM_FILE.coordinate_file_to_use)
				if WHICH_MOLECULE == PARAM_FILE.BH3NH3.molecule: gnuplotstr, TRAJ	= ANALYSIS_BH3NH3(coord_file, outcome, color, title, gnuplotstr, TRAJ)
				else: raise ValueError ("Implement Coordinate Analysis")
	return gnuplotstr, titling, TRAJ

def ANALYSIS(object_in):
	if   object_in.plottype == "2D": gnuplotstr = 'plot ';
	elif object_in.plottype == "3D": gnuplotstr = 'splot '; 
	ALL_WINDOWS		= sorted_nicely( glob.glob("SELECTED_INITIAL_CONDITIONS*") )			# Name of the energy windows present in the folder
	QY_FILE = open(PARAM_FILE.qy_file, 'w'); # QY = []
	for w, WINDOW in enumerate(ALL_WINDOWS):								# Nwindows
		print (f"{PARAM_FILE.bcolors.OKBLUE} Entering in folder %s{PARAM_FILE.bcolors.ENDC}" %(WINDOW))
		color 		= PARAM_FILE.viridis[w * int( len(PARAM_FILE.viridis)/len(ALL_WINDOWS) )]
		TRAJ		= np.zeros(10)
		titling		= True										# Only one title per window	
		ALL_STATES	= sorted_nicely( glob.glob("%s/TRAJECTORIES*" %(WINDOW)) )			# For each window we have multiple states	
		for STATE in ALL_STATES:									# Nstate in each window
			print (f"{PARAM_FILE.bcolors.OKGREEN} Entering in folder %s{PARAM_FILE.bcolors.ENDC}" %(STATE))
			PATH		= "%s/%s/"	%(PWD, STATE)						# Path were the files can be found
			file_traj	= PATH + PARAM_FILE.traj_file						# File with written the outcomes of the dynamics
			if isfile(file_traj):									# Traj for each electronic state
				gnuplotstr, titling, TRAJ = READ_TRAJfile(gnuplotstr, PATH, file_traj, w, color, titling, TRAJ)
		energy          = int( (float(WINDOW.split('_')[3].split('-')[0]) + float(WINDOW.split('_')[3].split('-')[1]))/2 )
		QY = TRAJ/np.sum(TRAJ); QY = np.insert(QY, 0, energy, axis=0)
		for el in QY:
			QY_FILE.write("%5.2f\t" %(el))
		QY_FILE.write("\n")
	QY_FILE.close() 
	return gnuplotstr

def QY_BH3NH3(object_in):
	if   object_in.plottype == "2D": gnuplotstr = 'plot ';
	elif object_in.plottype == "3D": gnuplotstr = 'splot ';
	file_to_open	= PWD + '/' + PARAM_FILE.qy_file
	with open(file_to_open, 'r') as qy:
		j = 0; 
		for i in range(0, len(PARAM_FILE.BH3NH3.reactivity)):
			if PARAM_FILE.BH3NH3.duplicate[i] == 1:
				index	= j * int( len(PARAM_FILE.viridis)/sum(PARAM_FILE.BH3NH3.duplicate) )
				gnuplotstr += '"%s" u 1:%i title "%s" with linespoints ls 1 lc rgb "%s",\\\n' %(file_to_open, i+2, PARAM_FILE.BH3NH3.labels[i], PARAM_FILE.viridis[index])
				j += 1 
	return gnuplotstr

def WRITE_SCRIPT(gnuplotstr, outfile):
	gnuplotscript = "%s.gp" %(outfile)
	with open(gnuplotscript, 'w') as FILE_to_WRITE:
		FILE_to_WRITE.write(gnuplotstr)
	os.system("gnuplot " + gnuplotscript)



RANGES          = [0.75, 2.25, 0.75, 3.25, 1, 4]                # Ranges for the object
TICS            = [0.5, 0.5, 0.5]                               # Tics for the object
LABELS          = ["longer N-H Bond length ({\\305})", "<B-H> Bond length ({\\305})", "B-N  Bond length ({\\305})"]     # Labels for the object
OFFSETS         = [0.5, -0.5,  1.75, 0.0, 0.5,  0.5]            # offests label fot the object
KEYS            = [2.0,  3.0,  3.5]                             # Keys position for the object
MARGINS		= [0.98, 0.25, 0.2, 0.8];
# Create the object
#nh3_bh3_coord   = GNUPLOT_SCRIPT("COORDINATEs_ANALYSIS", RANGES, TICS, LABELS, OFFSETS, KEYS, MARGINS, "line")
#gnuplotstr      = nh3_bh3_coord.script() + '\n\n'
#gnuplotstr	+= ANALYSIS(nh3_bh3_coord)
#WRITE_SCRIPT(gnuplotstr, nh3_bh3_coord.out_file)

RANGES          = [5, 9, 0, 1.0, None, None] 	    		# Ranges for the object
TICS            = [1, 0.2, None] 	                        # Tics for the object
LABELS          = ["Energy (eV)", "QY", None] 			# Labels for the object
OFFSETS         = [0.0,  0.5,  1.5, 0.0, None, None]  		# offests label fot the object
KEYS            = [8.5,  0.95,  None]                            # Keys position for the object
MARGINS         = [0.98, 0.125, 0.175, 0.98];
# Create the object
nh3_bh3_qy      = GNUPLOT_SCRIPT("QY", RANGES, TICS, LABELS, OFFSETS, KEYS, MARGINS, "linespoints")
gnuplotstr      = nh3_bh3_qy.script() + '\n\n' 
gnuplotstr      += QY_BH3NH3(nh3_bh3_qy)
WRITE_SCRIPT(gnuplotstr, nh3_bh3_qy.out_file)


if __name__ == "__main__":
	main()
