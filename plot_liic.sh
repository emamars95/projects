#! /usr/bin/bash 

read -p "Insert the file were relative energies are:   " nameFILE
NTATE=`tail -1 $nameFILE | awk '{print NF}' | sort -nu | tail -n 1`
nsinglet=`head -1 $nameFILE | tr -cd 'S' | wc -c`
ntriplet=`head -1 $nameFILE | tr -cd 'T' | wc -c`

read -p "It is a rigid scan? (Y, N)                    " LIICTYP
if [[ $LIICTYP == "y" || $LIICTYP == "Y" ]]; then
        LIICTYP="RIGIDSCAN"
	read -p "Insert the index of the last points that constitutes the scan (first point must be 0)   " NPOINT
        read -p "Define the x label (Amstrong is implicit) 		 " XLABEL
        read -p "Define XMIN						 " XMIN
        read -p "Define XMAX						 " XMAX
else 
	LIICTYP="NORMALLIIC"
fi

#Print the input file the values of name file, singlet and triplet to print and profile type
echo "$LIICTYP"   > INPUT_plot_liic
echo "$nameFILE" >> INPUT_plot_liic
echo "$nsinglet" >> INPUT_plot_liic
echo "$ntriplet" >> INPUT_plot_liic

#Check if in the folder we have the "d1_values" file it is an output for adc2 calculation
if test -f "d1_values"; then
	echo "D1 file found"
	CALCULATIONTYP="D1"	
else
	CALCULATIONTYP="NOTD1"
fi
#We print the type of calculation
echo $CALCULATIONTYP >> INPUT_plot_liic

echo ""
echo "**********************************"
echo "File name to plot   $nameFILE"
echo "N siglet states     $nsinglet"
echo "N triplet states    $ntriplet"
echo "Cal type            $CALCULATIONTYP"
echo ""

if [ $CALCULATIONTYP == "D1" ]; then 
	echo "d1 diagnostic will be added at the LIIC plot"
fi

if [ $LIICTYP == "RIGIDSCAN" ]; then
        echo $NPOINT >> INPUT_plot_liic 
	echo $XLABEL >> INPUT_plot_liic
	echo $XMIN   >> INPUT_plot_liic
	echo $XMAX   >> INPUT_plot_liic
fi

module load python/3.6.8
plot_liic.py INPUT_plot_liic > plot_liic.gp

gnuplot plot_liic.gp

display ${nameFILE}.png &
#rm -f plot_liic.gp
