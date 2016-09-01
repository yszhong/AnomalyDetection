# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 15:05:23 2016

@author: Zhong
"""

from sklearn import cluster
import numpy

def readdata():
    gd=open("all-good-dip-newest.txt","r")
    bd=open("all-bad-dip-newest.txt","r")
    matrix=[]
    lst=[]
    blst=[]
    for line in gd:
        line=line.strip().split()
        lst.append(line[0])
        line=line[1:]
        for nums in line:
            nums=float(nums)
        matrix.append(line)
    for line in bd:
        line=line.strip().split()
        lst.append(line[0])
        blst.append(line[0])
        line=line[1:]
        for nums in line:
            nums=float(nums)
        matrix.append(line)
    matrix=numpy.array(matrix).astype(numpy.float)
    return matrix,lst,blst
    
def setweight(matrix):
    weight=[1,1,1,1,1,1,1]
    for i in range(len(weight)):
        weight[i]*=len(weight)
        weight[i]/=sum(weight)
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            matrix[i][j]*=weight[j]
    return matrix

def clustering(matrix,lst,blst):
    dblabel=cluster.DBSCAN(eps=8E-4).fit_predict(matrix)
    dblabel=select(dblabel)
    print("DBScan finished.")
    kmlabel=cluster.KMeans(n_clusters=300).fit_predict(matrix)
    kmlabel=select(kmlabel)
    print("KMeans finished.")
    bw=cluster.estimate_bandwidth(matrix,quantile=0.01,n_samples=1000)
    ms=cluster.MeanShift(bandwidth=bw)
    mslabel=ms.fit_predict(matrix)
    mslabel=select(mslabel)
    print("MeanShift finished.")
    bc=cluster.Birch(threshold=0.01)
    bmat=matrix.tolist()
    bclabel=bc.fit_predict(bmat)
    bclabel=select(bclabel)
    print("Birch finished.")
    intesec=[]
    suspct=[]
    c=0
    for i in range(len(matrix)):
        #if bclabel[i]:
            #c+=1
        #if mslabel[i]:
        if dblabel[i] and kmlabel[i] and mslabel[i] and bclabel[i]:
            intesec.append(lst[i])
        if dblabel[i] or kmlabel[i] or mslabel[i] or bclabel[i]:
            suspct.append(lst[i])
    print(str(c))
    return intesec,suspct
    
def select(label):
    static=dict()
    for i in label:
        if i in static.keys():
            static[i]+=1
        if i not in static.keys():
            static[i]=0
    for i in range(len(label)):
        if static[label[i]]>10:
            label[i]=0
        if static[label[i]]<=10:
            label[i]=1
    return label
   
def evaluate(intesec,suspct,blst,lst):
    cntint=[0,len(intesec),len(lst)-len(intesec),0]
    cntsus=0
    for i in range(len(intesec)):
        if intesec[i] in blst:
            cntint[0]+=1
            cntint[1]-=1
    for i in range(len(lst)):
        if lst[i] not in intesec and lst[i] not in blst:
            cntint[3]+=1
            cntint[2]-=1
    for i in range(len(suspct)):
        if suspct[i] in blst:
            cntsus+=1
    print(str(cntint))
    print(str(cntint[0])+"/"+str(len(intesec)))
    print(str(cntsus)+"/"+str(len(suspct)))
    
if __name__=="__main__":
    matrix,lst,blst=readdata()
    print("Data loaded.")
    matrix=setweight(matrix)
    print("Weight set.")
    intesec,suspct=clustering(matrix,lst,blst)
    print("Detected.")
    evaluate(intesec,suspct,blst,lst)
    print("Succeed")