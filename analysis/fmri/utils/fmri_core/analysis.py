from .utils import write_to_logger, mask_img, data_to_img
from .rsa_searchlight import SearchLight as RSASearchlight
from .cross_searchlight import SearchLight

import numpy as np
from datetime import datetime
from nilearn.input_data import NiftiMasker
from scipy.signal import savgol_filter
from nipy.modalities.fmri.design_matrix import make_dmtx
from nipy.modalities.fmri.experimental_paradigm import BlockParadigm
from sklearn.preprocessing import FunctionTransformer
import sklearn.model_selection as ms
from nilearn import decoding, masking
from .rsa import rdm, wilcoxon_onesided


#######################################
# Analysis setup
#######################################
# TODO : make this return an image instead of just data? (use dataToImg)
# TODO : also need to make this return reoriented labels, verify it is working
def nipreproc(img, mask=None, sessions=None, logger=None, **kwargs):
    """
    applies nilearn's NiftiMasker to data
    :param img: image to be processed
    :param mask: mask (optional)
    :param sessions: chunks (optional)
    :param logger: logger instance
    :param kwargs: kwargs for NiftiMasker from NiLearn
    :return: preprocessed image (result of fit_transform() on img)
    """
    write_to_logger("Running NiftiMasker...", logger)
    return NiftiMasker(mask_img=mask,
                       sessions=sessions,
                       **kwargs).fit_transform(img)


def op_by_label(d, l, op=None, logger=None):
    """
    apply operation to each unique value of the label and
    returns the data in its original order
    :param d: data (2D numpy array)
    :param l: label to operate on
    :param op: operation to carry (scikit learn)
    :return: processed data
    """
    write_to_logger("applying operation by label at " + str(datetime.now()), logger)
    if op is None:
        from sklearn.preprocessing import StandardScaler
        op = StandardScaler()
    opD = np.concatenate([op.fit_transform(d[l.values == i])
                         for i in l.unique()], axis=0)
    lOrder = np.concatenate([l.index[l.values == i]
                            for i in l.unique()], axis=0)
    write_to_logger("Ended at " + str(datetime.now()), logger=logger)

    return opD[lOrder]  # I really hope this works...


def sgfilter(logger=None, **sgparams):
    write_to_logger("Creating SG filter", logger)
    return FunctionTransformer(savgol_filter, kw_args=sgparams)


#######################################
# Analysis
#######################################
# TODO : featureized design matrix
# take trial by trial (beta extraction) matrix and multiply by
# feature space (in same order)
def make_designmat(frametimes, cond_ids, onsets, durations, amplitudes=None,
                   design_kwargs=None, constant=False, logger=None):
    """
    Creates design matrix from TSV columns
    :param frametimes: time index (in s) of each TR
    :param cond_ids: condition ids. each unique string will become a regressor
    :param onsets: condition onsets
    :param durations: durations of trials
    :param amplitudes: amplitude of trials (default None)
    :param design_kwargs: additional arguments(motion parameters, HRF, etc)
    :param logger: logger instance
    :return: design matrix instance
    """
    if design_kwargs is None:
        design_kwargs = {}
    if "drift_model" not in design_kwargs.keys():
        design_kwargs["drift_model"] = "blank"

    write_to_logger("Creating design matrix at " + str(datetime.now()), logger)
    paradigm = BlockParadigm(con_id=cond_ids,
                             onset=onsets,
                             duration=durations,
                             amplitude=amplitudes)
    dm = make_dmtx(frametimes, paradigm, **design_kwargs)
    if constant is False:
        dm.matrix = np.delete(dm.matrix, dm.names.index("constant"), axis=1)
        dm.names.remove("constant")

    write_to_logger("Ended at " + str(datetime.now()), logger=logger)

    return dm


def predict(clf, x, y, log=False, logger=None):
    """
    Encoding prediction. Assumes data is pre-split into train and test
    For now, just uses Ridge regression. Later will use cross-validated Ridge.
    :param clf: trained classifier
    :param x: Test design matrix
    :param y: Test data
    :param logger: logging instance
    :return: Correlation scores, weights
    """
    pred = clf.predict(x)
    if y.ndim < 2:
        y = y[:, np.newaxis]
    if pred.ndim < 2:
        pred = pred[:, np.newaxis]

    if log:
        write_to_logger("Predicting at " + str(datetime.now()), logger)
    corrs = np.array([np.corrcoef(y[:, i], pred[:, i])[0, 1]
                     for i in range(pred.shape[1])])

    if log:
        write_to_logger("Ended at " + str(datetime.now()), logger=logger)

    return corrs


def roi(x, y, clf, m=None, cv=None, logger=None, **roiargs):
    """
    Cross validation on a masked roi. Need to decide if this
    function does preprocessing or not
    (probably should pipeline in)
    pa.roi(x, y, clf, m, cv, groups=labels['chunks'])
    :param x: input image
    :param y: labels
    :param clf: classifier or pipeline
    :param m: mask (optional)
    :param cv: cross validator
    :param roiargs: other model_selection arguments, especially groups
    :return: CV results
    """
    if m is not None:
        X = mask_img(x, m, logger=logger)
    else:
        X = x
    return ms.cross_val_score(estimator=clf, X=X, y=y, cv=cv, **roiargs)


def searchlight(x, y, m=None, groups=None, cv=None,
                write=False, logger=None, **searchlight_args):
    """
    Wrapper to launch searchlight
    :param x: Data
    :param y: labels
    :param m: mask
    :param groups: group labels
    :param cv: cross validator
    :param write: if image for writing is desired or not
    :param logger:
    :param searchlight_args:(default) process_mask_img(None),
                            radius(2mm), estimator(svc),
                            n_jobs(-1), scoring(none), cv(3fold), verbose(0)
    :return: trained SL object and SL results
    """
    write_to_logger("starting searchlight at " + str(datetime.now()), logger=logger)
    if m is None:
        m = masking.compute_epi_mask(x)
    searchlight_args["process_mask_img"] = m
    write_to_logger("searchlight params: " + str(searchlight_args), logger=logger)

    sl = SearchLight(mask_img=m, cv=cv, **searchlight_args)
    sl.fit(x, y, groups)
    write_to_logger("Searchlight ended at " + str(datetime.now()), logger=logger)
    if write:
        return sl, data_to_img(sl.scores_, x, logger=logger)
    else:
        return sl



def searchlight_rsa(x, y, m=None, write=False,
                    logger=None, **searchlight_args):
    """
    Wrapper to launch searchlight
    :param x: Data
    :param y: model
    :param m: mask
    :param write: if image for writing is desired or not
    :param logger:
    :param searchlight_args:(default) process_mask_img(None),
                            radius(2mm), estimator(svc),
                            n_jobs(-1), verbose(0)
    :return: trained SL object and SL results
    """
    write_to_logger("starting searchlight at " + str(datetime.now()), logger=logger)
    if m is None:
        m = masking.compute_epi_mask(x)
    write_to_logger("searchlight params: " + str(searchlight_args))
    sl = RSASearchlight(mask_img=m, **searchlight_args)
    sl.fit(x, y)
    write_to_logger("Searchlight ended at " + str(datetime.now()), logger=logger)

    if write:
        return sl, data_to_img(sl.scores_, x, logger=logger)
    else:
        return sl
