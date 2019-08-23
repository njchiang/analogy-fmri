import json
import os
from absl import flags
from absl import logging
from absl import app

import numpy as np
from tqdm import tqdm
import pandas as pd
from sklearn.linear_model import Ridge

from joblib import Parallel, delayed
import multiprocessing

from analysis.fmri.analogy_rsa import \
downsample_rdms_df_by_factor, create_models, models_to_df, plotmodels,\
roi_rdm, run_rsa_dfs, subject_rdms, plot_results

from analysis.fmri.analogy_utils import \
    projectSettings, analysisSettings, contrastSettings, order, \
    pu, pa, pv, compile_models, rsa, save_rois, load_rois, load_betas

paths = projectSettings["filepaths"]["hoffPaths"]

MAX_CPU = max(1, multiprocessing.cpu_count() // 2)

FLAGS = flags.FLAGS
flags.DEFINE_integer("threads", MAX_CPU, "number of cpu threads")
flags.DEFINE_string("phase", "AB", "phase (AB/CD/CDMatch/CDNoMatch")


accuracies = pu.load_labels(paths["code"], "labels", "group_accuracy.csv").set_index("Trial")

raw_models_df = pu.load_labels(os.path.join(paths["code"], "labels", "raw_models.csv"))

bart_df = (raw_models_df[::2]
            .reset_index(drop=True)
            .set_index("ABTag")[
                [c for c in raw_models_df.columns if "rstpostprob79" in c]])

w2vc_df = (raw_models_df[::2]
            .reset_index(drop=True)
            .set_index("ABTag")[
                [c for c in raw_models_df.columns if "concatword" in c]])

w2vd_df = (raw_models_df[::2]
            .reset_index(drop=True)
            .set_index("ABTag")[
                [c for c in raw_models_df.columns if "w2vdiff" in c]])

model_names = ["Word2vec-diff", "Word2vec-concat", "BART"]


## AB Encoding model ##
def run_voxel(v, features, fmri_data):
    ridge = Ridge()
    ridge.fit(features[:144], fmri_data[:144, v])
    yhat = ridge.predict(features[144:])
    return np.corrcoef(fmri_data[144:, v], yhat)[0, 1]

def main(_):
    maskname = "graymatter-bin_mask"

    results = {}
    # for sub in ["sub-01", "sub-02"]:
    for sub in projectSettings["subjects"]:
        mask = pu.load_img(paths["root"], "derivatives", sub, "masks", "{}.nii.gz".format(maskname))
        fmri_data, labels, _ = load_betas(projectSettings, sub, t="cope-LSS", center=True, scale=False)

        # TODO : add logic here to define models too
        if FLAGS.phase == "AB":
            selector = labels.AB == 1
            tag_key = "ABTag"
        elif FLAGS.phase == "CD":
            selector = labels.CD == 1
            tag_key = "CDTag"
        elif FLAGS.phase == "CDMatch":
            selector =(labels.CD == 1) & (labels.Match == "1")
            tag_key = "CDTag"
        elif FLAGS.phase == "CDNoMatch":
            selector =(labels.CD == 1) & (labels.Match == "0")
            tag_key = "CDTag"

        fmri_data = pu.mask_img(fmri_data, mask)

        trials = labels[selector]

        fmri_data = fmri_data[trials.index]
        labels = labels.loc[trials.index]

        results[sub] = {}
        for mname, model_df in zip(model_names, [w2vd_df, w2vc_df, bart_df]):
            logging.info("Running {}".format(mname))
            features = model_df.loc[[tag for tag in labels[tag_key]], :]
            result = Parallel(n_jobs=MAX_CPU)(delayed(run_voxel)(v, features, fmri_data) for v in range(fmri_data.shape[1]))
            result = np.array(result)
            pu.unmask_img(result, mask).to_filename(
                    os.path.join(paths["root"], "analysis", sub, "encoding", "{}-{}-{}_{}.nii.gz".format(sub, mname, "cope-LSS", FLAGS.phase)))

if __name__ == "__main__":
    app.run(main)