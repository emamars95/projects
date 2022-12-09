#!/bin/usr/env python3 
from TOOLS import GET_DATA

class BH3NH3:
    # Name of the molecule
    molecule	= "BH3NH3"
    # Number or atoms
    natoms	= 8
    # Reactivity of the molecule
    reactivity	= ["BNDISS", "BHDISS", "NHDISS", "BHDISSBHDISS", "NHDISSBHDISS", "NHDISSBHDISSBHDISS"]
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
    # Restart Folder Template
    restart_template = "/ddn/home/fzzq22/CODE_AND_SCRIPT/TEMPLATE_RESTARTs/NX_UMP2"

    def CHECK_REACTIVITY(coordinate_file, summary, data):
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
            if N_H_bond > 1.45:                            # N-H bond for diss
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

def main():
    pass

if __name__ == "__main__":
    main()