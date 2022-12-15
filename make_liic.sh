infile=$1
name=$2
MIN=$3
MAX=$4
STEP=$5

read -p "Insert PROGRAM NAME USED: BAGEL (B), MOLPRO (M), GAUSSIAN (G), TURBOMOLE (T)   " program

if [ -z "$infile" ] || [ -z "$name" ] || [ -z "$MIN" ] || [ -z "$MAX" ] || [ -z "$STEP" ]; then
	read -p "Insert the name of your template file:        " infile
        read -p "Insert the name of your input/output files:   " name
        read -p "Insert the index of the first point:          " MIN
        read -p "Insert the index of the last point:           " MAX
        read -p "Insert the step between each cont.  point     " STEP
fi

PROGRAM=${program^}

NATOMS=`head -1 *_${MIN}.xyz`						

if [ $PROGRAM == "B" ]; then 
	bash /ddn/home/fzzq22/CODE_AND_SCRIPT/BASH_COMMON_MODULE/MAKE_BAGEL_inputs.sh     $infile $name $MIN $MAX $STEP $NATOMS
elif [ $PROGRAM == "M" ]; then 
	bash /ddn/home/fzzq22/CODE_AND_SCRIPT/BASH_COMMON_MODULE/MAKE_MOLPRO_inputs.sh    $infile $name $MIN $MAX $STEP $NATOMS
elif [ $PROGRAM == "G" ]; then
	bash /ddn/home/fzzq22/CODE_AND_SCRIPT/BASH_COMMON_MODULE/MAKE_G09_inputs.sh       $infile $name $MIN $MAX $STEP $NATOMS
elif [ $PROGRAM == "T" ]; then
	bash /ddn/home/fzzq22/CODE_AND_SCRIPT/BASH_COMMON_MODULE/MAKE_TURBO_inputs.sh     $infile $name $MIN $MAX $STEP
else
	echo "Not recognized input"
fi
