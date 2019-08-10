"""
TODO : merge RSA and cross earchlights via refactor
The searchlight is a widely used approach for the study of the
fine-grained patterns of information in fMRI analysis, in which
multivariate statistical relationships are iteratively tested in the
neighborhood of each location of a domain.
"""
# Authors : Vincent Michel (vm.michel@gmail.com)
#           Alexandre Gramfort (alexandre.gramfort@inria.fr)
#           Philippe Gervais (philippe.gervais@inria.fr)
#
# License: simplified BSD

import time
import sys
import warnings
from distutils.version import LooseVersion

import numpy as np

import sklearn
from sklearn.externals.joblib import Parallel, delayed, cpu_count
from sklearn import svm
from sklearn.base import BaseEstimator

from nilearn import masking
from nilearn.image.resampling import coord_transform
from nilearn.input_data.nifti_spheres_masker import _apply_mask_and_get_affinity
from nilearn._utils.compat import _basestring
# from nilearn._utils.fixes import cross_val_score

from .rsa import rdm

ESTIMATOR_CATALOG = dict(svc=svm.LinearSVC, svr=svm.SVR)


def search_light(X, y, A, metric="spearman", rdm_metric="euclidean",
                 n_jobs=-1, verbose=0):
    """Function for computing a search_light
    Parameters
    ----------
    X : array-like of shape at least 2D
        data to fit.
    y : array-like
        target variable to predict.
    A : scipy sparse matrix.
        adjacency matrix. Defines for each feature the neigbhoring features
        following a given structure of the data.
    metric : basestring
        distance method for RSA
    n_jobs : int, optional
        The number of CPUs to use to do the computation. -1 means
        'all CPUs'.
    verbose : int, optional
        The verbosity level. Defaut is 0
    Returns
    -------
    scores : array-like of shape (number of rows in A)
        search_light scores
    """
    group_iter = GroupIterator(A.shape[0], n_jobs)
    scores = Parallel(n_jobs=n_jobs, verbose=verbose)(
        delayed(_group_iter_search_light)(
            list_rows=A.rows[list_i],
            X=X, y=y, metric=metric, rdm_metric=rdm_metric,
            thread_id=thread_id + 1, total=A.shape[0],
            verbose=verbose)
        for thread_id, list_i in enumerate(group_iter))
    return np.concatenate(scores, axis=0)


class GroupIterator(object):
    """Group iterator
    Provides group of features for search_light loop
    that may be used with Parallel.
    Parameters
    ----------
    n_features : int
        Total number of features
    n_jobs : int, optional
        The number of CPUs to use to do the computation. -1 means
        'all CPUs'. Defaut is 1
    """
    def __init__(self, n_features, n_jobs=1):
        self.n_features = n_features
        if n_jobs == -1:
            n_jobs = cpu_count()
        self.n_jobs = n_jobs

    def __iter__(self):
        split = np.array_split(np.arange(self.n_features), self.n_jobs)
        for list_i in split:
            yield list_i


def _group_iter_search_light(list_rows, X, y, metric, rdm_metric, thread_id,
                             total, verbose=0):
    """Function for grouped iterations of search_light
    Parameters
    -----------
    list_rows : array of arrays of int
        adjacency rows. For a voxel with index i in X, list_rows[i] is the list
        of neighboring voxels indices (in X).
    X : array-like of shape at least 2D
        data to fit.
    y : array-like
        target variable to predict.
    metric : basestring
        distance metric for RSA
    thread_id : int
        process id, used for display.
    total : int
        Total number of voxels, used for display
    verbose : int, optional
        The verbosity level. Defaut is 0
    Returns
    -------
    par_scores : numpy.ndarray
        score for each voxel. dtype: float64.
    """
    if y.ndim > 1:
        n_models = y.shape[0]
        par_scores = np.zeros([len(list_rows), n_models])
    else:
        par_scores = np.zeros(len(list_rows))
    t0 = time.time()
    for i, row in enumerate(list_rows):
        # X: activity patterns
        # y: model rdm

        # par_scores[i] = np.mean(cross_val_score(estimator, X[:, row],
        #                                         y, cv=cv, n_jobs=1,
        #                                         **kwargs))
        ### RUN RSA ###
        roi_rdm = rdm(X[:, row], metric=rdm_metric)  # set up default
        # distance
        if y.shape[0] > 1:
            par_scores[i] = 1 - rdm(np.vstack([roi_rdm, y]).astype(np.float64),
                                    metric=metric, return_p=False)[0:n_models]
        else:
            par_scores[i] = 1 - rdm(np.vstack([roi_rdm, y]).astype(np.float64),
                                    metric=metric, return_p=False)

        ###############

        if verbose > 0:
            # One can't print less than each 10 iterations
            step = 11 - min(verbose, 10)
            if (i % step == 0):
                # If there is only one job, progress information is fixed
                if total == len(list_rows):
                    crlf = "\r"
                else:
                    crlf = "\n"
                percent = float(i) / len(list_rows)
                percent = round(percent * 100, 2)
                dt = time.time() - t0
                # We use a max to avoid a division by zero
                remaining = (100. - percent) / max(0.01, percent) * dt
                sys.stderr.write(
                    "Job #%d, processed %d/%d voxels "
                    "(%0.2f%%, %i seconds remaining)%s"
                    % (thread_id, i, len(list_rows), percent, remaining, crlf))
    return par_scores


