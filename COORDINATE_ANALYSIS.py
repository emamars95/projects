#!/usr/local/Cluster-Apps/python/3.6.8/bin/python3.6

# THIS script is used to performe advanced coordinates analysis. This is a specific tool to investigate non radiative interaction between the excited states. 
# The first formulation regards the diabatic trapping between n->pi^* state and n'->sigma^* states.

import glob
import sys
import os
import numpy
sys.path.append('/ddn/home/fzzq22/CODE_AND_SCRIPT/PYTHON_COMMON_MODULE/')
import TRAJECTORY_MODULES
import ANALYSIS_MODULES, TOOLS

PWD     	= os.getcwd()
original_stdout = sys.stdout                    # Save a reference to the original standard output

PARAMETER_FILE_NAME     = str(sys.argv[1])
# --------------------------- READING THE PARAMETERS ------------------------------------------- #
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
        TEMPLATE_GEO            = PARAMETER_FILE.readline().rstrip()
        if int( len(TEMPLATE_GEO) ) == 0:
                raise ValueError ('The parameter file lacks some records!')
# --------------------------- END OF READING THE PARAMETERS ------------------------------------ #

# --------------------------- ADDITIONAL  PARAMETERS ------------------------------------------- #
lower_state     = 2
upper_state     = 3
FILE_DATA	= "Trajectory.dat"
NX_TYPEOFDYN	= "/RESULTS/typeofdyn.log"
NX_COORD	= "/RESULTS/COORDINATES.out"
# ---------------------------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------------------------- #
def WRITE_FILES_LABEL(FILE, label):
	FILE.write( "\tTime\t" )
	for l in label:
       		FILE.write( "\t%s veloc" %(l) )
	for l in label:
        	FILE.write( "\t%s coord" %(l) )
	FILE.write("\n" )
	return
# ---------------------------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------------------------- #
def WRITE_FILES_DATA(FILE, TRAJ_NAME, time, GRAD, COORD, index):
	FILE.write("%s\t%9.2f\t" %(TRAJ_NAME, time) )
	for grad in GRAD:
		FILE.write("%9.5f\t" %(grad) )
	for coord in COORD:
		FILE.write("%9.5f\t" %(coord) )
	FILE.write("%s\t" %(index) )
	FILE.write("\n")
	return
# ---------------------------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------------------------- #
def FIND_MIN_GAP(time, TYPE_OF_DYN):
	DE 	= []
	min_index, max_index    = -5 , 5	 
	for t in range(min_index, max_index + 1):
		if t <= 0:
			DE.append(TOOLS.GET_DATA_FROM_STRING(TYPE_OF_DYN, " %6.2f " %(time + t * TIMESTEP), 12) )
		if t > 0:
			DE.append(TOOLS.GET_DATA_FROM_STRING(TYPE_OF_DYN, " %6.2f " %(time + t * TIMESTEP), 12) )
# We save the time corresponding to the minimum value of the energy gap between the two state. argmin give the index of the array.              # 
	#print (time, "    ",DE, "     ", time + (numpy.argmin(DE) + min_index) * TIMESTEP)
	return time + (numpy.argmin(DE) + min_index) * TIMESTEP
# ---------------------------------------------------------------------------------------------- #

# ---------------------- MAIN FUNCTION TO ANALYZE OH DISS -------------------------------------- #
def ANALYSIS_OHDISS(index, COORDINATE_FILE, TYPE_OF_DYN, EVENT):
	COORD		= []
# We from check time - av_index * TIMESTEP to time + (max_index - av_index) * TIMESTEP
	index_OO	= 2		
# Here we want find the point of the adiabatic event with low energy gap. Since this function is called when no jup occurs between 		#
# lower -> upper state the first point is searched looking at the curvature of the O-O bon lenght in time (computed at the 4th order). 		# 
	with open(COORDINATE_FILE, "r" ) as FILE:						# File were the coordinates are stored		#
		for j, line in enumerate(reversed (FILE.readlines() ) ):			# We read the file from the bottom to the top. 	#
			COORD.append( float(line.split()[index_OO - 1]) )			# We append O-O bond lenght			#
