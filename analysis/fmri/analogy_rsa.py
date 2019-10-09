import json
import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.feature_selection import VarianceThreshold

from .analogy_utils import analysisSettings, contrastSettings, \
    projectSettings, order, \
    pu, pa, pv, compile_models, rsa, save_rois, load_rois


def reduce_by_factor(rdm, factor):
    if rdm.ndim != 2:
        rdm = rsa.squareform(rdm)

    if (len(rdm) % factor) != 0:
        print("Factor issue, are you sure that's right?")
    return sum([rdm[i::factor, i::factor] for i in range(factor)])/factor


def downsample_rdms_by_factor(all_rdms, factor):
    downsampled_rdms = {}

    for mask, rdms in all_rdms.items():
        these_avg_rdms = []
        for rdm in rdms:
            these_rdms = []
            reduced_rdm = reduce_by_factor(rdm, factor)
            these_avg_rdms.append(reduced_rdm)
        downsampled_rdms[mask] = np.stack(these_avg_rdms)
    return downsampled_rdms


def downsample_rdms_df_by_factor(rdms, factor):
    results = [rsa.squareform(reduce_by_factor(rdms.iloc[i, 3:].astype(
        np.float64),
        factor))
               for i in range(len(rdms))]
    return pd.concat(
        [rdms.iloc[:, :3], pd.DataFrame(np.vstack(results),
                                        dtype=np.float)], axis=1)


def get_model_rdms(raw_models, modelnames):
    models = create_models(raw_models, modelnames)
    return models_to_df(models)


def get_model_rdm(models, label, metric="cosine"):
    if isinstance(label, str):
        features = models[[c for c in models.columns if label in c]]
    else:
        features = []
        for l in label:
            features.append(models[[c for c in models.columns if l in c]])
        features = np.hstack(features)
    return rsa.rdm(features, metric=metric)


def create_models(models, modelnames):
    stacked_models_avg = []
    stacked_models_subrel = []
    stacked_models_9rel = []
    stacked_models_full = []
    for i, model in enumerate(modelnames):
        if (model == "numchar") or (model == "typicality"):
            metric = "euclidean"
        else:
            metric = "cosine"

        this_rdm = get_model_rdm(models, model, metric)
        stacked_models_full.append(this_rdm)
        # Same as full
        stacked_models_avg.append(this_rdm)
        stacked_models_subrel.append(this_rdm)
        stacked_models_9rel.append(this_rdm)
        # stacked_models_avg.append(
        #     rsa.squareform(
        #         reduce_by_factor(this_rdm, 2), checks=False
        #     )
        # )
        # stacked_models_subrel.append(
        #     rsa.squareform(
        #         reduce_by_factor(this_rdm, 2), checks=False
        #         # reduce_by_factor(this_rdm, 4), checks=False
        #     )
        # )
        # stacked_models_9rel.append(
        #     rsa.squareform(
        #         reduce_by_factor(this_rdm, 16), checks=False
        #         # reduce_by_factor(this_rdm, 32), checks=False
        #     )
        # )

    return {"stacked_models": {
        "full": np.array(stacked_models_full),
        "avg": np.array(stacked_models_avg),
        "subrel": np.array(stacked_models_subrel),
        "9rel": np.array(stacked_models_9rel)
    }, "names": [str(m).replace("[", "").replace("]", "").replace(", ", "+")
                 for m in modelnames]}


def models_to_df(models):
    models_df_dict = []
    for k, n in {"full": "full", "avg": "avg",
                 "subrel": "subrel", "9rel": "downsampled"}.items():
        arr = pd.DataFrame(models["stacked_models"][k])
        names = [n for _ in range(len(arr))]
        models_df_dict.append(pd.concat([
            pd.DataFrame({"type": names, "name": models["names"]}),
            arr
        ], axis=1))
    return pd.concat(models_df_dict, axis=0, join="outer", sort=False)