##############################################################################
# Class for search_light #####################################################
##############################################################################
class SearchLight(BaseEstimator):
    """Implement search_light analysis using an arbitrary type of classifier.
    Parameters
    -----------
    mask_img : Niimg-like object
        See http://nilearn.github.io/manipulating_images/input_output.html
        boolean image giving location of voxels containing usable signals.
    process_mask_img : Niimg-like object, optional
        See http://nilearn.github.io/manipulating_images/input_output.html
        boolean image giving voxels on which searchlight should be
        computed.
    radius : float, optional
        radius of the searchlight ball, in millimeters. Defaults to 2.
    n_jobs : int, optional. Default is -1.
        The number of CPUs to use to do the computation. -1 means
        'all CPUs'.
    cv : cross-validation generator, optional
        A cross-validation generator. If None, a 3-fold cross
        validation is used or 3-fold stratified cross-validation
        when y is supplied.
    verbose : int, optional
        Verbosity level. Defaut is False
    Notes
    ------
    The searchlight [Kriegeskorte 06] is a widely used approach for the
    study of the fine-grained patterns of information in fMRI analysis.
    Its principle is relatively simple: a small group of neighboring
    features is extracted from the data, and the prediction function is
    instantiated on these features only. The resulting prediction
    accuracy is thus associated with all the features within the group,
    or only with the feature on the center. This yields a map of local
    fine-grained information, that can be used for assessing hypothesis
    on the local spatial layout of the neural code under investigation.
    Nikolaus Kriegeskorte, Rainer Goebel & Peter Bandettini.
    Information-based functional brain mapping.
    Proceedings of the National Academy of Sciences
    of the United States of America,
    vol. 103, no. 10, pages 3863-3868, March 2006
    """

    def __init__(self, mask_img, process_mask_img=None, radius=2.,
                 n_jobs=1, rdm_metric="euclidean", metric="spearman",
                 verbose=0):
        self.mask_img = mask_img

        self.process_mask_img = process_mask_img
        self.radius = radius
        self.n_jobs = n_jobs
        self.rdm_metric = rdm_metric
        self.metric = metric
        self.verbose = verbose

    def fit(self, imgs, y):
        """Fit the searchlight
        Parameters
        ----------
        imgs : Niimg-like object
            See http://nilearn.github.io/manipulating_images/input_output.html
            4D image.
        y : 1D array-like
            Target variable to predict. Must have exactly as many elements as
            3D images in img.
        groups : array-like, optional
            group label for each sample for cross validation. Must have
            exactly as many elements as 3D images in img. default None
            NOTE: will have no effect for scikit learn < 0.18
        """

        # Get the seeds
        process_mask_img = self.process_mask_img
        if self.process_mask_img is None:
            process_mask_img = self.mask_img

        # Compute world coordinates of the seeds
        process_mask, process_mask_affine = masking._load_mask_img(
            process_mask_img)
        process_mask_coords = np.where(process_mask != 0)
        process_mask_coords = coord_transform(
            process_mask_coords[0], process_mask_coords[1],
            process_mask_coords[2], process_mask_affine)
        process_mask_coords = np.asarray(process_mask_coords).T

        X, A = _apply_mask_and_get_affinity(
            process_mask_coords, imgs, self.radius, True,
            mask_img=self.mask_img)

        scores = search_light(X, y, A, metric=self.metric,
                              rdm_metric=self.rdm_metric, n_jobs=self.n_jobs,
                              verbose=self.verbose)

        scores_3D = []
        for g in range(scores.shape[1]):
            these_scores = np.zeros(process_mask.shape)
            these_scores[process_mask] = scores[:, g]
            scores_3D.append(these_scores)
        scores_3D = np.stack(scores_3D, -1)

        # scores_3D = np.zeros(process_mask.shape)
        # scores_3D[process_mask] = scores
        self.scores_ = scores_3D
        return self