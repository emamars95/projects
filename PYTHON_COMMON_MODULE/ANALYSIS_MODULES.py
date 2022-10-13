#!/usr/local/Cluster-Apps/python/3.6.8/bin/python3.6

import subprocess

def GET_TRAJ(INPUT_FILE, PATHWAY):					# Here we want to get in a list all traj that shows some reaction pathway
	TRAJ_LIST	= []
	with open(INPUT_FILE, "r") as TRAJ_OUTCOME:
		for line in TRAJ_OUTCOME:
# NAME, EX energy, EX prob, Reactivity. If the reactivity record is missed we simply not take that trajectory into account. 
			if len(line.split()) > 3:
# If the reactivity record is present we check wheter the trajectory shows the reactivity we want. 			
				if line.split()[3] == PATHWAY:
					TRAJ_LIST.append(line.split()[0])
	return TRAJ_LIST						# We return the list with the trajectories. 

#----------------------------------------------------------------------------------------------------------------------------#
def TRAJECTORY_ISOLATE_CROSSING(lower_state, upper_state, TIMESTEP, TYPE_OF_DYN):
        CROSSING_ARRAY          = []
        CROSSING                = False
        with open(TYPE_OF_DYN, "r") as fp:
                for i, lisline in enumerate(fp):
                        lisline = lisline.split()

                        TIMEBREAK = float(lisline[2]) - TIMESTEP        # Consider the previus step (plot at the step before the failure occurs)

                        if lisline[6]   == str(upper_state) and CROSSING == False:
                                CROSSING        = True
                                CROSSING_ARRAY.append(TIMEBREAK)
                        if lisline[6]   == str(lower_state) and CROSSING == True:
                                CROSSING        = False
                                CROSSING_ARRAY.append(TIMEBREAK)

        return CROSSING_ARRAY

#----------------------------------------------------------------------------------------------------------------------------#
def CHOSE_LABELS_COORDPLOT(INPUT_COORD):
	label, index 	= [], []
	if ( "A" in INPUT_COORD):
		label.append("O-O")
		index.append(2)
	if ( "B" in INPUT_COORD):
		label.append("O--H")
		index.append(4)
	if ( "C" in INPUT_COORD):
		label.append("C-C")
		index.append(5)
	if ( "D" in INPUT_COORD):
		label.append("C=O")
		index.append(6)
	if ( "E" in INPUT_COORD):
		label.append("C=O pyr")
		index.append(7)
	if ( "F" in INPUT_COORD):
		label.append("O-H")
		index.append(3)
	if ( "G" in INPUT_COORD):
		label.append("C-O")
		index.append(8)
	return label, index 

