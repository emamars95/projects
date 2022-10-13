#NX script for generate the data to plot in spectrum 

here=`pwd`
cd $here
for i in {2..20}
do
	#re-new the mkd file that will be used by the perl script
	sed "s/nfs = 2/nfs = ${i}/" mkd_saved.inp > mkd.inp
	nohup $NX/makedir.pl
	#rename the default 
	mv cross-section.dat cross-section_${i}.dat
	rm -f mkd.inp
done

#Make the cross-section for all spectrum 
#sed "s/nfs = 2/nfs = 2-4/" mkd_saved.inp > mkd.inp
#nohup $NX/makedir.pl
#mv cross-section.dat cross-section_all.dat
#rm -f mkd.inp

#copy gnuplot script
#cp /ddn/home/fzzq22/CODE_AND_SCRIPT/script_NX/spectrum.gp $here

