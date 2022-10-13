#generate the input file for LIIC in molpro 
infile=$1
name=$2
MIN=$3
MAX=$4
STEP=$5
NATOMS=$6

for (( i=$MIN; i<=$MAX; i+=$STEP )); do
        #Name of the output files
        outfile=${name}_${i}.com

        #Copy the geometry of the $i-th file in the g09 input file
        cat $infile > $outfile && sed -i "8,$((8 + $NATOMS))d" $outfile && cat geom_*${i}.xyz >> $outfile
        sed -i '8,9d' $outfile && echo "" >> $outfile && echo "" >> $outfile

        chk="${name}_${i}.chk"

        #post modification: wfu and mol file
        sed -i "s/GAUSSIAN.chk/$chk/g" $outfile

done

