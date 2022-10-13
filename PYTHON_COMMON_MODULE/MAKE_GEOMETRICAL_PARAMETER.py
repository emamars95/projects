#!/usr/local/Cluster-Apps/python/3.6.8/bin/python3.6

import sys
sys.path.append('/ddn/home/fzzq22/CODE_AND_SCRIPT/PYTHON_COMMON_MODULE')

import TRAJECTORY_MODULES

TIMESTEP	= float(input(" Insert the time step between two consecutive points:    "))
N_TEMPLATE_GEO	= str(  input(" Insert the name of the coordinates template        :    "))

TEMPLATE_GEO	= "/ddn/home/fzzq22/CODE_AND_SCRIPT/BIN_GEO_INP/" + N_TEMPLATE_GEO

TRAJECTORY_MODULES.MAKE_GEOMETRICAL_COORDINATES(TIMESTEP, TEMPLATE_GEO)

