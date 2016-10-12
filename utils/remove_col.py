"""TEST Script for different purpose."""

import os
# import re
# import glob
# import fnmatch
# import dicom
# import dicom.UID
# from dicom.dataset import Dataset, FileDataset
# import shutil
# import time
# import datetime
# import nibabel as nib
# import numpy as np
# import scipy
# import collections
from dax import XnatUtils
# import Ben_functions
import shlex

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Remove column from text file."


def parse_args():
    """Parser for arguments."""
    from argparse import ArgumentParser, RawDescriptionHelpFormatter
    argp = ArgumentParser(prog='Xnatqc', description=__purpose__,
                          formatter_class=RawDescriptionHelpFormatter)
    argp.add_argument('-d', "--directory", dest='directory', required=True,
                      help='Directory containing the files to be processed.')
    argp.add_argument('-c', '--column', dest='column', default='4',
                      help='Column number to be removed. Default: 4.')

    return argp.parse_args()


if __name__ == '__main__':
    args = parse_args()

    if not os.path.isdir(args.directory):
        raise Exception('Folder %s does not exist.' % args.directory)

    filenames = os.listdir(args.directory)
    nb_files = len(filenames)
    for ind, filename in enumerate(filenames):
        if filename.startwith('new_'):
            continue
        print 'Processing file %s - %d/%d' % (filename, ind + 1, nb_files)
        filepath = os.path.join(args.directory, filename)
        new_filepath = os.path.join(args.directory,
                                    "new_%s" % os.path.basename(filename))
        values = list()
        with open(filepath, 'r') as f:
            nb_lines = 0
            for ind, line in enumerate(f.readlines()):
                val = shlex.split(line)
                del val[int(args.column) - 1]
                values.append(val)

        nb_lines = len(values)
        nb_columns = len(values[0])

        with open(new_filepath, 'w') as outfile:
            outfile.write('%d\n' % nb_lines)
            outfile.write('%d\n' % nb_columns)
            for val in values:
                outfile.write(" ".join(val)+'\n')
