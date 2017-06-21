"""TEST Script for different purpose."""

import os
# import re
import glob
# import fnmatch
import dicom
import re
# import shutil
# import time
import datetime
import nibabel as nib
import numpy as np
# import scipy
# import collections
from dax import XnatUtils
# import shlex


__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'


def write_files(nii_file, bval):
    basedir = os.path.dirname(nii_file)
    basename = os.path.basename(nii_file).split('.')[0]
    bval_file = os.path.join(basedir, '{}.bval'.format(basename))
    bvec_file = os.path.join(basedir, '{}.bvec'.format(basename))
    with open(bval_file, 'w') as _bval:
        _bval.write(' '.join(bval))
    with open(bvec_file, 'w') as _bvec:
        _bvec.write(' '.join(bval) + '\n')
        _bvec.write(' '.join(bval) + '\n')
        _bvec.write(' '.join(bval))
    return bval_file, bvec_file


if __name__ == "__main__":
    project = 'prion'
    types = ['ep2d_diff_MDDW_p2FAD_2.5mm_iso_B0', 'ep2d_diff_MDDW_p2FAD_2.5mm_iso_B0-diffusion']
    directory = '/Users/byvernault/data/b0sedit'
    with XnatUtils.get_interface(host=os.environ['DPUK']) as xnat:
        scans = XnatUtils.list_project_scans(xnat, project)
        scans = XnatUtils.filter_list_dicts_regex(scans, 'type', types)
        for scan in sorted(scans, key=lambda k: k['session_label']):
            if 'BVAL' not in scan['resources'] or \
               'BVEC' not in scan['resources']:
                tp_dir = os.path.join(directory, scan['session_label'],
                                      scan['ID'])
                if not os.path.exists(tp_dir):
                    os.makedirs(tp_dir)
                scan_obj = XnatUtils.get_full_object(xnat, scan)
                bval_obj = scan_obj.resource('BVAL')
                bvec_obj = scan_obj.resource('BVEC')
                res_obj = scan_obj.resource('NIFTI')
                nii_file = XnatUtils.download_file_from_obj(tp_dir, res_obj)
                nii = nib.load(nii_file)
                nb_val = int(nii.header.get_data_shape()[-1])
                print('Number of volumes for {}/{}: {}'.format(
                    scan['session_label'], scan['ID'], str(nb_val)))
                bval = ['0'] * nb_val
                bvals, bvecs = write_files(nii_file, bval)
                XnatUtils.upload_file_to_obj(bvals, bval_obj)
                XnatUtils.upload_file_to_obj(bvecs, bvec_obj)
                print('-- uploaded to {}/{}.'.format(
                    scan['session_label'], scan['ID']))
