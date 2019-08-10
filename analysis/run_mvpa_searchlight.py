#!/usr/bin/python
import json
import sys
import os
from datetime import datetime
# import pandas as pd
import numpy as np

from BaseSearchlight import CVSearchlight

from fmri.analogy_utils import analysisSettings, pu, PATHS
paths = PATHS

def main(argv):
    import getopt
    # every possible variable
    roi = None
    sub = None
    phase = "AB"
    debug = False
    try:
        # figure out this line
        opts, args = getopt.getopt(argv, "h:m:s:p:j:v:r:d",
                                   ["help", "mask=", "sub=", "phase=", "jobs=", "verbose=", "radius=", "debug"])
    except getopt.GetoptError:
        print('run_mvpa_searchlight.py -m <maskfile> -s <sub>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', "--help"):
            print('run_mvpa_searchlight.py -m <maskfile> -p <phase> -s <sub>')
            sys.exit()
        elif opt in ("-d", "--debug"):
            debug = True
        elif opt in ("-m", "--mask"):
            roi = arg
        elif opt in ("-s", "--sub"):
            sub = arg
        elif opt in ("-p", "--phase"):
            phase = arg
        elif opt in ("-j", "--jobs"):
            analysisSettings["searchlight"]["n_jobs"] = int(arg)
        elif opt in ("-v", "--verbose"):
            analysisSettings["searchlight"]["verbose"] = int(arg)
        elif opt in ("-r", "--radius"):
            analysisSettings["searchlight"]["radius"] = int(arg)
    # if not con:
    #     print "not a valid contrast... exiting"
    #     sys.exit(1)

    if None in [sub, roi]:
        print("Argument missing")
        sys.exit(2)

    logger = pu.setup_logger(os.path.join(paths['root'], 'analysis', sub, 'multivariate', 'searchlight', "lss"), fname="{}_AB-Match.log".format(roi))
    mask_file = os.path.join(paths["root"], "derivatives", sub, "masks", "{}.nii.gz".format(roi))
    sl = CVSearchlight(sub, mask_file, phase=phase, settings=analysisSettings["searchlight"], logger=logger)
    # if debug:
        # _ = sl.run()
    pu.write_to_logger("Session ended at " + str(datetime.now()), logger=logger)



if __name__ == "__main__":
    main(sys.argv[1:])
