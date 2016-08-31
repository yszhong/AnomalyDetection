# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 19:58:31 2016

@author: Zhong
"""

fa=open("../data/rf-dip-predict-proba.txt","r")
#fa=open("../data/rf-with-black-list.txt","r")
value=dict()
for line in fa:
    line=line.strip().split()
    value[line[0]]=line[1]
fa.close()
print("table")
fb=open("../data/iptable.txt","r")
fd=open("../data/dip_score_z6_1.txt","w")
#fd=open("../data/black_list_compare.txt","w")
for line in fb:
    line=line.strip().split()
    if int(line[1])<=6788:
        continue
    if line[0] in value:
        fd.write(line[1]+"\t"+value[line[0]]+"\n")
    if line[0] not in value:
        fd.write(line[1]+"\t"+str(0.5)+"\n")
fb.close()
fd.close()
print("done")