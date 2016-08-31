#!/bin/bash

cd ~
cd /home/zhong/
cd ./sp/
ls -h
cd ./pythonsrc/
python newreflect.py
cd ../matlabsrc/
matlab -nodesktop -nosplash -r newincrement
