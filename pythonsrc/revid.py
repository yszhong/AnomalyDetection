# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 11:26:22 2016

@author: Zhong
"""

import threading
def writefile(startline):
    global lst, mutex, dealcount
    print ("Thread "+str(int(startline/1000))+" started")
    fa=open("../data/rf-cv400-1200-top-all.txt","r")
    ct=0
    for line in fa:
        ct+=1
        if ct<startline+1:
            continue
        if ct>startline+1000:
            break
        line=line.strip().split()
        fb=open("iptable.txt","r")
        for row in fb:
            row=row.strip().split()
            if row[0]==line[0]:
                st=row[1]+"\t"+line[1]+"\n"
                if int(row[1])>=1 and int(row[1])<=279769:
                    mutex.acquire()
                    lst[int(row[1])-1]=st
                    dealcount+=1
                    if dealcount%1000==0:
                        print (str(dealcount)+" IPs launched")
                    mutex.release()
        fb.close()
    fa.close()
    print("Thread "+str(int(startline/1000))+" finished")
if __name__=="__main__":
    global lst, mutex, dealcount
    lst=[str(int(i+1))+"\n" for i in range(279769)]
    mutex=threading.RLock()
    dealcount=0
    t=[]
    for i in range(280):
        t.append(threading.Thread(target=writefile,args=(i*1000,)))
        t[i].start()
    print ("Started")
    for i in t:
        i.join()
    print ("Joined")
    fs=open("../data/sip_score_z6_0.txt","w")
    fd=open("../data/dip_score_z6_0.txt","w")
    print ("Prepare to write")
    for i in range(6788):
        fs.write(lst[i])
    for i in range(279769-6788):
        fs.write(lst[i+6788])
    fs.close()
    fd.close()
    print ("Succeed")