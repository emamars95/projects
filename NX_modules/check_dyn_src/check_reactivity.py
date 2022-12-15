#!/usr/bin/env python3

from TOOLS                      import GET_DATA
from TRAJECTORY_MODULES         import GET_MOLECULE_LABEL, READING_PARAMETER_FILE
from NX_MODULES                 import GET_TIME_BASED_ON_D1
from molecules                  import *
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
def CHECK_REACTIVITY_HPP(result_folder: str, summary: str, data: str) -> tuple[str, str]:
    coordinate_file_to_use = f'{result_folder}/{PARAM_FILE.coordinate_file}'
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
def CHECK_REACTIVITY_NRMECI(result_folder: str, summary: str, data: str) -> tuple[str, str]:
    coordinate_file_to_use = f'{result_folder}/{PARAM_FILE.coordinate_file}'
    C_O_DOUBLE_BOND = GET_DATA(coordinate_file_to_use, 1)           # Collect C=O bond distance
    if float(C_O_DOUBLE_BOND) > 1.6:                                # Condition to observe non-radiative CI
        summary += "\t> NON-RADIATIVE CI <"
        data += "NRCI"
    return summary, data

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def CHECK_REACTIVITY(result_folder: str, time_traj: str, summary: str, data: str, time_validity: str, check: bool) -> tuple[str, str]:
        # Here we have to check at which molecule we are dealing with. Depending on the molecule the geometrical coordinates can be     
        # different and therefore, we have to adopt different procedure.   
        dictionary = READING_PARAMETER_FILE(f"{result_folder}/{PARAM_FILE.input_for_traj}")                                                             
        template_geo = dictionary.get('template_geo')
        which_molecule, molecule_class = GET_MOLECULE_LABEL(template_geo)
        # Now in which_molecule we have the label of the molecule we are dealing with. 
        if   which_molecule == "HPP":
            summary, data = CHECK_REACTIVITY_HPP(result_folder, summary, data)
        elif which_molecule == "PYRONE":
            summary, data = CHECK_REACTIVITY_NRMECI(result_folder, summary, data)
        elif which_molecule == "FORMALDEHYDE":
            summary, data = CHECK_REACTIVITY_NRMECI(result_folder, summary, data)
        elif which_molecule == "ACROLEIN":
            summary, data = CHECK_REACTIVITY_NRMECI(result_folder, summary, data)
        elif which_molecule == "OXALYL_fluoride":
            summary, data = CHECK_REACTIVITY_NRMECI(result_folder, summary, data)
        else:
            try:
                summary, data = molecule_class.CHECK_REACTIVITY(result_folder, summary, data, time_traj, time_validity, check)
            except:
                raise ValueError(f'{molecule_class} Failed. Did you have correctly implemented the new module?')
        return summary, data
