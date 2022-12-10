#!/bin/usr/env python3 
from TOOLS import GET_DATA

class BH3NH3:
    # Name of the molecule
    molecule = "BH3NH3"
    # Number or atoms
    natoms	= 8
    # Type of distinct (expected) reaction channel. Here BHdiss is expected to give the same result as NHdissBHdiss
    dic_reactivity = {
        "BNDISS":       [0, "BH_3 + NH_3"], 
        "BHDISS":       [1, "H_2 + BH_2-NH_2"],
        "NHDISS":       [2, "N-H diss"],
        "BHDISSBHDISS": [3, "H_2 + BH-NH_3"],
        "NHDISSBHDISS": [1, "H_2 + BH_2-NH_2"],
        "NHDISSBHDISSBHDISS": [3, "H_2 + BH-NH_3"],
        "NHDISSNHDISSBHDISSBHDISS": [4, "2H_2 + BH-NH"], 
        "NHDISSNHDISSBHDISSBHDISSBHDISS": [4, "2H_2 + BH-NH"], 
        "NHDISSBHDISSBHDISSBHDISS": [4, "2H_2 + BH-NH"], 
        "BNDISSBHDISS": [0, "BH_3 + NH_3"],
        "BNDISSBHDISSBHDISS": [5, "H_2 + BH + NH_3"]
    }
    # The ref_path must contain the files that will be used as the template for the dynamics
    folder_restart = "UMP2-RESTART"                       
    # Restart Folder Template
    restart_template = "/ddn/home/fzzq22/CODE_AND_SCRIPT/TEMPLATE_RESTARTs/BH3NH3-NX_UMP2/"
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
    def CHECK_REACTIVITY_BH3NH3(coordinate_file, summary, data):
        check = False
        B_N_bond = GET_DATA(coordinate_file, 1)             # Collect B-N bond distance
        # B-N dissociation
        if float(B_N_bond) > 2.0:                                               
            summary += "\t> B-N DISS < (%3.3f)" %(B_N_bond)
            data += "BNDISS"
            check = True
        if not "BNDISS" in data: 
            summary  += "\t\t\t"
        # We collect all 3 B-H and N-H bonds in two arrays
        longer_N_H_bond        = 0
        # N-H dissociation 
        for index in range(2,5):
            N_H_bond    = float(GET_DATA(coordinate_file, index))
            if N_H_bond > longer_N_H_bond: longer_N_H_bond = N_H_bond
            if N_H_bond > 1.45:                            # N-H bond for dissdata
                summary  += "\t> N-H DISS < (%3.3f)" %(N_H_bond)  
                data     += "NHDISS"
                check = True
        if not "NHDISS" in data:    
            summary    += "\t\t\t"
        # B-H dissociation
        for index in range(2,5):
            B_H_bond        = float(GET_DATA(coordinate_file, index + 3))
            if B_H_bond > 1.60:                            # B-H bond for diss
                summary  += "\t> B-H DISS < (%3.3f)" %(B_H_bond)
                data     += "BHDISS"
                check = True
        # Reaction is not determined
        if not check:
            summary += f"\tUNDERTERMINED"
            data += 'NOTDETER'
        return summary, data
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
    def CHECK_REACTIVITY(result_folder: str, summary: str, data: str, time_traj: str, time_validity: str, check: bool) -> tuple[str, str]:
        coordinate_file_to_use = f'{result_folder}/{PARAM_FILE.coordinate_file_to_use}'
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
        summary, data = CHECK_REACTIVITY_BH3NH3(coordinate_file_to_use, summary, data)
        return summary, data


def main():
    pass

if __name__ == "__main__":
    main()