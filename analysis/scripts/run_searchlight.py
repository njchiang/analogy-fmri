#!/usr/bin/python
import json
import sys
import os
from datetime import datetime
# import pandas as pd
import numpy as np
# from sklearn.svm import LinearSVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import LeaveOneGroupOut


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

from fmri.analogy_utils import analysisSettings, contrastSettings, pu, pa, load_data_lss, load_betas

# analysisSettings["searchlight"]["estimator"] = LinearSVC()


def run_subject(sub, modelname, maskname="grayMatter-bin_mask", settings=projectSettings,
                options=analysisSettings, logger=None):

    # fmri_data, labels, bg_image, mask = load_data_lss(sub, maskname,
    #                                                   t=contrastSettings[modelname]["t"],
    #                                                   normalize=False, logger=logger)

    fmri_data, labels, bg_image = load_betas(settings, sub, t=options["t"], logger=logger)

    mask = pu.load_img(os.path.join(
        paths['root'], 'derivatives', sub, 'masks',
        settings["templates"]["masks"].format(maskname)), logger=logger)

    fmri_data = pu.mask_img(fmri_data, mask, logger=logger)

    conditionSelector = np.where(labels[contrastSettings[modelname]["label"]] != "None")

    op = StandardScaler()
    scaledData = pa.op_by_label(fmri_data, labels['chunks'], op, logger=logger)

    # analysis
    # output order: CD2AB, AB2CD
    cv = LeaveOneGroupOut()
    fmri_data = pu.unmask_img(scaledData[conditionSelector], mask, logger=logger)
    result = pa.searchlight(fmri_data,
                            labels.iloc[conditionSelector][contrastSettings[modelname]["label"]],
                            m=mask, cv=cv,
                            groups=labels.iloc[conditionSelector][contrastSettings[modelname]["grouping"]],
                            logger=logger,
                            **options['searchlight'])

    outpath = os.path.join(paths["root"], "analysis", sub, "multivariate", "searchlight",
                           "{}-{}-cvsl.nii.gz".format(sub, modelname))
    pu.data_to_img(result.scores_, bg_image, logger=logger).to_filename(outpath)
    return result


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
        print('run_searchlight.py -m <maskfile> -c <contrast> -s <sub>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('run_searchlight.py -m <maskfile> -c <contrast> -s <sub>')
            sys.exit()
        elif opt in ("-m", "--mask"):
            roi = arg
        elif opt in ("-c", "--contrast"):
            con = arg
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

    if None in [sub, roi, con]:
        print("Argument missing")
        sys.exit(2)
    logger = pu.setup_logger(os.path.join(paths['root'], 'analysis', sub,
                                          'multivariate', 'searchlight'), fname="{}_{}-searchlight".format(con, roi))

    run_subject(sub, con, roi, analysisSettings, logger)
    pu.write_to_logger("Session ended at " + str(datetime.now()), logger=logger)



if __name__ == "__main__":
    main(sys.argv[1:])
