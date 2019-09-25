# Set up analysis and PATHS
# imports
import platform
import os
import pandas as pd
import numpy as np
import json
import sys

from sklearn.preprocessing import OneHotEncoder

from .utils.fmri_core import analysis as pa
from .utils.fmri_core import utils as pu
from .utils.fmri_core import vis as pv
from .utils.fmri_core import rsa


# if sys.platform == 'darwin':
#     home = os.path.join("/Users", "njchiang", "GitHub")
#     plat = "osx"

# elif sys.platform == "linux":
#     import platform
#     if platform.linux_distribution()[0] == "debian":
#         home = os.path.join("/home", "njchiang", "data", "CloudStation", "Grad",
#                            "Research", "montilab-ucla")
#         plat = "linux"
#     else:
#         home = os.path.join("/u", "project", "monti", "Analysis", "Analogy",
#                            "code")
#         plat = "hoff"
# else:
#     home = os.path.join("D:\\", "GitHub")
#     plat = "win"
# home = os.path.join("/u", "project", "monti", "Analysis", "Analogy", "code")
plat = "hoff"

# cfg = os.path.join(home, "analogy-fmri", "config", "project.json")

# not sure if this will work... 
cfg = "config/project.json"
with open(cfg, "r") as f:
    projectSettings = json.load(f)

# # sys.path.append(paths["github"])
# # sys.path.append(paths["code"])

projecttitle="Analogy"
PATHS = projectSettings["filepaths"]["{}Paths".format(plat)]
# sys.path.append(PATHS["github"])

# load analysis settings
# analysisSettings = pu.load_config(os.path.join(PATHS["code"], "config", "analyses.json"))
# contrastSettings = pu.load_config(os.path.join(PATHS["code"], "config", "contrasts.json"))
analysisSettings = pu.load_config("config/analyses.json")
contrastSettings = pu.load_config("config/contrasts.json")
# trial order
# order = pu.load_labels(os.path.join(PATHS["code"], "labels", "trialorder_rsa_absorted.csv"))
order = pu.load_labels(os.path.join("labels", "trialorder_rsa_absorted.csv"))

def compile_models(write=False):
    # return dictionary of dictionaries
    typicality = pu.load_labels(os.path.join("labels", "typicality.csv"))
    w2vdiffs = pu.load_labels(os.path.join("labels", "word2vec_diffs.csv"))
    humanratings = pu.load_labels(os.path.join("labels", "humanratings.csv"), skiprows=2)
    rstpostprob9 = pu.load_mat_data(os.path.join("labels", "rstpostprob9.mat"))
    rstpostprob79 = pu.load_mat_data(os.path.join("labels", "rstpostprob79.mat"))
    rstpostprob79norm = pu.load_mat_data(os.path.join("labels", "rstBART79norm.mat"))
    rstpostprob79power = pu.load_mat_data(os.path.join("labels", "rstBART79normpower.mat"))
    concatword = pu.load_mat_data(os.path.join("labels", "w2vconcat.mat"))
    mat_concatword = {}
    mat_rstpostprob79 = {}
    mat_rstpostprob79norm = {}
    mat_rstpostprob79power = {}
    mat_humanratings = {}
    mat_rstpostprob9 = {}
    mat_mainrel = {}
    mat_subrel = {}
    mat_rel = {}
    mat_sem = {}
    mat_intuit = {}
    mat_w2v = {}
    wordpairs = []
    mat_typicality = {}
    mainenc = OneHotEncoder(4)
    subenc = OneHotEncoder(10)
    for i in range(len(rstpostprob79["wordpair"])):
        wordpair = rstpostprob79["wordpair"][i, 0][0]
        wordpairs.append(wordpair)
        ci = np.where(concatword["wordpair"][:, :] == wordpair)[0][0]
        mat_concatword[wordpair] = concatword["concwordmat"].astype(np.float)[ci]
        mat_rstpostprob9[wordpair] = rstpostprob9["rstpostprob_sm"].astype(np.float)[i]
        mat_rstpostprob79[wordpair] = rstpostprob79["rstpostprob"].astype(np.float)[i]
        mat_humanratings[wordpair] = humanratings[humanratings.wordpair == wordpair].values[0, 1:].astype(np.float)
        mat_typicality[wordpair] = typicality[typicality.wordpair == wordpair].values[0, 1:].astype(np.float)
        mat_w2v[wordpair] = w2vdiffs[w2vdiffs.wordpair == wordpair].values[0, 1:].astype(np.float)

        mat_mainrel[wordpair] = mainenc.fit_transform(rstpostprob79["wordpair"][i, 1] -
                                                      1).toarray()[0, :-1]
        mat_subrel[wordpair] = subenc.fit_transform(rstpostprob79["wordpair"][i, 2] -
                                                    1).toarray()[0, :-1]
        mat_rel[wordpair] = np.hstack([mat_mainrel[wordpair], mat_subrel[wordpair]])
        mat_sem[wordpair] = np.hstack([mat_mainrel[wordpair][0] +
                                       mat_mainrel[wordpair][1],
                                       mat_mainrel[wordpair][2]])
        mat_intuit[wordpair] = np.hstack([mat_sem[wordpair],
                                          mat_rel[wordpair]])
    for i in range(len(rstpostprob79norm["wordpairname"])):
        wordpair = rstpostprob79norm["wordpairname"][i, 0][0]
        mat_rstpostprob79norm[wordpair] = rstpostprob79norm["pred_prob"].astype(np.float)[i]
        mat_rstpostprob79power[wordpair] = rstpostprob79power["pred_prob"].astype(np.float)[i]


    models = {
          "wordpairs": wordpairs,
          "humanratings": mat_humanratings,
          "rstpostprob79": mat_rstpostprob79,
          "rstpostprob79": mat_rstpostprob79,
          "rstpostprob79": mat_rstpostprob79,
          "rstpostprob9": mat_rstpostprob9,
          "w2vdiff": mat_w2v,
          "mainrel": mat_mainrel,
          "subrel": mat_subrel,
          "rel": mat_rel,
          "sem": mat_sem,
          "intuit": mat_intuit,
          "concatword": mat_concatword,
          "typicality": mat_typicality
             }
    return models


