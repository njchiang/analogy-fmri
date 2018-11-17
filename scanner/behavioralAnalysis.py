import os, sys
import getopt
import pandas as pd
import numpy as np


"""
experiment file for analogy behavioral. need to set paths for code directory and file directory.
This is meant to be modular and reusable code, so leave main intact. modify the extra functions as necessary
for each experiment
Qarr is either the positional variability or probe
"""

### Global Variables | Experiment parameters ###
# Paradigm attributes
RESPONSE_LIST = ["a", "l"]  # valid responses. This config would be for behavioral
# RESPONSE_LIST = ["4", "3"]  # valid responses.
OUTFORMAT = '%s\t%s\t%s'

# This means that the cord is facing the subject's feet!
# QTEXT = ["yes", "no"] # make sure this corresponds with RESPONSE_LIST

def getacc(r1, r2):
    if len(r1) != len(r2):
        print "not of same length, exiting"
        return
    acc = np.mean(np.array([e == r2[i] for i,e in enumerate(r1)]))
    return acc

def analyzesub(sub, run):
    outfile = ('_').join([str(sub), str(run), 'All.csv'])
    res = pd.read_csv(outfile)
    qresp = []
    for i in res['QResponse']:
        if i != 'None':
            qresp.append(i[2])
        else:
            qresp.append(None)

    cresp = []
    for i in res['QCorrResponse']:
        if i != 'None':
            cresp.append(i)
        else:
            cresp.append(None)

    q = np.asarray(qresp, dtype=str)
    c = np.asarray(cresp, dtype=str)
    match = np.array(res['Match'])
    rts = np.array(res['QDur'])
    np.equal(qresp, cresp)
    nresp = np.mean(q != 'None')
    overall_acc = getacc(q, c)
    match_acc = getacc(q[match == 1], c[match == 1])
    nomatch_acc = getacc(q[match == 0], c[match == 0])
    hit_acc = getacc(q[c == RESPONSE_LIST[0]], c[c == RESPONSE_LIST[0]])
    miss_acc = getacc(q[c == RESPONSE_LIST[1]], c[c == RESPONSE_LIST[1]])
    print "-------------------------------"
    print "Sub: " + str(sub) + "  Run: " + str(run)
    print "-------------------------------"
    print 'Category\tAccuracy(%)\tRT(s)'
    print (OUTFORMAT % ('Overall:', str(100*overall_acc), str(np.mean(rts))))
    print (OUTFORMAT % ('Match:  ', str(100*match_acc), str(np.mean(rts[match==1]))))
    print (OUTFORMAT % ('No Match:', str(100*nomatch_acc), str(np.mean(rts[match==0]))))
    print (OUTFORMAT % ('Arrangement 1:', str(100*hit_acc), str(np.mean(rts[c == RESPONSE_LIST[0]]))))
    print (OUTFORMAT % ('Arrangement 2:', str(100*miss_acc), str(np.mean(rts[c == RESPONSE_LIST[1]]))))
    print "Response Percentage:   " + str(100 * nresp)

    return [overall_acc, match_acc, nomatch_acc, hit_acc, miss_acc, nresp]

def main(argv):
    """
    should not need to modify this
    """
    if sys.platform == 'darwin':
        ROOT = os.path.join('/Users', 'njchiang')
    else:
        ROOT = 'D:\\'
    # PATH where all of the experiment files are
    PATH = os.path.join(ROOT, 'Cloudstation', 'Grad', 'Research', 'Analogy', 'Behavioral', 'Output')
    os.chdir(PATH)

    sub = ''
    runs = 0
    try:
        opts, args = getopt.getopt(argv, "hds:r:", ["sub=", "run="])
    except getopt.GetoptError:
        print 'behavioralAnalysis.py -s <sub> -r <runs> '
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'behavioralAnalysis.py -s <sub> -r <runs> '
            sys.exit()
        elif opt in ("-s", "--sub"):
            sub = arg
        elif opt in ("-r", "--run"):
            runs = arg.split(',')
        elif opt in ("-d", "--debug"):
            print "debug mode"
            debug = True

    completeResults = np.array([analyzesub(sub, r) for r in runs])
    cmean = completeResults.mean(axis=0)
    print "----------------------------------"
    print "Overall:   " + str(100*cmean[0])
    print "Match:   " + str(100*cmean[1])
    print "No Match:   " + str(100*cmean[2])
    print "Arrangement 1:   " + str(100*cmean[3])
    print "Arrangement 2:   " + str(100*cmean[4])
    print "Response percentage:   " + str(100*cmean[5])

if __name__ == "__main__":
    main(sys.argv[1:])
