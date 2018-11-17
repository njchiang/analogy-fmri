"""Notebook that goes through making regressors for FSL"""
# these should be the only things i need
# need to trim 4 TRs
import os
import sys
import pandas as pd
import numpy as np
ROOT = os.path.join('D:\\', 'fmri', 'Analogy')


def runparse(r):
    return str("Run" + str(r)[-1])


# write an AB/CD/Probe regressors (main effects)
def writeABCDtxt(sub, run, fulldata):
    ABdf = fulldata[fulldata['AB'] == 1][['Onset', 'Duration', 'Intensity']]
    ABdf.to_csv(path_or_buf=os.path.join(ROOT, 'data', sub, 'behav', 'regressors', runparse(run) + '_AB.txt'), sep=' ', index=False, header=False)
    CDdf = fulldata[fulldata['CD'] == 1][['Onset', 'Duration', 'Intensity']]
    CDdf.to_csv(path_or_buf=os.path.join(ROOT, 'data', sub, 'behav', 'regressors', runparse(run) + '_CD.txt'), sep=' ', index=False, header=False)
    Pdf = fulldata[fulldata['Probe'] == 1][['Onset', 'Duration', 'Intensity']]
    Pdf.to_csv(path_or_buf=os.path.join(ROOT, 'data', sub, 'behav', 'regressors', runparse(run) + '_Probe.txt'), sep=' ', index=False, header=False)


# write specific regressors (sub conditions)
def writesubcond(stim, spec, sub, run, fulldata):
    for i in np.arange(int(np.max(fulldata[fulldata[stim]==1][str(stim) + str(spec)]))):
        print(i)
        partialPD = fulldata[fulldata[stim]==1]
        wPD = partialPD[partialPD[str(stim) + str(spec)] == str(i+1)][['Onset', 'Duration', 'Intensity']]
        wPD.to_csv(path_or_buf=os.path.join(ROOT, 'data', sub, 'behav', 'regressors', runparse(run) + '_' + stim + '_' + spec + '_' + str(i+1) + '.txt'), sep=' ', index=False, header=False)


# write condition regressors (main conditions)
def writeConditiontxt(sub, run):
    fulldata = pd.read_csv(
        os.path.join(ROOT, 'data', sub, 'behav', 'from_scanner', str(sub) + '_' + str(run) + '.tsv'), sep='\t')
    fulldata['Intensity'] = pd.Series(np.ones(len(fulldata.index)), index=fulldata.index)
    TrialType = np.empty(len(fulldata.index), dtype="S5")
    for c in ["AB", 'CD', 'Probe']:
        TrialType[np.array(fulldata[c].tolist()) == 1] = c
    fulldata['TrialType'] = pd.Series(TrialType, index=fulldata.index)
    fulldata.to_csv(path_or_buf=os.path.join(ROOT, 'data', sub, 'behav', 'labels', 'Run' + run[-1] + '.tsv'),
                    sep='\t', index=False)
    writeABCDtxt(sub, run, fulldata)
    for stim in ['AB', 'CD']:
        for spec in ['MainRel', 'SubRel']:
            writesubcond(stim, spec, sub, run, fulldata)


def main(argv):
    import getopt
    sub = None
    try:
        # figure out this line
        opts, args = getopt.getopt(argv, "hs:",
                                   ["sub="])
    except getopt.GetoptError:
        print('setup_regressors.py -s <subject>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('setup_regressors.py -s <subject>')
            sys.exit()
        elif opt in ("-s", "--sub"):
            sub = arg

    print(sub)
    for r in ['001', '002', '003', '004', '005', '006', '007', '008']:
        writeConditiontxt(sub, r)


if __name__ == "__main__":
    main(sys.argv[1:])