def load_rois(t="pymvpa", logger=None):
    betas = {}
    labels = {}
    for s in projectSettings["subjects"].keys():
        pu.write_to_logger("Loading {} betas".format(s), logger)
        betas[s] = np.load(os.path.join(PATHS["root"], "derivatives", s, "rois",
                                        "{}_{}-betas.npz".format(s, t)))
        labels[s] = pu.load_labels(os.path.join(PATHS["root"], "derivatives", s, "rois",
                                                "{}_{}_labels.csv".format(s, t)))
    return betas, labels


def save_rois(masks_dict, t="tstat-LSS", logger=None):
    for sub in projectSettings["subjects"]:
        pu.write_to_logger("Writing {} betas".format(sub), logger)
        if "condensed" in t:
            img, labels, _ = load_condensed_betas(projectSettings, sub, t,
                                                  logger=logger)
        else:
            img, labels, _ = load_betas(projectSettings, sub, t, logger=logger)
        betas = {}
        for mask, maskname in masks_dict.items():
            betas[mask] = pu.mask_img(img, pu.load_img(
                os.path.join(
                    PATHS['root'], 'derivatives', sub, 'masks',
                    projectSettings["templates"]["masks"].format(maskname)),
                logger=logger
            ))
        labels.to_csv(os.path.join(PATHS["root"], "derivatives", sub, "rois",
                                   "{}_{}_labels.csv".format(sub, t)), index=False)

        np.savez_compressed(os.path.join(PATHS["root"], "derivatives", sub, "rois",
                                         "{}_{}-betas.npz".format(sub, t)), **betas)


def load_condensed_betas(settings, sub, t="LSS-condensed", logger=None):
    # whiten the data
    labels = order[::2].loc[:, ["ABTag",
                                "ABMainRel",
                                "ABSubRel"]].reset_index(drop=True)
    labels["AB"] = 1
    labels["TrialTag"] = labels["ABTag"]
    fmri_data = pu.load_img(os.path.join(
        PATHS['root'], 'derivatives', sub, 'betas',
        "{}_task-analogy_betas-{}.nii.gz".format(sub, t)),
        logger=logger)

    bg_image = pu.load_img(
        os.path.join(PATHS['root'], 'derivatives', sub,
                     'reg', settings["templates"]["reg"]),
        logger=logger
    )
    return fmri_data, labels, bg_image


