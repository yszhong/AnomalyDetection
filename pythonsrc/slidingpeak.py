# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 14:47:17 2016

This program realizes an algorithm of anomaly detection. 

@author: Yunsong Zhong
"""

import numpy
from sklearn import cluster
import os
import pandas
import logging

def readfile():
	# read anomaly groundtruth
	f = open("../data/bad-feature-norm.txt", "r")
	badlist = []
	for line in f:
		line = line.strip().split()
		badlist.append(line[0])
	f.close()
	# read normal groundtruth
	f = open("../data/good-feature-norm.txt", "r")
	goodlist = []
	for line in f:
		line = line.strip().split()
		goodlist.append(line[0])
	f.close()
	# read time series
	f = open("../data/http-dip-1w-ip-ts1.txt", "r")
	ts = []
	ground = []
	for line in f:
		line = line.strip().split()
		numer = []
		for x in line[1:]:
			numer.append(int(x))
		ts.append(numer)
		if line[0] in badlist:
			ground.append([1])
		if line[0] in goodlist:
			ground.append([0])
	ts = numpy.array(ts)
	ground = numpy.array(ground)
	f.close()
	return ts, ground

def readallfile():
	f = open("../data/huangyixiang_ts_4.txt", "r")
	ts = []
	for line in f:
		line = line.strip().split()
		numer = []
		for x in line[1:]:
			numer.append(int(x))
		ts.append(numer)
	ts = numpy.array(ts)
	f.close()
	return ts

def slidingwindow(M, winsize):
	partts = []
	for i in range(M.shape[1]):
		part = M[:, i:i + winsize]
		partts.append(part)
	return partts	

def fftdetect(mat):
	freq = []
	for i in range(mat.shape[0]):
		f = numpy.fft.fft(mat[[i], :])
		f = abs(f)
		freq.append(f[0][1])
	freq = numpy.array(freq)
	label = numpy.zeros(len(freq))
	i = 0
	for num in freq:
		if num > 3 * numpy.mean(freq):
			label[i] = 1
		i += 1
	return label

def clustering(mat):
	ap = cluster.AffinityPropagation(damping = 0.75)
	ap.fit(mat)
	lab = ap.labels_
	af = numpy.array(ap.affinity_matrix_)
	label = numpy.zeros(len(lab))
	for i in range(lab):
		if -af[i, lab[i]] > numpy.linalg.norm(mat[lab[i]]):
			label[i] = 1
	return label

def evaluate(label, ground):
	eval = numpy.zeros((2, 2))
	for i in range(len(ground)):
		# TP
		if label[i] == 1 and ground[i] == 1:
			eval[0, 0] += 1
		# FP
		if label[i] == 1 and ground[i] == 0:
			eval[1, 0] += 1
		# FN
		if label[i] == 0 and ground[i] == 1:
			eval[0, 1] += 1
		# FN
		if label[i] == 0 and ground[i] == 0:
			eval[1, 1] += 1
	return eval

def slidingpeak(winsize):
	ts, ground = readfile()
	partts = slidingwindow(ts, winsize)
	lab = []
	for i in range(ts.shape[1] - winsize):
		dl = fftdetect(partts[i])
		lab.append(dl)
	lab = numpy.array(lab)
	label = numpy.zeros(ts.shape[0])
	for i in range(lab.shape[1]):
		temp = lab[:, [i]]
		if numpy.count_nonzero(temp) >= winsize - 1:
			label[i] = 1
	eval = evaluate(label, ground)
	return eval

def outputwindow(winsize):
	ts = readallfile()
	partts = slidingwindow(ts, winsize)
	if not os.path.exists("../result/sw/allsw" + str(winsize) + "/"):
		os.makedirs("../result/sw/allsw" + str(winsize) + "/")
	for i in range(len(partts)):
		part = partts[i]
		f = open("../result/sw/allsw" + str(winsize) + "/" + str(i) + ".csv", "w")
		for line in part:
			wline = ""
			for item in line:
				wline += str(item) + ","
			wline = wline + "\n"
			f.write(wline)
		f.close()

if __name__ == "__main__":
	#"""
	# set logging configure
	logsize = os.path.getsize("../result/slidingpeak.log")
	if logsize / 1024 / 1024 > 1:
		os.remove("../result/slidingpeak.log")
	logging.basicConfig(level = logging.INFO, 
						format = "%(asctime)s %(filename)s line:%(lineno)d %(levelname)s\n %(message)s",
						datefmt = "%b %d %Y %H:%M:%S",
						filename = "../result/slidingpeak.log",
						filemode = "a")
	console = logging.StreamHandler()
	console.setLevel(logging.INFO)
	console.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
	logging.getLogger("").addHandler(console)
	# present algorithm
	logging.info("Affinity Propagation") # comment on log
	for winsize in [4,8,12,16]:
		logging.info(str(winsize))
		eval = slidingpeak(winsize)
		logging.info(str(eval)) # output accuracy matrix
	#"""
	#outputwindow(3)