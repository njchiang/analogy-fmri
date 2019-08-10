import os
import numpy as np
import pandas as pd
import statsmodels.api as sm

from .analogy_utils import pu, pa, pv

from sklearn.linear_model import Ridge, LinearRegression


def calc_scores(fmri_data, regressors):
    results = sm.OLS(fmri_data, regressors).fit()
    return results.params[0], results.tvalues[0]


def load_func(paths, settings, sub,
              maskname="graymatter-bin_mask",
              logger=None):
    labels = []
    imgs = []
    # will need to mask image
    for ri, r in enumerate(settings["subjects"][sub]):
        imgs.append(
            os.path.join(
                paths['root'], 'derivatives', sub, 'func',
                settings["templates"]["func"].format(sub, r)))

        labels.append(pu.load_labels(
            paths["root"], 'derivatives', sub, 'func',
            settings["templates"]["events"].format(sub, r), logger=logger))

    labels = pd.concat(labels).reset_index(drop=True)
    fmri_data = pu.concat_imgs(imgs, logger=logger)
    return fmri_data, labels


def create_lss_from_lsa(design, trial, tt="AB"):
    nuisance_regressor_1 = (design[tt]
                            .drop(columns=trial)
                            .sum(axis=1))

    nuisance_regressor_2 = (design
                          .drop(columns="nuisance")
                          .drop(columns=tt)
                          .sum(axis=1))
    motion_regressor = design["nuisance"]
    regressor = design[tt, trial]
    regressors = pd.concat([regressor, nuisance_regressor_1,
                            nuisance_regressor_2, motion_regressor], axis=1)
    return regressors


def load_aggregated_data(paths, sub, maskname, logger=None):
    mask = pu.load_img(
        os.path.join(paths["root"], "derivatives", sub, "masks",
                     "{}.nii.gz".format(maskname)), logger=logger)
    fmri_data = []
    des_mats = []
    labels = []
    s = sub
    for r in ["run-01", "run-02", "run-03", "run-04",
              "run-05", "run-06", "run-07", "run-08"]:
        data, des, label = load_run_and_regressors(paths, s, r, mask)
        fmri_data.append(data - data.mean(axis=0))
        # sort by index then join
        tags = []
        tt = []
        for d in des.names:
            if ":" in d:
                ttype = d.split("_")[1]
                tt.append(ttype)
                trial = d.split("_")[0]
                if ttype == "AB":
                    tags.append(trial.split("::")[0])
                elif ttype == "CD":
                    tags.append(trial.split("::")[1])
                elif ttype == "Probe":
                    tags.append(trial)
            else:
                tags.append(d)
                tt.append("nuisance")

        headers = pd.MultiIndex.from_tuples(
            zip(tt, tags), names=["type", "tag"])
        des_mats.append(pd.DataFrame(des.matrix, columns=headers))
        labels.append(label)

    fmri_data = np.concatenate(fmri_data, axis=0)
    design = pd.concat(des_mats, axis=0, ignore_index=False, sort=False).reset_index(drop=True)
    return fmri_data, design.fillna(0)


def load_run_and_regressors(paths, sub, run, mask,
                            tr=1, logger=None):

    labels = pu.load_labels(
        os.path.join(paths["root"], "derivatives", sub, "func",
                     "{}_task-analogy_{}_events.csv").format(sub, run),
        logger=logger)
    motion = pu.load_labels(
        os.path.join(paths["root"], "derivatives", sub,
                     "mc", run, "prefiltered_func_data_mcf_final.par"),
        sep=" ", header=None, logger=logger).dropna(axis=1)

    fmri_data = pu.mask_img(
        os.path.join(paths["root"], "derivatives", sub, "func",
                     "{}_task-analogy_{}_bold.nii.gz".format(sub, run)),
        mask, logger=logger
    )

    frametimes = np.arange(0, fmri_data.shape[0], tr)

    # append ABTag or CDTag
    cond_ids = ["_".join([r["TrialTag"], r["TrialType"]])
                for _, r in labels.iterrows()]

    onsets = labels["Onset"]
    durations = labels["Duration"]
    design_kwargs = {"drift_model": "blank", "add_regs": motion.values}

    LSA_des = pa.make_designmat(frametimes, cond_ids, onsets, durations,
                                design_kwargs=design_kwargs, logger=logger)
    return fmri_data, LSA_des, labels

def regress_lsa_run(paths, sub, run, maskname="graymatter-bin_mask",
                  tr=1, write=False, logger=None):
    mask = pu.load_img(
        os.path.join(paths["root"], "derivatives", sub, "masks",
                     "{}.nii.gz".format(maskname)), logger=logger)

    fmri_data, LSA_des, labels = load_run_and_regressors(
        paths, sub, run, mask=mask, tr=tr)

    result = LinearRegression().fit(LSA_des.matrix, fmri_data)

    regressors = LSA_des.names
    sorted_new_betas = result.coef_[:, np.array(regressors[0:len(labels)],
                                                dtype=int).argsort()].T

    if write:
        pu.unmask_img(sorted_new_betas, mask, logger).to_filename(
            os.path.join(paths["root"], "derivatives", sub, "betas",
                         "{}_task-analogy_{}_betas-LSA.nii.gz".format(sub, run))
        )

    return sorted_new_betas