def load_betas(settings, sub, t="tstat-LSS", center=True, scale=False,
               logger=None):
    labels = []
    imgs = []
    # whiten the data
    for ri, r in enumerate(settings["subjects"][sub]):
        if center:
            imgs.append(
                pu.center_img(os.path.join(
                    PATHS['root'], 'derivatives', sub, 'betas',
                    settings["templates"]["betas"].format(sub, r, t)),
                    logger=logger))
        else:
            imgs.append(os.path.join(PATHS['root'], 'derivatives', sub, 'betas',
                                     settings["templates"]["betas"].format(sub, r, t)))
        if "subrel" in t:
            labels.append(pu.load_labels(PATHS["root"],
                                         'derivatives', sub, 'betas',
                                         "{}_task-analogy_{}_events-subrel.tsv".format(sub, r),
                                         sep='\t', logger=logger))
            labels[ri]["chunks"] = pd.Series([ri+1 for _ in range(len(labels[
                                                                        ri]))])
        else:
            labels.append(pu.load_labels(PATHS["root"],
                                         'derivatives', sub, 'func',
                                         settings["templates"]["events"].format(sub, r),
                                         logger=logger))

    labels = pd.concat(labels).reset_index(drop=True)
    fmri_data = pu.concat_imgs(imgs, logger=logger)

    bg_image = pu.load_img(
        os.path.join(PATHS['root'], 'derivatives', sub,
                     'reg', settings["templates"]["reg"]),
        logger=logger
    )
    return fmri_data, labels, bg_image

