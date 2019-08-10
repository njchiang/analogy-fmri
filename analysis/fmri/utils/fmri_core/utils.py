import os, sys
import logging
import json
import numpy as np
import pandas as pd
from datetime import datetime
from scipy.io import loadmat
from scipy.io import savemat
from nilearn import image
from nilearn import masking


#######################################
# Setup logging
#######################################
def setup_logger(*loc, fname="analysis"):
    """
    Setting up log file
    :param loc: location of file
    :param fname: log file name
    :return: logger instance
    """
    logging.basicConfig(filename=os.path.join(*loc,
                                              fname + "-" +
                                              sys.platform + ".log"),
                        datefmt="%m-%d %H:%M",
                        level=logging.DEBUG)
    logger = logging.getLogger(fname)
    logger.info("--------------------------------")
    logger.info("Session started at " + str(datetime.now()))
    return logger


def write_to_logger(msg, logger=None):
    """
    Writes to logger
    :param msg: Message to write
    :param logger: logger handle
    :return: None
    """
    if logger is not None:
        logger.info(msg)
    else:
        print(msg)
    return


#######################################
# File I/O
#######################################
# JSON I/O
def load_config(*path, logger=None):
    """
    Load JSON config file
    :param path: path to json
    :param logger: logger instance
    :return: dict with JSON contents
    """
    write_to_logger("Loading JSON config from " + os.path.join(*path), logger)
    with open(os.path.join(*path), "r") as f:
        d = json.load(f)
    return d


def write_config(d, *path, logger=None):
    """
    Write JSON file
    :param d: dict to write
    :param logger: logger instance
    :param path: path to location
    :return: None
    """
    write_to_logger("Writing JSON config to " + os.path.join(*path), logger)
    with open(os.path.join(*path), "wt") as f:
        json.dump(d, f, indent=4)
    return


# TODO : change this to keyworded?
def format_bids_name(*args):
    """
    write BIDS format name (may change this later)
    :param args: items to join
    :return: name
    """
    return ("_").join(args)


# Matlab I/O
def save_mat_data(*fn, logger=None, **kwargs):
    """
    :param fn: path to file
    :param logger: logger file
    :param kwargs: any key value pairs-- keys will become
    fieldnames of the struct with value.
    :return: None: write a mat file
    """
    write_to_logger("Saving mat data to " + os.path.join(*fn), logger)
    savemat(os.path.join(*fn), kwargs)
    return kwargs


def load_mat_data(*args, logger=None):
    """
    Loads matlab file (just a wrapper)
    :param args: path to file
    :param logger: logger instance or none
    :return: dict
    """
    write_to_logger("Loading mat file...", logger)
    return loadmat(os.path.join(*args))


# Nilearn
def load_img(*path, logger=None):
    """
    Simple wrapper for nilearn load_img to load NIFTI images
    :param path: path to subject directory
    :param logger: logfile ID
    :return: Nifti1Image
    """
    bs = os.path.join(*path)
    write_to_logger("Reading file from: " + bs, logger)
    return image.load_img(bs, dtype=np.float64)


def concat_imgs(imgs, logger=None):
    """
    Simple wrapper for concat_imgs
    :param imgs: list of nifti images or filenames
    :param logger: logfile ID
    :return: Nifti1Image
    """
    write_to_logger("Concatenating {} images".format(len(imgs)), logger)
    return image.concat_imgs(imgs, dtype=np.float64)


def index_img(imgs, index, logger=None):
    """
    Simple wrapper for index_img
    :param imgs:
    :param index:
    :param logger:
    :return:
    """
    write_to_logger("Slicing image", logger)
    return image.index_img(imgs, index)


def load_labels(*args, logger=None, **pdargs):
    """
    Simple wrapper using Pandas to load label files
    :param args: path to file directory
    :param logger: logfile ID
    :param pdargs: pandas read_csv args
    :return: pandas DataFrame with labels
    """
    lp = os.path.join(*args)
    write_to_logger("Loading label file from: " + lp, logger)
    return pd.read_csv(lp, **pdargs)


#######################################
# Image processing
#######################################
def estimate_mask(im, st="background", logger=None):
    """
    mask the wholehead image (if we don"t have one).
    wrapper for NiLearn implementation
    :param im: image
    :param st: type of automatic extraction. epi for epi images,
    background for all other.
    :param logger: logger file
    :return: mask
    """
    write_to_logger("Estimating masks...", logger)
    if st == "epi":
        mask = masking.compute_epi_mask(im)
    else:
        mask = masking.compute_background_mask(im)
    return mask


def mask_img(im, mask=None, logger=None):
    """
    Wrapper for apply_mask (adds logging)
    :param im: image
    :param mask: mask. if none, will estimate mask to generate 2d
    :param logger: logger ID
    :return: masked image
    """
    # solved as of nilearn 2.3
    # if isinstance(im, str):
    write_to_logger("Applying mask", logger)
    return masking.apply_mask(im, mask, dtype=np.float64)
    # else:
    #     write_to_logger("Masking file")
    #     return masking._apply_mask_fmri(im, mask, dtype=np.float64)


def data_to_img(d, img, copy_header=False, logger=None):
    """
    Wrapper for new_image_like
    :param img: Image with header you want to add
    :param d: data
    :param copy_header: Boolean
    :param logger: logger instance
    :return: Image file
    """
    write_to_logger("converting data to image...", logger)
    return image.new_img_like(image.mean_img(img), d, copy_header=copy_header)


def center_img(img, logger=None):
    """

    :param img:
    :param logger:
    :return:
    """
    write_to_logger("centering image", logger)
    return image.math_img("img - np.mean(img, axis=-1, keepdims=True)",
                          img=img)


def unmask_img(d, mask, logger=None):
    """
    Unmasks matrix d according to mask
    :param d: numpy array (2D)
    :param mask: mask
    :param logger: logger instance
    :return: image file
    """
    write_to_logger("unmasking image...", logger)
    return masking.unmask(d, mask)


def clip_brain(mask):
    """
    Finds the min and max indices on each axis of the mask
    :param mask: 3d image
    :return: indices (list of tuples)
    """
    return [(d.min(), d.max()) for d in np.where(mask > 0)]
#######################################
# Computation
#######################################
