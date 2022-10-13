#!/usr/bin/env python3

import sys
import os
import random
import time

sys.path.append('/ddn/home/fzzq22/CODE_AND_SCRIPT/PYTHON_COMMON_MODULE')
import TRAJECTORY_MODULES
import NX_MODULES
import PARAM_FILE

PWD 			= os.getcwd()
PARAMETER_FILE_NAME     = str(sys.argv[1])

# --------------------------- READING THE PARAMETERS --------------------------------------------------	#
(CALCULATION, STATE_LIST, binx, binx, binx, binx,
	binx, binx, binx, TIMESTEP, binx) = TRAJECTORY_MODULES.READING_PARAMETER_FILE (PARAMETER_FILE_NAME)
# -----------------------------------------------------------------------------------------------------	#

# Compute the total number of state used in NX along the dynamics				 	#
nmstates, nstates	                = TRAJECTORY_MODULES.COUNTING_STATES(STATE_LIST)
# Compute the time at which the dynamics is not anymore valid, i.e. crossing between S0 and S1		#
TIMEBREAK, BREAKREASON, INIT_ENERGY	= TRAJECTORY_MODULES.TRAJECTORY_BREAK_NX("en.dat", nmstates, TIMESTEP)
print (f"{PARAM_FILE.bcolors.OKCYAN} Dynamics stopped at %5.2f due %s{PARAM_FILE.bcolors.ENDC}" %(TIMEBREAK, BREAKREASON) )
# Refine the time at which the dynamics has to be restarted looking at the d1 before the crossing	#
if BREAKREASON: TIMEBREAK = TIMEBREAK - TIMESTEP
CORRECT_TIME, D1 = NX_MODULES.GET_TIME_BASED_ON_D1_REVERSED(PWD, TIMEBREAK - 15, TIMEBREAK)
#CORRECT_TIME	 = CORRECT_TIME - 30
print (f"{PARAM_FILE.bcolors.OKCYAN} Chosen time at %5.2f with D1 %5.3f{PARAM_FILE.bcolors.ENDC}" %(CORRECT_TIME, D1))

# We prepare the folder where the dynamics will be restarted
def PREPARE_FOLDER_TO_RESTART_SHARC(FOLDER_RESTART):
	# The folder must contain the files that will be used as the template for the dynamics.
	REF_PATH        = "/ddn/home/fzzq22/CODE_AND_SCRIPT/TEMPLATE_RESTARTs/TEMPLATE_BAGEL/"
	# Create the folders
	os.system('rm -rf ' + FOLDER_RESTART + ' && mkdir -p ' + FOLDER_RESTART)
	# Copy the files for the main folder
	INPUT_FILE      = REF_PATH + 'input  '
	RUN_SH          = REF_PATH + 'run.sh '
	plot_input	= REF_PATH + 'INPUT_plot_traj.in '
	os.system('cp %s %s %s   %s' %(INPUT_FILE, RUN_SH, plot_input, FOLDER_RESTART))		# Copy in the restart folder
	seed = random.randint(0, 20000000)							# Generate random seed
	os.system("sed -i 's/rngseed xxxx/rngseed %i/g' %s/input" %(seed, FOLDER_RESTART))	# Update random seed in the input file
	# We extract geom and veloc from the NX dynamics. They will be the initial value to restart the dynamics
	# We obtain the following file: geom, geom.xyz, veloc
	NX_MODULES.MAKE_GEOM_VELOC_NX(CORRECT_TIME, TIMESTEP)
	os.system('mv geom geom.xyz veloc  %s' %(FOLDER_RESTART))				# mv the files from the current folder 
	qm_folder	= REF_PATH + 'QM' 
	os.system('cp -r %s  %s' %(qm_folder, FOLDER_RESTART))					# Copy in the QM restart folder
	os.chdir( '%s/QM/INIT_POINT' %(FOLDER_RESTART))                     			# Go in INIT_POINT and run BAGEL
	os.system('bash MAKE_BAGEL_TEMPLATE.sh %s/BAGEL_A_sa*.json %s/geom.xyz BAGEL' %(REF_PATH, FOLDER_RESTART))
	os.system("BAGEL BAGEL.json > BAGEL.out")
	os.system("cp BAGEL.archive ../archive.1.init")
#	os.chdir( '%s' %(FOLDER_RESTART))
#	os.system("nohup ./run.sh &")
	return

def PREPARE_FOLDER_TO_RESTART_NX(FOLDER_RESTART):
	REF_PATH        = '/ddn/home/fzzq22/CODE_AND_SCRIPT/TEMPLATE_RESTARTs/NX_UMP2/'
#	REF_PATH        = '/ddn/home/fzzq22/CODE_AND_SCRIPT/TEMPLATE_RESTARTs/NX_MP2/'
	# Create the folder
	os.system('rm -rf ' + FOLDER_RESTART + ' && mkdir -p ' + FOLDER_RESTART)
	# Copy the files for the main folder
	control_file	= REF_PATH + 'control.dyn'
	job_ad_folder	= REF_PATH + 'JOB_AD'
	plot_input	= REF_PATH + 'INPUT_plot_traj.in'
	os.system('cp -r %s %s  %s' %(control_file, job_ad_folder, FOLDER_RESTART))
	# We extract geom and veloc from the NX dynamics. They will be the initial value to restart the dynamics
	NX_MODULES.MAKE_GEOM_VELOC_NX(CORRECT_TIME, TIMESTEP)
	# After thant geom, geom.xyz and veloc files are created we move them into the main folder
	os.system('mv %s %s %s  %s' %('geom', 'geom.xyz', 'veloc', FOLDER_RESTART))		# mv the files from the current folder
	os.chdir(FOLDER_RESTART)
	os.system('run-NX.sh moldyn.pl>moldyn.log &')
	time.sleep(1)
	os.system('cp %s %s/%s' %(plot_input, FOLDER_RESTART, 'RESULTS'))
	return

#folder_restart         = "XMS-RESTART-12-9-3s_"                # name used during 2-HPP project
#folder_restart         = "XMS-RESTART-4-8-5s_"
#folder_restart         = "XMS-RESTART-4-7-5s_"
#folder_restart         = "XMS-RESTART-4-3-2s_"

folder_restart         = "UMP2-RESTART_"                       # Name used for BH3NH3 project
#older_restart         = "MP2-RESTART_"
FOLDER_RESTART  = '%s/../%s' %(PWD, folder_restart + str(CORRECT_TIME))

#PREPARE_FOLDER_TO_RESTART_SHARC(FOLDER_RESTART)
PREPARE_FOLDER_TO_RESTART_NX(FOLDER_RESTART)





