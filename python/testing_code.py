"""TEST Script for different purpose."""

import os
# import re
# import glob
# import fnmatch
import dicom
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
# import shlex

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Set the scna types from DICOM header."


TYPES = ['WIP b3000_80 SENSE', 'WIP b2000_vx1.3 SENSE',
         'WIP b1500_vx1.3 SENSE', 'WIP b500_vx1.3 SENSE',
         'WIP b90_vx1.3 SENSE']


def parse_args():
    """Parser for arguments."""
    from argparse import ArgumentParser, RawDescriptionHelpFormatter
    argp = ArgumentParser(prog='Set_types_from_dicom', description=__purpose__,
                          formatter_class=RawDescriptionHelpFormatter)
    argp.add_argument('-p', "--project", dest='project', required=True,
                      help='Project ID on XNAT.')
    argp.add_argument('-s', '--session', dest='sessions', required=True,
                      help='Sessions label on XNAT.')

    return argp.parse_args()


if __name__ == '__main__':
    args = parse_args()

    # Scans on XNAT:
    try:
        xnat = XnatUtils.get_interface()
        li_scans = XnatUtils.list_project_scans(xnat, args.project)
        li_scans = XnatUtils.filter_list_dicts_regex(li_scans, 'session_label',
                                                     args.sessions.split(','))
        li_scans = sorted(li_scans, key=lambda k: k['session_label'])
        for scan_d in li_scans:
            # If type is unknown or empty, run:
            if scan_d['type'] in TYPES:
                print (" - setting type for %s/%s"
                       % (scan_d['session_label'], scan_d['ID']))
                scan_obj = XnatUtils.get_full_object(xnat, scan_d)
                new_type = scan_d['type'].split(' SENSE')[0].split('WIP ')[1].strip()
                scan_obj.attrs.set('type', new_type)

    finally:
        xnat.disconnect()
