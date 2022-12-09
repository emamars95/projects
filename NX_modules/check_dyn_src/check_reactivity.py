#!/usr/bin/env python3

from os.path                    import isfile
from TOOLS                      import GET_DATA
from TRAJECTORY_MODULES         import GET_MOLECULE_LABEL, READING_PARAMETER_FILE
from NX_MODULES                 import GET_TIME_BASED_ON_D1
from BH3NH3                     import BH3NH3
from Pyridine                   import Pyridine
import PARAM_FILE

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def MAKE_COORDINATES_FILE(result_folder: str, time: str) -> None:
    coord_file = f'{result_folder}/{PARAM_FILE.coordinate_file}'
    coord_file_to_use = f'{result_folder}/{PARAM_FILE.coordinate_file_to_use}'
    fpnew = open(coord_file_to_use, 'w')
    with open(coord_file, 'r') as fp:
        for i, line in enumerate(fp):
            fpnew.write(line)
            # The time is the first column of the file
            if i > 1 and time == float(line.split()[0]):              
                break 

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def CHECK_REACTIVITY_HPP(coordinate_file_to_use: str, summary: str, data: str) -> tuple[str, str]:
    O_H_INTER_DISTANCE = GET_DATA(coordinate_file_to_use, 3)       # Collect O--H distance
    C_O_DOUBLE_BOND = GET_DATA(coordinate_file_to_use, 5)          # Collect C=O bond distance
    O_O_PEROXIDE_BOND = GET_DATA(coordinate_file_to_use, 1)        # Collect O-O bond distance
    C_O_SINGLE_BOND = GET_DATA(coordinate_file_to_use, 7)          # Collect C-O bond distance
     
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
def CHECK_REACTIVITY_NRMECI(coordinate_file_to_use: str, summary: str, data: str) -> tuple[str, str]:
    C_O_DOUBLE_BOND = GET_DATA(coordinate_file_to_use, 1)           # Collect C=O bond distance
    if float(C_O_DOUBLE_BOND) > 1.6:                                # Condition to observe non-radiative CI
        summary += "\t> NON-RADIATIVE CI <"
        data += "NRCI"
    return summary, data

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def CHECK_REACTIVITY_BH3NH3(coordinate_file_to_use: str, time_traj: str, summary: str, data: str, time_validity: str, check: bool) -> tuple[str, str]:
    # Check the D1 diagonistic. If we want to perform the check the bool variable will be True
    if check:
        # get time where dynamics is still valid based on d1 
        time_d1, d1 = GET_TIME_BASED_ON_D1(result_folder, 0, time_traj)          
        # If the file do not exist or the time at which the d1 overcome the treshold is bigger than the validity time   
        if not isfile(coordinate_file_to_use) or time_d1 < time_validity:
            MAKE_COORDINATES_FILE(result_folder, time_d1)                         
            summary += f'\tD1 {d1:5.4f} at TIME {time_d1:5.1f} fs' 
    # If the check is False we do not perform the D1 check for the dynamics
    else:
        if not isfile(coordinate_file_to_use):
            MAKE_COORDINATES_FILE(result_folder, time_validity) 
    summary, data = BH3NH3.CHECK_REACTIVITY(coordinate_file_to_use, summary, data)
    return summary, data

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def CHECK_REACTIVITY(result_folder: str, time_traj: str, summary: str, data: str, time_validity: str, check: bool) -> tuple[str, str]:
        # Here we have to check at which molecule we are dealing with. Depending on the molecule the geometrical coordinates can be     
        # different and therefore, we have to adopt different procedure.   
        dictionary = READING_PARAMETER_FILE(f"{result_folder}/{PARAM_FILE.input_for_traj}")                                                             
        template_geo = dictionary.get('template_geo')
        which_molecule, molecule_class = GET_MOLECULE_LABEL(template_geo)
        coordinate_file = f'{result_folder}/{PARAM_FILE.coordinate_file}'
        # Now in which_molecule we have the label of the molecule we are dealing with. 
        if   which_molecule == "HPP":
            summary, data = CHECK_REACTIVITY_HPP(coordinate_file, summary, data)
            restart_folder = glob.glob(result_folder + "../XMS-RESTART-12-9*")[0]      # Name in which the trajectory was restarted for HPP
        elif which_molecule == "PYRONE":
            summary, data = CHECK_REACTIVITY_NRMECI(coordinate_file, summary, data)
        elif which_molecule == "FORMALDEHYDE":
            summary, data = CHECK_REACTIVITY_NRMECI(coordinate_file, summary, data)
        elif which_molecule == "ACROLEIN":
            summary, data = CHECK_REACTIVITY_NRMECI(coordinate_file, summary, data)
        elif which_molecule == "OXALYL_fluoride":
            summary, data = CHECK_REACTIVITY_NRMECI(coordinate_file, summary, data)
        elif which_molecule == "BH3NH3":
            coordinate_file = f'{result_folder}/{PARAM_FILE.coordinate_file_to_use}'
            summary, data = CHECK_REACTIVITY_BH3NH3(coordinate_file, time_traj, summary, data, time_validity, check)
        elif which_molecule == "Pyridine":
            summary, data = Pyridine.CHECK_REACTIVITY(coordinate_file, summary, data)
        else: 
            raise ValueError (f'Value not recognized in {template_geo}')
        return summary, data
