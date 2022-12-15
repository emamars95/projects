#!/bin/bash 
# This program serve to fix the velocities of the final.output files computed with NX
# The geometries and velocities are extracted from an abin calculations

eval "$(conda shell.bash hook)"
conda activate python3

read -e -p "wirte the path where I can find the final.output.1.n files: " final_output_zero_veloc_path
read -e -p "point where I can find the velocities.xyz files (abin output for instance): " veloc_file

python3 /ddn/home/fzzq22/CODE_AND_SCRIPT/PYTHON_COMMON_MODULE/fix_veloc.py $final_output_zero_veloc_path $veloc_file