#!/usr/bin/env python3

from glob                   import glob
from os                     import chdir, system
from os.path                import isfile
from TOOLS                  import sorted_nicely
from random                 import random 

import PARAM_FILE

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# Chose random trajectories from a bunch s
def LABEL_TRAJ(PWD: str, wanted_traj: int, total_traj: int):
    all_traj = sorted_nicely(glob("TRAJ*"))
    prob = wanted_traj/total_traj
    i = 0
    print(f"The probability to select one trajectory is: {prob:10.2f} and the total number of trajectories are: {len(all_traj):10.2f}")
    print(f"The expected number of trajectory to submit are: {prob*len(all_traj):10.2f}")
    to_submit_file = f"{PWD}/{PARAM_FILE.to_submit_file}"
    fp = open(to_submit_file, 'w')
    fp.write(f"TRAJ n\tRandom number")
    for traj_name in all_traj:
        # Random number between 0 and 1
        rd	= random()			        
        # The probability to be selected is the number of trajs we want devided the total number of trajectories we have
        # Select trajectory depending on the random number
        if (prob > rd):					
            traj_folder	= f'{PWD}/{traj_name}/'
            fp.write(f'{traj_name}\t{rd:10.3f}\n')
            i += 1
    fp.close()
    print(f"The final number of labeled trajectory are: {i}")

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def SUBMIT(traj_name: str):
	system("nohup $NX/moldyn.pl > moldyn.log &")
	print (f"{traj_name} submitted")

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# Submit the trajectory for NX dynamics
def SUBMIT_TRAJECTORIES(PWD: str):
    first_traj      = int(input("Insert first traj to submit   "))		
    last_traj       = int(input("Insert last traj to submit    "))
    print("INITIAL CONDITIONS from ", first_traj, " to ", last_traj, " will be submitted")
    to_submit_file = f"{PWD}/{PARAM_FILE.to_submit_file}"
    traj_to_submit = []
    if isfile(to_submit_file):
        labeling = True 
        fp = open(to_submit_file, 'r')
        for line in fp:
            traj_to_submit.append(line.split()[0]) 
    else:
        labeling = False

    for i in range(first_traj, last_traj + 1):
        traj_name = f"TRAJ{i}"
        traj_folder = f'{PWD}/{traj_name}/'
        # Eneter in the folder
        chdir(traj_folder)
        # If we have previusly labeled the traj to sumbit
        if labeling and (traj_name in traj_to_submit):						
            SUBMIT(traj_name)	  # If the traj is labelled
        elif labeling and (traj_name not in traj_to_submit):
            #print(f'{traj_name} is not submitted because it was not labeled')
            pass
        else:
            # All the trajectory in the range chosen are submitted				  
            SUBMIT(traj_name)     

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def CHECK_INPUT_AND_DEFAULT(input_val: str, default_val: str) -> int:
    default_val = int(default_val)
    if not input_val:
        input_val = default_val
    else: 
        input_val = int(input_val)
    return input_val

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# Subroutine to submit dynamics
def SUBMIT_DYNAMICS(PWD: str):
    if not isfile(PARAM_FILE.to_submit_file):                    # If this file does not exist we ask if they want label the trajectory to submit
        # Labeling means to chose a subgroup of trajectory to submit based on random number generator
        labeling = input("Do you want label the trajectory to submit ? (y/n)               ")
        # If the user want to label trajectories then we ask the the variable to compute the probability: wanted_traj/total_traj
        # Higher is this probability (0 < p < 1) higher is the proportion sumitted vs not submitted
        if labeling.lower() == "y":
            default_wanted_traj = 30
            wanted_traj = input(f"How many trajectory you want? ({default_wanted_traj:5.0f} default) ")
            wanted_traj = CHECK_INPUT_AND_DEFAULT(wanted_traj, default_wanted_traj)
            default_total_traj = 476+295+30+1
            total_traj = input(f"How many trajectory in total? ({default_total_traj:5.0f} default) ")
            total_traj = CHECK_INPUT_AND_DEFAULT(total_traj, default_total_traj)
            print(f"Number of traj requested: {wanted_traj} and number of total trajectories: {total_traj}")
            LABEL_TRAJ(PWD, wanted_traj, total_traj)
        elif labeling.lower() == "n":
            pass
        else:
            SUBMIT_DYNAMICS(PWD)
    SUBMIT_TRAJECTORIES(PWD)
