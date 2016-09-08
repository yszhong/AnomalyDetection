# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 08:49:28 2016
The first algorithm is to apply kmeans clustering using weight in random forest. 
The second one is to apply random forest to every cluster in kmeans. 
@author: Zhong
"""

from sklearn import cluster
from sklearn import ensemble
import numpy
import random
import time
import warnings

def kmc(D, k):
    km = cluster.KMeans(n_clusters = k)
    km.fit(D)
    label = km.labels_
    return label

def loadmetri():
    pts = []
    metri = []
    f = open("../data/all-good-dip-newest.txt", "r")
    for line in f:
        line = line.strip().split()
        pts.append(line[0])
        line = line[1:]
        metri.append(line)
    f = open("../data/all-bad-dip-newest.txt", "r")
    for line in f:
        line = line.strip().split()
        pts.append(line[0])
        line = line[1:]
        metri.append(line)
    m = []
    for line in metri:
        t = []
        for thing in line:
            t.append(float(thing))
        m.append(t)
    metri = numpy.array(m)
    return pts, metri

def rfc(M, label):
    rf = ensemble.RandomForestClassifier()
    rf.fit(M, label)
    importance = rf.feature_importances_
    return importance

def validate(label, truth, M, cluster_width = 10, threshold = 0.01):
    cldict = dict()
    result = numpy.array([[0.0, 0.0], [0.0, 0.0]])
    i = 0
    for item in label:
        if item in cldict.keys():
            cldict[item].append(i)
        if item not in cldict.keys():
            cldict[item] = [i]
        i += 1
    for ks in cldict.keys():
        flag = False
        if len(cldict[ks]) <= cluster_width:
            flag = True
        for thing in cldict[ks]:
            if bidistance(thing, cldict[ks], M) > threshold:
                flag = True
            if flag:
                if truth[thing]:
                    result[0, 1] += 1
                if not truth[thing]:
                    result[0, 0] += 1
            if not flag:
                if truth[thing]:
                    result[1, 1] += 1
                if not truth[thing]:
                    result[1, 0] += 1
    return result

def bidistance(item, group, matrix):
    item = matrix[item]
    m = []
    for thing in group:
        m.append(matrix[thing])
    m = numpy.array(m)
    average = numpy.mean(m, axis = 0)
    distance = numpy.linalg.norm(item - average)
    return distance

def integrate1():
    pts, M = loadmetri()
    label = kmc(M, 90)
    importance = rfc(M, label)
    N = []
    for item in M:
        outer = []
        for i in range(len(importance)):
            outer.append(item[i] * importance[i])
        N.append(outer)
    label = kmc(N, 90)
    label = numpy.array(label)
    truth = numpy.zeros(2427)
    truth = numpy.concatenate((truth, numpy.ones(8074)), axis = 0)
    vl = validate(label, truth, N)
    return vl

def integrate2():
    pts, M = loadmetri()
    truth = numpy.zeros(2427)
    truth = numpy.concatenate((truth, numpy.ones(8074)), axis = 0)
    pd = []
    pdlabel = []
    randlist = random.sample(range(10501), 2000)
    for i in randlist:
        pd.append(M[i])
        if i < 2427:
            pdlabel.append([1])
        else:
            pdlabel.append([0])
    M = numpy.delete(M, randlist, axis = 0)
    truth = numpy.delete(truth, randlist)
    pdlabel = numpy.array(pdlabel)
    km = cluster.KMeans(n_clusters = 90)
    km.fit(M)
    label = km.labels_
    kmdict = dict()
    lbdict = dict()
    i  = 0
    for item in label:
        lbd = 1 if truth[i] else 0
        if item in kmdict.keys():
            kmdict[item].append(M[i])
            lbdict[item].append(lbd)
        if item not in kmdict.keys():
            kmdict[item] = []
            kmdict[item].append(M[i])
            lbdict[item] = []
            lbdict[item].append(lbd)
        i += 1
    rf = []
    i = 0
    for item in kmdict.keys():
        rft = ensemble.RandomForestClassifier()
        rf.append(rft)
        rf[i].fit(kmdict[item], lbdict[item])
        i += 1
    label = km.predict(pd)
    belief = []
    for i in range(len(label)):
        a = rf[label[i]].predict(pd[i].reshape(1, -1))
        a = 1 if a[0] > 0.5 else 0
        belief.append(a)
    label = validate(belief, pdlabel, pd, threshold = 0.5)
    return label

if __name__ == "__main__":
    print "Started."
    start = time.clock()
    label = integrate1()
    end = time.clock()
    T = end - start
    print "Time cost: " + str(T) + " seconds."
    print str(label)
    start = time.clock()
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        label = integrate2()
    end = time.clock()
    T = end - start
    print "Time cost: " + str(T) + " seconds."
    print str(label)
    print "Succeed!"