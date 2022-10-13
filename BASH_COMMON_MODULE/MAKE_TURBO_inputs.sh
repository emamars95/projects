#! /usr/bin/bash

#controlscript="/ddn/home/fzzq22/CODE_AND_SCRIPT/BIN_CONTROL_SCRIPT/"$1
controlscript=$1
name=$2
MIN=$3
MAX=$4
STEP=$5

here=`pwd`

cp -f $controlscript $here

for (( i=$MIN; i<=$MAX; i+=$STEP )); do
 	#the folder in which the calculation will be run (with geo $geometryfile)
	foldername=${name}_${i}
	geometryfile="geom_${i}.xyz"

	cd ${here}

	#Make the folder and copy the file in
        rm -rf   ${foldername}
	mkdir -p ${foldername}
	cp $geometryfile  $foldername #&& rm -f $geometryfile
	cp $controlscript $foldername

	#convert xyz file in the coord file readable from Turbomole
	cd  $foldername
	x2t $geometryfile > coord

	#Once the file are copied the control file can be generated
	define < $controlscript > out_define &

done

