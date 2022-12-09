#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np


def main():
	pass

# -------------------------------------------------------------------------------------	#
def PREP_PLOT_QY():
	fp = open(PARAM_FILE.qy_file)
	fp.readline()
	x = []
	y = []
	for line in fp: 
		line = line.split()
		x.append(line[0])
		y.append(line[1:])
	#print(x, y)
	PLOT_QY(x,y)
	return 

# -------------------------------------------------------------------------------------	#
def PLOT_QY(self, x: list, y: list):
	y = np.array(y).T
	for i, y_value in enumerate(y):
		plt.scatter(x, y_value)
	plt.xlabel('Energy (eV)')
	plt.ylabel('QY')
	plt.legend()
	plt.show()


if __name__ == "__main__":
	main()