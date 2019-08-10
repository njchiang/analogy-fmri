# TODO : populate after development is done
from nilearn import plotting as nplt
from .utils import unmask_img
from numpy import allclose
from scipy.spatial.distance import squareform
from scipy.stats import rankdata
from numpy import eye
from matplotlib.pyplot import colorbar, imshow
from sklearn.preprocessing import minmax_scale

def plot_anat(anat_img, **kwargs):
    nplt.plot_anat(anat_img, **kwargs)
    return


def plot_epi(epi_img, **kwargs):
    nplt.plot_epi(epi_img, **kwargs)
    return


def plot_stat_map(stat_img, bg_img, **kwargs):
    nplt.plot_stat_map(stat_img, bg_img, **kwargs)
    return


def plot_roi(roi, bg, **kwargs):
    nplt.plot_roi(roi, bg, **kwargs)
    return


def plot_connectome(mat, coords, **kwargs):
    nplt.plot_connectome(mat, coords, **kwargs)
    return


def plot_masked(mat, mask, **kwargs):
    nplt.plot_stat_map(unmask_img(mat, mask), **kwargs)
    return


def plot_rdm(rdm, rank=True, scale=True, ax=None, cb=True,
             mode="rdm", **plot_args):
    # for now, can only pass in a vector or square matrix (allclose might break).
    # TODO : fix error handling
    if rdm.ndim > 1 and rdm.shape[0] == rdm.shape[1]:
        if allclose(rdm, rdm.T):
            rdm = squareform(rdm, checks=False)  # transform to vector if square

    if rank:
        rdm = rankdata(rdm)

    if scale:
        rdm = minmax_scale(rdm)

    rdm = squareform(rdm)

    if mode is not "rdm":
        rdm += eye(rdm.shape[0])

    if ax is not None:
        im = ax.imshow(rdm, **plot_args)
    else:
        im = imshow(rdm, **plot_args)

    if cb:
        colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    return im
