# -*- coding: utf-8 -*-
"""
Fuse anomaly data from verified set and clustering result.

Created on Aug 23 2016
@author: Zhong Yunsong
"""

from sklearn import cluster
import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot
import numpy
import sys

def kmeansanomaly(metri):
    kmodel = cluster.KMeans(n_clusters = 90)
    kmodel.fit(metri)
    label = kmodel.labels_
    return label, kmodel

def loadmetri():
    pts = []
    metri = []
    f = open("../data/all-good-dip-newest.txt", "r")
    for line in f:
        line = line.strip().split()
        pts.append(line[0])
        line = line[1:]
        metri.append(line)
    f.close()
    f = open("../data/all-bad-dip-newest.txt", "r")
    for line in f:
        line = line.strip().split()
        pts.append(line[0])
        line = line[1:]
        metri.append(line)
    metri = numpy.array(metri)
    f.close()
    return pts, metri

def distance(point):
    dist = numpy.linalg.norm(point)
    return dist

def majoranom(pt, threshold):
    isanom = False
    if distance(pt) >= threshold:
        isanom = True
    return isanom

def minoranom(pt, threshold):
    isanom = True
    if distance(pt) >= threshold:
        isanom = False
    return isanom


def fusion(pts, label, metri, kmd, threshold = 4, tmajor = 4.7, tminor = 1E-4):
    anomalist = []
    groupdict = dict()
    for p in label:
        if p in groupdict.keys():
            groupdict[p] += 1
        if p not in groupdict.keys():
            groupdict[p] = 0
    for p in range(len(label)):
        temp = []
        for thing in metri[p]:
            temp.append(float(thing))
        temp = numpy.array(temp)
        pcenter = kmd.transform(temp.reshape(1, -1))
        if groupdict[label[p]] <= threshold:
            isanom = minoranom(pcenter, tminor)
        elif groupdict[label[p]] > threshold:
            isanom = majoranom(pcenter, tmajor)
        if isanom:
            anomalist.append(pts[p])
    return anomalist

def saveanom(anomalist):
    f = open("../result/newlabel/new_list.txt", "w")
    for line in anomalist:
        f.write(str(line) + "\n")
    f.close()

def visualize(anomalist):
    """
    pyplot.figure(1)
    pyplot.subplot(1, 1, 1)
    pyplot.plot(anomalist)
    pyplot.title("Anomalist")
    pyplot.xlabel("IP")
    pyplot.ylabel("Anomaly Score")
    pyplot.legend()
    pyplot.show()
    pyplot.savefig(filename, format = "eps")
    """
    pts = []
    f = open("../data/all-bad-dip-newest.txt", "r")
    for line in f:
        line = line.strip().split()
        pts.append(line[0])
    f.close()
    overlap = 0
    old = len(pts)
    newlst = len(anomalist)
    for line in anomalist:
        if line in pts:
            overlap += 1
            old -= 1
            newlst -= 1
    piedata = [old, overlap, newlst]
    pyplot.pie(piedata)
    pyplot.show()
    pyplot.savefig("../result/newlabel/dstrpie.png")
    print piedata

if __name__ == "__main__":
    print "Algorithm begin."
    pts, metri = loadmetri()
    print "File loaded."
    label, kmodel = kmeansanomaly(metri)
    print "KMeans Finished."
    t = []
    for i in range(len(sys.argv) - 1):
        t.append(float(sys.argv[i + 1]))
    anomalist = fusion(pts, label, metri, kmodel, t[0], t[1], t[2])
    print "Data Fused."
    saveanom(anomalist)
    print str(len(anomalist)) + " records detected."
    pd = visualize(anomalist)
    print "Succeed!"
