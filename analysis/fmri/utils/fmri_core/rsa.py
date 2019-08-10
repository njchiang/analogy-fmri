from scipy.stats import wilcoxon, spearmanr
from scipy.spatial.distance import pdist, squareform
from sklearn.model_selection import LeaveOneOut
from .utils import write_to_logger, mask_img, data_to_img
# from . import searchlight

import numpy as np


def add_diag(x, v):
    """
    memory efficient way to add a diagonal matrix with a square matrix
    :param x: square matrix to be appended
    :param v: vector of diagonal elements
    :return:
    """
    for i in range(len(v)):
        x[i, i] += v[i]
    return x


def sumproduct(x1, x2):
    """
    memory efficient way to multiply two matrices and add the result
    :param x1:
    :param x2:
    :return:
    """
    if x1.shape[1] != x2.shape[0]:
        return None
    try:
        total = 0
        for r in range(x1.shape[0]):
            total += np.dot(x1[r], x2).sum()
    # still use dot product, just with stacked vectors...
    except MemoryError:
        total = 0
        # slow
        for i in range(x1.shape[0]):
            for j in range(x2.shape[1]):
                total += sum(x1[i] * x2[:, j])

    return total


def ssq(x):
    total = 0
    for i in range(x.shape[0]):
        total += (x[i]**2).sum()
    return total


# TODO : Add RSA functionality (needs a .fit)
def shrink_cov(x, df=None, shrinkage=None, logger=None):
    """
    Regularize estimate of covariance matrix according to optimal shrinkage
    method Ledoit& Wolf (2005), translated for covdiag.m (rsatoolbox- MATLAB)
    :param x: T obs by p random variables
    :param df: degrees of freedom
    :param shrinkage: shrinkage factor
    :return: sigma, invertible covariance matrix estimator
             shrink: shrinkage factor
             sample: sample covariance (un-regularized)
    """
    # TODO : clean this code up
    t, n = x.shape
    if df is None:
        df = t-1
    x = x - x.mean(0)
    sampleCov = 1/df * np.dot(x.T, x)
    prior_diag = np.diag(sampleCov)  # diagonal of sampleCov
    if shrinkage is None:
        try:
            d = 1 / n * np.linalg.norm(sampleCov-np.diag(prior_diag),
                                       ord='fro')**2
            r2 = 1 / n / df**2 * np.sum(np.dot(x.T**2, x)) - \
                1 / n / df * np.sum(sampleCov**2)
        except MemoryError:
            write_to_logger("Low memory option", logger)
            d = 1 / n * np.linalg.norm(add_diag(sampleCov, -prior_diag),
                                       ord='fro')**2
            write_to_logger("d calculated")
            r2 = 1 / n / df**2 * sumproduct(x.T**2, x)

            write_to_logger("r2 part 1")

            r2 -= 1 / n / df * ssq(sampleCov)
            write_to_logger("r2 part 2")
        shrink = max(0, min(1, r2 / d))
    else:
        shrink = 0

    # sigma = shrink * prior + (1-shrink) * sampleCov
    # sigma = add_diag((1-shrink) * sampleCov, shrink*prior_diag)
    # return sigma, shrink, sampleCov
    return add_diag((1-shrink)*sampleCov, shrink*prior_diag), \
        shrink, prior_diag


# DON'T NEED ANY OF THIS IF SIGMA and INV_SIGMA are known,
# can use pdist(..., VI=INV_SIGMA)
def noise_normalize_beta(betas, resids, df=None, shrinkage=None, logger=None):
    """
    "whiten" beta estimates according to residuals.
    Generally, because there are more features than
    samples regularization is used to find the covariance matrix (see covdiag)
    :param betas: activity patterns ( nBetas (trials) by nVoxels, for example)
    :param resids: residuals (n voxels by nTRs)
    :param df: degrees of freedom. if none, defaults to nTRs- nBetas
    :param shrinkage: shrinkage (see covdiag)
    :param logger: logger instance
    :return: whitened betas (will have diagonal covariance matrix)
    """
    # find resids, WHAT ARE DEGREES OF FREEDOM
    # TODO : add other measures from noiseNormalizeBeta
    vox_cov_reg, shrink, _ = shrink_cov(resids, df,
                                        shrinkage=shrinkage, logger=logger)
    whiten_filter = whitening_filter(vox_cov_reg)
    whitened_betas = np.dot(betas, whiten_filter)
    # estimated true activity patterns
    return whitened_betas


def whitening_filter(x):
    """
    calculates inverse square root of a square matrix using SVD
    :param x: covariance matrix
    :return: inverse square root of a square matrix
    """
    _, s, vt = np.linalg.svd(x)
    return np.dot(np.diag(1/np.sqrt(s)), vt).T


def spearman_noise_bounds(rdms):
    """
    Calculate upper and lower bounds on spearman correlations
    using double dipping
    (See Nili et al 2014)
    :param rdms: Stacked RDMs
    :return: (upper bound, lower bound)
    """
    # upper bound: each subject's correlation with mean
    mean_rdm = rdms.mean(0)
    upper = 1 - spearman_distance(np.vstack([mean_rdm, rdms]))[0][0, 1:]
    # lower bound: each subject's correlation with mean of other subjects
    loo = LeaveOneOut()
    lower = 1 - \
        np.array([spearman_distance(np.vstack([rdms[test],
                                               rdms[train].mean(0)]))[0]
                  for train, test in loo.split(rdms)
                  ])
    return np.vstack([upper, lower])


def rdm(X, square=False, logger=None, return_p=False, **pdistargs):
    """
    Calculate distance matrix
    :param X: data
    :param square: shape of output (square or vec)
    :param pdistargs: notably: include "metric"
    :return: pairwise distances between items in X
    """
    # add crossnobis estimator
    if logger is not None:
        write_to_logger("Generating RDM", logger)
    p = None
    if "metric" in pdistargs:
        if pdistargs["metric"] == "spearman":
            r, p = spearman_distance(X)
            if r.shape is not ():
                r = squareform(r, checks=False)
                p = squareform(r, checks=False)
        else:
            r = pdist(X, **pdistargs)
    else:
        r = pdist(X, **pdistargs)

    if square:
        r = squareform(r, checks=False)
        if p is not None:
            p = squareform(p, checks=False)

    if p is not None and return_p is True:
        return r, p
    else:
        return r


def spearman_distance(x):
    """
    Spearman distance of a matrix. To find distance between two entities,
    stack them and pass in
    :param x: entries
    :return: Spearman distance (1 - rho)
    """
    rho, p = spearmanr(x, axis=1)
    return 1 - rho, p


def wilcoxon_onesided(x, **kwargs):
    """
    Runs one sided nonparametrix t test
    :param x: data
    :param kwargs: arguments for wilcoxon
    :return: p-values
    """
    _, p = wilcoxon(x, **kwargs)
    if np.median(x) > 0:
        res = p/2
    else:
        res = 1 - p/2
    return res


