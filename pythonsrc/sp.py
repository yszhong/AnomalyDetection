# -*- coding: utf-8 -*-
"""
Created on Fri Jul 15 12:17:03 2016

@author: Zhong Yunsong
"""

import networkx
import os
import math

def getprior():
    prior = networkx.Graph()
    
    f = open("../data/sip_score_z2_1.txt", "r")
    for line in f:
        line = line.strip().split()
        line[0] = int(line[0])
        line[1] = float(line[1])
        if line[1] <= 0 :
            line[1] = 1E-6
        if line[1] >= 1:
            line[1] = 1 - 1E-6
        if line[0] not in prior.nodes():
            pro = [math.log(1 - line[1]), math.log(line[1])]
            prior.add_node(line[0], info = pro, dip = 0)
    f.close()
    print "Source IP prior read"
    
    f = open("../data/dip_score_z6_0.txt", "r")
    for line in f:
        line = line.strip().split()
        if not len(line):
            continue
        line[0] = int(line[0])
        line[1] = float(line[1])
        if line[1] <= 0:
            line[1] = 1E-6
        if line[1] >= 1:
            line[1] = 1 - 1E-6
        if line[0] not in prior.nodes():
            pro = [math.log(1 - line[1]), math.log(line[1])]
            prior.add_node(line[0], info = pro, dip = 1)
    f.close()
    print "Destination IP prior read"
    return prior
    
def setedge(prior, filename):
    #delete edges from previous timestamp
    for (u, v) in prior.edges():
        prior.remove_edge(u, v)
    #get edges of new timestamp
    f = open(filename, "r")
    for line in f:
        line = line.strip().split()
        line[0] = int(line[0])
        line[1] = int(line[1])
        prior.add_edge(line[0], line[1])
    f.close()
    print "Edges read"
    return prior

