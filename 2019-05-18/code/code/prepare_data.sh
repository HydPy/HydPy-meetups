#!/bin/sh

for i in -1 0 1 2 3 4 5 6 7 8 9; 
	do 
		echo $i; 
		python prepare_data.py $i; 
	done;
