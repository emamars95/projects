#FOR DYNAMICS USE INSTEAD THE NX SCRIPT $NX/dynout2xyz.pl
#
#Script to convert the geometries from NX file into xyz file
#This script will take all geometries saved in the final output file and will convert them in xyz files.

here=`pwd`

read -e -p "Is it the file in xyz format or from NX format (X or N)?            "  format
read -e -p "Insert the name of your xyz file collecting multiple geometries     "  file
read -e -p "Insert the number of atoms in your xyz file                         "  natoms
read -e -p "Insert the index of the fist  geo to extract (from 0)               "  index_start
read -e -p "Insert the index of the final geo to extract                        "  index_finish

time_start=`bc <<< "scale=2; $index_start/2"`
time_finish=`bc <<< "scale=2; $index_finish/2"`

folder=GEO_PROFILE

mkdir -p $folder
rm    -f $folder/*xyz
cd 	 $folder								# Everything done in GEO_PROFILE

if [ "${format}" == "X" ]; then 
	effective=$(($natoms+2))        					# one line for the number of atoms and one for the comment
	for (( i=${index_start}; i<=${index_finish}; i++ ))
	do
		h=$((${effective} * (${i}+1) ))
		head -$h ${here}/${file} | tail -${effective} > geom_${i}.xyz
		sed -i "2s/.*/${i}/" geom_${i}.xyz				# The second line is changed with the index of the geometry
	done

elif [ "${format}" == "N" ]; then
	# copy everything in the out file in NX format, to convert in xyz use the command  $NX/nx2xyz
	awk '/Geometry/{flag=1;next}/Velocity/{flag=0}flag' ${here}/$file > out_tmp
	# awk "/$time_start fs/{flag=1}/ $time_finish  /{flag=0}flag" ../$file > out_tmp
        for (( i=${index_start}; i<=${index_finish}; i++ ))
        do
		h=$(($natoms * (${i}+1) ))
		head -$h out_tmp | tail -${natoms} > geom
		#time_awk=`bc <<< "scale=2; $i/2"`
		#awk "/$time_awk fs/{flag=1;next}/------------/{flag=0}flag" out_tmp | awk '/geometry/{flag=1;next}/velocity/{flag=0}flag' | head -${natoms} > geom
		cp geom geom_${i}
		$NX/nx2xyz && mv geom.xyz geom_${i}.xyz				# create the xyz file and rename it
        done

	for (( i=${index_start}; i<=${index_finish}; i++ ))
	do 
		cat geom_$i.xyz >> output.xyz
	done


else 
	echo "chose X or N"
	exit -1 
fi

