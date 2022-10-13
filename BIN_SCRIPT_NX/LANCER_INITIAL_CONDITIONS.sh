#$NX/xyz2nx < *.xyz

here=`pwd`
cd $here

if [ -d "INITIAL_CONDITIONS" ]; then 
	echo "INITIAL_CONDITIONS folder already exist"
	echo "Delete it before to proceed plz"
	exit -1
fi  

read -p "In how many folder y want split the calculation?  " ncalculations
$NX/split_initcond.pl <<EOF
$ncalculations
n
EOF

printf "\n\nInitial conditions are splitted in $ncalculations \n\n"

for ((i=1; i<=$ncalculations; i++ ))
do 
	cd ${here}/INITIAL_CONDITIONS/I${i}
	nohup $NX/initcond.pl > initcond.log &
	sleep 2
done

#$NX/merge_initcond.pl
