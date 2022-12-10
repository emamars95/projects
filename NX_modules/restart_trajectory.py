#!/usr/bin/env python3

from os 			import mkdir, getcwd, chdir, system
from random			import randint
from os.path 		import isfile, isdir
from shutil 		import rmtree, copy, copytree, move


from TRAJECTORY_MODULES     import GET_MOLECULE_LABEL, READING_PARAMETER_FILE, COUNTING_STATES, TRAJECTORY_BREAK_NX
from NX_MODULES				import MAKE_GEOM_VELOC_NX, GET_TIME_BASED_ON_D1
from molecules				import *
import PARAM_FILE

PWD = getcwd() + '/'
hline = "*****************************************************************\n" 

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def COPY_FILES(folder_restart: str, ref_path: str, file_list: str) -> None:
	# Create the folder
	if isdir(folder_restart):
		rmtree(folder_restart)
	mkdir(folder_restart)
	# copy list of files in a folder
	for file_name in file_list:
		file_to_copy = ref_path + file_name
		if isfile(file_to_copy): 
			copy(file_to_copy, folder_restart)
		else:
			copytree(file_to_copy, folder_restart + file_name)

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def MOVE_FILES(folder_restart: str, file_list: str) -> None:
	# Move list of files in a folder
	for file_name in file_list:
		move(PWD + file_name, folder_restart)

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def PREPARE_FOLDER_TO_RESTART_SHARC(folder_restart: str, correct_time: float, timestep: float, natoms: int, ref_path: str):
	COPY_FILES(folder_restart, ref_path, ['input', 'run.sh', 'INPUT_plot_traj.in', 'QM'])
	seed = random.randint(0, 20000000)													# Generate random seed
	system(f"sed -i 's/rngseed xxxx/rngseed {seed:i}/g' {folder_restart}/input")		# Update random seed in the input file
	# We extract geom and veloc from the NX dynamics. They will be the initial value to restart the dynamics
	# We obtain the following file: geom, geom.xyz, veloc
	MAKE_GEOM_VELOC_NX(correct_time, timestep, natoms)
	MOVE_FILES(folder_restart, ['geom', 'geom.xyz', 'veloc'])
	chdir(f'{folder_restart}/QM/INIT_POINT')                     					# Go in INIT_POINT and run BAGEL
	system(f'bash MAKE_BAGEL_TEMPLATE.sh {ref_path}/BAGEL_A_sa*.json {folder_restart}/geom.xyz BAGEL')
	system('BAGEL BAGEL.json > BAGEL.out')
	system('cp BAGEL.archive ../archive.1.init')
#	chdir( '%s' %(folder_restart))
#	system("nohup ./run.sh &")

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def PREPARE_FOLDER_TO_RESTART_NX(folder_restart: str, correct_time: float, timestep: float, natoms: int, ref_path: str) -> None:
	COPY_FILES(folder_restart, ref_path, ['control.dyn', 'INPUT_plot_traj.in', 'JOB_AD'])
	# We extract geom and veloc from the NX dynamics. They will be the initial value to restart the dynamics
	MAKE_GEOM_VELOC_NX(correct_time, timestep, natoms)
	# After thant geom, geom.xyz and veloc files are created we move them into the main folder
	MOVE_FILES(folder_restart, ['geom', 'geom.xyz', 'veloc'])
	chdir(folder_restart)
	system(". load-NX.sh && nohup $NX/moldyn.pl > moldyn.log &")

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def CHOOSE_FOLDER(class_molecule) -> tuple[str: str]:
	# The ref_path must contain the files that will be used as the template for the dynamics
	folder_restart = class_molecule.folder_restart
	restart_template = class_molecule.restart_template
	return folder_restart, restart_template

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def main():
	try:	
		param_file = str(sys.argv[1])
	except:
		param_file = PARAM_FILE.input_for_traj
		if not isfile(PARAM_FILE.input_for_traj):
			raise NameError(f'File {PARAM_FILE.input_for_traj} does not exist')
		else:
			print(f'The parameter are read from the file {PARAM_FILE.input_for_traj}')
			print('\n')
			print(hline)
	dictionary = READING_PARAMETER_FILE(param_file)
	state_list, timestep, template_geo = dictionary.get('states').split(), dictionary.get('time_step'), dictionary.get('template_geo')
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
	correct_time, D1 = GET_TIME_BASED_ON_D1(PWD, 0, timebreak)
    #correct_time	 = correct_time - 30
	print(f"{PARAM_FILE.bcolors.OKCYAN} At time {correct_time:5.2f} we have D1 {D1:5.3f} which is the under the limit for threshold {PARAM_FILE.thresh_d1:5.3f}{PARAM_FILE.bcolors.ENDC}")
	correct_time    = timebreak
	print(f"{PARAM_FILE.bcolors.OKCYAN} Restarting time: {correct_time:5.2f}{PARAM_FILE.bcolors.ENDC}")

	folder_restart, ref_path = CHOOSE_FOLDER(class_molecule)
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

