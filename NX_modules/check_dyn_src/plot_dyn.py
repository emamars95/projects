#!/usr/bin/env python3

from os                 import chdir, system
from datetime           import datetime
from TRAJECTORY_MODULES import READING_PARAMETER_FILE
import PARAM_FILE

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def MODIFY_FILE(file_to_modify: str, time_traj: float):
    system(f"sed -i '3s/0/{time_traj- 100}/' {file_to_modify}")    # We update the INPUT files with minxrange.
    system(f"sed -i '4s/0/{time_traj}/'      {file_to_modify}")    # We update the INPUT files with maxxrange.

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def COPY_FILE(traj_name: str, result_folder: str, file_to_copy: str, path_to_inputfile: str):
    newfp = open(f'{result_folder}/{file_to_copy}', 'w')
    with open(f'{path_to_inputfile}/{file_to_copy}', 'r') as fp:
        for line in fp:
            line = line.replace('traj1', traj_name)
            newfp.write(line)
    newfp.close()

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def MAKE_D1_FILE(result_folder: str):
    file_moldyn = f'{result_folder}/../moldyn.log'
    dictionary = READING_PARAMETER_FILE(f"{result_folder}/{PARAM_FILE.input_for_traj}")
    timestep = dictionary.get('time_step')
    d1file = open(PARAM_FILE.d1_file, 'w')
    i = 0 
    with open(file_moldyn, 'r') as moldyn:
        for line in moldyn:
            if 'D1 diagnostic for MP2:' in line:
                time = timestep * i
                # 4 is the location where to find the D1 value along the dynamics
                d1file.write(f'{time:5.3f}\t{float(line.split()[4]):6.4f}\n')                           
                i += 1

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def PLOT_TRAJ_FINISHED(traj_name: str, result_folder: str, time_traj: float, path_to_inputfile: str):
    print(f'{traj_name}\t is just finished. It will be fully analyzed automatically.\n')
    chdir(result_folder)
    # We modify the two file changing name of the trajectories and the time
    COPY_FILE(traj_name, result_folder, PARAM_FILE.input_for_traj, path_to_inputfile)
    # RUN our script to generate trajectory plots.                   
    system(f"{PARAM_FILE.plot_traj_script} {PARAM_FILE.input_for_traj}")                               
    # We make also a zoom of the dynamics
    if time_traj > 100:
        COPY_FILE(traj_name, result_folder, PARAM_FILE.input_for_zoom, path_to_inputfile)
        MODIFY_FILE(PARAM_FILE.input_for_zoom, time_traj)
        system(f"{PARAM_FILE.plot_traj_script} {PARAM_FILE.input_for_zoom} &>/dev/null")             # RUN our script to generate the trajectory of the last part of the dynamics.   
    fp = open(f'{result_folder}/{PARAM_FILE.dont_analyze_file}', 'w')
    # datetime object containing current date and time
    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    fp.write('PLOT GENERATED the: {dt_string}') 
    fp.close()
    MAKE_D1_FILE(result_folder)

