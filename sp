#!/bin/bash

cd ~
cd /home/zhong/
cd ./sp/
ls -h
cd ./pythonsrc/
python newreflect.py
cd ../matlabsrc/
for ((i=0;i<10;i+=1)); do c=$(echo 0.1*$i|bc); done
matlab -nodesktop -nosplash -r newincrement
