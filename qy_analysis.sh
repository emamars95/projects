#!/bin/bash 

eval "$(conda shell.bash hook)"
conda activate python3

path_script="/ddn/home/fzzq22/CODE_AND_SCRIPT" 

python3 ${path_script}/Global_Analysis/qy_analysis.py 