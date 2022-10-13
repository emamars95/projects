rm -f LIIC.xyz
for i  in {0..5}  			# loop over how many intermediate geometries you want
do
    j=$(($i+17))
    awk -v step=$i '    		 # give the current step to awk for the interpolation
    BEGIN{mode = "paste"; nrsteps=5}    # begin in paste mode: just print everything that comes before the actual values that need to be interpolated
    {
        if (mode == "write") {           # write mode are all the lines where the interpolation is happening
            if ($1 == "constants") {
                mode = "paste"  	 # go back to paste mode after it is done
            } else {
                print $1"\t"$2+($3-$2)/nrsteps*step  #do the interpolation
            }
        }
        if (mode == "paste") {
            print $0
            if ($1 == "Variables:") {    #If the keyword "variables" is found go into write mode to do interpolation
                mode = "write"
            }
        }
    }' geom > geom_$j.gzmat
    obabel -igzmat geom_$j.gzmat -oxyz -Ogeom_$j.xyz  #convert gzmat into xyz
    cat geom_$j.xyz >> LIIC.xyz
done