def speagle(prior, trans = [0.4, 0.6, 0.8, 0.2, 0.4, 0.6, 0.8, 0.2]):
    belief=networkx.Graph()
    
    for (u, v) in prior.edges():
        prior[u][v]["message_forward"] = [1, 1];
        prior[u][v]["message_backward"] = [1, 1];

    count = 0
    repeat = True
    while repeat:
        threshold = -1
        count += 1
        # max iteration times
        if count > 12:
            repeat = False
        # initialization
        for (u, v) in prior.edges():
            sum_forward = [0, 0]
            sum_backward = [0, 0]
            for (s, d) in prior.edges(u):
                if d is not v:
                    sum_forward[0] += prior[s][d]["message_forward"][0]
                    sum_forward[1] += prior[s][d]["message_forward"][1]
            for (s, d) in prior.edges(v):
                if s is not u:
                    sum_backward[0] += prior[s][d]["message_backward"][0]
                    sum_backward[1] += prior[s][d]["message_backward"][1]
            
            to_part = [0, 0]
            from_part = [0, 0]
            info = networkx.get_node_attributes(prior, "info")
            to_part[0] = info[u][0] + sum_forward[0]
            to_part[1] = info[u][1] + sum_forward[1]
            from_part[0] = info[v][0] + sum_backward[0]
            from_part[1] = info[v][1] + sum_backward[1]
            # toward message
            term = [[0, 0], [0, 0]]
            term[0][0] = to_part[0] + trans[0]
            term[0][1] = to_part[1] + trans[1]
            term[1][0] = to_part[0] + trans[2]
            term[1][1] = to_part[1] + trans[3]
            newmsg = [0, 0]
            newmsg[0] = math.log(math.exp(term[0][0]) + math.exp(term[0][1]))
            newmsg[1] = math.log(math.exp(term[1][0]) + math.exp(term[1][1]))
            newmsg[0] -= math.log(math.exp(newmsg[0]) + math.exp(newmsg[1]))
            newmsg[1] -= math.log(math.exp(newmsg[0]) + math.exp(newmsg[1]))
            fark = [0, 0]
            fark[0] = math.exp(newmsg[0]) - math.exp(prior[u][v]["message_forward"][0])
            fark[1] = math.exp(newmsg[1]) - math.exp(prior[u][v]["message_forward"][1])
            fark = (fark[0] ** 2 + fark[1] ** 2) ** 0.5
            threshold = max([threshold, fark])
            prior[u][v]["message_forward"] = newmsg
            # backward message
            term[0][0] = from_part[0] + trans[4]
            term[0][1] = from_part[1] + trans[5]
            term[1][0] = from_part[0] + trans[6]
            term[1][1] = from_part[1] + trans[7]
            newmsg[0] = math.log(math.exp(term[0][0]) + math.exp(term[0][1]))
            newmsg[1] = math.log(math.exp(term[1][0]) + math.exp(term[1][1]))
            newmsg[0] -= math.log(math.exp(newmsg[0]) + math.exp(newmsg[1]))
            newmsg[1] -= math.log(math.exp(newmsg[0]) + math.exp(newmsg[1]))
            fark = [0, 0]
            fark[0] = math.exp(newmsg[0]) - math.exp(prior[u][v]["message_backward"][0])
            fark[1] = math.exp(newmsg[1]) - math.exp(prior[u][v]["message_backward"][1])
            fark = (fark[0] ** 2 + fark[1] ** 2) ** 0.5
            threshold = max([threshold, fark])
            prior[u][v]["message_backward"] = newmsg
        # stop condition
        if threshold < 1E-3:
            repeat = False
    print str(count - 1) + " iterations finished"
    # generate belief
    inform = networkx.get_node_attributes(prior, "info")
    destin = networkx.get_node_attributes(prior, "dip")
    for key in inform:
        if key not in belief.nodes():
            belief.add_node(key, belief = math.exp(inform[key][1]), dip = destin[key])
    bel = networkx.get_node_attributes(belief, "belief")
    for nds in bel:
        bel[nds] = [math.log(1 - bel[nds]), math.log(bel[nds])]
    for n in prior.nodes():
        if destin[n]:
            for (u, v) in prior.edges(n):
                bel[n] += prior[u][v]["message_forward"]
        if not destin[n]:
            for (u, v) in prior.edges(n):
                bel[n][0] += prior[u][v]["message_forward"][0]
                bel[n][1] += prior[u][v]["message_forward"][1]
    for i in range(2):
        nwm = bel[n]
        bel[n][i] -= math.log(math.exp(nwm[0]) + math.exp(nwm[1]))
    for k in bel:
        bel[k]  = math.exp(bel[k][1])
    networkx.set_node_attributes(belief, "belief", bel)
    return belief
        
def btop(belief):
    blf = networkx.get_node_attributes(belief,"belief")
    networkx.set_node_attributes(belief, "info", blf)
    return belief
    
def writebelief(belief):
    if os.path.exists("../result/pt/"):
        os.makedirs("../result/pt/")
    fs = open("../result/pt/sip_score.txt", "wt")
    fd = open("../result/pt/dip_score.txt", "wt")
    bd = networkx.get_node_attributes(belief, "dip")
    for u in belief.nodes():
        blf = networkx.get_node_attributes(belief, "belief")
        if bd[u]:
            fd.write(str(u) + "\t" + str(blf[u]) + "\n")
        if not bd[u]:
            fs.write(str(u) + "\t" + str(blf[u]) + "\n")
    fs.close()
    fd.close()
    print "Belief writtern to file"

if __name__ == "__main__":
    print "Algorithm established."
    prior = getprior()
    for p,dname,filenameset in os.walk("../data/increment1/"):
        for filename in filenameset:
            print filename + " Starts..."
            filename = "../data/increment1/" + filename
            prior = setedge(prior, filename)
            belief = speagle(prior)
            prior = btop(belief)
    writebelief(belief)
    print "Succeed."