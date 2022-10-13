#!/bin/bash
here=`pwd`

folder="THEODORE_ANALYSIS_ALONG_LIIC"
rm -rf   $folder
mkdir -p $folder

read -p "Prompt the number of excited state:   " n_state

for i in {0..100..1}
{
        cd       $folder

	namefolder="liic_${i}"
	mkdir    $namefolder

	cp $here/*_${i}.mol    $namefolder
        cp $here/*_${i}_s?.mol $namefolder

	cd $namefolder

	name=`echo *_${i}.mol | sed 's/\(^.*\).mol.*$/\1/'`

	THEODORE_IN.sh $name $n_state	

        cd $here
}
