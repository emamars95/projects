here=`pwd`

. load-NX.sh

generateIC(){
	local ncal=$1
	for ((i=0; i<=$(($ncal-1)); i++ ))
	do
		j=$(($i+1))
		cd ${here}/INITIAL_CONDITIONS
		folder=I${j}
		rm -rf $folder
		mkdir -p $folder && cd $folder
		cp ${here}/GEO_PROFILE/geom_${i}.xyz . && cp ${here}/initqp_input .
		$NX/xyz2nx < geom_${i}.xyz
		nohup $NX/initcond.pl > initcond.log 
	done
}


splitIC() {
	local ncal=$1
	local mcal=$2
	for ((i=1; i<=$ncal; i++ ))
	do
		#mv I0 I0_extra 		# First point is extra (501 point otherwise)
		folder="IC_${i}"	
		mkdir ${here}/${folder}
		for ((j=1; j<=$mcal; j++ ))
		do
			index=$(( (${i}-1)*$mcal + ${j} ))
			echo "i: $i index: $index ncal: $ncal j: $j"
			cp -r I${index} ${folder}/I${j}
		done
		cd ${here}/${folder}
		$NX/merge_initcond.pl 2> out <<EOF
	$mcal
EOF
		cd ${here}	
	
	done
}

runIC() {
	local ncal=$1
	for ((i=1; i<=$ncal; i++ ))
	do
		folder=IC_${i} 
		cp ../initqp_input_1 ${folder}/I_merged/initqp_input
		cp -r JOB_AD ${folder}/I_merged/
		cd ${folder}/I_merged/
		cp final_output final_output.old
		nohup $NX/initcond.pl > initcond.log &
		cd ${here}	
	done
}

mergeIC(){
	local ncal=$1
	for ((i=1; i<=$(($ncal)); i++ ))
	do
		folder=IC_${i}
		cp -r ${folder}/I_merged ${here}/I${i}
	done

	$NX/merge_initcond.pl <<EOF
	$ncal
EOF
}

totic=500
split=10
msplit=$((${totic}/${split}))
echo $split $msplit

#generateIC $totic
#splitIC $split $msplit
#runIC $split
mergeIC $split