def plotmodels(models, save=False):
    f = plt.figure(figsize=(30, 10))
    axarr = f.subplots(len(models.type.unique()), len(models.name.unique()))
    for i, t in enumerate(models.type.unique()):
        rdms = models[models.type==t]
        axarr[i, 0].set_ylabel(t)
        for j, m in enumerate(models.name.unique()):
            pv.plot_rdm(rdms[rdms.name==m].iloc[:, 2:].dropna(axis=1),
                        ax=axarr[i,j], cb=False, cmap="plasma")
            axarr[0, j].set_title(m)


def plot_results(df_gp):
    return (df_gp
            .mean()
            .drop(["upper", "lower"], axis=1)).plot(
        yerr=(df_gp
              .std()
              .drop(["upper", "lower"], axis=1)/np.sqrt(15)),
        kind="bar",
        error_kw=dict(capsize=0.75, elinewidth=0.5),
        figsize=(18,12)
    )


def roi_rdm(roi, label, metric="euclidean", avg=True, subset=None,
            subrel=False):
    # should we do entire chunk-wise standardization or just AB?
    # roi = pa.op_by_label(roi, label.chunks)
    if subrel:
        selector = label[label.AB == 1]\
            .sort_values(["ABSubRel", "chunks"]).index
        if subset is not None:
            this_roi = roi[selector][subset]
        else:
            this_roi = roi[selector]
        # testing
        # this_roi = pa.op_by_label(this_roi,
        #                           label.chunks[selector].reset_index(drop=True))
        out = rsa.rdm(this_roi, metric=metric)
    else:
        selector = label[label.AB == 1]\
            .sort_values(["ABSubRel", "TrialTag"]).index
        if subset is not None:
            this_roi = roi[selector][subset]
        else:
            this_roi = roi[selector]
        # testing
        # this_roi = pa.op_by_label(this_roi,
        #                           label.chunks[selector].reset_index(drop=True))
        # this option is not great
        # out = rsa.rdm((this_roi[::2] + this_roi[1::2]) / 2, metric="euclidean")
        # this option seems to work better
        if avg:
            out = (rsa.rdm(this_roi[::2], metric=metric) +
                   rsa.rdm(this_roi[1::2], metric=metric)) / 2
        else:
            out = rsa.rdm(this_roi, metric=metric)
        # compare with this
        # out = rsa.rdm(this_roi, metric="euclidean")
    return out


def run_rsa(subject_rdms, stacked_models):
    res = {}
    for mask, rdms in subject_rdms.items():
        res[mask] = {}
        res[mask]["corr"] = np.array([rsa.rdm(np.vstack([rdm, stacked_models]), metric="spearman")[0] for rdm in rdms])
        res[mask]["pval"] = np.array([rsa.rdm(np.vstack([rdm, stacked_models]), metric="spearman")[1] for rdm in rdms])
    return res


def run_rsa_dfs(rdms, models):
    result_df = rdms.iloc[:, :3].copy()
    ceils_df = rdms.iloc[:, :3].copy()
    modelnames = models.name.unique()
    for m in modelnames:
        result_df[m] = 0
        for i, r in rdms.iterrows():
            result_df.loc[i, m] = 1 - rsa.rdm(np.vstack([
                r.iloc[3:],
                models[models.name==m].iloc[:, 2:]
            ]).astype(np.float64), metric="spearman")
    result_df["upper"], result_df["lower"] = 0, 0
    for b in rdms.betatype.unique():
        for m in rdms.roi.unique():
            bounds = rsa.spearman_noise_bounds(
                rdms[(rdms.betatype==b) & (rdms.roi==m)].iloc[:, 3:].values
            )
            result_df.loc[(result_df.roi == m) & (result_df.betatype==b), "upper"] = bounds[0]
            result_df.loc[(result_df.roi == m) & (result_df.betatype==b), "lower"] = bounds[1]
    return result_df


