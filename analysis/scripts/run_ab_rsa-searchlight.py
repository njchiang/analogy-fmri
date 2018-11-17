#!/usr/bin/python
import json
import sys
import os
from datetime import datetime
# import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.svm import LinearSVC
from sklearn.preprocessing import StandardScaler


if sys.platform == 'darwin':
    cfg = os.path.join("/Users", "njchiang", "CloudStation", "Grad",
                       "Research", "montilab-ucla", "analogy", "config", "project.json")
    plat = "osx"

elif sys.platform == "linux":
    import platform
    if platform.linux_distribution()[0] == "debian":
        cfg = os.path.join("/home", "njchiang", "data", "CloudStation", "Grad",
                           "Research", "montilab-ucla", "analogy", "config", "project.json")
        plat = "linux"
    else:
        cfg = os.path.join("/u", "project", "monti", "Analysis", "Analogy",
                           "code", "analogy", "config", "project.json")
        plat = "hoff"
else:
    cfg = os.path.join("D:\\", "CloudStation", "Grad",
                       "Research", "montilab-ucla", "analogy", "config", "project.json")
    plat = "win"

with open(cfg, "r") as f:
    projectSettings = json.load(f)

paths = projectSettings["filepaths"]["{}Paths".format(plat)]
sys.path.append(paths["github"])
sys.path.append(paths["code"])

from fmri.analogy_utils import analysisSettings, contrastSettings, order, \
    pu, pa, pv, compile_models, rsa, save_rois, load_rois, load_betas

from fmri.analogy_rsa import get_model_rdms

# analysisSettings["searchlight"]["estimator"] = LinearSVC()

# "humanratings", "typicality"
modelnames = ["rel", "numchar",
              "w2vdiff", "concatword",
              "rstpostprob9", "rstpostprob79",
              # ["rel", "rstpostprob9"],
              # ["rel", "w2vdiff"],
              # ["rstpostprob9", "concatword"],
              # ["rstpostprob9", "w2vdiff"]
              ]
raw_models_df = pu.load_labels(
    os.path.join(paths["code"], "labels", "raw_models.csv"))
model_rdms = get_model_rdms(raw_models_df, modelnames)


def run_subject(sub, maskname="graymatter-bin_mask",
                settings=projectSettings,
                options=analysisSettings, logger=None):

    mask = pu.load_img(paths["root"], "derivatives", sub,
                       "masks", "{}.nii.gz".format(maskname))

    fmri_data, labels, bg_image = load_betas(settings, sub,
                                             t="cope-LSS", center=True,
                                             scale=False, logger=logger)
    selector = labels[labels.AB == 1].sort_values(["SubRel", "TrialTag"])

    fmri_data = pu.index_img(fmri_data, selector.index)

    options["searchlight"]["rdm_metric"] = "correlation"

    results = pa.searchlight_rsa(
        fmri_data,
        model_rdms[(model_rdms.type == "full")].dropna(axis=1).values[:, 2:],
        m=mask,
        write=False,
        logger=logger,
        **options["searchlight"])

    pu.data_to_img(results.scores_, bg_image).to_filename(
        os.path.join(paths["root"], "analysis", sub,
                     "multivariate", "rsa",
                     "{}_{}_AB_corr_rsaSearchlight.nii.gz".format(sub,
                                                                  maskname)))
    return results


def main(argv):
    import getopt
    # every possible variable
    con = None
    roi = None
    sub = None
    try:
        # figure out this line
        opts, args = getopt.getopt(argv, "h:m:c:s:j:v:r",
                                   ["mask=", "contrast=", "sub="])
    except getopt.GetoptError:
        print('run_cd_match_searchlight.py -m <maskfile> -c <contrast> -s <sub>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('run_cd_match_searchlight.py -m <maskfile> -c <contrast> -s <sub>')
            sys.exit()
        elif opt in ("-m", "--mask"):
            roi = arg
        elif opt in ("-s", "--sub"):
            sub = arg
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
    logger = pu.setup_logger(os.path.join(paths['root'], 'analysis', sub,
                                          'multivariate', "rsa"),
                             fname="{}_AB-pearson.log".format(roi))

    run_subject(sub, roi, settings=projectSettings,
                options=analysisSettings, logger=logger)
    pu.write_to_logger("Session ended at " + str(datetime.now()), logger=logger)



if __name__ == "__main__":
    main(sys.argv[1:])
