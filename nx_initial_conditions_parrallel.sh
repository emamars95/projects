
#!/bin/bahs
# This script create a set of intial conditions for the spectra calculation with NX. 
# 1) generateIC
# Given a number (n) we split the total number of geometries into n Initial Conditions (ICs)
# For each IC we run xyz2nx tool to convert the geometry from xyz into NX format
# For each IC we run initcond.pl to generate the NX format
# 2) splitIC
# We merge (using merge_initcond) the ICs into bunches of mcal. The total number of folder will be ncal
# 3) runIC
# For each ncal we run the spectra calculation using initcond.
# Since the folder are ncal we will run initcond parallel job
# 4) mergeIC
# We merge all results

here=`pwd`
cd $here
. load-NX.sh

folder_ic="INITIAL_CONDITIONS"

generateIC() {
        local ncalculations=$1
        echo -e "We generate the first set of intial conditions: total number of geometries ${ncalculations}"
        
        if [ -d "${folder_ic}" ]; then 
	        echo "${folder_ic} folder already exist"
	        echo "Delete it before to proceed plz"
	        exit -1
        else 
            mkdir ${folder_ic}
        fi
        k=0   
        for ((i=1; i<=$((${ncalculations})); i++ ))
        do
                j=$(($i-1))
                cd ${here}/${folder_ic}
                mkdir -p I${i} && cd I${i}
                cp ${here}/GEO_PROFILE/geom_${j}.xyz . && cp ${here}/initqp_input .
                $NX/xyz2nx < geom_${j}.xyz
                $NX/initcond.pl > initcond.log 
                var=`expr ${i} % 50`
                if [ "${var}" == "0" ]; then
                    advanc=$(( ${k} * (50 * 100/${ncalculations}) ))
                    echo -e "Done: ~ ${advanc} %"
                    k=$((${k}+1))
                fi
        done
        echo -e "\n"
}

splitIC() {
        local ncal=$1
        local mcal=$2
        echo -e "We split the intial condition into ${ncal} folder with a total of ${mcal} geometries each"
        for ((i=1; i<=${ncal}; i++ ))
        do
                cd ${here}/${folder_ic}
                folder="IC_${i}"
                mkdir ${folder}
                for ((j=1; j<=${mcal}; j++ ))
                do
                        index=$(( (${i}-1)*${mcal} + ${j} ))
                        #echo "i: ${i} index: ${index}"
                        mv I${index} ${folder}/I${j}
                done
                cd ${folder}
                $NX/merge_initcond.pl &>/dev/null <<EOF
$mcal
EOF
        done
        echo -e "\n"
}

runIC() {
        local ncal=$1
        echo -e "We run the intial condition for the ${ncal} folders"
        for ((i=1; i<=$(($ncal)); i++ ))
        do
                cd ${here}/${folder_ic}
                folder="IC_${i}"
                cp ${here}/initqp_input_1 ${folder}/I_merged/initqp_input
                cp -r ${here}/JOB_AD ${folder}/I_merged/
                cd ${folder}/I_merged/
                cp final_output final_output.old
                nohup $NX/initcond.pl > initcond.log &
        done
        echo -e "\n"
}

mergeIC() {
        local ncal=$1
        
        for ((i=1; i<=$(($ncal)); i++ ))
        do
                folder="IC_${i}"
                cp -r ${here}/${folder_ic}/${folder}/I_merged ${here}/${folder_ic}/I${i}
        done
        cd ${here}/${folder_ic}
        $NX/merge_initcond.pl <<EOF
${ncal}
EOF
        echo -e "\n"
}

totic=500
split=10
msplit=$((${totic}/${split}))

echo -e "Number of geometries are: ${totic}"
echo -e "Number of geometries for each IC: ${msplit}"
echo -e "\n"
#generateIC ${totic}
#splitIC ${split} ${msplit}
#runIC $split
mergeIC $split
