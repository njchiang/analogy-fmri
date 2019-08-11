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

from fmri.analogy_utils import analysisSettings, contrastSettings, projectSettings, \
    PATHS, order, \
    pu, pa, pv, rsa, \
    compile_models, save_rois, load_rois, load_betas

paths = PATHS
# analysisSettings["searchlight"]["estimator"] = LinearSVC()


class CVSearchlight:
    def __init__(self, sub, mask_file=None, settings=analysisSettings["searchlight"], phase="AB", logger=None, phase_equals=True, phase_val=1):
        self.logger = logger
        self.sub = sub
        self.phase = phase
        self.target = "{}MainRel".format(phase.upper())
        self.mask = pu.load_img(mask_file, logger=logger) if mask_file else None
        self.fmri_data, self.labels, self.bg_image = load_betas(projectSettings, sub, t="cope-LSS", logger=logger)
        self.select_data(phase, phase_equals, phase_val)
        self.init_sl(settings)
        self.outpath = os.path.join(paths["root"], "analysis", sub, "multivariate", "searchlight", "mvpa", "{}_{}-cvsl.nii.gz".format(sub, phase))

    def select_data(self, phase="AB", equals=True, val=1):
        if equals:
            self.selector = self.labels[self.labels[phase] == val]
        else:
            self.selector = self.labels[self.labels[phase] != val]
        self.fmri_data = pu.index_img(self.fmri_data, self.selector.index)

    def init_sl(self, settings):
        settings["estimator"] = Pipeline(steps=[  # (
            # "variance_threshold", VarianceThreshold()),
            ("scaling", StandardScaler()),
        #            ("feature_select", SelectPercentile(f_classif, percentile=20)),
        #            ("feature_select", SelectKBest(f_classif, k=100)),
            ("svm", LinearSVC(C=0.05))
        #            ("plr", LogisticRegression(C=0.05, penalty="l1", tol=0.01))
        ])
        self.cv = LeaveOneGroupOut()
        self.sl_options = settings

    def run(self, **unused):
        result = pa.searchlight(self.fmri_data, self.selector[self.target],
                                m=self.mask, cv=self.cv,
                                groups=self.selector['chunks'], write=False,
                                logger=self.logger, **self.sl_options)
        pu.data_to_img(result.scores_, self.bg_image, logger=self.logger).to_filename(self.outpath)
        return result


class RSASearchlight(CVSearchlight):
    def __init__(self, sub, mask_file=None, settings=analysisSettings["searchlight"], phase="AB", logger=None, phase_equals=True, phase_val=1):
        super(RSASearchlight, self).__init__(sub, mask_file, settings=settings, phase=phase, logger=logger, phase_equals=phase_equals, phase_val=phase_val)
        self.outpath = os.path.join(paths["root"], "analysis", sub, "multivariate", "searchlight", "rsa", "{}_{}-rsa.nii.gz".format(sub, phase))

    def select_data(self, phase="AB", equals=True, val=1):
        # will be a little more complex
        if equals:
            self.selector = self.labels[self.labels[phase] == val].sort_values(["SubRel", "TrialTag"])
        else:
            self.selector = self.labels[self.labels[phase] != val]
        self.fmri_data = pu.index_img(self.fmri_data, self.selector.index)

    def init_sl(self, settings):
        settings["rdm_metric"] = "correlation"
        self.sl_options = settings

    def run(self, modelrdms):
        result = pa.searchlight_rsa(
            self.fmri_data, modelrdms,
            m=self.mask, write=False,
            logger=self.logger, **self.sl_options)
        pu.data_to_img(result.scores_, self.bg_image, logger=self.logger).to_filename(self.outpath)
        return result
        # class CrossSearchlight(CVSearchlight):
#     def select_data(self, phase=None):
#         conditionSelector = np.where(labels[contrastSettings[modelname]["label"]] != "None")

# def run_subject(sub, maskname="graymatter-bin_mask", settings=projectSettings, options=analysisSettings, logger=None):
#     mask = pu.load_img(paths["root"], "derivatives", sub, "masks", "{}.nii.gz".format(maskname), logger=logger)

#     fmri_data, labels, bg_image = load_betas(settings, sub, t="cope-LSS", logger=logger)

#     selector = labels[labels.AB == 1]

#     fmri_data = pu.index_img(fmri_data, selector.index)

#     options["searchlight"]["estimator"] = Pipeline(steps=[  # (
#         # "variance_threshold", VarianceThreshold()),
#         ("scaling", StandardScaler()),
#     #            ("feature_select", SelectPercentile(f_classif, percentile=20)),
#     #            ("feature_select", SelectKBest(f_classif, k=100)),
#         ("svm", LinearSVC(C=0.05))
#     #            ("plr", LogisticRegression(C=0.05, penalty="l1", tol=0.01))
#     ])
#     # analysis
#     # output order: CD2AB, AB2CD
#     cv = LeaveOneGroupOut()

#     result = pa.searchlight(fmri_data,
#                             selector.ABMainRel, m=mask, cv=cv,
#                             groups=selector['chunks'], write=False,
#                             logger=logger,
#                             **options['searchlight'])

#     outpath = os.path.join(paths["root"], "analysis", sub, "multivariate", "searchlight", "lss", "{}_AB-cvsl.nii.gz".format(sub))
#     pu.data_to_img(result.scores_, bg_image, logger=logger).to_filename(outpath)
#     return result

