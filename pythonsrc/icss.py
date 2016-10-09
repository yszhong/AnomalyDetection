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
	for i in range(len(data)):
		data[i] = data[i] * data[i]
	ck = cumsum(data)
	ct = ck[len(ck) - 1]
	t = len(data)
	dk = numpy.zeros(len(ck))
	for i in range(len(ck)):
		dk[i] = ck[i] / ct - i / t
	return dk

def step(data):
	changepoints = []
	dk = centercusum(data)
	e, pos1 = checkcritical(dk)
	if e:
		p=pos1
		while e:
			t2 = p
			dk2a = centercusum(data[:t2 + 1])
			e, p = checkcritical(dk2a)
		kfirst = t2
		p = pos1 + 1
		e = True
		while e:
			t1 = p
			dk2b = centercusum(data[t1:])
			e, p2 = checkcritical(dk2b)
			p = p2 + p
		klast = t1 - 1
		if kfirst == klast:
			changepoints = kfirst
		else:
			changepoints = [kfirst, klast]
	return changepoints

def checkcritical(dk):
	Dstar = 1.358
	absdk = dk
	for i in range(len(absdk)):
		absdk[i] = abs(absdk[i])
	value = max(absdk)
	position = numpy.argmax(absdk)
	M = value * math.sqrt(len(absdk) / 2)
	if M > Dstar:
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

def ICSS(data):
	potential = step(data)
	potential.insert(0, 0)
	potential.append(len(data))
	potential = list(set(potential))
	converged = False
	while not converged:
		newcps = []
		for i in range(1, len(potential) - 2):
			frm = potential[i - 1] + 1
			to = potential[i + 1]
			Dk = centercusum(data[frm:to + 1])
			e, p = checkcritical(Dk)
			if e:
				newcps.append(frm + p)
		newcps.insert(0, 0)
		newcps.append(len(data))
		converged = isconverged(potential, newcps)
		if not converged:
			potential = newcps
	changepoints = potential[1:len(potential)]
	return changepoints

if __name__ == "__main__":
	data = [1, 2, 3]
	changepoints = ICSS(data)