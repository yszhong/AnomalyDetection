# select connections in verified IP list
import os
gd = open("../data/all-good-dip-newest.txt", "r")
bd = open("../data/all-bad-dip-newest.txt", "r")
tb = open("../data/iptable.txt", "r")
ipdict = dict()
for line in tb:
    line = line.strip().split()
    line[1] = int(line[1])
    ipdict[line[0]] = line[1]
lst = []
for line in gd:
    line = line.strip().split()
    line = line[0]
    lst.append(ipdict[line])
for line in bd:
    line = line.strip().split()
    line = line[0]
    lst.append(ipdict[line])
wf = open("../result/edges.txt", "w")
wf.truncate()
wl = []
for roots, dirs, paths in os.walk("../data/increment1/"):
    for files in paths:
        print "Filename: " + files
        files = os.path.join(roots, files)
        files = open(files, "r")
        for line in files:
            line = line.strip().split()
            line[0] = int(line[0])
            line[1] = int(line[1])
            flag = False
            if line[0] in lst or line[1] in lst:
                flag = True
            if flag:
                if [line[0], line[1]] not in wl:
                    wl.append([line[0], line[1]])
                    line = str(line[0]) + "\t" + str(line[1]) + "\n"
                    wf.write(line)
wf.close()
print "Succeed"