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
			p = p2 + p
		klast = t1 - 1
		if kfirst == klast:
			changepoints = kfirst
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

def ICSS(dat, B = 0.95):
	data = dat
	potential = step(data, B)
	potential.append(len(data) - 1)
	potential.append(0)
	potential = list(set(potential))
	potential.sort()
	converged = False
	while not converged:
		newcps = []
		for i in range(1, len(potential) - 1):
			frm = potential[i - 1] + 1
			to = potential[i + 1]
			Dk = centercusum(data[frm:to + 1])
			e, p = checkcritical(Dk, B)
			if e:
				newcps.append(frm + p)
		newcps.append(0)
		newcps.append(len(data) - 1)
		newcps = list(set(newcps))
		newcps.sort()
		converged = isconverged(potential, newcps)
		if not converged:
			potential = newcps
	changepoints = potential[1:len(potential) - 1]
	return changepoints

if __name__ == "__main__":
	data = [3, 2, 17, 4, 3, 6, 806, 2, 7, 9, 11, 22, 1, 0, 0, 4, 3, 5]
	changepoints = ICSS(data)
	print changepoints