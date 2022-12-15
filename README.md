# Tool for quantum chemistry data analysis # 

This repository contains the first drafts to create an analysis tool for quantum chemistry outputs. The main goals are 

## Linear Interpolation in Internal Coordinates ##

Linear Interpolation in Internal Coordinates (LIIC) are scans along a linear combination of molecular degrees of freedom widely used to interpret molecular reactivity. To perform a LIIC we need (a) two input files that are the initial (I_GEOM) and final (F_GEOM) geometries, in XYZ format, that has to be interpolated and (b) an integer number (N) denoting the number of geometries that has to be generated. In addition, we need (c) an input template (INP_TEMP) that specify the number of electronic states will be computed by a quantum chemistry call and at which level of theory. The workflow boils down to the following

(i) Read I_GEOM and F_GEOM as XYZ input files. 
(ii) Convert the XYZ input files into internal coordinates (Z-matrix): ZI_GEOM and ZF_GEOM.
(iii) Perform the linear interpolation resulting in N distinct geometries expressed in terms of Z-matrices: {Z_GEOMS}.
(iv) Convert all N geometries into XYZ coordinates files: {GEOMS}. 
(v) Using {GEOMS} and the INP_TEMP, I render N input files for a quantum chemistry call. 
(vi) Invoke the quantum chemistry call and collect the results. The analysis of the output is perfomerd in case some errors occured. 
(vii) Read the output from the quantum chemistry outputs and organize the results inside a table that can be easily parsed. 

## Trajectory Anlysis ## 
