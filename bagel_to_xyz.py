#!/usr/local/Cluster-Apps/python/3.6.8/bin/python3.6

import sys
import os
import subprocess

AtoB		= 1.8897259886
FILE_NAME 	= str(sys.argv[1])
OUT_FILE	= open(FILE_NAME.split('.')[0] + ".xyz", "w")
natom = subprocess.check_output("wc -l %s" % (FILE_NAME), shell = True).decode('ascii').split()[0]
OUT_FILE.write(natom + "\n\n")
for line in open(FILE_NAME, "r"):
	line	= line.split()
	for index in range(7,10):
		line[index] = float(line[index].replace(',', '')) / AtoB
	to_print= line[3].replace(',', '').replace('"', '') 
	OUT_FILE.write("%s\t%9.6f\t%9.6f\t%9.6f\n" %(to_print,line[7],line[8],line[9]))
OUT_FILE.close()
