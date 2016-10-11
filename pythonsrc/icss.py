# -*- coding: utf-8 -*-
"""
Created on Sun Oct  9 22:15:37 2016

This program realizes a python version of ICSS (Iterated Cumulative Sums of Squares) algorithm. 
Refined by Matlab code of rvlasveld/ICSS on Github. 
Algorithm is from Inclan et al. 1994, Use of Cumulative Sums of Squares for Retrospective Detection of Changes of Variance

@author: Yunsong Zhong
"""
import numpy
import math

def cumsum(data):
	for i in range(len(data)):
		if i > 0:
			data[i] += data[i - 1]
	return data

def centercusum(data):
	dat = range(len(data))
	for i in range(len(data)):
		dat[i] = math.pow(data[i], 2)
	ck = cumsum(dat)
	ct = ck[-1]
	if ct == 0:
		return [0 for i in range(len(dat))]
	t = len(data)
	dk = numpy.zeros(len(ck))
	for i in range(len(ck)):
		dk[i] = float(ck[i]) / ct - float(i + 1) / t
	#import pdb
	#pdb.set_trace()
	return dk

def step(dat, B):
	data = dat
	changepoints = []
	dk = centercusum(data)
	e, pos1 = checkcritical(dk, B)
	if e:
		p = pos1
		while e:
			t2 = p
			dk2a = centercusum(data[:t2 + 1])
			e, p = checkcritical(dk2a, B)
		kfirst = t2
		p = pos1 + 1
		e = True
		while e:
			t1 = p
			dk2b = centercusum(data[t1:])
			e, p2 = checkcritical(dk2b, B)
			p = p2 + p + 1
		klast = t1 - 1
		if kfirst == klast:
			changepoints = [kfirst]
		else:
			changepoints = [kfirst, klast]
	return changepoints

def checkcritical(dk, B):
	Dstar = {0.5:0.828, 0.75:1.019, 0.90:1.224, 0.95:1.358, 0.99:1.628}
	absdk = dk
	for i in range(len(absdk)):
		absdk[i] = abs(absdk[i])
	value = max(absdk)
	position = numpy.argmax(absdk)
	if sum(absdk) == 0:
		position = len(absdk) - 1
	M = value * math.sqrt(len(absdk) / 2)
	if M > Dstar[B]:
		exceed = True
	else:
		exceed = False
	return exceed, position

def isconverged(old, new):
	diff = 2
	converged = True
	if len(old) == len(new):
		for i in range(len(new)):
			low = min([old[i], new[i]])
			high = max([old[i], new[i]])
			if high - low > diff:
				converged = False
				break
	else:
		converged = False
	return converged

def ICSS(data, B = 0.95):
	if len(data) == 0:
		return []
	potential = step(data, B)
	potential.append(len(data) - 1)
	potential.append(0)
	potential = list(set(potential))
	potential.sort()
	previous = []
	converged = False
	while not converged:
		newcps = []
		for i in range(1, len(potential) - 1):
			frm = potential[i - 1] + 1
			to = potential[i + 1] + 1
			Dk = centercusum(data[frm:to])
			e, p = checkcritical(Dk, B)
			if e:
				newcps.append(frm + p)
		newcps.append(0)
		newcps.append(len(data) - 1)
		newcps = list(set(newcps))
		newcps.sort()
		converged = isconverged(potential, newcps)
		if not converged: # Revise for iteration-repeat problem, Yunsong Zhong
			for records in previous:
				if not converged:
					converged = isconverged(records, newcps)
		if not converged:
			potential = newcps
			previous.append(potential)
	changepoints = potential[1:len(potential) - 1]
	return changepoints

if __name__ == "__main__":
	data = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 6.000000000000001, 7.500000000000001, 7.500000000000002, 9.000000000000002, 3.500000000000001, 1.5000000000000002, 2.0000000000000004, 1.5000000000000002, 1.5000000000000004, 1.5000000000000002, 1.0000000000000002, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.5000000000000004, 7.000000000000001, 7.000000000000001, 7.000000000000001, 16.000000000000004, 13.0, 13.000000000000002, 13.0, 1.0000000000000002, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.5000000000000004, 13.500000000000002, 16.000000000000004, 25.000000000000007, 29.000000000000007, 19.000000000000007, 23.500000000000007, 20.000000000000004, 18.500000000000004, 22.500000000000004, 15.500000000000004, 10.000000000000002, 5.000000000000001, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 4.000000000000001, 6.000000000000001, 25.000000000000004, 39.5, 38.50000000000001, 43.5, 41.0, 35.00000000000001, 34.5, 30.000000000000004, 17.000000000000004, 8.500000000000002, 6.000000000000001, 4.500000000000001, 1.0000000000000002, 1.0000000000000002, 1.0000000000000002, 4.500000000000001, 4.500000000000001, 4.500000000000001, 4.500000000000001, 0.0, 0.0, 0.0, 0.0, 4.000000000000001, 10.000000000000002, 17.0, 17.000000000000004, 16.0, 10.000000000000002, 6.000000000000001, 7.000000000000002, 4.500000000000001, 4.500000000000001, 1.5000000000000002, 0.5000000000000001, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.5000000000000002, 1.5000000000000002, 3.500000000000001, 3.500000000000001, 2.0000000000000004, 2.0000000000000004, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.5000000000000002, 6.5, 7.500000000000001, 7.5, 6.000000000000001, 9.000000000000002, 8.000000000000002, 8.000000000000002, 8.000000000000002, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.0, 1.5000000000000002, 7.500000000000001, 7.500000000000001, 7.500000000000001, 6.000000000000001, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
	changepoints = ICSS(data)
	print changepoints