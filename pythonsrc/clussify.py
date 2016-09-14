# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 08:49:28 2016
The first algorithm is to apply kmeans clustering using weight in random forest. 
The second one is to apply random forest to every cluster in kmeans. 
@author: Zhong
"""

from sklearn import cluster
from sklearn import ensemble
from sklearn import metrics
import numpy
import random
import time
import warnings
import sys

def afc(D):
    af = cluster.AffinityPropagation()
    af.fit(D)
    label = af.labels_
    return label

def loadmetri():
    # Preprocessing features
    pts = []
    metri = []
    #f = open("../data/all-good-dip-newest.txt", "r")
    #f = open("../data/new-good.txt", "r")
    f = open("../data/good-feature.txt", "r")
    for line in f:
        line = line.strip().split()
        pts.append(line[0])
        line = line[1:]
        metri.append(line)
    #f = open("../data/all-bad-dip-newest.txt", "r")
    #f = open("../data/new-bad.txt", "r")
    f = open("../data/bad-feature.txt", "r")
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
    # Get random forest importance
    rf = ensemble.RandomForestClassifier()
    rf.fit(M, label)
    importance = rf.feature_importances_
    return importance

def validate(label, truth, M, cluster_width = 10, threshold = 2):
    # Verify the clustering accuracy
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
                    result[0, 0] += 1
                if not truth[thing]:
                    result[0, 1] += 1
            if not flag:
                if truth[thing]:
                    result[1, 0] += 1
                if not truth[thing]:
                    result[1, 1] += 1
    result = numpy.array(result)
    A = anomindexes(result)
    return result, A

def bidistance(item, group, matrix):
    # Compute distances between two points
    item = matrix[item]
    m = []
    for thing in group:
        m.append(matrix[thing])
    m = numpy.array(m)
    average = numpy.mean(m, axis = 0)
    distance = numpy.linalg.norm(item - average)
    return distance

def anomindexes(emat):
    # Compute several indexes
    TP = emat[0, 0]
    FP = emat[0, 1]
    FN = emat[1, 0]
    TN = emat[1, 1]
    P = TP / (TP + FP)
    R = TP / (TP + FN)
    F = 2 * P * R / (P + R)
    Acc = (TP + FN) / (TP + TN + FP + FN)
    evl = [Acc, P, R, F]
    return evl

def cluseval(label, truth):
    rand = metrics.adjusted_rand_score(truth, label)
    mutual = metrics.adjusted_mutual_info_score(truth, label)
    homo = metrics.homogeneity_score(truth, label)
    complete = metrics.completeness_score(truth, label)
    v = metrics.v_measure_score(truth, label)
    result = [rand, mutual, homo, complete, v]
    return result

def integrate1():
    # The first algorithm
    pts, M = loadmetri()
    truth = numpy.ones(2427)
    truth = numpy.concatenate((truth, numpy.zeros(8074)), axis = 0)
    rate = 1
    N = M
    iter = 0
    lastimp = numpy.zeros(len(M[0]))
    while rate > 0.01 and iter < 5:
        label = afc(N)
        importance = rfc(N, label)
        M = N
        N = []
        for item in M:
            outer = []
            for i in range(len(importance)):
                outer.append(item[i] * importance[i])
            N.append(outer)
        rate = numpy.linalg.norm(importance-lastimp) / numpy.linalg.norm(importance)
        lastimp = importance
        iter += 1
    label = numpy.array(label)
    vl = cluseval(label, truth)
    return vl, importance, iter

def integrate2(nc, cw, th, pc = 0.5):
    # The second algorithm
    pts, M = loadmetri()
    truth = numpy.ones(2427)
    truth = numpy.concatenate((truth, numpy.zeros(8074)), axis = 0)
    pd = []
    pdlabel = []
    randlist = random.sample(range(10501), 5250)
    for i in randlist:
        pd.append(M[i])
        if i < 2427:
            pdlabel.append([1])
        else:
            pdlabel.append([0])
    M = numpy.delete(M, randlist, axis = 0)
    truth = numpy.delete(truth, randlist)
    pdlabel = numpy.array(pdlabel)
    km = cluster.KMeans(n_clusters = nc)
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
    rf = dict()
    for item in kmdict.keys():
        rft = ensemble.RandomForestClassifier()
        rf[item] = rft
        rf[item].fit(kmdict[item], lbdict[item])
    belief = []
    for i in range(len(pd)):
        label = km.predict(pd[i].reshape(1, -1))
        if len(label) is not 1:
            print label
        rft = rf[label[0]]
        a = rft.predict(pd[i].reshape(1, -1))
        a = 1 if a[0] > pc else 0
        belief.append(a)
    label, A = validate(belief, pdlabel, pd, cluster_width = cw, threshold = th)
    return label, A

def baseline1(cw, th, pc = 0.5):
    # Random Forest baseline
    pts, M = loadmetri()
    truth = numpy.ones(2427)
    truth = numpy.concatenate((truth, numpy.zeros(8074)), axis = 0)
    pd = []
    pdlabel = []
    randlist = random.sample(range(10501), 5250)
    for i in randlist:
        pd.append(M[i])
        if i < 2427:
            pdlabel.append([1])
        else:
            pdlabel.append([0])
    M = numpy.delete(M, randlist, axis = 0)
    truth = numpy.delete(truth, randlist)
    pdlabel = numpy.array(pdlabel)
    rf = ensemble.RandomForestClassifier()
    rf.fit(M, truth)
    belief = []
    for i in range(len(pdlabel)):
        a = rf.predict(pd[i].reshape(1, -1))
        a = 1 if a > pc else 0
        belief.append(a)
    label, A = validate(belief, pdlabel, pd, cluster_width = cw, threshold = th)
    return label, A

def baseline2():
    # Clustering baseline
    pts, M = loadmetri()
    #label = kmc(M, nc)
    label = afc(M)
    label = numpy.array(label)
    truth = numpy.ones(2427)
    truth = numpy.concatenate((truth, numpy.zeros(8074)), axis = 0)
    m = cluseval(label, truth)
    return m

if __name__ == "__main__":
    print "Started."
    nc = 100
    cw = 10
    th = 0.1
    pc = 0.7
    if len(sys.argv) > 1:
        nc = int(sys.argv[1])
    if len(sys.argv) > 2:
        cw = float(sys.argv[2])
    if len(sys.argv) > 3:
        th = float(sys.argv[3])
    if len(sys.argv) > 4:
        pc = float(sys.argv[4])
    #"""
    print "Start AP."
    start = time.clock()
    label = baseline2()
    end = time.clock()
    T = end - start
    print "Time cost: " + str(T) + " seconds."
    print "AP Rate: " + str(label)
    print "Start WeightBased."
    start = time.clock()
    label, importance, iter = integrate1()
    end = time.clock()
    T = end - start
    print "Time cost: " + str(T) + " seconds."
    print "WeightBased Rate: " + str(label) + "\t" + str(iter)
    print "Importance: " + str(importance)
    #"""
    print "Start RF."
    start = time.clock()
    label, A = baseline1(cw, th, pc)
    end = time.clock()
    T = end - start
    print "Time cost: " + str(T) + " seconds."
    print "RF Rate: " + str(label) + "\n" + str(A)
    print "Start ClusterBased."
    start = time.clock()
    with warnings.catch_warnings():
        warnings.simplefilter("error")
    label, A = integrate2(nc, cw, th, pc)
    end = time.clock()
    T = end - start
    print "Time cost: " + str(T) + " seconds."
    print "ClusterBased Rate:" + str(label) + "\n" + str(A)
    #"""
    print "Succeed!"
