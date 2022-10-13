#bash for gaussian 09

for k in 0 #LIIC point we want 
do 
	for i in {1..8} # number of state we are interested in
	do
		namechk=liic_${k}_nto_${i}.chk
		namefchk=liic_${k}_nto_${i}.fchk
		cubocc=liic_${k}_occ_${i}.cub
		virocc=liic_${k}_vir_${i}.cub

		cp gaussian_liic*${k}.chk $namechk
		#run the calculation for get the ntos   
		g09 <<EOFlele
		%nprocshared=4
		%chk=$namechk
		#Geom=AllCheck ChkBas Guess=(Read,Only) Density=(Check,Transition=${i}) Pop=(NTO,SaveNTO)
EOFlele

		formchk $namechk			#format the chk
		cubegen 0 mo=homo $namefchk $cubocc	#produce cube files
		cubegen 0 mo=lumo $namefchk $virocc
	done
done
