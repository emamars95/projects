infile=$1		# Input file containing the BAGEL template

outfile="BAGEL.json"	# The name of the outputfile
geom_tmp="geom_tmp.xyz"	# TMP geometry file that will be generated and then deleted

# Copy the entire Bagel input file in a new file and delate the section related with the xyz coordinates
cat $infile > $outfile && sed -i '7,18d' $outfile 	# If in Bhor, 8,19 in Angstrom (there will be one extra line in Bagel input
echo "geometry"  > $geom_tmp			 	# We need to add one line otherwise the first record will be cut
cat "../../geom" >> $geom_tmp		# Put the coordinates in
while read -r line; do
	awk '{print "{ \"atom\" : \""   $1   "\",  \"xyz\" : ["   $3   "  \t,"    $4   "  \t,"   $5   " \t ]},"     }' >> tmp.xyz	#in Bagel format
done < <( tail -13 $geom_tmp)		# The file where xyz coordinates are stored

sed -E -i '12 s/]},/]}/' tmp.xyz	# Remuve the last comma 
sed -i "/geometry/r tmp.xyz" $outfile	# Add it to the input of BAGEL
rm -f $geom_tmp	tmp.xyz			# Remove the tmp file

archive="archive"
mol="orbitals.molden"

sed -i "s/casscf_fc.molden/$mol/g" $outfile	# Change the default name with the correct ones
sed -i "s/casscf_fc/$archive/g"    $outfile

