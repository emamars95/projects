#!/usr/bin/env python3

hline = "*****************************************************************\n" 

from subprocess                     import check_output
from os                             import chdir
from glob                           import glob
from os.path                        import isfile
from NX_MODULES                     import GET_EXCITATION_ENERGY
from TOOLS                          import sorted_nicely, GET_DATA
from check_dyn_src.check_reactivity import MAKE_COORDINATES_FILE, CHECK_REACTIVITY
from check_dyn_src.plot_dyn         import PLOT_TRAJ_FINISHED
import PARAM_FILE

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def INITIALIZATION(makedir_file: str, traj_name: str) -> tuple[str, str]:
    # The two string are initialized with the name of the trajectory.
    print(f"{PARAM_FILE.bcolors.OKBLUE}*****  The dynamics of {traj_name:<10} is checked         *****\n{PARAM_FILE.bcolors.ENDC}") 
    # We add the name of the trajectory at the first column
    summary = str(traj_name) + "\t"                                             
    data = str(traj_name) + "\t"
    # We collect the excitation energy from the makedir.log file
    data += GET_EXCITATION_ENERGY(makedir_file, traj_name) + "\t"       
    return summary, data

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def ERROR_IN_DYNAMICS(summary: str, data: str) -> tuple[str, str]:
    summary  += "*  ::ERROR::  *\t"
    data     += "ERROR"
    return summary, data

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def STOP_SIGNAL_IN_DYNAMICS(summary: str, data: str, traj_name: str, result_folder: str, path_to_inputfile: str, time_traj: float, check: bool) -> tuple[str, str]:
    dont_analyze_file = f'{result_folder}/{PARAM_FILE.dont_analyze_file}'
    # MAKE PLOTS if the file PARAM_FILE.dont_analyze_file is not present
    if not isfile(dont_analyze_file):                   
        PLOT_TRAJ_FINISHED(traj_name, result_folder, time_traj, path_to_inputfile)
        summary += f"* JUST FINISHED *\t{time_traj:8.2f} fs"      
    # DO NOT MAKE PLOTS and analyze the dynamics only  
    else:    
        summary += f"FINISHED AT {time_traj:6.1f} fs"                        
        energy_discontinuity_file = f'{result_folder}/{PARAM_FILE.error_dyn}'
        # If the error file (due energy discontinuity) is present in the folder
        if isfile(energy_discontinuity_file):                         
            with open(energy_discontinuity_file, 'r') as fp:
                # Time is the first column of the file
                time_validity = float(fp.readline().split()[0])                                    
            MAKE_COORDINATES_FILE(result_folder, time_validity) 
            summary += f"\tENERGY DISC. at {time_validity} fs"
        # If there is not any energy discontinuity we add a dummy value >> realistic one 
        else:
            time_validity = 100000.00
        summary, data = CHECK_REACTIVITY(result_folder, time_traj, summary, data, time_validity, check)
    return summary, data

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def DYNAMICS_IS_RUNNING(summary: str, data: str, time_traj: float) -> tuple[str, str]:
    summary  += f"   RUNNING   \t{time_traj:8.2f} fs" 
    data     += "RUNNING"  
    return summary, data

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def CHECK_TRAJECOTRY(makedir_file: str, traj_name: str, traj_folder: str, result_folder: str, path_to_inputfile: str, check: bool) -> tuple[str, str]:
    summary, data = INITIALIZATION(makedir_file, traj_name)
    # Collect TRAJ time (record 0) from the en.dat file
    time_traj = float(GET_DATA(result_folder + "/en.dat", 0)) 

    error_signal, stop_signal = False, False
    # Read from moldyn.log if the dynamics is finished without errors
    try:     
        error_signal = check_output('grep "::ERROR::" %s/moldyn.log ' % (traj_folder), shell = True).decode('ascii')
    except: pass
    # Read from moldyn.log if the dynamics is finished without errors
    try:    
        stop_signal = check_output('grep "moldyn.pl: End of dynamics" %s/moldyn.log ' % (traj_folder), shell = True).decode('ascii')
    except:    pass

    # DYNAMICS NOT FINISHED (ERROR!)
    if error_signal:                                        
        summary, data = ERROR_IN_DYNAMICS(summary, data)
    # DYNAMICS finished NORMALLY!
    elif stop_signal:                                      
        summary, data = STOP_SIGNAL_IN_DYNAMICS(summary, data, traj_name, result_folder, path_to_inputfile, time_traj, check)
    # DYNAMICS IS RUNNING
    else:
        summary, data = DYNAMICS_IS_RUNNING(summary, data, time_traj)
  
    return summary, data

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def ROUTINE_DYNAMICS(PWD: str, allname: list[str], summary_file: str, traj_file: str, folder: str, path_to_inputfile: str, check: bool) -> None:
    summary_file = open(f'{PWD}/{summary_file}', 'w')
    traj_file = open(f'{PWD}/{traj_file}', 'w')
    makedir_file = f'{PWD}/makedir.log'
    # For the folder present in PWD we enter sequentially in each of them
    for traj_name in allname:
        chdir(PWD)
        traj_folder = f'{PWD}/{traj_name}/{folder}' 
        result_folder = glob(f'{traj_folder}/RESULTS/')
        if result_folder:
            summary, data = CHECK_TRAJECOTRY(makedir_file, traj_name, traj_folder, result_folder[0], path_to_inputfile, check)    
            summary_file.write(summary + '\n')    
            traj_file.write(data + '\n')   
    traj_file.close()      
    summary_file.close()
   
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# Subroutine to check the dynamics outcomes
def CHECK_DYNAMICS(PWD: str) -> None:
    allname = sorted_nicely(glob("TRAJ*"))
    print (hline)
    print ("*****             The dynamics will be checked              *****\n")
    print (hline)
    folder = '' 
    ROUTINE_DYNAMICS(PWD, allname, PARAM_FILE.summary_file, PARAM_FILE.traj_file, folder, path_to_inputfile = PWD, check = True)
    print (hline)
    print ("*****       The restarted dynamics will be checked         *****\n")
    print (hline) 
    folder = 'UMP2*'
    path_to_inputfile = '/ddn/home/fzzq22/CODE_AND_SCRIPT/TEMPLATE_RESTARTs/NX_UMP2'
    ROUTINE_DYNAMICS(PWD, allname, PARAM_FILE.summary_file_restart, PARAM_FILE.traj_file_restart, folder, path_to_inputfile, check = False)
