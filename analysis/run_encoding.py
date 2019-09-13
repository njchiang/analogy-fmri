import json
import os
from absl import flags
from absl import logging
from absl import app

import numpy as np
from tqdm import tqdm
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold, StratifiedKFold, StratifiedShuffleSplit, KFold, permutation_test_score, cross_val_score
from sklearn.metrics import make_scorer
from joblib import Parallel, delayed
import multiprocessing

from fmri.analogy_rsa import \
downsample_rdms_df_by_factor, create_models, models_to_df, plotmodels,\
roi_rdm, run_rsa_dfs, subject_rdms, plot_results

from fmri.analogy_utils import \
    projectSettings, analysisSettings, contrastSettings, order, \
    pu, pa, pv, compile_models, rsa, save_rois, load_rois, load_betas

paths = projectSettings["filepaths"]["hoffPaths"]

MAX_CPU = max(1, multiprocessing.cpu_count() // 2)

FLAGS = flags.FLAGS
flags.DEFINE_integer("threads", MAX_CPU, "number of cpu threads")
flags.DEFINE_string("phase", "AB", "phase (AB/CD/CDMatch/CDNoMatch")
flags.DEFINE_boolean("betas", False, "output betas only")
flags.DEFINE_boolean("debug", False, "debug mode")
flags.DEFINE_string("cv", None, "[run/relation/lor]")
flags.DEFINE_integer("n_folds", 4, "Number of CV folds")
flags.DEFINE_integer("permutations", 0, "Number of permutations")


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

CV_LIB = {
    "lor": GroupKFold,
    "run": StratifiedKFold, # StratifiedShuffleSplit,
    "relation": StratifiedKFold # StratifiedShuffleSplit
}

def corrcoef(y, y_pred):
    return np.corrcoef(y, y_pred)[0, 1]

## AB Encoding model ##
def run_voxel(v, features, fmri_data):
    ridge = Ridge()
    ridge.fit(features[:144], fmri_data[:144, v])
    yhat = ridge.predict(features[144:])
    return np.corrcoef(fmri_data[144:, v], yhat)[0, 1]

# TODO : incorporate and run
def run_cv_voxel(v, model, features, fmri_data, cv, groups, scoring, permutations=None):
    cv_splits = cv.split(features, groups, groups=groups)
    if permutations:
        score, _, pvalue = permutation_test_score(model, features, fmri_data[:, v], groups=groups, scoring=scoring, cv=cv_splits, n_permutations=permutations, n_jobs=1)
        return score, pvalue
    else:
        score = np.mean(cross_val_score(model, features, fmri_data[:, v], groups=groups, scoring=scoring, cv=cv_splits, n_jobs=1))
        return score

def get_betas(v, model, features, fmri_data, pred_features, pred_fmri_data):
    model.fit(features, fmri_data[:, v])
    yhat = model.predict(pred_features)
    return model.coef_, np.corrcoef(pred_fmri_data[:, v], yhat)[0, 1]

def main(_):
    maskname = "graymatter-bin_mask"
    if FLAGS.debug:
        return
    results = {}
    # for sub in ["sub-01", "sub-02"]:
    for sub in projectSettings["subjects"]:
        logging.info("Starting subject {}".format(sub))
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

        if FLAGS.betas:
            val_trials = labels[labels.CD==1]
            val_fmri_data = fmri_data[val_trials.index]
            val_labels = labels.loc[val_trials.index]

        trials = labels[selector]

        fmri_data = fmri_data[trials.index]
        labels = labels.loc[trials.index]

        cv = CV_LIB.get(FLAGS.cv, KFold)(FLAGS.n_folds)
        groups = trials["SubRel"] if FLAGS.cv == "relation" else trials["chunks"]
        # groups = trials["MainRel"] if FLAGS.cv == "relation" else trials["chunks"]
        model = Ridge()
        scoring = make_scorer(corrcoef)

        results[sub] = {}


        for mname, model_df in zip(model_names, [w2vd_df, w2vc_df, bart_df]):
            logging.info("Running {}".format(mname))
            features = model_df.loc[[tag for tag in labels[tag_key]], :]
            # result = Parallel(n_jobs=MAX_CPU)(delayed(run_voxel)(v, features, fmri_data) for v in range(fmri_data.shape[1]))
            if FLAGS.betas:
                val_features = model_df.loc[[tag for tag in val_labels["CDTag"]], :]
                results = Parallel(n_jobs=MAX_CPU)(delayed(get_betas)(v, model, features, fmri_data, val_features, val_fmri_data) for v in range(fmri_data.shape[1]))
                result, preds = list(zip(*results))
                result = np.array(result).T
                pu.unmask_img(result, mask).to_filename(
                        os.path.join(paths["root"], "analysis", sub, "encoding", "{}_{}_{}_{}_encoding-betas.nii.gz".format(sub, mname, "cope-LSS", FLAGS.phase)))
                preds = np.array(preds)
                pu.unmask_img(preds, mask).to_filename(
                        os.path.join(paths["root"], "analysis", sub, "encoding", "{}_{}_{}_{}_pred-CD.nii.gz".format(sub, mname, "cope-LSS", FLAGS.phase)))

            if FLAGS.cv:
                result = Parallel(n_jobs=MAX_CPU)(delayed(run_cv_voxel)(v, model, features, fmri_data, cv, groups, scoring, FLAGS.permutations) for v in range(fmri_data.shape[1]))
                result = np.array(result)
                pu.unmask_img(result, mask).to_filename(
                        os.path.join(paths["root"], "analysis", sub, "encoding", "{}_{}_{}_{}_cv-{}.nii.gz".format(sub, mname, "cope-LSS", FLAGS.phase, FLAGS.cv)))

if __name__ == "__main__":
    logging.set_verbosity(logging.DEBUG)
    logging.info("Launching script")
    app.run(main)