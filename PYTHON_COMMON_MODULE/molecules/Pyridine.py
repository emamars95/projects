#!/bin/usr/env python3 

from TOOLS import GET_DATA
import PARAM_FILE 

class Pyridine:
    # Name of the molecule
    molecule	= "Pyridine"
    # Number or atoms
    natoms	= 15
    # Type of distinct (expected) reaction channel. Here BHdiss is expected to give the same result as NHdissBHdiss
    dic_reactivity = {
        "BNDISS":               [0, "BH_3 + Py"], 
        "BHDISS":               [1, "H + BH_2-Py"],
        "BHDISSPYRN":           [1, "H + BH_2-Py"],
        "BHDISSPuckering":      [1, "H + BH_2-Py"],
        "BHDISSPYRNPuckering":  [1, "H + BH_2-Py"],
        "PYRN":                 [2, "BH_3-Py"],
        "Puckering":            [2, "BH_3-Py"],
        "PYRNPuckering":        [2, "BH_3-Py"]        
    }
    # The ref_path must contain the files that will be used as the template for the dynamics
    folder_restart = "UMP2-RESTART"                       
    # Restart Folder Template
    restart_template = "/ddn/home/fzzq22/CODE_AND_SCRIPT/TEMPLATE_RESTARTs/PyBH3-NX_UMP2/"
    thresh_d1 = 0.7


    def CHECK_REACTIVITY(result_folder: str, summary: str, data: str, time_traj: str, time_validity: str, check: bool) -> tuple[str, str]:
        coordinate_file = f'{result_folder}/{PARAM_FILE.coordinate_file}'
        check = False
        B_N_bond = GET_DATA(coordinate_file, 1)             # Collect B-N bond distance
        # B-N dissociation
        if float(B_N_bond) > 2.0:                                               
            summary += "\t> B-N DISS < (%3.3f)" %(B_N_bond)
            data += "BNDISS"
            check = True
        if not "BNDISS" in data: 
            summary  += "\t\t\t"
        # We collect all 3 B-H in one array
        # B-H dissociation
        for index in range(2,5):
            B_H_bond        = float(GET_DATA(coordinate_file, index))
            if B_H_bond > 1.60:                            # B-H bond for diss
                summary  += "\t> B-H DISS < (%3.3f)" %(B_H_bond)
                data     += "BHDISS"
                check = True
        if not "BHDISS" in data:
            summary  += "\t\t\t"
        # N pyramidalization
        Pyr_N = GET_DATA(coordinate_file, 9) 
        if abs(float(Pyr_N)) > 7.5:                                               
            summary += "\t> PYR N < (%3.3f)" %(Pyr_N)
            data += "PYRN"
            check = True  
        if not "PYRN" in data:
            summary  += "\t\t\t"  
        # Ring puckering   
        puckering_Q = GET_DATA(coordinate_file, 5)             
        if float(puckering_Q) > 0.175:                                               
            summary += "\t> Puckering < (%3.3f)" %(puckering_Q)
            data += "Puckering"
            check = True    
        # Else
        if not check:
            summary += f"\tUNDERTERMINED"
            data += 'NOTDETER'
        return summary, data

    def WRITE_GEOMETRICAL_CORDINATES(input_coord, gnuplot_time_label):
        gnuplot_coord   = '';   index           = []
        if ( "A" in input_coord ):
                gnuplot_coord   += '  plot "COORDINATES.out" using %s:2 w l lw 5 dt 11 lc rgbcolor "#FF4500" title "N-B bond" axes x1y2'   % (gnuplot_time_label)  # Orange
                y2label         =  '"Bond Length ({\\305})"'
                index.append(2)
        if ( "B" in input_coord ):
                gnuplot_coord += ', \\\n  "" using %s:3 w l lw 5 dt 11 lc rgbcolor "#FFD700" title "B-H bonds" axes x1y2'        % (gnuplot_time_label)
                gnuplot_coord += ', \\\n  "" using %s:4 w l lw 5 dt 11 lc rgbcolor "#FFD700" notitle axes x1y2'                  % (gnuplot_time_label)
                gnuplot_coord += ', \\\n  "" using %s:5 w l lw 5 dt 11 lc rgbcolor "#FFD700" notitle axes x1y2'                  % (gnuplot_time_label)
                index.append(3); index.append(4); index.append(5)
        return gnuplot_coord, y2label, index

def main():
    pass

if __name__ == "__main__":
    main()