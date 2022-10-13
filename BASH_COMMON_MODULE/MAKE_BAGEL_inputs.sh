#generate the input file for LIIC in molpro 
infile=$1		# BAGEL template
name=$2			# name of the calculation
MIN=$3
MAX=$4
STEP=$5
NATOMS=$6		# Number of atoms

for (( i=$MIN; i<=$MAX; i+=$STEP )); do
        # Name of the geometry file
	geom_file=geom_${i}.xyz
	# The script will create a file ${name}_${i}.json with the current geometry coordintes. They can be 
# in A or Bohr. The CAS parameter must be adjusted in the template.
	MAKE_BAGEL_TEMPLATE.sh $infile $geom_file ${name}_${i}
done
