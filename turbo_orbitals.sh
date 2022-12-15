#! /usr/bin/bash 
here=`pwd`
cd $here
name_current_folder=${PWD##*/}
cat control > control_backup

#sed from ^ = line beginning to pattern :$
#embed all tille patter (.*) and print as 1
#skip the remaining line characters .* till the end of the line $
numberline=`grep -n "last SCF" control | sed 's/^\(.*\):\$.*$/\1/'`

read -p "Do you want compute the MOs (M), NTOs (N) or DIFFERENCE DENSITIES based on NTOs (D)? " choice
if [[ ${choice^^} == *M* ]]; then 
	read -p "Insert the first index of MOs you want to compute   " MOSmin
	read -p "Insert the last  index of MOs you want to compute   " MOSmax
	sed -i "${numberline}i \$pointval mo ${MOSmin}-${MOSmax} fmt=cub" control
	ricctools -proper
elif [[ ${choice^^} == *N* ]]; then
	sed -i "${numberline}i \$pointval nto 1-2 fmt=cub" control
	read -p "Insert the last  index of NTO you want to compute   " max
elif [[ ${choice^^} == *D* ]]; then 
	read -p "Insert the last  index of DIF you want to compute   " max
	#sed -i "${numberline}i \$anadens \n  calc diffden from\n  1d0 diffden.cao\n\$pointval fmt=cub" control
fi

ORB() {
  mult=$1; string=$2; i=$3; CCfile=$4
  echo "Parsing $CCfile file"
    if [[ ${choice^^} == *N* ]]; then               				# NTOs calculation
            ricctools -ntos $CCfile >  out_ricctools_${i}   			# Compute the NTO of state i. We save the output
            ricctools -proper       >> out_ricctools_${i}                      	# Write the cube file for the first two NTOs
            for j in 1 2; do                                                	# For each NTO (two at max) we check the coefficient
                    # First two lines contain a strings. The third and foruth contains the coefficients
                    coeff=`grep -A3 "%contrib" out_ricctools_${i} | head -$(($j + 2)) | tail -1 | awk '{print $3}'` # Get coeff of NTOs
		    coeff=${coeff%.*}						# Take the integer part
                    if (( $(echo "$coeff > 10" |bc -l) )); then			# Check if the percentage is larger than 20%
                            echo "weight for NTO$j is $coeff%"	
                            cp nto_occ_${j}.cub occ_${name_current_folder}_${string}${i}l_${j}_0.${coeff}.cub
                            cp nto_vir_${j}.cub vir_${name_current_folder}_${string}${i}l_${j}_0.${coeff}.cub
                    fi
                    rm -f nto_occ_${j}.cub nto_vir_${j}.cub                 	# We rm the cub files 
            done
    elif [[ ${choice^^} == *D* ]]; then
            nohup ricctools -diffden $CCfile
            cp *00${i}-approxdiffden*.cao diffden.cao && ricc2 -fanal && cp diffden.cao diffden_${string}_${i}.cao
    fi
  echo  "*************************************************************************"
}

if [[ ${choice^^} == *D* ]] || [[ ${choice^^} == *N* ]]; then
	for (( i = 1; i <= ${max}; i++ )); do                   # Loop on the states we want to print  
		padding=`printf %4s $i | tr ' ' -`              # Padding for turbomole with - and the number of the state
		if test -f "CCLE0-1--1${padding}"; then 	# If singlets eigenvectors are present compute the singlet NTOs
			ORB 1 "s" $i "CCLE0-1--1${padding}"
		fi 
		if test -f "CCLE0-1--3${padding}"; then		# If triplet eigenvectors are present compute also the triplet NTOs
			ORB 3 "t" $i "CCLE0-1--3${padding}"
		fi
	done
fi	

