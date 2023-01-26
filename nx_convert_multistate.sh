#!/bin/bash 
# This bash script simply partion the different trajectories for the same energy windows into 
# the electronic state that contribute to the specific energy window. 
# In the main folder all input file has to be placed. 


. load-NX.sh

name_root="final_output"
file_log="makedir.log"
file_dyn="control.dyn"
folder="TRAJECTORIES"

multi_state() 
{
    readarray -d '' entries < <(printf '%s\0' ${name_root}.* | sort -zV)
    # #array[@] is the lenght of the array. If it is zero we have any output files
    if [ ${#entries[@]} == "0" ]; then
        echo "There are any file called ${name_root} in your local directory"
        exit -1 
    fi
    # We need to check if the input for NX is provided in the folder
    if [ -f "$file_dyn" ]; then
        echo "$file_dyn exists."
    else 
        echo "$file_dyn does not exist."
        exit -1
    fi
    # As well as the input for the electronic structure job 
    if [ -z "$(ls -A JOB_*/)" ]; then
        echo "No JOB_AD or JOB_NAD directory"
        exit -1
    fi
    # We initialize the running state and the total number of states to be included in the dynamics
    nstatdyn=2
    nstat=8 
    # We create the input file for makedir.pl 
    cat <<EOT > mkd.inp
    type = 4
    run_IS = 0
EOT
    # We loop over the sorted input files 
    for entry in "${entries[@]}"
    do
        echo -e "File: ${entry}\n"
        # Number of line in the input file must be more than zero otherwise that state
        # do not contribute to the absorption corss section of that particular window
        nline_in_file=`wc -l ${entry} | awk '{print $1}'`
        if [ "${nline_in_file}" != "0" ]; then
            rm -rf ${folder}
            cp ${entry} ${name_root}
            # We update the control file depending on which state we calculating
            sed -i "/nstat =/c\nstat = ${nstat}" $file_dyn 
            sed -i "/nstatdyn =/c\nstatdyn = ${nstatdyn}" $file_dyn
            # We run the makedir.pl file (input created before)
            ${NX}/makedir.pl > ${file_log}
            folder_renamed="${folder}_s$((${nstatdyn} - 1))" 
            # We move some files and we rename the folder
            mv ${entry} ${file_log} ${folder}
            mv ${folder} ${folder_renamed}
        else
            mv ${entry} ${entry}_empty
        fi 
        # We update the running state and the total number of state in the calculation
        nstatdyn=$((${nstatdyn} + 1))
        nstat=$((${nstat} + 1))
    done
}

multi_state