# We first look at the region of the configuration space situable (O-O < 1.9). The change in curvature could occurs at very long OO bond 	# 
			if COORD[j] < 1.85:			 				
				time 		= float(line.split()[0]) + 2 * TIMESTEP		# j - 2 where 2 = TIMESTEP * 2			#  
				ddoh            = TOOLS.CURVATURE(COORD, j-2)/TIMESTEP**2	# 0 = O-O bond distance (j-2 -> we compute at the 4th order) 
				if ddoh < 0:							# we break when an inflection point in the O-O bond lenght is found. 
# We refine the point found searcing for the minimum energy gap	between upper and lower state							# 				
					break							# The time is found we break the loop 		# 
# Using the time we compute the velocites and we extract the coordinates. Since the time could be later from the opened file in the previous	#
# part of function we close the file and we opend it again using the GET_VELOC function.							# 			
	GRAD, COORD = GET_VELOC(index, COORDINATE_FILE, TYPE_OF_DYN, time)

	return GRAD, time, COORD								# we pass grad, time, coord. 
# ---------------------------------------------------------------------------------------------- #

# ---------------------- MAIN FUNCTION TO GET VELOCITIES --------------------------------------- #
def GET_VELOC(index, COORDINATE_FILE, TYPE_OF_DYN, time):
	COORD, GRAD     = [], []
	for k in range(0, len(index)):
		COORD.append([])
# Find the effective time when the energy gap is minimum
	time = FIND_MIN_GAP(time, TYPE_OF_DYN)
	with open(COORDINATE_FILE, "r" ) as FILE:
		for j, line in enumerate(reversed (FILE.readlines() ) ):
# Record zero is the time read in FILE. We check if we arrive at two point before to compute the gradient at the 4th order.			#
			if round(float(line.split()[0]), 2) <= round(time + TIMESTEP * 2, 2):							
# We compute the gradient at the 4th order: GRAD[j] requires the values of j-2 j-1 j j+1 and j+2. 						#
				for k in range(0, len(index)):
# We need care with pyr angle. In fact for the gradient we want to know if the pyr angle grow or decrease in the absolute			#
# value, i.e. if the molecule increase or decrease the orbital overlap. 									#
					#if index[k] - 1 == 6:
					#	COORD[k].append( abs(float(line.split()[index[k] - 1])) )
					#else: 
						COORD[k].append( float(line.split()[index[k] - 1]) )
			if round(float(line.split()[0]), 2) == round(time - TIMESTEP * 2, 2):
				for k in range(0, len(index)):
					GRAD.append(- TOOLS.GRADIENT(COORD[k], i=2)/TIMESTEP)
				break
	return GRAD, numpy.array(COORD)[:,2]							# we pass grad,       coord. 
# ---------------------------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------------------------- #
def MAIN():
	ALLNAME 	= TOOLS.sorted_nicely(glob.glob("TRAJ*"))		# All folder in the current directory
	TRAJ_OHDISS     = ANALYSIS_MODULES.GET_TRAJ(FILE_DATA, "OHDISS")        # All traj showing OH release (adiabatic event)
	print("CHECK SCRIPT \n\n")
	print("Folder in which we have observed the OHDISS events\n", TRAJ_OHDISS)
	total_diabatic_trapping 		= 0				# Counter for the total events 
		
	for TRAJ_NAME in ALLNAME:
		# Here just some name (path to the file too) that are used for the analysis
		TYPE_OF_DYN                     = TRAJ_NAME + NX_TYPEOFDYN; COORDINATE_FILE = TRAJ_NAME + NX_COORD
		if os.path.isfile(COORDINATE_FILE):                             # Check if in the folder has been run some dynamics and the dynamics is completed
			# Event is when we observe  a complete cycle of S1 -> S2 and S2 -> S1 crossing.
			EVENT          		= ANALYSIS_MODULES.TRAJECTORY_ISOLATE_CROSSING(lower_state, upper_state, TIMESTEP, TYPE_OF_DYN)
			# Last time step in the NX dynamics.
			BREAK_TIME              = TOOLS.GET_DATA(COORDINATE_FILE, 0)
