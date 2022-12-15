#!/usr/bin/env python3

from os                         import getcwd
from os.path					import isfile, basename
from glob 						import glob
from subprocess					import check_output
from sys						import argv
from TOOLS						import sorted_nicely
import rlcompleter, readline
readline.parse_and_bind('tab:complete')

PWD = getcwd()

def INITIALIZATION() -> tuple[str, str]:
	final_output_zero_veloc_path = argv[1]
	print('Please be sure that your input files are not in the working directory or they will be overwritten')
	veloc_file	= argv[2]
	return final_output_zero_veloc_path, veloc_file

def COUNT_STATES(final_output_zero_veloc_path: str) -> tuple[list, int]:
	nx_file_root = 'final_output.1.'

	final_output_array = sorted_nicely(glob(f'{final_output_zero_veloc_path}/{nx_file_root}*'))
	nstates = int(len(final_output_array))
	return final_output_array, nstates

def COUNT_ATOMS_and_GEOMS(final_output_1: str) -> tuple[int, int]:
	print(f'Reading {final_output_1} file to determine number of atoms and geometries')
	natoms, ngeom = -1, 0
	count = False
	with open(final_output_1, 'r') as fp: 
		for line in fp:
			if count:
				natoms += 1
			if ("Geometry" in line) and (natoms == -1):
				count = True
			if "Velocity" in line:
				count = False
			if "Initial condition" in line:
				ngeom += 1
	print(f"for your final.output input file I have found natoms: {natoms} and ngeoms: {ngeom}")
	return natoms, ngeom

def WRITE_VELOC(fp, velocs_list: list[list], natoms: int):
	# velocs is a list of dimension natoms and each row contain atom, number and velocities in components 
	for atom in velocs_list:
		# for each row we slice into the velocities components
		veloc = atom.split()[1:4]
		for component in veloc:
			fp.write(f"{float(component):13.9f}\t")
		fp.write(f"\n")


def FIX_VELOCITIES(final_output_array: str, veloc_file: str, natoms: int):
	for zero_veloc_file in final_output_array:
		fp_name = f'{PWD}/{basename(zero_veloc_file)}'
		# To avoid overwriting of the files in the working folder 
		if isfile(fp_name):
			fp_name = fp_name + '_corr'
		fp = open(fp_name, 'w')
		counter = 0		
		print(f'fixing velocities for file: {zero_veloc_file}')
		with open(zero_veloc_file, 'r') as fp_read:
			for line in fp_read: 
				if "Velocity in NX input format:" in line:
					fp.write(line)
					counter +=1
					cmd = f'head -{(natoms + 2) * counter} {veloc_file} | tail -{natoms}' 		
					velocs_list = check_output(cmd, shell = True).decode('ascii').splitlines()
					WRITE_VELOC(fp, velocs_list, natoms)
					# we skip the following line of the file since they have been already replaced
					for j in range(1, natoms + 1):
						fp_read.readline()
				else:
					fp.write(line)
				
		fp.close()

def main():
	final_output_zero_veloc_path, veloc_file = INITIALIZATION()
	final_output_array, nstates = COUNT_STATES(final_output_zero_veloc_path)
	#print(final_output_array, nstates)
	natoms, ngeom = COUNT_ATOMS_and_GEOMS(final_output_array[0])
	FIX_VELOCITIES(final_output_array, veloc_file, natoms)
if __name__ == '__main__':
	main()