#
# def load_data_pymvpa(sub, maskname, normalize=True, logger=None):
#     imgFile = os.path.join(PATHS['root'], 'derivatives', sub, 'betas',
#                            pu.format_bids_name(sub, 'task-analogy',
#                                                'betas-pymvpa.nii.gz'))
#     mask = pu.load_img(PATHS['root'],
#                        'derivatives', sub, 'masks',
#                        maskname + '.nii.gz', logger=logger)
#     labels = pu.load_labels(PATHS['root'],
#                             'derivatives', sub, 'betas',
#                             pu.format_bids_name(sub, 'task-analogy',
#                                                 'events-pymvpa.tsv'),
#                             sep='\t', index_col=0, logger=logger)
#     maskedImg = pa.mask_img(imgFile, mask)
#     # conditionSelector = np.where(labels['ab'] == 1)
#
#     if normalize:
#         resids = []
#         # whiten the data
#         for r in range(8):
#             residFile = os.path.join(PATHS['root'], 'derivatives', sub, 'func',
#                                      pu.format_bids_name(sub, 'task-analogy',
#                                                          "run-0{}".format(r+1),
#                                                          'resids-pymvpa.nii.gz'))
#             resids.append(pa.mask_img(residFile, mask, logger=logger))
#
#         fmri_data = rsa.noise_normalize_beta(maskedImg,
#                                              np.vstack(resids), logger=logger)
#         # fmri_data = rsa.noise_normalize_beta(maskedImg[conditionSelector],
#         #                                      np.vstack(resids), logger=logger)
#     else:
#         # fmri_data = maskedImg[conditionSelector]
#         fmri_data = maskedImg
#
#     # these_labels = labels.iloc[conditionSelector]
#     bg_image = pu.load_img(os.path.join(PATHS['root'],
#                                         'derivatives',
#                                         sub, 'reg', 'BOLD_template.nii.gz'), logger=logger)
#     return fmri_data, labels, bg_image, mask
#
#
# subrel utils
# def load_data_subrel(sub, maskname, t="cope", normalize=False, logger=None):
#     mask = pu.load_img(PATHS['root'],
#                        'derivatives', sub, 'masks',
#                        maskname + '.nii.gz', logger=logger)
#
#     labels = []
#     imgs = []
#     # whiten the data
#     for r in range(8):
#         imgFile = os.path.join(PATHS['root'], 'derivatives', sub, 'betas',
#                                "{}_task-analogy_run-0{}_betas-{}-subrel.nii.gz".format(sub, r+1, t))
#         labels.append(pu.load_labels(PATHS["root"],
#                                      'derivatives', sub, 'betas',
#                                      "{}_task-analogy_run-0{}_events-subrel.tsv".format(sub, r+1),
#                                      sep='\t', logger=logger))
#         labels[r]["chunks"] = pd.Series([r+1 for i in range(len(labels[r]))])
#
#         if normalize:
#             residFile = os.path.join(PATHS['root'], 'derivatives', sub, 'func',
#                                      pu.format_bids_name(sub, 'task-analogy',
#                                                          "run-0{}".format(r+1),
#                                                          'resids-subrel.nii.gz'))
#             maskedImg = pa.mask_img(imgFile, mask, logger=logger)
#             resids = pa.mask_img(residFile, mask, logger=logger)
#             imgs.append(rsa.noise_normalize_beta(maskedImg, resids, logger=logger))
#         else:
#             imgs.append(pa.mask_img(imgFile, mask, logger=logger))
#
#     #         resids.append(pa.mask_img(residFile, mask))
#     #         run_data = noise_normalize_beta()
#     labels = pd.concat(labels).reset_index(drop=True)
#
#     fmri_data = np.vstack(imgs)
#
#     bg_image = pu.load_img(os.path.join(PATHS['root'],
#                                         'derivatives',
#                                         sub, 'reg', 'BOLD_template.nii.gz'), logger=logger)
#     return fmri_data, labels, bg_image, mask
#
#
# # LSS utils
# def load_data_lss(sub, maskname, t="cope", normalize=False, logger=None):
#     mask = pu.load_img(PATHS['root'],
#                        'derivatives', sub, 'masks',
#                        maskname + '.nii.gz', logger=logger)
#
#     labels = []
#     imgs = []
#     # whiten the data
#     for r in range(8):
#         imgFile = os.path.join(PATHS['root'], 'derivatives', sub, 'betas',
#                                "{}_task-analogy_run-0{}_betas-{}-LSS.nii.gz".format(sub, r+1, t))
#         labels.append(pu.load_labels(PATHS["root"],
#                                      'derivatives', sub, 'func',
#                                      "{}_task-analogy_run-0{}_events.tsv".format(sub, r+1),
#                                      sep='\t', logger=logger))
#         labels[r]["chunks"] = pd.Series([r+1 for i in range(len(labels[r]))])
#
#         residFile = os.path.join(PATHS['root'], 'derivatives', sub, 'func',
#                                  pu.format_bids_name(sub, 'task-analogy',
#                                                      "run-0{}".format(r+1),
#                                                      'resids-lss.nii.gz'))
#         if normalize:
#             maskedImg = pa.mask_img(imgFile, mask, logger=logger)
#             resids = pa.mask_img(residFile, mask, logger=logger)
#             imgs.append(rsa.noise_normalize_beta(maskedImg, resids, logger=logger))
#         else:
#             imgs.append(pa.mask_img(imgFile, mask, logger=logger))
#
#     #         resids.append(pa.mask_img(residFile, mask))
#     #         run_data = noise_normalize_beta()
#     labels = pd.concat(labels).reset_index(drop=True)
#
#     mainrels = []
#     subrels = []
#     for _, r in labels.iterrows():
#         if r["CD"] == 1:
#             mainrels.append(r["CDMainRel"])
#             subrels.append(r["CDSubRel"])
#         elif r["AB"] == 1:
#             mainrels.append(r["ABMainRel"])
#             subrels.append(r["ABSubRel"])
#         else:
#             mainrels.append("None")
#             subrels.append("None")
#
#     labels["MainRel"] = mainrels
#     labels["SubRel"] = subrels
#     fmri_data = np.vstack(imgs)
#
#     bg_image = pu.load_img(os.path.join(PATHS['root'],
#                                         'derivatives',
#                                         sub, 'reg', 'BOLD_template.nii.gz'), logger=logger)
#     return fmri_data, labels, bg_image, mask

#
# def reorder_data_pymvpa(data, old_order, new_order):
#     return np.vstack([data[old_order.trialtag == v] for v in new_order.TrialTag])
#
#
# def reorder_data_lss(data, old_order, new_order):
#     return np.vstack([data[old_order.TrialTag == v] for v in new_order.TrialTag])
#
#
# def reorder_data_subrel(data, old_order=None, new_order=None):
#     return data[old_order.index]
#
#
# def generate_rdms(method, maskname, order,
#                   loadfunc, loadfunc_args=None, reorderfunc=reorder_data_lss,
#                   logger=None):
#     full = []
#     for sub in projectSettings["subjects"].keys():
#         fmri_data, these_labels, _, _ = loadfunc(sub, maskname, **loadfunc_args)
#         fmri_reordered_data = reorderfunc(fmri_data, these_labels, order)
#         if method == "avg":
#             full.append(pa.rdm((fmri_reordered_data[::2] +
#                                 fmri_reordered_data[1::2])/2,
#                                metric="euclidean", logger=logger))
#         else:
#             full.append(pa.rdm(fmri_reordered_data, metric="euclidean", logger=logger))
#     return np.array(full)
