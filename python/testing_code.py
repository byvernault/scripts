"""TEST Script for different purpose."""

import os
import re
# import glob
import fnmatch
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

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Test Code"


def filter_list_dicts_regex(list_dicts, key, expressions, nor=False,
                            full_regex=False):
    """Filter the list of dictionary from XnatUtils.list_* using the regex.

    :param list_dicts: list of dictionaries to filter
    :param key: key from dictionary to filter using regex
    :param expressions: list of regex expressions to use (OR)
    :return: list of items from the list_dicts that match the regex
    """
    flist = list()
    if nor:
        flist = list_dicts
    for exp in expressions:
        if not full_regex:
            exp = fnmatch.translate(exp)
        regex = re.compile(exp)
        if nor:
            flist = [d for d in flist if not regex.match(d[key])]
        else:
            flist.extend([d for d in list_dicts
                          if regex.match(d[key])])
    return flist

if __name__ == '__main__':
    host = 'http://cmic-xnat.cs.ucl.ac.uk'
    user = os.environ['XNAT_USER']
    pwd = os.environ['XNAT_PASS']

    xnat = XnatUtils.get_interface(host=host, user=user, pwd=pwd)

    li_scans = XnatUtils.list_project_scans(xnat, projectid='DIAN')

    fr = False

    print 'List of types:'
    types = list(set([l.get('type') for l in li_scans]))
    print types
    print len(types)

    exps = ['MPRAGE*', 'resting*fMRI']
    print 'Test 1 with: ' + str(exps)
    li_sc = filter_list_dicts_regex(li_scans, 'type', exps, full_regex=fr)
    types = list(set([l.get('type') for l in li_sc]))
    print types
    print len(types)

    if fr:
        print 'test 2 and 3 will not work because there are nohting before the *'
    else:
        exps = ['*fMRI*']
        print 'Test 2 with: ' + str(exps)
        li_sc = filter_list_dicts_regex(li_scans, 'type', exps)
        types = list(set([l.get('type') for l in li_sc]))
        print types
        print len(types)

        exps = ['*']
        print 'Test 3 with: ' + str(exps)
        li_sc = filter_list_dicts_regex(li_scans, 'type', exps)
        types = list(set([l.get('type') for l in li_sc]))
        print types
        print len(types)

    exps = ['resting.*fMRI']
    print 'Test 3 with: ' + str(exps)
    li_sc = filter_list_dicts_regex(li_scans, 'type', exps, full_regex=fr)
    types = list(set([l.get('type') for l in li_sc]))
    print types
    print len(types)
