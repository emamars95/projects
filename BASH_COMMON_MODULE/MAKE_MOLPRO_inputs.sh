#generate the input file for LIIC in molpro 
infile=$1
namein=$2
MIN=$3
MAX=$4
STEP=$5
NATOMS=$6

name="${namein,,}"			# Convert the name in lower case: molpro write wfu and mol file in lowercase string. 


for (( i=$MIN; i<=$MAX; i+=$STEP )); do
        #Name of the output files
	outfile=${name}_${i}.com
        cat $infile > $outfile && sed -i "12,$((12 + 1 + $NATOMS))d" $outfile && sed -i "/geometry/r geom_${i}.xyz" $outfile

        #archive=${name}_${i}.w
        #molden=${name}_${i}.mol
        sed -i "s/MOLPRO/${name}_${i}/g"    	$outfile
        #sed -i "s/MOLPRO.mol/$molden/g" 	$outfile
done

