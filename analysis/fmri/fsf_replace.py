#!/usr/bin/env python
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
encoding.py: basic encoding process
inputs: subject data, model, parameters
outputs: either matrix or writes to NIFTI
"""

#!/usr/bin/env python
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
# this script represents just throwing pymvpa at the problem. doesn't work great, and I suspect it's
# because we're using an encoding model.
"""
Wrapper for PyMVPA analysis. Implemented as a program to be able to run multiple models quickly.

For troubleshooting and parameter testing an ipynb exists too.
"""
# initialize stuff
import sys
import os

PROJECTTITLE = 'Analogy'

def replacetext(template, replacements, output):
    # replacements = {'###SUB###': sub, '###RUN###': run, ###SCAN###, scan, ###T1###: t1, ###IN###: input, ###OUTPUT###: output}
    # still need vol though...
    with open(template, 'r') as infile, open(output, 'w') as outfile:
        for line in infile:
            for src, target in replacements.iteritems():
                line = line.replace(src, target)
            outfile.write(line)
    return


def parsemapping(filename):
    # parses filemapping.txt
    import csv
    df = {}
    with open(filename, 'r') as f:
        readCSV = csv.reader(f, delimiter=',')
        for row in readCSV:
            if len(row) > 0:
                df[row[1]] = row[0]
    return df


def main(argv):
    import getopt
    fmap = 'filemapping.txt'
    template = None
    sub = None
    try:
        # figure out this line
        opts, args = getopt.getopt(argv, "h:s:t:f",
                                   ["sub=", "filename=", "project=", "write"])
    except getopt.GetoptError:
        print 'fsf_replace.py -s <subject> -f <filemapping>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'fsf_replace.py -s <subject> -f <filemapping>'
            sys.exit()
        elif opt in ("-s", "--sub"):
            sub = arg
        elif opt in ("-f", "--fmap"):
            fmap = arg
        elif opt in ("-t", "--template"):
            template = arg

    if sub is None or template is None:
        sys.exit(2)

    if sys.platform == 'darwin':
        sys.path.append(os.path.join("/Users", "njchiang", "CloudStation", "Grad", "Research",
                                     PROJECTTITLE, "code"))
    else:
        # sys.path.append(os.path.join("D:\\", "fmri", PROJECTTITLE, "code"))
        sys.path.append(os.path.join("D:\\", "CloudStation", "Grad", "Research",
                                     PROJECTTITLE, "code"))
    from analogy_code import projectutils as pu
    # need a trial_type attribute
    PATHS, _, _ = pu.initpaths()
    df = parsemapping(os.path.join(PATHS['root'], 'data', sub, 'behav', fmap))
    for run, scan in df.iteritems():
        if 'Run' in run:
            output = run + 'Match_NoMatch'
            outfile = os.path.join(PATHS['root'], 'data', sub, 'notes', output + '.fsf')
            replacements = {'###SUB###': sub, '###RUN###': run, '###SCAN###': scan,
                            '###T1###': df['T1'], '###OUTPUT###': output}
            replacetext(template, replacements, outfile)


if __name__ == "__main__":
    main(sys.argv[1:])