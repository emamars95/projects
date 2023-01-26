#!/bin/usr/env python3 

from TOOLS import GET_DATA
import PARAM_FILE 

class Pyridine_BoricAcid:
    # Name of the molecule
    molecule	= "Pyridine_BoricAcid"
    # Number or atoms
    natoms	= 18
    # Type of distinct (expected) reaction channel. Here BHdiss is expected to give the same result as NHdissBHdiss
    dic_reactivity = {
        "BNDISS":               [0, "B(OH)_3 + Py"],
        "BNDISSPuckering":      [0, "B(OH)_3 + Py"], 
        "RUNNING":              [0, "B(OH)_3 + Py"], 
        "BOHDISS":              [1, "OH + B(OH)_2-Py"],
        "BOHDISSPuckering":     [1, "OH + B(OH)_2-Py"],
        "BOHDISSBOHDISS":       [1, "OH + B(OH)_2-Py"]     
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
        if float(B_N_bond) > 2.5:                                               
            summary += "\t> B-N DISS < (%3.3f)" %(B_N_bond)
            data += "BNDISS"
            check = True
        if not "BNDISS" in data: 
            summary  += "\t\t\t"
        # We collect all 3 B-H in one array
        # B-H dissociation
        for index in range(2,5):
            B_O_bond        = float(GET_DATA(coordinate_file, index))
            if B_O_bond > 1.60:                            # B-H bond for diss
                summary  += "\t> B-OH DISS < (%3.3f)" %(B_O_bond)
                data     += "BOHDISS"
                check = True
        if not "BOHDISS" in data:
            summary  += "\t\t\t"
        # Ring puckering   
        puckering_Q = GET_DATA(coordinate_file, 5)             
        if float(puckering_Q) > 0.175:                                               
            summary += "\t> Puckering < (%3.3f)" %(puckering_Q)
            data += "Puckering"
            check = True    
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
                gnuplot_coord += ', \\\n  "" using %s:3 w l lw 5 dt 11 lc rgbcolor "#FFD700" title "B-OH bonds" axes x1y2'       % (gnuplot_time_label)
                gnuplot_coord += ', \\\n  "" using %s:4 w l lw 5 dt 11 lc rgbcolor "#FFD700" notitle axes x1y2'                  % (gnuplot_time_label)
                gnuplot_coord += ', \\\n  "" using %s:5 w l lw 5 dt 11 lc rgbcolor "#FFD700" notitle axes x1y2'                  % (gnuplot_time_label)
                index.append(3); index.append(4); index.append(5)
        if ( "C" in input_coord ):
                gnuplot_coord += ', \\\n  "" using %s:6 w l lw 5 dt 11 lc rgbcolor "#21908d" title "Puckering" axes x1y2'        % (gnuplot_time_label)
                y2label         =  '"Bond Length ({\\305})\\Puckering angle"'
        return gnuplot_coord, y2label, index

def main():
    pass

if __name__ == "__main__":
    main()