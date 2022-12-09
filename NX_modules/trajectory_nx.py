#!/usr/bin/env python3

from os                         import getcwd
from submit_dyn_src.submit_dyn  import SUBMIT_DYNAMICS
from check_dyn_src.check_dyn    import CHECK_DYNAMICS

PWD   = getcwd()
hline = "*****************************************************************\n" 

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
def main():
    choice = input("Do you want submit DYNAMICS? (y or n)                            ")  
    if   choice.upper() == "Y":        
        SUBMIT_DYNAMICS(PWD)
    elif choice.upper() == "N":
        CHECK_DYNAMICS(PWD)
    else:
        print  (" Chose Y or N, lower characters are accepted                     \n")
        main()

if __name__ == '__main__':
    print ('\n')
    print (hline)
    print (" This script allows you to submit the dynamics in NX or to check   ")
    print (" the evolution of the trajectories. The program will automatically ")
    print (" plots and summary of the dynamics                                 ")
    print ('\n')
    print (hline)
    print ("\n")
    main() 
