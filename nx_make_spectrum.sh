#!/bin/bash
# NX script for generate the data to plot in spectrum 

here=`pwd`
cd ${here}
. load-NX.sh
file=mkd_saved.inp
rm -f ${file}

read -p "Last excited state computed: " states

folder="/ddn/home/fzzq22/CODE_AND_SCRIPT/NX_modules/"
file=${folder}/${file}
for ((i=2; i<=${states}; i++))
do
	# re-new the mkd file that will be used by the perl script
	sed "s/nfs = 2/nfs = ${i}/" ${file} > ${here}/mkd.inp
	nohup $NX/makedir.pl 
	# rename the default 
	mv cross-section.dat cross-section_${i}.dat
	rm -f mkd.inp
done

