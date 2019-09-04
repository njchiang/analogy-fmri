#!/usr/bin/python
import json
import sys
import os
from datetime import datetime
# import pandas as pd
import numpy as np
from absl import flags
from absl import logging
from absl import app
import multiprocessing

from BaseSearchlight import CVSearchlight, RSASearchlight

from fmri.analogy_utils import analysisSettings, pu, PATHS
from fmri.analogy_rsa import get_model_rdms
paths = PATHS
MAX_CPU = max(1, multiprocessing.cpu_count() // 2)

FLAGS = flags.FLAGS
flags.DEFINE_boolean("debug", False, "debug mode")
flags.DEFINE_integer("jobs", MAX_CPU, "number of cpu threads")
flags.DEFINE_string("phase", "AB", "phase (AB/CD/CDMatch/CDNoMatch")
flags.DEFINE_string("mask", None, "mask")
flags.DEFINE_string("sub", None, "subject")
flags.DEFINE_string("analysis", "cvsl", "analysis type")
flags.DEFINE_integer("radius", None, "SL radius")
flags.DEFINE_integer("verbosity", None, "searchlight verbosity")

def main(_):
    import getopt
    # every possible variable
    roi = FLAGS.mask
    sub = FLAGS.sub
    phase = FLAGS.phase
    debug = FLAGS.debug
    analysis = FLAGS.analysis
    if FLAGS.jobs:
        analysisSettings["searchlight"]["n_jobs"] = int(FLAGS.jobs)
    if FLAGS.verbosity:
        analysisSettings["searchlight"]["verbose"] = int(FLAGS.verbosity)
    if FLAGS.radius:
        analysisSettings["searchlight"]["radius"] = int(FLAGS.radius)
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
    
    if not debug:
        _ = sl.run(**slargs)
    pu.write_to_logger("Session ended at " + str(datetime.now()), logger=logger)


if __name__ == "__main__":
    app.run(main)
