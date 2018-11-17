import sys, os
import logging

if sys.platform == 'darwin':
    sys.path.append(os.path.join("/Users", "njchiang", "GitHub", "task-fmri-utils"))
else:
    sys.path.append(os.path.join('D:\\', 'GitHub', 'task-fmri-utils'))

# import fmri_core.projectanalysis as pa
######################################
# Global variables
logging.basicConfig(datefmt='%m-%d %H:%M', level=logging.DEBUG)
LOGGER = logging.getLogger()
LOGGER.info('--------------------------------')


# lambda functions
zs = lambda v: (v - v.mean(0)) / v.std(0)  # z-score function


######################################
# initialize paths
def initpaths(lname=None, debug=False):
    pass


######################################
# subject data I/O
# load a single run
def loadrundata(p, s, r, m=None, c='trial_type', logger=LOGGER):
    pass


# load all runs for a subject
def loadsubdata(p, s, m=None, c=None, logger=LOGGER):
    pass


# load trial timing information
def loadevents(p, s):
    pass


# load data, append trial timings, filter and z-score
def preprocess_data(paths, sub, runs, filter_params=[121,2], roi="grayMatter", z=True, logger=LOGGER):
    pass


# load motion regressors
# // TODO : path is probably wrong
def loadmotionparams(p, s, logger=LOGGER):
    import numpy as np
    import os
    pa.write_to_logger("Loading motion parameters... ", logger)
    res = {}
    for sub in s.keys():
        mcs = [np.loadtxt(os.path.join(p['root'], 'data', sub, 'analysis', 'preproc',
                                       r + '_preproc.par'))
               for r in s[sub]]
        res[sub] = np.vstack(mcs)
    return res

# TODO : path is probably wrong
# load human ratings (provided by hongjing)
def loadhumanratings(p, logger=LOGGER):
    import pandas as pd
    # humanmat = pd.read_csv(os.path.join('labels',
    #                                 'modeloutput.top15.sel_1.final1.v3.csv'),
    #                    header=[0, 1, 2], index_col=0)
    pa.write_to_logger("Loading human rating information", logger)
    return pd.read_csv(os.path.join(p['root'], 'data', 'standard', 'regressors',
                                   'modeloutput.top15.sel_1.final1.v3.csv'),
                       header=1, index_col=0, skiprows=1).T


############################################
# amend events
# TODO : check if this is necessary
def adjustevents(e, c='trialtag'):
    import numpy as np
    # rounding for now, ONLY because that works for this dataset. But should not round for probe
    ee = []
    for i, d in enumerate(e):
        if 'intensity' in d.keys():
            ee.append({'onset': d['onset'],
                       'duration': d['duration'],
                       'condition': d[c],
                       'intensity': int(d['intensity'])})
        else:
            ee.append({'onset': d['onset'],
                       'duration': d['duration'],
                       'condition': d[c],
                       'intensity': 1})
    return ee


# helper function to convert list to dict... unsure if necessary
def events2dict(events):
    evvars = {}
    for k in events[0]:
        try:
            evvars[k] = [e[k] for e in events]
        except KeyError:
            raise ValueError("Each event property must be present for all "
                             "events (could not find '%s')" % k)
    return evvars
