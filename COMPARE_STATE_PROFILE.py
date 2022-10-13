#!/usr/local/Cluster-Apps/python/3.6.8/bin/python3.6
import sys
original_stdout = sys.stdout

point_to_set_as_zero = int(input("Point to set as zero for all calculation (default = 0)   "))
STATE	       = int(input(" Which state do you want compare? 0 = S0, 1 = S1         "))
N_output       = "S" + str(STATE) + "_comparison"  
N_calculations = int(input(" How many calculation you want compare?              "))
energy_total = []
all_files    = []
Xcoord       = []
for i in range(0, N_calculations):
	energy = []
	NAME_FILE = input("Insert the name of the file with Excitation Energies     ")
	all_files.append(NAME_FILE)
	with open(NAME_FILE, "r") as openfile:
		for npoint, line in enumerate(openfile):
			if npoint == point_to_set_as_zero:
				zeroenergy = float(line.split()[STATE + 1])
	with open(NAME_FILE, "r") as openfile:	
		for line in openfile:
			Xcoord.append(float(line.split()[0]))
			energy.append(float(line.split()[STATE + 1]) - zeroenergy)
	energy_total.append(energy)
	#print(energy)
with open(N_output, "w") as openfile:
	for j in range(0, npoint + 1):
		openfile.write("%5.3f \t" %(Xcoord[j]))
		for i in range(0, N_calculations):
			openfile.write("%9.5f \t" %(energy_total[i][j]) )	
		openfile.write("\n")

# '#440154' dark purple '#472c7a' purple '#3b518b' blue '#2c718e' blue '#21908d' blue-green '#27ad81' green '#5cc863' green '#aadc32' lime green '#fde725' yellow
Color = ["#440154", "#472c7a", "#3b518b", "#2c718e", "#21908d", "#27ad81", "#5cc863", "#aadc32", "#fde725", "#007f00", "#ff0000", "#00bfbf", "#bf00bf", "#bfbf00"]

gnustring = ''
gnustring += 'set terminal pngcairo enhanced dashed font "Helvetica,28.0" size 1500,1200\n'
gnustring += 'set output "%s.png"\n\n'                  %(N_output)
gnustring += 'set xlabel "LIIC coordinate"\n'         

gnustring += '  set ytics nomirror\n  set key right\n  set ylabel "Relative Energy (eV)"\n  set yrange[-2:1]\n'
gnustring += '  set title offset 0,-0.8\n'

gnustring += '  plot  "%s" ' %(N_output)

for i in range(0, N_calculations):
	gnustring += ' u 1:%i title "%s" lw 6.0 lt 1 lc rgb "%s" w l'    %(i+2,all_files[i],Color[i])
	if i != N_calculations - 1:
		gnustring += '   ,\\\n   ""'
sys.stdout = open('plot_liic.gp', 'w')
print(gnustring)
			

