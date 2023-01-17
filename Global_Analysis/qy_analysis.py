#!/usr/bin/env python3

import os
import sys
import numpy     as np 
from glob        import glob
from os.path 	 import isfile
from collections import defaultdict, OrderedDict

from TOOLS      import GET_DATA, sorted_nicely
from TRAJECTORY_MODULES import READING_PARAMETER_FILE, WHICH_MOLECULE
from write_qy.write_qy import WRITE_QY_FILE
from plot.plot import PREP_PLOT_QY 
import PARAM_FILE

PWD     = os.getcwd()
# -------------------------------------------------------------------------------------	#
def main():
	COMPUTE_QY()
	#PREP_PLOT_QY()
# -------------------------------------------------------------------------------------	#

# -------------------------------------------------------------------------------------	#
def COMPUTE_QY():
	file_traj = PARAM_FILE.traj_file
	reactivity_excited = GlobalAnalysis().ANALYSIS(file_traj)

	which_molecule, molecule_class = GET_WHICH_MOLECULE(reactivity_excited)
	qy_result = GlobalAnalysis().QY(reactivity_excited, molecule_class)
	WRITE_QY_FILE(qy_result, molecule_class, name_file=PARAM_FILE.qy_file)

	file_traj = PARAM_FILE.traj_file_restart
	reactivity_restarted = GlobalAnalysis().ANALYSIS(file_traj)

	reactivity_final = MERGE_RESTARTED(reactivity_excited, reactivity_restarted, molecule_class)
	qy_result = GlobalAnalysis().QY(reactivity_final, molecule_class)
	WRITE_QY_FILE(qy_result, molecule_class, name_file=PARAM_FILE.qy_file_restart)
	return

# -------------------------------------------------------------------------------------	#
def GET_WHICH_MOLECULE(dictionary: dict) -> str:
	window = list(dictionary.keys())[0]
	state = list(dictionary[window].keys())[0]
	fp = f'{PWD}/{state}/{PARAM_FILE.input_for_traj}'
	in_dictionary = READING_PARAMETER_FILE(fp)
	return WHICH_MOLECULE(in_dictionary)

# -------------------------------------------------------------------------------------	#
def MERGE_RESTARTED(reactivity: dict, reactivity_restarted: dict, molecule_class) -> dict:
	for window, reactivity_window in reactivity.items():
		for state, reactivity_state in reactivity_window.items():
			# key = trajectory label, value = reactivity expected
			#print(window, state)
			for key, value in reactivity_state.items():
				# reactivity expected for the restarted dynamics
				reactivity_restarted_value = reactivity_restarted[window][state].get(key)
				# If the restarted trajectory finished without an error and the reactivity is listed for the molecule
				if reactivity_restarted_value in molecule_class.dic_reactivity:
					# We update the reactivity of the molecule with the restarted value
					reactivity[window][state][key] = reactivity_restarted_value
					#print(key, reactivity_restarted_value)
	return reactivity

# -------------------------------------------------------------------------------------	#
class GlobalAnalysis():	
	def __int__(self):
		pass

	def ANALYSIS(self, file_traj: str) -> dict:
		# WINDOWS/STATES/TRAJECTORIES is the structure of the tree
		reactivity = defaultdict()
		# All folder containing the intial condition are selected
		all_windows = sorted_nicely(glob("SELECTED_INITIAL_CONDITIONS*"))	
		# we iterate over the number of window using the dummy index w						
		for w, window in enumerate(all_windows):
			print (f"{PARAM_FILE.bcolors.OKBLUE} Entering in folder %s{PARAM_FILE.bcolors.ENDC}" %(window))
			reactivity[window] = self.ANALYSIS_WINDOWS(window, file_traj)
			reactivity = self.CHECK_DICT_VALUE(reactivity, window)
		return reactivity

	def ANALYSIS_WINDOWS(self, window: str, file_traj: str) -> dict:
		reactivity_windows = defaultdict()
		# All states present in each initial condition folder are selected 
		all_states = sorted_nicely(glob(f"{window}/TRAJECTORIES*"))
		# We iterate over the number of states 				
		for state in all_states:
			print (f"{PARAM_FILE.bcolors.OKGREEN} Entering in folder {state}{PARAM_FILE.bcolors.ENDC}")
			path_to_file_traj = f"{PWD}/{state}/{file_traj}"
			# File with written the outcomes of the dynamics	
			if isfile(path_to_file_traj):
				# We analyze all trajectories in each state folder									
				reactivity_windows[state] = self.ANALYSIS_STATES(state, path_to_file_traj)
				reactivity_windows = self.CHECK_DICT_VALUE(reactivity_windows, state)
		return reactivity_windows

	def ANALYSIS_STATES(self, state: str, path_to_file_traj: str) -> dict:
		reactivity_states = defaultdict(str)
		fp = open(path_to_file_traj, 'r')
		for line in fp:
			try:
				traj = line.split()[0]      
				outcome = line.split()[3]
				reactivity_states[traj] = outcome
				#print(traj, outcome)
			# In case we don't we print a warning
			except:	
				print(f"{traj: <10} no outcome! You should check what is happening manually")						
		fp.close()
		return reactivity_states

	def CHECK_DICT_VALUE(self, dictionary: dict, key: str) -> dict:
		if dictionary[key] is None:
			del dictionary[key]
		return dictionary

	def QY(self, reactivity: dict, which_molecule_calss) -> tuple(dict, dict):
		print(f'\n\nWe compute QY as requested\n\n')
		# counts dict has key = reactivity and values = number of trajectory showing that pathway
		counts_result = self.COUNTS(reactivity)
		#print(counts_result)
		# qy_result is the dictionary that contains the qy. key = reactivity and values = qy.
		qy_result = {}
		total = {}
		for window, counts_window in counts_result.items():
			print (f"{PARAM_FILE.bcolors.OKBLUE} Energy window {window} eV{PARAM_FILE.bcolors.ENDC}")
			qy_result[window] = defaultdict(int)
			for key, value in counts_window.items():
				descriptors_for_the_key = which_molecule_calss.dic_reactivity.get(key)
				if descriptors_for_the_key:
					# 0 is the index of the reactivity, 1 is the label, ...
					index_for_the_key = descriptors_for_the_key[0]
					qy_result[window][index_for_the_key] += value
				else: 
					print(f'Found the following {key} key that is not present in the molecule class with value {value}')

			total = sum(qy_result[window].values())
			for key, value in qy_result[window].items():
				qy_result[window][key] = value/total 
			qy_result[window] = OrderedDict(sorted(qy_result[window].items()))

		return qy_result, total

	def COUNTS(self, reactivity: dict) -> dict:
		count_result = {}
		for window, reactivity_window in reactivity.items():
			counts = defaultdict(int)
			for state, reactivity_state in reactivity_window.items():
				for key, value in reactivity_state.items():
					counts[value] +=1 

			average_energy = self.AVERAGE_ENERGY(window)
			count_result[average_energy] = counts

		return count_result

	def AVERAGE_ENERGY(self, window: str) -> int:
		try:
			values = window.split('_')[3].split('-')
			max_energy, min_energy = float(values[0]), float(values[1])
			# it is simply the average energy of the window used to plot the value associated with each window								
			average_energy = int((max_energy + min_energy)/2)	
			return average_energy
		except:
			raise ValueError(f"It looks like the format of the folder {window} is not correct")		

if __name__ == "__main__":
	main()