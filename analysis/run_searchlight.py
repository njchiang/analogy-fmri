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

from fmri.analogy_utils import analysisSettings, pu, PATHS, rsa
from fmri.analogy_rsa import get_model_rdms

paths = PATHS
# MAX_CPU = max(1, multiprocessing.cpu_count() // 2)
MAX_CPU = max(1, multiprocessing.cpu_count() - 1)

FLAGS = flags.FLAGS
flags.DEFINE_boolean("debug", False, "debug mode")
flags.DEFINE_integer("jobs", MAX_CPU, "number of cpu threads")
flags.DEFINE_string("phase", "AB", "phase (AB/CD/CDMatch/CDNoMatch")
flags.DEFINE_string("mask", None, "mask")
flags.DEFINE_string("sub", None, "subject")
flags.DEFINE_string("analysis", "cvsl", "analysis type")
flags.DEFINE_integer("radius", None, "SL radius")
flags.DEFINE_integer("verbose", None, "searchlight verbosity")

def get_cd_models(dfs, trials):
    bart_df = (dfs[::2]
            .reset_index(drop=True)
            .set_index("ABTag")[
                [c for c in dfs.columns if "rstpostprob79" in c]
            ])

    w2vc_df = (dfs[::2]
                .reset_index(drop=True)
                .set_index("ABTag")[
                    [c for c in dfs.columns if "concatword" in c]
                ])

    w2vd_df = (dfs[::2]
                .reset_index(drop=True)
                .set_index("ABTag")[
                    [c for c in dfs.columns if "w2vdiff" in c]
                ])

    def _get_dist_model(df):
        dsts = np.concatenate(
        [rsa.pdist(df.loc[
            [t.split("::")[0], t.split("::")[1]]],
               metric="cosine")
             for t in trials.TrialTag])
        return rsa.rdm(dsts.reshape(-1, 1), metric="euclidean")

    w2vc = rsa.rdm(w2vc_df.loc[[t for t in trials.CDTag]], metric="cosine")
    w2vc_dist_cd = _get_dist_model(w2vc_df)

    w2vd_cd = rsa.rdm(w2vd_df.loc[[t for t in trials.CDTag]], metric="cosine")
    w2vd_dist_cd = _get_dist_model(w2vd_df)

    bart_cd = rsa.rdm(bart_df.loc[[t for t in trials.CDTag]], metric="cosine")
    bart_dist_cd = _get_dist_model(bart_df)

    models = np.array([w2vc, w2vd_cd, bart_cd, w2vc_dist_cd, w2vd_dist_cd, bart_dist_cd])
    modelnames = "Word2vec-concat", "Word2vec-diff", "BART", "w2vc-dist", "w2vd-dist", "BART-dist"

    return models, modelnames


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
        analysisSettings["searchlight"]["verbose"] = int(FLAGS.verbose)
    if FLAGS.radius:
        analysisSettings["searchlight"]["radius"] = int(FLAGS.radius)
    # if not con:
    #     print "not a valid contrast... exiting"
    #     sys.exit(1)

    if None in [sub, roi]:
        print("Argument missing")
        sys.exit(2)

    logger = pu.setup_logger(os.path.join(paths['root'], 'analysis', sub, 'multivariate', 'searchlight', "lss"), fname="{}_{}-Match.log".format(roi, FLAGS.phase))
    mask_file = os.path.join(paths["root"], "derivatives", sub, "masks", "{}.nii.gz".format(roi))
    if analysis == "cvsl":
        pu.write_to_logger("Running MVPA", logger)
        sl = CVSearchlight(sub, mask_file, phase=phase, settings=analysisSettings["searchlight"], logger=logger)
        slargs = {}
    elif analysis == "rsa":
        pu.write_to_logger("Running RSA", logger)

        raw_models_df = pu.load_labels(os.path.join(paths["code"], "labels/raw_models.csv"))
        sl = RSASearchlight(sub, mask_file, phase=phase, settings=analysisSettings["searchlight"], logger=logger)

        if FLAGS.phase == "CD":
            sl.fmri_data = pu.index_img(sl.fmri_data, sl.selector.Match == '1')
            sl.labels = sl.labels[sl.selector.Match == '1']
            sl.selector = sl.labels
            modelrdms, modelnames = get_cd_models(raw_models_df, sl.labels)
        else:
            modelnames = [
                "mainrel", "rel",
                "numchar", "humanratings", "typicality",
                "w2vdiff", "concatword", "accuracy",
                "rstpostprob9", "rstpostprob79", "bart79thresh",
                "rstpostprob270"]
            model_rdms = get_model_rdms(raw_models_df, modelnames)
            # modelrdms = model_rdms[(model_rdms.type == "full")].dropna(axis=1).values[:, 2:].astype(np.float64)
            # deal with NAs in bart thresh
            modelrdms = model_rdms[(model_rdms.type == "full")].iloc[:, 2:].fillna(0).values.astype(np.float64)
        slargs = {"modelrdms": modelrdms}
    else:
        pu.write_to_logger("wrong analysis specified, exiting...", logger)
        sys.exit(2)

    if not debug:
        _ = sl.run(**slargs)
    pu.write_to_logger("Session ended at " + str(datetime.now()), logger=logger)


if __name__ == "__main__":
    app.run(main)
