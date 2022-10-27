#!/usr/bin/env python3

from os.path import isfile, isdir
from shutil import rmtree, copy, copytree, move
import sys
import os
import random
import time

from TRAJECTORY_MODULES     import GET_MOLECULE_LABEL, READING_PARAMETER_FILE, COUNTING_STATES, TRAJECTORY_BREAK_NX
import NX_MODULES
import PARAM_FILE

PWD = os.getcwd() + '/'
hline = "*****************************************************************\n" 

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def COPY_FILES(folder_restart, ref_path, file_list):
	# Create the folder
	if isdir(folder_restart):
		rmtree(folder_restart)
		print('removing folder')
	os.mkdir(folder_restart)
	# copy list of files in a folder
	for file_name in file_list:
		file_to_copy = ref_path + file_name
		if isfile(file_to_copy): 
			copy(file_to_copy, folder_restart)
		else:
			copytree(file_to_copy, folder_restart + file_name)

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def MOVE_FILES(folder_restart, file_list):
	# Move list of files in a folder
	for file_name in file_list:
		move(PWD + file_name, folder_restart)

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def PREPARE_FOLDER_TO_RESTART_SHARC(folder_restart, correct_time, timestep, natoms, ref_path):
	COPY_FILES(folder_restart, ref_path, ['input', 'run.sh', 'INPUT_plot_traj.in', 'QM'])
	seed = random.randint(0, 20000000)													# Generate random seed
	os.system(f"sed -i 's/rngseed xxxx/rngseed {seed:i}/g' {folder_restart}/input")		# Update random seed in the input file
	# We extract geom and veloc from the NX dynamics. They will be the initial value to restart the dynamics
	# We obtain the following file: geom, geom.xyz, veloc
	NX_MODULES.MAKE_GEOM_VELOC_NX(correct_time, timestep, natoms)
	MOVE_FILES(folder_restart, ['geom', 'geom.xyz', 'veloc'])
	os.chdir(f'{folder_restart}/QM/INIT_POINT')                     					# Go in INIT_POINT and run BAGEL
	os.system(f'bash MAKE_BAGEL_TEMPLATE.sh {ref_path}/BAGEL_A_sa*.json {folder_restart}/geom.xyz BAGEL')
	os.system('BAGEL BAGEL.json > BAGEL.out')
	os.system('cp BAGEL.archive ../archive.1.init')
#	os.chdir( '%s' %(folder_restart))
#	os.system("nohup ./run.sh &")

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def PREPARE_FOLDER_TO_RESTART_NX(folder_restart, correct_time, timestep, natoms, ref_path):
	COPY_FILES(folder_restart, ref_path, ['control.dyn', 'INPUT_plot_traj.in', 'JOB_AD'])
	# We extract geom and veloc from the NX dynamics. They will be the initial value to restart the dynamics
	NX_MODULES.MAKE_GEOM_VELOC_NX(correct_time, timestep, natoms)
	# After thant geom, geom.xyz and veloc files are created we move them into the main folder
	MOVE_FILES(folder_restart, ['geom', 'geom.xyz', 'veloc'])
	os.chdir(folder_restart)
	os.system(". load-NX.sh && nohup moldyn.pl > moldyn.log &")

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def CHOOSE_FOLDER():
	print('Please write your favourite folder name and be sure to have selected or SHARC or NX')
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

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
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
			print('\n')
			print(hline)
    # --------------------------- READING THE PARAMETERS --------------------------------------------------	#
	(binx, state_list, binx, binx, binx, binx,
    	binx, binx, binx, timestep, template_geo) = READING_PARAMETER_FILE(param_file)
    # -----------------------------------------------------------------------------------------------------	#
	which_molecule, class_molecule = GET_MOLECULE_LABEL(template_geo)
	natoms = class_molecule.natoms
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
	print(f"{PARAM_FILE.bcolors.OKCYAN} At time {correct_time:5.2f} we have D1 {D1:5.3f} which is the under the limit for threshold {PARAM_FILE.thresh_d1:5.3f}{PARAM_FILE.bcolors.ENDC}")
	correct_time    = timebreak
	print(f"{PARAM_FILE.bcolors.OKCYAN} Restarting time: {correct_time:5.2f}{PARAM_FILE.bcolors.ENDC}")

	folder_restart, ref_path = CHOOSE_FOLDER()
	folder_restart  = f'{PWD}/../{folder_restart}_{str(correct_time)}/' 

	#PREPARE_FOLDER_TO_RESTART_SHARC(folder_restart, correct_time, timestep, natoms, ref_path)
	PREPARE_FOLDER_TO_RESTART_NX(folder_restart, correct_time, timestep, natoms, ref_path)

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
if __name__ == '__main__':
	print(hline)
	print('This script allow to restart trajectories from a previus NX dynamics')
	print('\n')
	print(hline)
	main()

