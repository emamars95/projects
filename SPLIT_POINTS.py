#!/usr/local/Cluster-Apps/python/3.6.8/bin/python3.6

import os
import numpy
import math
import progressbar

# -------------------------------------------------------------------------------------- #
def FIX_periodicity(distance):
	if distance > 180:
		distance = distance - 360
	elif distance < - 180:
		distance = distance + 360
	return distance
# -------------------------------------------------------------------------------------- #
def DIST_1_di(ic, conf, index1):
	return abs( FIX_periodicity(ic[index1] - ref_ic[conf][index1]) )

def DIST_2_di(ic, conf, index1, index2):
	return math.sqrt( FIX_periodicity(ic[index1] - ref_ic[conf][index1])**2 + FIX_periodicity(ic[index2] - ref_ic[conf][index2])**2 )
# -------------------------------------------------------------------------------------- #

path	= '/ddn/home/fzzq22/PHOTO-ABS-PROJECT/CONFORMER_ANALYSIS/TDA-PBE0_6-311G*/'
ref_ic	= []
for conf in ["a","b","c","d","e","f","g","h"]:
	folder		= "1" + conf + "/"
	ic		= open(path + folder + "COORDINATES.out", "r").readlines()[2].split()
	for i in range(0,len(ic)): 
		ic[i]	= float(ic[i])
	# The coordinates of the reference geometries.
	ref_ic.append(ic)

#print (numpy.array(ref_ic))

npoint		= 500
nconformer	= 8
bar = progressbar.ProgressBar(maxval=npoint, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
bar.start()

os.system("rm -rf 1A 1B 1C 1D 1E 1F 1G 1H")
counter		= numpy.zeros(nconformer)
# COORDINATES COLUMN				#
# time 			: 0
# d6  -> C_9C_3C_1H_7 	: 2
# d10 -> O_4C_3C_2H_7 	: 4
# d11 -> O_5O_4C_3C_2 	: 5
# d12 -> H_6O_5O_4C_3 	: 6
indexd6, indexd10, indexd11, indexd12 = 2, 4, 5, 6
# CONFORMERS COLUMN 				#
# 1a			: 0
# 1b			: 1
# 1c			: 2
# 1d			: 3
# 1e			: 4
# 1f			: 5
# 1g			: 6
# 1h 			: 7
for index in range (1, npoint + 1):
	folder		= "INITIAL_CONDITIONS/I" 	+ str(index) + "/"
	geom_file	= "geom_"			+ str(index) + ".xyz"
	ic_file		= "coord_"			+ str(index)
	cmd 		= '$SHARC/geo.py -g ' + folder + geom_file + ' < ~/CODE_AND_SCRIPT/BIN_GEO_INP/Geo_HPP_conformers.inp > '  + folder + ic_file  + ' 2>/dev/null' 
	os.system(cmd)
	ic		= open(folder + ic_file, "r").readlines()[2].split()
	for i in range(0, len(ic)):
		ic[i]   = float(ic[i])

	#print (ic)
	# DIST take the arrat with coordinates, the confomer index and the column with the coordinate to use
	#			1a, 1c, 1e		1b, 1d, 1f		 	1g, 1h		
	d11_list	= [DIST_1_di(ic, 0, indexd11), DIST_1_di(ic, 1, indexd11) , DIST_1_di(ic, 6, indexd11)]
	#print (d11_list, d11_list.index(min(d11_list)))

	if d11_list.index(min(d11_list))	== 0:				# 1a 1c 1e
		#				1a			1c				1e
		d12_list	= [DIST_1_di(ic, 0, indexd12), DIST_1_di(ic, 2, indexd12), DIST_1_di(ic, 4, indexd12)] 
		#print (d12_list, d12_list.index(min(d12_list)))
		if d12_list.index(min(d12_list))	== 1:			# 1c 
			CONFORMER       = ["C", 2]
		else:								# 1a 1e
			#				1a					1e	
			d6_d10_list	= [DIST_2_di(ic, 0, indexd6, indexd10), DIST_2_di(ic, 4, indexd6, indexd10)]
			#print (d6_d10_list, d6_d10_list.index(min(d6_d10_list)))
			if d6_d10_list.index(min(d6_d10_list)) == 0:		# 1a	
				CONFORMER       = ["A", 0]
			else:							# 1e
				CONFORMER       = ["E", 4]

	if d11_list.index(min(d11_list))        == 1:                           # 1b 1d 1f
                #                               1b                      1d                              1f
		d12_list        = [DIST_1_di(ic, 1, indexd12), DIST_1_di(ic, 3, indexd12), DIST_1_di(ic, 5, indexd12)]
		if d12_list.index(min(d12_list))        == 1:                   # 1d
			CONFORMER       = ["D", 3]
		else:								# 1b 1f
                        #                               1b                                      1f      
			d6_d10_list     = [DIST_2_di(ic, 1, indexd6, indexd10), DIST_2_di(ic, 5, indexd6, indexd10)]
			if d6_d10_list.index(min(d6_d10_list)) == 0:            # 1b
				CONFORMER       = ["B", 1]
			else:							# 1f
				CONFORMER       = ["F", 5]
	
	if d11_list.index(min(d11_list))        == 2:				# 1g 1h
		d12_list        = [DIST_1_di(ic, 6, indexd12), DIST_1_di(ic, 7, indexd12)]
		if d12_list.index(min(d12_list))        == 1:			# 1h
			CONFORMER       = ["H", 7]
		else:								# 1g
			CONFORMER       = ["G", 6]

	counter[CONFORMER[1]]   += 1 
	bar.update(index)
	if counter[CONFORMER[1]] == 1:
		os.system("mkdir -p 1" + CONFORMER[0])
	#print(CONFORMER, CONFORMER[1], counter[CONFORMER[1]])	
	new_folder		= "1" + CONFORMER[0] + "/I" + str(int(counter[CONFORMER[1]]))
	os.system("cp -r " +  folder  + " " + new_folder)

bar.finish()
print (counter)
