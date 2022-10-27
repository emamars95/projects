#!/usr/bin/env python3

import os
from os.path                import isfile
import glob
import subprocess

from NX_MODULES             import GET_EXCITATION_ENERGY, SUBMIT_TRAJECTORIES, LABEL_TRAJ, GET_TIME_BASED_ON_D1
from TOOLS                  import sorted_nicely, GET_DATA
from TRAJECTORY_MODULES     import GET_MOLECULE_LABEL, READING_PARAMETER_FILE
import PARAM_FILE

PWD   = os.getcwd()
hline = "*****************************************************************\n" 

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def COPY_FILE(traj_name, result_folder, file_to_copy, time_traj, where_file_to_copy):
    os.system(f"cp {where_file_to_copy}/{file_to_copy} {result_folder}")                     # Copy INPUT file for PLOT_TRAJ.py
    os.system(f"sed -i 's/traj1/{traj_name}/' {result_folder}/{file_to_copy}")               # We update the INPUT files with
    if "zoom" in file_to_copy:                                    # If it is the zoom INPUT we also modify the maxxrange and
        os.system(f"sed -i '3s/0/{str(time_traj- 100)}/' {result_folder}/{file_to_copy}")    # We update the INPUT files with minxrange.
        os.system(f"sed -i '4s/0/{str(time_traj)}/'      {result_folder}/{file_to_copy}")    # We update the INPUT files with maxxrange.

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def CHECK_RESTARTED_DYNAMICS_HPP(restart_folder, summary):
    method, time_restart = os.path.basename(os.path.normpath(restart_folder)).split("_")
    d1_file  = "/d1_" + str(time_restart) + "fs.tmp"
    d1_time_restart = GET_DATA(restart_folder + d1_file, 4)  # Extract the d1 value at the restart time
    summary += "\t RESTARTED AT : %8.2f fs with d1 : %s" %(time_restart, d1_time_restart)
    return summary

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
def CHECK_REACTIVITY_BH3NH3(coordinate_file, summary, data):
    check = False
    B_N_BOND             = GET_DATA(coordinate_file, 1)       # Collect B-N bond distance
    if float(B_N_BOND) > 2.0:                                               
        summary += "\t> B-N DISS < (%3.3f)" %(B_N_BOND)
        data += "BNDISS"
        check = True
    if not "BNDISS" in data: 
        summary  += "\t\t\t"
    # We collect all 3 B-H and N-H bonds in two arrays
    LONGER_N_H_BOND        = 0;
    for index in range(2,5):
        N_H_BOND    = float(GET_DATA(coordinate_file, index))
        if N_H_BOND > LONGER_N_H_BOND: LONGER_N_H_BOND = N_H_BOND
        if N_H_BOND > 1.45:                            # N-H bond for diss
            summary  += "\t> N-H DISS < (%3.3f)" %(N_H_BOND)  
            data     += "NHDISS"
            check = True
    if not "NHDISS" in data:    
        summary    += "\t\t\t"
    for index in range(2,5):
        B_H_BOND        = float(GET_DATA(coordinate_file, index + 3))
        if B_H_BOND > 1.60:                            # B-H bond for diss
            summary  += "\t> B-H DISS < (%3.3f)" %(B_H_BOND)
            data     += "BHDISS"
            check = True
    if not check:
        summary += f"\tUNDERTERMINED"
        data += 'NOTDETER'
    return summary, data

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def TAIL_COORDINATES_FILE(result_folder, line):
    coord_file = result_folder + "/" + PARAM_FILE.coordinate_file
    coord_file_to_use = result_folder + "/" + PARAM_FILE.coordinate_file_to_use
    os.system(f"head -{line} {coord_file} > {coord_file_to_use}")

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def CHECK_REACTIVITY(traj_name, result_folder, time_traj, summary, data, data_restart):
        # Here we have to check at which molecule we are dealing with. Depending on the molecule the geometrical coordinates can be     #
        # different and therefore, we have to adopt different procedure.                                                                #
        *binx, template_geo = READING_PARAMETER_FILE("%s/%s" %(result_folder, PARAM_FILE.input_for_traj))
        which_molecule, molecule_class = GET_MOLECULE_LABEL(template_geo)
        # Now in which_molecule we have the label of the molecule we are dealing with. 
        if   which_molecule == "HPP":
                summary, data = CHECK_REACTIVITY_HPP(result_folder, summary, data)
                restart_folder = glob.glob(result_folder + "../XMS-RESTART-12-9*")[0]      # Name in which the trajectory was restarted for HPP
                summary = CHECK_RESTARTED_DYNAMICS_HPP(restart_folder, summary)
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

                restart_folder = glob.glob(result_folder + "../*UMP2*")                     # Name in which the trajectory was restarted for HPP
                if restart_folder:
                    result_folder = restart_folder[0] + '/RESULTS/'
                    coordinate_file = result_folder + PARAM_FILE.coordinate_file
                    PLOT_TRAJ_FINISHED(traj_name, result_folder, time_traj, PARAM_FILE.BH3NH3.restart_template)
                    *binx, data_restart = CHECK_REACTIVITY_BH3NH3(coordinate_file, summary, data_restart)
        else: 
            raise ValueError (f'Value not recognized in {template_geo}')
        return summary, data, data_restart

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def PLOT_TRAJ_FINISHED(traj_name, result_folder, time_traj, where_file_to_copy):
    print(f'{traj_name}\t is just finished. It will be fully analyzed automatically.\n')
    os.chdir(result_folder)
    COPY_FILE(traj_name, result_folder, PARAM_FILE.input_for_traj, time_traj, where_file_to_copy)       # We modify the two file changing name of the trajectories and the time
    os.system(f"{PARAM_FILE.plot_traj_script} {PARAM_FILE.input_for_traj}")                             # RUN our script to generate trajectory plots.
    if time_traj > 100:
        COPY_FILE(traj_name, result_folder, PARAM_FILE.input_for_zoom, time_traj, where_file_to_copy)
        os.system(f"{PARAM_FILE.plot_traj_script} {PARAM_FILE.input_for_zoom} &>/dev/null")             # RUN our script to generate the trajectory of the last part of the dynamics.
    os.system(f'touch {result_folder}/{PARAM_FILE.dont_analyze_file}')                                  # We write the file to not analyze the folder again
    os.chdir(PWD)

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def CHECK_TRAJECOTRY(traj_name, traj_folder, result_folder):
    # The two string are initialized with the name of the trajectory.
    print(f"{PARAM_FILE.bcolors.OKBLUE}*****  The dynamics of {traj_name:<10} is checked         *****\n{PARAM_FILE.bcolors.ENDC}") 
    summary = str(traj_name) + "\t"                                             # We add the name of the trajectory at the first column
    data = str(traj_name) + "\t"
    data += GET_EXCITATION_ENERGY(PWD + "/makedir.log", traj_name) + "\t"       # We collect the excitation energy from the makedir.log file
    data_restart = data

    time_traj = GET_DATA(result_folder + "/en.dat", 0)                          # Collect TRAJ time (record 0) from the en.dat file

