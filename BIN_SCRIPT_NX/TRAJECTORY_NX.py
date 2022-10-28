#!/usr/bin/env python3

import os
from os.path                import isfile
import glob
import subprocess

from NX_MODULES             import GET_EXCITATION_ENERGY, SUBMIT_TRAJECTORIES, LABEL_TRAJ, GET_TIME_BASED_ON_D1
from TOOLS                  import sorted_nicely, GET_DATA
from TRAJECTORY_MODULES     import GET_MOLECULE_LABEL, READING_PARAMETER_FILE
import PARAM_FILE
from BH3NH3 import CHECK_REACTIVITY_BH3NH3

PWD   = os.getcwd()
hline = "*****************************************************************\n" 

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def CHECK_REACTIVITY_HPP(result_folder, summary, data):
    coordinate_file = result_folder + '/' + PARAM_FILE.coordinate_file
    O_H_INTER_DISTANCE = GET_DATA(coordinate_file, 3)       # Collect O--H distance
    C_O_DOUBLE_BOND = GET_DATA(coordinate_file, 5)          # Collect C=O bond distance
    O_O_PEROXIDE_BOND = GET_DATA(coordinate_file, 1)        # Collect O-O bond distance
    C_O_SINGLE_BOND = GET_DATA(coordinate_file, 7)          # Collect C-O bond distance
     
    if float(O_H_INTER_DISTANCE) > 1.8  and float(C_O_DOUBLE_BOND) > 1.6:        # Condition to observe non-radiative CI 
        summary     += "\t> NON-RADIATIVE CI <"
        data    += "NRCI"
    elif float(O_O_PEROXIDE_BOND) > 1.8 and float(O_H_INTER_DISTANCE) >= 2.0:    # Condition to observe OH release
        summary     += "\t# OH DISSOCIATION  #"
        data     += "OHDISS"
    elif float(C_O_SINGLE_BOND) > 1.8   and float(O_H_INTER_DISTANCE)  < 2.0:     # Condition to O2 release
        summary     += "\t# O2 DISSOCIATION  #"
        data     += "O2DISS"
    elif float(C_O_SINGLE_BOND) > 1.8   and float(O_H_INTER_DISTANCE) >= 2.0:     # Condition to O2H release
        summary  += "\t# O2H DISSOCIATION #"
        data     += "O2HDISS"    
    elif float(O_H_INTER_DISTANCE) < 1.6 :                                        # Condition to have 1,5-Hshift
        summary  += "\t*   1,5 - Hshift   *"
    return summary, data

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def CHECK_REACTIVITY_NRMECI(result_folder, summary, data):
    coordinate_file = result_folder + '/' + PARAM_FILE.coordinate_file
    C_O_DOUBLE_BOND = GET_DATA(coordinate_file, 1)                  # Collect C=O bond distance
    if float(C_O_DOUBLE_BOND) > 1.6:                                # Condition to observe non-radiative CI
        summary += "\t> NON-RADIATIVE CI <"
        data += "NRCI"
    return summary, data

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def TAIL_COORDINATES_FILE(result_folder, line):
    coord_file = result_folder + "/" + PARAM_FILE.coordinate_file
    coord_file_to_use = result_folder + "/" + PARAM_FILE.coordinate_file_to_use
    os.system(f"head -{line} {coord_file} > {coord_file_to_use}")

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def CHECK_REACTIVITY(result_folder, time_traj, summary, data, dictionary):
        # Here we have to check at which molecule we are dealing with. Depending on the molecule the geometrical coordinates can be     #
        # different and therefore, we have to adopt different procedure.   
        dictionary = READING_PARAMETER_FILE(f"{result_folder}/{PARAM_FILE.input_for_traj}")                                                             #
        template_geo = dictionary.get('template_geo')
        which_molecule, molecule_class = GET_MOLECULE_LABEL(template_geo)
        # Now in which_molecule we have the label of the molecule we are dealing with. 
        if   which_molecule == "HPP":
                summary, data = CHECK_REACTIVITY_HPP(result_folder, summary, data)
                restart_folder = glob.glob(result_folder + "../XMS-RESTART-12-9*")[0]      # Name in which the trajectory was restarted for HPP
        elif which_molecule == "PYRONE":
                summary, data = CHECK_REACTIVITY_NRMECI(result_folder, summary, data)
        elif which_molecule == "FORMALDEHYDE":
                summary, data = CHECK_REACTIVITY_NRMECI(result_folder, summary, data)
        elif which_molecule == "ACROLEIN":
                summary, data = CHECK_REACTIVITY_NRMECI(result_folder, summary, data)
        elif which_molecule == "OXALYL_fluoride":
                summary, data = CHECK_REACTIVITY_NRMECI(result_folder, summary, data)
        elif which_molecule == "BH3NH3":
                time_d1, d1 = GET_TIME_BASED_ON_D1(result_folder, 0, time_traj)
                TAIL_COORDINATES_FILE(result_folder, int(time_d1 / 0.5 + 2))                # 1 is the title 1 is time = 0
                summary += f"\tD1 {d1:5.4f} at TIME {time_d1:5.1f} fs"
                coordinate_file = result_folder + '/' + PARAM_FILE.coordinate_file_to_use
                summary, data = CHECK_REACTIVITY_BH3NH3(coordinate_file, summary, data)
        else: 
            raise ValueError (f'Value not recognized in {template_geo}')
        return summary, data

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def COPY_FILE(traj_name, result_folder, file_to_copy, time_traj, path_to_inputfile):
    os.system(f"cp {path_to_inputfile}/{file_to_copy} {result_folder}")                      # Copy INPUT file for PLOT_TRAJ.py
    os.system(f"sed -i 's/traj1/{traj_name}/' {result_folder}/{file_to_copy}")               # We update the INPUT files with
    if "zoom" in file_to_copy:                                    # If it is the zoom INPUT we also modify the maxxrange and
        os.system(f"sed -i '3s/0/{str(time_traj- 100)}/' {result_folder}/{file_to_copy}")    # We update the INPUT files with minxrange.
        os.system(f"sed -i '4s/0/{str(time_traj)}/'      {result_folder}/{file_to_copy}")    # We update the INPUT files with maxxrange.

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def GENERATE_D1_FILE(result_folder):
    file_moldyn = f'{result_folder}/../moldyn.log'
    dictionary = READING_PARAMETER_FILE(f"{result_folder}/{PARAM_FILE.input_for_traj}")
    d1file = open(PARAM_FILE.d1_file, 'w')
    i = 0; timestep = dictionary.get('time_step')
    with open(file_moldyn, 'r') as moldyn:
        for line in moldyn:
            if 'D1 diagnostic for MP2:' in line:
                time = timestep * i
                d1file.write(f'{time:5.3f}\t{float(line.split()[4]):6.4f}')                 # 4 is the location where to find the D1 value along the dynamics
                i += 1

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def PLOT_TRAJ_FINISHED(traj_name, result_folder, time_traj, path_to_inputfile):
    print(f'{traj_name}\t is just finished. It will be fully analyzed automatically.\n')
    COPY_FILE(traj_name, result_folder, PARAM_FILE.input_for_traj, time_traj, path_to_inputfile)        # We modify the two file changing name of the trajectories and the time
    os.system(f"bash {PARAM_FILE.plot_traj_script} {PARAM_FILE.input_for_traj}")                        # RUN our script to generate trajectory plots.
    if time_traj > 100:
        COPY_FILE(traj_name, result_folder, PARAM_FILE.input_for_zoom, time_traj, path_to_inputfile)
        os.system(f"bash {PARAM_FILE.plot_traj_script} {PARAM_FILE.input_for_zoom} &>/dev/null")        # RUN our script to generate the trajectory of the last part of the dynamics.    
    os.system(f'touch {result_folder}/{PARAM_FILE.dont_analyze_file}')                                  # We write the file to not analyze the folder again   
    GENERATE_D1_FILE(result_folder)
    os.chdir(PWD)

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def CHECK_TRAJECOTRY(traj_name, traj_folder, result_folder, path_to_inputfile):
    # The two string are initialized with the name of the trajectory.
    print(f"{PARAM_FILE.bcolors.OKBLUE}*****  The dynamics of {traj_name:<10} is checked         *****\n{PARAM_FILE.bcolors.ENDC}") 
    summary = str(traj_name) + "\t"                                             # We add the name of the trajectory at the first column
    data = str(traj_name) + "\t"
    data += GET_EXCITATION_ENERGY(PWD + "/makedir.log", traj_name) + "\t"       # We collect the excitation energy from the makedir.log file
    time_traj = GET_DATA(result_folder + "/en.dat", 0)                          # Collect TRAJ time (record 0) from the en.dat file

    error_signal, stop_signal = False, False
    # Read from moldyn.log if the dynamics is finished without errors
    try:     
        error_signal    = subprocess.check_output('grep "::ERROR::" %s/moldyn.log ' % (traj_folder), shell = True).decode('ascii')
    except: pass
    # Read from moldyn.log if the dynamics is finished without errors
    try:    
        stop_signal    = subprocess.check_output('grep "moldyn.pl: End of dynamics" %s/moldyn.log ' % (traj_folder), shell = True).decode('ascii')
    except:    pass

    if error_signal:                                        # DYNAMICS NOT FINISHED (ERROR!)
        summary  += "*  ::ERROR::  *\t"
        data     += "ERROR"
    elif stop_signal:                                       # DYNAMICS IS finished NORMALLY!
        if not isfile(f'{result_folder}/{PARAM_FILE.dont_analyze_file}'):                 # MAKE PLOTS if the file PARAM_FILE.dont_analyze_file is not present
            PLOT_TRAJ_FINISHED(traj_name, result_folder, time_traj, path_to_inputfile)
            summary += f"* JUST FINISHED *\t{float(time_traj):8.2f} fs"      
        else:    
            summary += f"FINISHED AT {float(time_traj):6.1f} fs"                        # The plots will be not generated again
            if isfile(result_folder + '/' + PARAM_FILE.error_dyn):                      # If the error file (due energy discontinuity) is present in the folder
                summary += "\t ENERGY DISCONTINUITY"    
                data += "ENERGY_DISCONTINUITY"
            else: 
                summary, data = CHECK_REACTIVITY(result_folder, time_traj, summary, data)
    else:
        summary  += "   RUNNING   \t%8.2f fs"                %(float(time_traj))
        data     += "RUNNING"    
    return summary, data

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def ROUTINE_DYNAMICS(allname, summary_file, traj_file, folder, path_to_inputfile):
    import sys
    summary_file = open(summary_file, 'w')
    traj_file = open(traj_file, 'w')
    # For the folder present in PWD we enter sequentially in each of them
    for traj_name in allname:
        traj_folder = f'{PWD}/{traj_name}/' 
        result_folder = glob.glob(traj_folder + folder)
        if result_folder:
            os.chdir(traj_folder)                 
            summary, data = CHECK_TRAJECOTRY(traj_name, traj_folder, result_folder[0], path_to_inputfile)    
            summary_file.write(summary + '\n')    
            traj_file.write(data + '\n')   
            sys.exit()
    traj_file.close()      
    summary_file.close()
   
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# Subroutine to check the dynamics outcomes
def CHECK_DYNAMICS():
    allname = sorted_nicely(glob.glob("TRAJ*"))
    print (hline)
    print ("*****             The dynamics will be checked              *****\n")
    print (hline) 
    folder = 'RESULTS/'
    ROUTINE_DYNAMICS(allname, PARAM_FILE.summary_file, PARAM_FILE.traj_file, folder, path_to_inputfile = PWD)
    print (hline)
    print ("*****       The restarted dynamics will be checked         *****\n")
    print (hline) 
    folder = 'UMP2*/RESULTS/'
    path_to_inputfile = '/ddn/home/fzzq22/CODE_AND_SCRIPT/TEMPLATE_RESTARTs/NX_UMP2'
    ROUTINE_DYNAMICS(allname, PARAM_FILE.summary_file_restart, PARAM_FILE.traj_file_restart, folder, path_to_inputfile)

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# Subroutine to submit some dynamics
def SUBMIT_DYNAMICS():
    if not isfile(PARAM_FILE.to_submit_file):                    # If this file does not exist we ask if they want label the trajectory to submit
        # Labeling means to chose a subgroup of trajectory to submit based on random number generator
        labeling = input("Do you want label the trajectory to submit ? (Y)              ")
        # If the user want to label trajectories then we ask the the variable to compute the probability: wanted_traj/total_traj
        # Higher is this probability (0 < p < 1) higher is the proportion sumitted vs not submitted
        if labeling.upper() == "Y":
            default_wanted_traj = 10 
            wanted_traj = input(f"How many trajectory you want? ({default_wanted_traj:5.0f} default) ")
            if not wanted_traj: 
                wanted_traj = default_wanted_traj                  # Default value
            default_total_traj = 20+1
            total_traj = input(f"How many trajectory in total? ({default_total_traj:5.0f} default) ")
            if not total_traj:
                total_traj = default_total_traj
            print(f"Number of traj requested: {wanted_traj} and number of total trajectories: {total_traj}")
            LABEL_TRAJ(PWD, wanted_traj, total_traj)
    SUBMIT_TRAJECTORIES(PWD)

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def main():
    choice = input("Do you want submit DYNAMICS? (y or n)                            ")  
    if   choice.upper() == "Y":        
        SUBMIT_DYNAMICS()
    elif choice.upper() == "N":
        CHECK_DYNAMICS()
    else:
        print  (" Chose Y or N, lower characters are accepted                     \n")
        main()
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
if __name__ == '__main__':
    print ('\n')
    print (hline)
    print (" This script allows you to submit the dynamics in NX or to check   ")
    print (" the evolution of the trajectories. The program will automatically ")
    print (" plots and summary of the dynamics                                 ")
    print ('\n')
    print (hline)
    print ("\n")
    main() 
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#          
