#!/usr/bin/bash
#This program wants to simplify the run of theodore with state density analysis scripts analyze_sden.py
#It requires the state NOs and the state-averange NOs in molden format 
HERE=`pwd`
SCRIPTFOLDER="/ddn/home/fzzq22/CODE_AND_SCRIPT"
BINANAFILE="${SCRIPTFOLDER}/BIN_THEODORE"
name=$1
n_state=$2

echo "Name file: $name       Number of excited state inserted $n_state"
if [[ $name == "" || $n_state == "" ]]; then

	echo "SA MOs molden file should be named  as: name.mol"
	echo "Single state MOs molden file should be named as: name_s0.mol, name_s1.mol ..."

	read -p "Prompt the name of the molden file:   " name
	read -p "Prompt the number of excited state:   " n_state
	if [ $name == "" ]; then 
		echo "give a name as input"
		exit -1
	fi
	if [ $n_state == "" ]; then 
        	echo "give a number of state as input"
        	exit -1
	fi
fi
cd ${BINANAFILE}
#nos a type of input followed by the state average NOs and each state NOs.
printf "rtype=\'nos\' \nmo_file=\'./NAMEDEFAULT.mol\' \nana_files=[" > dens_ana.in
for (( i = 0; i <= $(($n_state-1)); i++ )) 
do 
	printf "\'./NAMEDEFAULT_s${i}.mol\'," >> dens_ana.in
done
printf "\'./NAMEDEFAULT_s${i}.mol\'] \n" >> dens_ana.in
#Perform a population analysis, Perform analysis of unpaired electrons, Perform attachment/detachment analysis and compute the NDOs
#Bond order analysis
printf "rd_ene=False \npop_ana=True \nunpaired_ana=True \nAD_ana=True \nmolden_orbitals=True \nalphabeta=False \nBO_ana=True \nprop_list=[\'nu\', \'nunl\', \'p\']" >> dens_ana.in
 
sed -i "s/NAMEDEFAULT/${name}/g" dens_ana.in
cp dens_ana.in $HERE/

cd $HERE

#lunch thodore
analyze_sden.py > theodore_${name}.out

mv ndo_jmol.spt ${name}.spt
