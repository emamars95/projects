#submit job

name=$1
MIN=$2
MAX=$3
STEP=$4
REVERSE=$5

here=`pwd`
################################################################################################
if [ -z "$name" ] || [ -z "$MIN" ] || [ -z "$MAX" ] || [ -z "$STEP" ] || [ $MAX -lt $MIN ] || [ -z "$REVERSE" ]; then
        read -p "Insert the name of your input/output files:   " name
	read -p "Insert the index of the first point:          " MIN
        read -p "Insert the index of the last point:           " MAX
        read -p "Insert the step between each cont.  point     " STEP
	read -p "IT is a reverse LIIC (Y,N)    " REVERSE
fi

REVERSE=${REVERSE^^}

printf "\n"
################################################################################################
if test -f "${name}_${MIN}/control"; then
   	CALCULATION="TURBO"
   	printf "$CALCULATION calculation detected."
else
	key_BAGEL=`   grep "bagel"  ${name}_${MIN}*`
	key_GAUSSIAN=`grep "chk"    ${name}_${MIN}*`
	if [ ! -z "$key_BAGEL" ]; then
		CALCULATION="BAGEL"
		printf "$CALCULATION calculation detected. Archive files will be saved locally "
	elif [ ! -z "$key_GAUSSIAN" ]; then
		CALCULATION="GAUSSIAN"
		printf "$CALCULATION calculation detected. CHK files will be saved locally "
	else
		CALCULATION="MOLPRO"
		printf "$CALCULATION calculation detected. Wfu files will be saved in default folder. "
		#rm -rf /tmp/fzzq22/*.w
	fi
fi
################################################################################################
function check {
	i=$1
	j=$2
	flag_check=$3 
	n_check=$4
	CALCULATION=$5
        if [ $CALCULATION == "BAGEL" ]; then
        	BAGEL "${name}_${i}.json" > "${name}_${i}.out"
        	if (( $i $flag_check $n_check )); then
                	cp ${name}_${i}.archive ${name}_${j}.archive
        	fi
        fi
        if [ $CALCULATION == "MOLPRO" ]; then
		#PATH_WFU="/ddn/home/fzzq22/wfu/"
                molpro -n 4 -W ./ "${name}_${i}.com"
                if (( $i $flag_check $n_check )); then
			cp ${name}_${i}.w ${name}_${j}.w
                        #cp ${PATH_WFU}/${name}_${i}.w ${PATH_WFU}/${name}_${j}.w
			rm /tmp/fzzq22/${name}_${i}.w
                fi
        fi
        if [ $CALCULATION == "GAUSSIAN" ]; then
                g09 "${name}_${i}.com"
                if (( $i $flag_check $n_check )); then
                        cp ${name}_${i}.chk ${name}_${j}.chk
                fi
        fi
        if [ $CALCULATION == "TURBO" ]; then
                cd ${name}_${i}
		key_ricc2=`grep "ricc2"     control` 			# The control file request an riic2 calculation (cc2 or adc2)
		key_escf=`grep  "scfinstab" control`                    # The control file request an escf  calculation (tda-dft, td-scf, ...)
                # ------------------------------------------------- #
		key_mp4=`grep   "mp4"       control`			# MP4/CCSD are run with the ccsdf12 program
		key_ccsd=`grep  "ccsd"      control`
		# ------------------------------------------------- #
		key_ccsdf12=${key_mp4}${key_ccsd}			# The key for the ccsdf12 module to run with Turbomole

		dscf > dscf.out
		if (( $i $flag_check $n_check )); then
			cp mos ${here}/${name}_${j}/mos				# we copy the mos file into the next folder
		fi
		if   [ ! -z "$key_escf"    ]; then 
                        escf  > escf.out      &
		elif [ ! -z "$key_ccsdf12" ]; then 
                       	ccsdf12  > ricc2.out  &
		elif [ ! -z "$key_ricc2"   ]; then
	               	ricc2 > ricc2.out     &
		else
			echo "In control file none of the allowed keywords for excited states calculations are found"
		fi
		sleep 0
                cd $here
        fi
}


################################################################################################

if [ $REVERSE == "Y" ]; then
        printf "\nYOU HAVE CHOSE TO GO FROM $MAX to $MIN with STEP $STEP \n"
        {
        for (( i=$MAX; i>=$MIN; i-=$STEP )); do
                j=$((${i}-${STEP}))
		check $i $j ">" $MIN $CALCULATION 
        done
        } &

elif [ $REVERSE == "N" ]; then
        printf "\nYOU HAVE CHOSE TO GO FROM $MIN to $MAX with STEP $STEP \n"
        {
        for (( i=$MIN; i<=$MAX; i+=$STEP )); do
                j=$((${i}+${STEP}))
		check $i $j "<" $MAX $CALCULATION
        done
        } &
else
        echo "Chose Y or N"
        exit -1
fi
