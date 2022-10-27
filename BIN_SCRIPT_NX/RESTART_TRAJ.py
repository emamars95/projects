#!/usr/bin/env python3

from os.path import isfile
import sys
import os
import random
import time

from TRAJECTORY_MODULES     import GET_MOLECULE_LABEL, READING_PARAMETER_FILE, COUNTING_STATES, TRAJECTORY_BREAK_NX
import NX_MODULES
import PARAM_FILE

PWD = os.getcwd()

# We prepare the folder where the dynamics will be restarted
def PREPARE_FOLDER_TO_RESTART_SHARC(folder_restart, correct_time, timestep, natoms, ref_path):
	# Create the folders
	os.system('rm -rf ' + folder_restart + ' && mkdir -p ' + folder_restart)
	# Copy the files for the main folder
	input_file      = ref_path + 'input  '
	run_sh          = ref_path + 'run.sh '
	plot_input	= ref_path + 'INPUT_plot_traj.in '
	os.system('cp %s %s %s   %s' %(input_file, run_sh, plot_input, folder_restart))		# Copy in the restart folder
	seed = random.randint(0, 20000000)							# Generate random seed
	os.system("sed -i 's/rngseed xxxx/rngseed %i/g' %s/input" %(seed, folder_restart))	# Update random seed in the input file
	# We extract geom and veloc from the NX dynamics. They will be the initial value to restart the dynamics
	# We obtain the following file: geom, geom.xyz, veloc
	NX_MODULES.MAKE_GEOM_VELOC_NX(correct_time, timestep, natoms)
	os.system('mv geom geom.xyz veloc  %s' %(folder_restart))				# mv the files from the current folder 
	qm_folder	= ref_path + 'QM' 
	os.system('cp -r %s  %s' %(qm_folder, folder_restart))					# Copy in the QM restart folder
	os.chdir( '%s/QM/INIT_POINT' %(folder_restart))                     			# Go in INIT_POINT and run BAGEL
	os.system('bash MAKE_BAGEL_TEMPLATE.sh %s/BAGEL_A_sa*.json %s/geom.xyz BAGEL' %(ref_path, folder_restart))
	os.system("BAGEL BAGEL.json > BAGEL.out")
	os.system("cp BAGEL.archive ../archive.1.init")
#	os.chdir( '%s' %(folder_restart))
#	os.system("nohup ./run.sh &")
	return

def PREPARE_FOLDER_TO_RESTART_NX(folder_restart, correct_time, timestep, natoms, ref_path):
	# Create the folder
	os.system('rm -rf ' + folder_restart + ' && mkdir -p ' + folder_restart)
	# Copy the files for the main folder
	control_file	= ref_path + 'control.dyn'
	job_ad_folder	= ref_path + 'JOB_AD'
	plot_input	= ref_path + 'INPUT_plot_traj.in'
	os.system('cp -r %s %s  %s' %(control_file, job_ad_folder, folder_restart))
	# We extract geom and veloc from the NX dynamics. They will be the initial value to restart the dynamics
	NX_MODULES.MAKE_GEOM_VELOC_NX(correct_time, timestep, natoms)
	# After thant geom, geom.xyz and veloc files are created we move them into the main folder
	os.system('mv %s %s %s  %s' %('geom', 'geom.xyz', 'veloc', folder_restart))		# mv the files from the current folder
	os.chdir(folder_restart)
	os.system('run-NX.sh moldyn.pl>moldyn.log &')
	time.sleep(1)
	os.system('cp %s %s/%s' %(plot_input, folder_restart, 'RESULTS'))
	return

def CHOOSE_FOLDER():
	print('Please write your favourite name in the subroutine and be sure to have selected or SHARC or NX')
	# The ref_path must contain the files that will be used as the template for the dynamics

	#folder_restart = "XMS-RESTART-12-9-3s"                # name used during 2-HPP project
	#folder_restart = "XMS-RESTART-4-8-5s"
	#folder_restart = "XMS-RESTART-4-7-5s"
	#folder_restart = "XMS-RESTART-4-3-2s"
	# ref_path = "/ddn/home/fzzq22/CODE_AND_SCRIPT/TEMPLATE_RESTARTs/TEMPLATE_BAGEL/"

	folder_restart = "UMP2-RESTART"                       # Name used for BH3NH3 project
	#folder_restart = "MP2-RESTART"
	ref_path = '/ddn/home/fzzq22/CODE_AND_SCRIPT/TEMPLATE_RESTARTs/NX_UMP2/'
	#ref_path = '/ddn/home/fzzq22/CODE_AND_SCRIPT/TEMPLATE_RESTARTs/NX_MP2/'
	return folder_restart, ref_path

def main():
	try:	
		param_file = str(sys.argv[1])
	except:
		param_file = PARAM_FILE.input_for_traj
		if not isfile(PARAM_FILE.input_for_traj):
			raise NameError(f'File {PARAM_FILE.input_for_traj} does not exist')
			sys.exit()
		else:
			print(f'The parameter are read from the file {PARAM_FILE.input_for_traj}')
    # --------------------------- READING THE PARAMETERS --------------------------------------------------	#
	(calculation, state_list, binx, binx, binx, binx,
    	binx, binx, binx, timestep, template_geo) = READING_PARAMETER_FILE(param_file)
    # -----------------------------------------------------------------------------------------------------	#
	which_molecule = GET_MOLECULE_LABEL(template_geo)
	natoms = PARAM_FILE.which_molecule.natoms
    # Compute the total number of state used in NX along the dynamics				 	#
	nmstates, nstates = COUNTING_STATES(state_list)
    # Compute the time at which the dynamics is not anymore valid, i.e. crossing between S0 and S1		#
	timebreak, breakreason, init_energy	= TRAJECTORY_BREAK_NX("en.dat", nmstates, timestep)
	print(f"{PARAM_FILE.bcolors.OKCYAN} Dynamics stopped at {timebreak:5.2f} due {breakreason}{PARAM_FILE.bcolors.ENDC}")
    # Refine the time at which the dynamics has to be restarted looking at the d1 before the crossing	#
	if breakreason: 
		timebreak = timebreak - timestep
	#correct_time, D1 = NX_MODULES.GET_TIME_BASED_ON_D1_REVERSED(PWD, timebreak - 15, timebreak)
	correct_time, D1 = NX_MODULES.GET_TIME_BASED_ON_D1(PWD, 0, timebreak)
    #correct_time	 = correct_time - 30
	print(f"{PARAM_FILE.bcolors.OKCYAN} At time {correct_time:5.2f} we have D1 {D1:5.3f} which is the limit for threshold {PARAM_FILE.thresh_d1:5.3f}{PARAM_FILE.bcolors.ENDC}")
	correct_time    = timebreak
	print(f"{PARAM_FILE.bcolors.OKCYAN} Chosen time at {correct_time:5.2f}{PARAM_FILE.bcolors.ENDC}")

	folder_restart, ref_path = CHOOSE_FOLDER()
	folder_restart  = f'{PWD}/../{folder_restart}_{str(correct_time)}' 

	#PREPARE_FOLDER_TO_RESTART_SHARC(folder_restart, correct_time, timestep, natoms, ref_path)
	PREPARE_FOLDER_TO_RESTART_NX(folder_restart, correct_time, timestep, natoms, ref_path)

if __name__ == '__main__':
	print('This script allow to restart trajectories from a previus NX dynamics')
	main()