# This section is dedicated in case the file DONT_ANALYZE is found in the RESULT folder. This file is created after that plots are generated    #
# and the excited state dynamics is fully stopped. In such cases, we do not want to plot them again. However, maybe we want restart the ground  #
# state dynamics.  

    if isfile(result_folder + '/' + PARAM_FILE.dont_analyze_file):      # If the file is present in the folder
        summary += f"FINISHED AT {float(time_traj):6.1f} fs"                    # The plots will be not generated again
        if isfile(result_folder + '/' + PARAM_FILE.error_dyn):          # If the error file (due energy discontinuity) is present in the folder
            summary += "\t ENERGY DISCONTINUITY"
            data += "ENERGY_DISCONTINUITY"
        else: 
            summary, data, data_restart = CHECK_REACTIVITY(traj_name, result_folder, time_traj, summary, data, data_restart)

# This section is dedicated in case the file DONT_ANALYZE is NOT found in the result folder. In this cases the dynamics is not stopped yet    #
# or at least it is just finished. In this last case, the file DONT_ANALYZE will be created, warning that is not necessary to analyze         #
# the data anymore. In case the plot has never been generated, the input files are also copied in the REUSULT folder.                #        

    else:
        ERROR_SIGNAL        = False; STOP_SIGNAL        = False    # Logical varaibles to indicate if an error is find in the NX dynamics
        # Read from moldyn.log if there is an error
        try:     ERROR_SIGNAL    = subprocess.check_output('grep "::ERROR::" %s/moldyn.log ' % (traj_folder), shell = True).decode('ascii')
        except:    pass
        # Read from moldyn.log if the dynamics is finished without errors
        try:    STOP_SIGNAL    = subprocess.check_output('grep "moldyn.pl: End of dynamics" %s/moldyn.log ' % (traj_folder), shell = True).decode('ascii')
        except:    pass
            # IF THERE IS AN ERROR IN A TRAJECOTRY NOT ALREADY CHECKED
        if ERROR_SIGNAL:
            summary  += "*  ::ERROR::  *\t"
            data     += "ERROR"
        # JUST FINISHED TRAJECTORY! IT HAS TO BE PLOTTED AND ANALYZED
        elif STOP_SIGNAL:                                    # If the dynamics is just finished!
            PLOT_TRAJ_FINISHED(traj_name, result_folder, time_traj, PWD)
            summary += f"* JUST FINISHED *\t{float(time_traj):8.2f} fs"      
            os.system('grep "d1 diagnostic for MP2:" ' + traj_folder + '/moldyn.log | awk \'{printf "%9.2f\\t%s\\n", counter/2, $5; counter++}\' > d1_values')
        # STILL RUNNING.
        else:                                        # Otherwise the dynamics is still running
            summary  += "   RUNNING   \t%8.2f fs"                %(float(time_traj))
            data     += "RUNNING"    
    return summary, data, data_restart

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def ROUTINE_DYNAMICS(allname, summary_file, traj_file, folder):
    # For the folder present in PWD we enter sequentially in each of them
    for traj_name in allname:
        traj_folder = f'{PWD}/{traj_name}/' 
        result_folder = traj_folder + folder
        if os.path.isdir(result_folder):                        # If some dynamics has been restarted then we check the dynamics output
           os.chdir(traj_folder)                 
           summary, data, data_restart = CHECK_TRAJECOTRY(traj_name, traj_folder, result_folder)    
           summary_file.write(summary + '\n')    
           traj_file.write(data + '\n')           
    traj_file.close()      
    summary_file.close()

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# Subroutine to check the dynamics outcomes
def CHECK_DYNAMICS():
    allname = sorted_nicely(glob.glob("TRAJ*"))
    print (hline)
    print ("*****             The dynamics will be checked              *****\n")
    print (hline) 
    summary_file = open(PARAM_FILE.summary_file  , 'w')
    traj_file = open(PARAM_FILE.traj_file, 'w')
    folder = 'RESULTS/'
    ROUTINE_DYNAMICS(allname, summary_file, traj_file, folder)
    print (hline)
    print ("*****       The restarted dynamics will be checked         *****\n")
    print (hline) 
    summary_file = open(PARAM_FILE.summary_file_restart, 'w')
    traj_file = open(PARAM_FILE.traj_file_restart, 'w')
    folder = 'UMP2*/RESULTS/'
    ROUTINE_DYNAMICS(allname, summary_file, traj_file, folder)

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
