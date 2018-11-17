"""
This program writes the LSS regressors for the Analogy project.
Example call:
module load python/3.6.1
python3 setup-lss.py sub-01 run-01
Output will be in derivatives/misc/regressors/LSS
"""
import os
import pandas as pd
import argparse
ROOT = "/u/project/monti/Analysis/Analogy"


# write an AB/CD/Probe regressors (main effects)
def writeABCDtxt(sub, run, fulldata):
    output_files = {"AB": os.path.join(ROOT, "derivatives", sub,
                                       "misc", "regressors",
                                       "{}_{}_AB.txt".format(sub, run)),
                    "CD": os.path.join(ROOT, "derivatives", sub,
                                       "misc", "regressors",
                                       "{}_{}_CD.txt".format(sub, run)),
                    "Probe": os.path.join(ROOT, "derivatives", sub,
                                          "misc", "regressors",
                                          "{}_{}_Probe.txt".format(sub, run))}
    ABdf = fulldata[fulldata["AB"] == 1][["Onset", "Duration", "Intensity"]]
    ABdf.to_csv(path_or_buf=output_files["AB"],
                sep=" ", index=False, header=False)
    CDdf = fulldata[fulldata["CD"] == 1][["Onset", "Duration", "Intensity"]]
    CDdf.to_csv(path_or_buf=output_files["CD"],
                sep=" ", index=False, header=False)

    Pdf = fulldata[fulldata["Probe"] == 1][["Onset", "Duration", "Intensity"]]
    Pdf.to_csv(path_or_buf=output_files["Probe"],
               sep=" ", index=False, header=False)
    return output_files


def replacetext(template, replacements, output):
    with open(template, 'r') as infile, open(output, 'w') as outfile:
        for line in infile:
            for src, target in replacements.items():
                line = line.replace(src, target)
            outfile.write(line)
    return


def write_lss(sub, run, vol, files=None):
    if files is None:
        files = {"AB": "{}_{}_AB.txt".format(sub, run),
                 "CD": "{}_{}_CD.txt".format(sub, run),
                 "Probe": "{}_{}_Probe.txt".format(sub, run)}

    for k, f in files.items():
        df = pd.read_csv(f, sep=" ", header=None)
        with open(os.path.join(ROOT, "derivatives", sub, "betas",
                               "{}_{}_LSS-list.txt".format(sub, run)), "w") as o:
            for i in range(len(df)):
                # beta of interest
                df[i:i+1].to_csv(os.path.join(ROOT, "derivatives", sub,
                                              "misc", "regressors", "LSS",
                                              "{}_{}_trial-{}_{}.txt"
                                              .format(sub, run, i+1, k)),
                                 sep=" ", index=False, header=False)
                # nuisance for condition
                nuisance = pd.concat([df[0:i], df[i+1:]]).reset_index(drop=True)
                nuisance.to_csv(os.path.join(ROOT, "derivatives", sub,
                                             "misc", "regressors", "LSS",
                                             "{}_{}_nuisance-{}_{}.txt"
                                             .format(sub, run, i+1, k)),
                                sep=" ", index=False, header=False)
                replacements = {"###SUB###": sub, "###RUN###": run, "###TRIAL###": str(i+1), "###VOL###": str(vol)}
                replacetext(os.path.join(ROOT, "derivatives", "standard", "templates",
                                         "LSS-template-AB.fsf"),
                            replacements,
                            os.path.join(ROOT, "derivatives", sub, "betas", "LSS",
                                         "{}_task-analogy_{}_LSS-AB-{}.fsf".format(sub, run, i+1)))
                o.write(os.path.join(ROOT, "derivatives", sub, "betas", "LSS",
                                     "{}_task-analogy_{}_LSS-AB-{}.fsf\n".format(sub, run, i+1)))
                replacetext(os.path.join(ROOT, "derivatives", "standard", "templates",
                                         "LSS-template-CD.fsf"),
                            replacements,
                            os.path.join(ROOT, "derivatives", sub, "betas", "LSS",
                                         "{}_task-analogy_{}_LSS-CD-{}.fsf".format(sub, run, i+1)))
                o.write(os.path.join(ROOT, "derivatives", sub, "betas", "LSS",
                                     "{}_task-analogy_{}_LSS-CD-{}.fsf\n".format(sub, run, i+1)))
                replacetext(os.path.join(ROOT, "derivatives", "standard", "templates",
                                         "LSS-template-Probe.fsf"),
                            replacements,
                            os.path.join(ROOT, "derivatives", sub, "betas", "LSS",
                                         "{}_task-analogy_{}_LSS-Probe-{}.fsf".format(sub, run, i+1)))
                o.write(os.path.join(ROOT, "derivatives", sub, "betas", "LSS",
                                     "{}_task-analogy_{}_LSS-Probe-{}.fsf\n".format(sub, run, i+1)))
    return


def main(sub, run, vol):
    fulldata = pd.read_csv(
        os.path.join(ROOT, "derivatives", sub, "func",
                     "{}_task-analogy_{}_events.tsv".format(sub, run)),
        sep="\t")

    files = writeABCDtxt(sub, run, fulldata)
    write_lss(sub, run, vol, files)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("sub", help="subject: e.g. sub-01")
    p.add_argument("run", help="run number: e.g. run-01")
    p.add_argument("vol", help="volumes: e.g. 288")
    args = p.parse_args()
    main(args.sub, args.run, args.vol)
