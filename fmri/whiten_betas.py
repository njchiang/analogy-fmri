# Set up analysis and paths
projecttitle = 'Analogy'
import sys, os
if sys.platform == 'darwin':
    homedir = os.path.join("/Users", "njchiang")
    sys.path.append(os.path.join(homedir, "GitHub", "task-fmri-utils"))
    sys.path.append(os.path.join(homedir, "GitHub", "tikhonov"))
elif sys.platform == "linux":
    homedir = os.path.join("/home", "njchiang", "data")
    sys.path.append(os.path.join(homedir, "GitHub", "task-fmri-utils"))
    sys.path.append(os.path.join(homedir, "GitHub", "tikhonov"))
else:
    homedir = os.path.join("D:\\")
    sys.path.append(os.path.join(homedir, "GitHub", "task-fmri-utils"))
    sys.path.append(os.path.join(homedir, "GitHub", "tikhonov"))


# imports
from fmri_core import analysis as pa
from fmri_core import utils as pu
from fmri_core import vis as pv
from fmri_core import rsa

import numpy as np

# load configuration
os.chdir(os.path.join(homedir, "CloudStation", "Grad", "Research", "montilab-ucla"))
projectSettings = pu.load_config(os.path.join('analogy', 'config', 'project.json'))
analysisSettings = pu.load_config(os.path.join('analogy', 'config', 'analyses.json'))
if sys.platform == 'darwin':
    paths = projectSettings['filepaths']['osxPaths']
elif sys.platform == "linux":
    paths = projectSettings["filepaths"]["linuxPaths"]
else:
    paths = projectSettings['filepaths']['winPaths']


# order the trials the same for all subjects so the RDMs can be stacked
order = {"full": pu.load_labels("analogy/labels/trialorder_rsa_absorted.csv"),
         "match": pu.load_labels("analogy/labels/trialorder_rsa_match.csv"),
         "nomatch": pu.load_labels("analogy/labels/trialorder_rsa_nomatch.csv")
         }


def reorder_data(data, old_order, new_order):
    return np.vstack([data[old_order.trialtag == v] for v in new_order.TrialTag])


def load_data(sub, maskname):
    imgFile = os.path.join(paths['root'], 'derivatives', sub, 'betas', pu.format_bids_name(sub, 'task-analogy', 'betas-pymvpa.nii.gz'))
    mask = pu.load_img(paths['root'],
                       'derivatives', sub, 'masks',
                       maskname + '.nii.gz')
    labels = pu.load_labels(paths['root'],
                            'derivatives', sub, 'betas',
                            pu.format_bids_name(sub, 'task-analogy', 'events-pymvpa.tsv'),
                            sep='\t', index_col=0)
    maskedImg = pa.mask_img(imgFile, mask)
    conditionSelector = np.where(labels['ab'] == 1)

    resids = []
    # whiten the data
    for r in range(8):
        residFile = os.path.join(paths['root'], 'derivatives', sub, 'func',
                                 pu.format_bids_name(sub, 'task-analogy',
                                                     "run-0{}".format(r+1),
                                                     'resids-pymvpa.nii.gz'))
        resids.append(pa.mask_img(residFile, mask))

    fmri_data = rsa.noise_normalize_beta(maskedImg[conditionSelector], np.vstack(resids))

    these_labels = labels.iloc[conditionSelector]
    bg_image = pu.load_img(os.path.join(paths['root'],
                                        'derivatives',
                                        sub, 'reg', 'BOLD_template.nii.gz'))
    return fmri_data, these_labels, bg_image, mask


def generate_rdms(maskname, order):
    full = []
    match = []
    nomatch = []
    for sub in projectSettings["subjects"].keys():
        fmri_data, these_labels, _, _ = load_data(sub, maskname)
        fmri_reordered_data = reorder_data(fmri_data, these_labels, order["full"])
        full.append(pa.rdm((fmri_reordered_data[::2] + fmri_reordered_data[1::2])/2, metric="euclidean"))
        match.append(pa.rdm(reorder_data(fmri_data, these_labels, order["match"]), metric="euclidean"))
        nomatch.append(pa.rdm(reorder_data(fmri_data, these_labels, order["nomatch"]), metric="euclidean"))
    return np.array(full), np.array(match), np.array(nomatch)


def all_subject_rdms(maskname, order, save=True, load=True):
    rdms = {}
    if load:
        try:
            full = np.load(os.path.join(paths['cloud'],
                                        "analysis",
                                        "rsa", "rdms",
                                        "subject-rdms_{}_{}-ab-whitened.npy".format(maskname, "full")))
            match = np.load(os.path.join(paths['cloud'],
                                         "analysis",
                                         "rsa", "rdms",
                                         "subject-rdms_{}_{}-ab-whitened.npy".format(maskname, "match")))
            nomatch = np.load(os.path.join(paths['cloud'],
                                           "analysis",
                                           "rsa", "rdms",
                                           "subject-rdms_{}_{}-ab-whitened.npy".format(maskname, "nomatch")))
            save=False
        except FileNotFoundError:
            full, match, nomatch = generate_rdms(maskname, order)
    else:
        full, match, nomatch = generate_rdms(maskname, order)

    rdms["full"] = full
    rdms["match"] = match
    rdms["nomatch"] = nomatch

    if save:
        for k in rdms.keys():
            np.save(os.path.join(paths['root'],
                                 "analysis",
                                 "rsa", "rdms",
                                 "subject-rdms_{}_{}-ab-whitened.npy".format(maskname, k)),
                    rdms[k])

    return rdms


all_subject_rdms("svm-abmainrel-bin_mask", order)