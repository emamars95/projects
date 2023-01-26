#!/usr/bin/env python3

#########################################################################################
# This program extract and convert energies from the most common 3rd party QC			#
# and give in output a file containing, along the column, singlets and triplets states 	#
# energies and, along the rows with the possibility of plotting the LIIC 				#
######################################################################################### 

# This module contains:
# The main menu 
# A subroutine to convert the input give inline to a string if necessary


# return string if the input is given in bytes
def to_str(bytes_or_str):
	if isinstance(bytes_or_str, bytes):
		value = bytes_or_str.decode('utf-8')
	else:
		value = bytes_or_str
	return value # Instance of str 

# Main menu
def main():
	import init.config as config
	import init.init_subrutine as init
	import sys

	if len(sys.args) > 1:
		parameterfile = to_str(sys.argv[1])
		init.parsing(parameterfile)
	else:
		init.menu()
		init.set_up()

if __name__ == '__main__':
	main()