# OH DISS -------------------------------------------------------------------------------------- #
			if TRAJ_NAME in TRAJ_OHDISS:
				check = False					# If there is some crossing between S1 and S2 during dynamics
				if EVENT:					# If at least one jump from lower -> up state is present
					print (TRAJ_NAME)
					print ("  Event:  ", EVENT)
					for e, t in enumerate(reversed(EVENT)): # REVERSED ORDER
						# Get the O-O bond lenght, search in the COORDINATE_FILE grepping the time t
						OO_lenght	= TOOLS.GET_DATA_FROM_STRING(COORDINATE_FILE, t, 1) 
						# e%2 means that is the entrance time and not the exit time	
						if e%2 == 1 and t > BREAK_TIME - 20: # and OO_lenght < 1.9:	# We take the entrace of the event (1st record)
# must restricted between the actual value of time and 60 fs before the end of the dynamics. Otherwise some records do not match
# we can have jump to S1 and S2 that becomes both n->sigma* after that the OH is released.
							#print ("  Event:  ", EVENT, "  Time entrance  ", t, "  O-O bond:  ", OO_lenght)
							time = t				# Save time of the event
							check = True				# Event found! We associated such event with O-O release.
						elif e%2 == 1 and t <= BREAK_TIME - 20:
							total_diabatic_trapping += 1
					print ("total_diabatic_trapping events: ", total_diabatic_trapping) 
				#if check == True:						# Using it to copute the velocities at the correct point
				#	GRAD, COORD     = GET_VELOC(index, COORDINATE_FILE, TYPE_OF_DYN, time)
				#	print(" - ADIABATIC EVENT FOR " + TRAJ_NAME + " OCCURRED AT TIME "  + str(time))
					#WRITE_FILES_DATA(ADIABATIC_EVENT_FILE, TRAJ_NAME, time, GRAD, COORD, "ADIA")

				#if check == False:						# In case the two state never cross but we have an adiabatic transition.	
				#	GRAD, time, COORD               = ANALYSIS_OHDISS(index, COORDINATE_FILE, TYPE_OF_DYN, EVENT)
				#	print(" - ADIABATIC EVENT FOR " + TRAJ_NAME + " OCCURRED AT TIME "  + str(time))
				#	WRITE_FILES_DATA(ADIABATIC_EVENT_FILE, TRAJ_NAME, time, GRAD, COORD, "ADIA")


# Check for diabatic trapping ----------------------------------------------------------------- #
#			if EVENT:
#				for e, time in enumerate(EVENT):
#					if e%2 == 0 and time < BREAK_TIME - 60:        # We take the entrace of the diabatic event (1st record)
#						GRAD, COORD     = GET_VELOC(index, COORDINATE_FILE, TYPE_OF_DYN, time)
#						print("  * DIABATIC TRAPPING FOR " + TRAJ_NAME + " OCCURRED AT TIME " + str(time))
#						WRITE_FILES_DATA(DIABATIC_EVENT_FILE, TRAJ_NAME, time, GRAD, COORD, "DIAB")
	print(total_diabatic_trapping, len(TRAJ_OHDISS))
	print("averange diabatic trapping before OH ", total_diabatic_trapping/len(TRAJ_OHDISS) )
	return
# ---------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------- #
label,  index		= ANALYSIS_MODULES.CHOSE_LABELS_COORDPLOT(INPUT_COORD)
DIABATIC_EVENT_FILE	= open("DIABATIC_EVENT.dat", "w")
ADIABATIC_EVENT_FILE	= open("ADIABATIC_EVENT.dat", "w")
WRITE_FILES_LABEL(DIABATIC_EVENT_FILE, label)
WRITE_FILES_LABEL(ADIABATIC_EVENT_FILE, label)

MAIN()

DIABATIC_EVENT_FILE.close()	
ADIABATIC_EVENT_FILE.close()
# ---------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------- #

