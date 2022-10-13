infile=$1		# Input file containing the BAGEL template with no atoms
geom_file=$2		# File with the geometry Angstrom
outfile=$3    		# The name of the outputfile

NATOMS=`wc -l $geom_file  | awk '{print $1}'`
NATOMS=$(($NATOMS-2))

name_input=${outfile}.json

# Copy the entire Bagel input file in a new file and delete the section related with the xyz coordinates
cat $infile > $name_input
while read -r line; do
	awk '{print "{ \"atom\" : \""   $1   "\",  \"xyz\" : ["   $2   "  \t,"    $3   "  \t,"   $4   " \t ]},"     }' >> tmp.xyz	#in Bagel format
done < <( tail -$(($NATOMS+1)) $geom_file)		# The file where xyz coordinates are stored

sed -E -i "$NATOMS s/]},/]}/" tmp.xyz		# Rm the last comma 
sed -i "/geometry/r tmp.xyz"  $name_input	# Add it to the input of BAGEL
rm -f tmp.xyz					# Remove the tmp file

archive="${outfile}"
mol="${outfile}.molden"

sed -i "s/casscf_fc.molden/$mol/g" $name_input	# Change the default name with the correct ones
sed -i "s/casscf_fc/$archive/g"    $name_input