def subject_rdms(rois, labels, masks_dict, metric="correlation", subset=None,
                 b="tstat-LSS"):
    subject_names = []
    mask_names = []
    betatypes = []
    out_rdms = []
    if "condensed" in b:
        avg = False
    else:
        avg = True

    for s in projectSettings["subjects"]:
        for m in masks_dict:
            if "subrel" in b:
                out_rdms.append(roi_rdm(rois[s][m], labels[s], metric=metric,
                                        avg=avg, subset=subset, subrel=True))
            else:
                out_rdms.append(roi_rdm(rois[s][m], labels[s], metric=metric,
                                        avg=avg, subset=subset))
            mask_names.append(m)
            subject_names.append(s)
            betatypes.append(b)
    return pd.concat(
        [pd.DataFrame({"subject": subject_names, "roi": mask_names, "betatype": betatypes}),
         pd.DataFrame(out_rdms, dtype=np.float)], axis=1
    ).infer_objects()

# def plotmodels_old(models, save=False):
#
#     stacked_models = models["stacked_models"]
#     modelnames = models["names"]
#     f = plt.figure(figsize=(30, 10))
#     axarr = f.subplots(len(stacked_models), len(modelnames))
#     for i, m in enumerate(models["names"]):
#         ticks = np.arange(0, 288, 32) - 0.5
#
#         pv.plot_rdm(stacked_models["all"][i], ax=axarr[0, i], cb=False, cmap="plasma")
#         #         axarr[i].set_axis_off()
#         axarr[0, i].set_title(m)
#         axarr[0, i].xaxis.set_major_formatter(plt.NullFormatter())
#         axarr[0, i].yaxis.set_major_formatter(plt.NullFormatter())
#         axarr[0, i].xaxis.set_tick_params(width=3)
#         axarr[0, i].yaxis.set_tick_params(width=3)
#         axarr[0, i].set_xticks(ticks)
#         axarr[0, i].set_yticks(ticks)
#         axarr[0, i].grid(which="major", color="black", linestyle="-", linewidth=3)
#
#         ticks = np.arange(0, 144, 16) - 0.5
#
#         pv.plot_rdm(stacked_models["avg"][i], ax=axarr[1, i], cb=False, cmap="plasma")
#         #         axarr[i].set_axis_off()
#         axarr[1, i].set_title(m)
#         axarr[1, i].xaxis.set_major_formatter(plt.NullFormatter())
#         axarr[1, i].yaxis.set_major_formatter(plt.NullFormatter())
#         axarr[1, i].xaxis.set_tick_params(width=3)
#         axarr[1, i].yaxis.set_tick_params(width=3)
#         axarr[1, i].set_xticks(ticks)
#         axarr[1, i].set_yticks(ticks)
#         axarr[1, i].grid(which="major", color="black", linestyle="-", linewidth=3)
#
#         ticks = np.arange(0, 72, 8) - 0.5
#
#         pv.plot_rdm(stacked_models["subrel"][i], ax=axarr[2, i], cb=False, cmap="plasma")
#         #         axarr[i].set_axis_off()
#         axarr[2, i].set_title(m)
#         axarr[2, i].xaxis.set_major_formatter(plt.NullFormatter())
#         axarr[2, i].yaxis.set_major_formatter(plt.NullFormatter())
#         axarr[2, i].xaxis.set_tick_params(width=3)
#         axarr[2, i].yaxis.set_tick_params(width=3)
#         axarr[2, i].set_xticks(ticks)
#         axarr[2, i].set_yticks(ticks)
#         axarr[2, i].grid(which="major", color="black", linestyle="-", linewidth=3)
#
#         ticks = np.arange(0, 9, 3) - 0.5
#
#         pv.plot_rdm(stacked_models["9rel"][i], ax=axarr[3, i], cb=False, cmap="plasma")
#         #         axarr[i].set_axis_off()
#         axarr[3, i].set_title(m)
#         axarr[3, i].xaxis.set_major_formatter(plt.NullFormatter())
#         axarr[3, i].yaxis.set_major_formatter(plt.NullFormatter())
#         axarr[3, i].xaxis.set_tick_params(width=3)
#         axarr[3, i].yaxis.set_tick_params(width=3)
#         axarr[3, i].set_xticks(ticks)
#         axarr[3, i].set_yticks(ticks)
#         axarr[3, i].grid(which="major", color="black", linestyle="-", linewidth=3)
#
#     if save:
#         f.savefig(os.path.join(paths["cloud"], "Figures", "models.png"))
#
#     return