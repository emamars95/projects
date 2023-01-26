#!/usr/bin/env python3

import config
import write_file

import os
import glob
import re

def FC_reference(liic_0,grep):                                          #grep is passed and depends on the Program used: G09 and ADC(2) grep = 4,  .. 
        if config.fc_choice == "Y" :                            		#IF the first point is the FC point
                print(config.energy_keyword, liic_0)
                for line in open(liic_0, 'r'):
                        match = re.findall(config.energy_keyword, line)         #Find the record containing the S0 Energy in A.U
                        if match:
                                config.fc_energy = float(line.split()[grep])    #SAVE the 4-th record for g09 5-th for ADC(2)
                                print("FC_energy read from liic_0  ", config.fc_energy)
        else :
                R_FILE    = open(config.REF_FILE, "r")                 #Open file containing FC energy for scailing
                config.fc_energy = float(R_FILE.readline())     #Read the energy asociated with the FC reference
                R_FILE.close()
        return()

def TDDFT_energies():
	for i in range(0, config.n_point):
		ex_data = []
		n_state = 0				                             	#Total number of state is conted automatically 

		for FILE_NAME in glob.glob("*liic*_" + str(i) + str(config.typ_keyword)):	 #config.typ_keyword=.log	
			FILE    = open(FILE_NAME, "r")      				#open files containing ground ground state energy for the i-th point

			for line in FILE:                      	 			#Look in the file line
				match = re.findall(config.energy_keyword, line)		#Find the record containing the S0 Energy in A.U
				if match:                               		#if match is not null
					config.s0_energy = float(line.split()[4])      	#Take the 4-th record and save it as so ground state energy (always singlet)

				matchs = re.findall(config.s_keyword, line)    		#Excitation energies singlets
				if matchs:
					n_state = n_state + 1
					ex_data.append(line.split()[3])    		#Keep records: [3] -> spin     [4] ->  eV Energy
					ex_data.append(line.split()[4])

				matcht = re.findall(config.t_keyword, line)    		#Excitation energies triplets
				if (matcht and config.triplet_choice == "Y"):
					n_state = n_state + 1
					ex_data.append(line.split()[3])
					ex_data.append(line.split()[4])

			FILE.close()                            #all file is investigated and then closed
		write_file.write_output(i,n_state,ex_data)

def EOM_CCSD_energies():
	for i in range(0, config.n_point):
		ex_data = []
		n_state = 0
	
		FILE_NAME   = glob.glob("*liic*_" + str(i) + str(config.typ_keyword))[0]
		NAME_S0_OUT = str(i) + ".out_tmp" 
		cmd_make = "grep 'E(CORR)' " + FILE_NAME + " | tail -1 | awk '{print $4}' > " + NAME_S0_OUT   #Extract S0 energy 
		os.system(cmd_make)
		with open(NAME_S0_OUT) as FILE:
			config.s0_energy = float(FILE.readline())
		if (config.fc_choice == "Y" and i == 0):
			config.fc_energy = config.s0_energy
		cmd_rm = "rm -rf " + NAME_S0_OUT
		os.system(cmd_rm)

		for line in open(FILE_NAME):
			matchs = re.findall("Singlet-\?Sym", line)             #Excitation energies singlets
			if matchs:
				n_state = n_state + 1
				ex_data.append(line.split()[3])                 #Keep records: [3] -> spin     [4] ->  eV Energy
				ex_data.append(line.split()[4])
		write_file.write_output(i, n_state, ex_data)

def ADC2_energies():
       for i in range(0, config.n_point):
                ex_data = []
                n_state = 0                                                             #Total number of state is conted automatically 

                for FILE_NAME in glob.glob("*liic*_" + str(i) + "/" + str(config.typ_keyword)):        #config.typ_keyword=ricc2.out       
                        cmd='grep "D1 diagnostic" ' + str(FILE_NAME) + ' | awk \'{print $5}\' >> d1_values '
                        os.system(cmd)
                        FILE    = open(FILE_NAME, "r")                                  #open files containing ground ground state energy for the i-th point

                        for line in FILE:                                               #Look in the file line
                                match = re.findall(config.energy_keyword, line)         #Find the record containing the S0 Energy in A.U
                                if match:                                               #if match is not null
                                        config.s0_energy = float(line.split()[5])       #Take the 4-th record and save it as so ground state energy (always singlet)

                                matchs = re.findall("Energy:", line)             #Excitation energies singlets
                                if (matchs and n_state < 10) :
                                        #print(line.split())
                                        n_state = n_state + 1
                                        ex_data.append(str(config.s_keyword))                 #Keep records: [3] -> spin     [4] ->  eV Energy
                                        ex_data.append(line.split()[3])
                                elif (matchs and n_state >= 10 and config.triplet_choice == "Y") :
                                        n_state = n_state + 1
                                        ex_data.append(str(config.s_keyword))
                                        ex_data.append(line.split()[3])

                        FILE.close()                            #all file is investigated and then closed
                write_file.write_output(i,n_state,ex_data)


def G09andADC2_energies():
        if (config.calc_choice == "A" or config.calc_choice == "B"):
                 liic_0 = glob.glob("*liic*_0" + str(config.typ_keyword))[0]     #Filename of the first point
                 FC_reference(liic_0,grep=4)
                 TDDFT_energies()

        if config.calc_choice == "I":
                 EOM_CCSD_energies()	

        if (config.calc_choice == "H"):
                 liic_0 = glob.glob("*liic*_0/" + str(config.typ_keyword))[0]   #For adc(2) we have the folder liic*
                 FC_reference(liic_0,grep=5)
                 ADC2_energies()

