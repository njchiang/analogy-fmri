#!/usr/bin/python
import json
import sys
import os
from datetime import datetime
# import pandas as pd
import numpy as np

from BaseSearchlight import CVSearchlight, RSASearchlight

from fmri.analogy_utils import analysisSettings, pu, PATHS
from fmri.analogy_rsa import get_model_rdms
paths = PATHS

def main(argv):
    import getopt
    # every possible variable
    roi = None
    sub = None
    phase = "AB"
    debug = False
    analysis = "cvsl"
    try:
        # figure out this line
        opts, args = getopt.getopt(argv, "h:m:s:p:j:v:r:t:a:d",
                                   ["help", "mask=", "sub=", "phase=", "jobs=", "verbose=", "radius=", "analysis", "debug"])
    except getopt.GetoptError:
        print('run_mvpa_searchlight.py -m <maskfile> -s <sub>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', "--help"):
            print('run_mvpa_searchlight.py -m <maskfile> -p <phase> -s <sub>')
            sys.exit()
        elif opt in ("-d", "--debug"):
            debug = True
        elif opt in ("-a", "--analysis"):
            analysis = arg
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
    if analysis == "cvsl":
        pu.write_to_logger("Running MVPA", logger)
        sl = CVSearchlight(sub, mask_file, phase=phase, settings=analysisSettings["searchlight"], logger=logger)
        slargs = {}
    elif analysis == "rsa":
        pu.write_to_logger("Running RSA", logger)
        modelnames = [
            "mainrel", "rel",
            "numchar", "humanratings", "typicality"
            "w2vdiff", "concatword",
            "rstpostprob9", "rstpostprob79"]
        raw_models_df = pu.load_labels("labels/raw_models.csv")
        model_rdms = get_model_rdms(raw_models_df, modelnames)
        modelrdms = model_rdms[(model_rdms.type == "full")].dropna(axis=1).values[:, 2:]
        sl = RSASearchlight(sub, mask_file, phase=phase, settings=analysisSettings["searchlight"], logger=logger)
        slargs = {"modelrdms": modelrdms}
    else:
        pu.write_to_logger("wrong analysis specified, exiting...", logger)
        sys.exit(2)
    
    if debug:
        _ = sl.run(**slargs)
    pu.write_to_logger("Session ended at " + str(datetime.now()), logger=logger)


if __name__ == "__main__":
    main(sys.argv[1:])
