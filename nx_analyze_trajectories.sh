#!/bin/bash

eval "$(conda shell.bash hook)"
conda activate python3

. load-NX.sh

path_script="/ddn/home/fzzq22/CODE_AND_SCRIPT/" 

python3 ${path_script}/NX_modules/trajectory_nx.py