#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob

"""
list_files = glob.glob(os.path.join('/Users/byvernault/DATA/PRION_CMIC', 'a*/*-ep2d_diff_MDDW_p2FAD_2*B0*.nii'))
list_files = list(set([files.split('B0')[0] for files in list_files]))

for fpath in list_files:
    old_nii = glob.glob(fpath+'*.nii.gz')[0]
    if not 'B0' in old_nii:
        nii = glob.glob(fpath+'*.nii')[0]
        if 'diffusion' in nii:
            new_nii = '%sB0-diffusion_%s' % (fpath, old_nii.split(fpath)[1])
        else:
            new_nii = '%sB0_%s' % (fpath, old_nii.split(fpath)[1])
        print old_nii, new_nii
        os.rename(old_nii, new_nii)
"""

list_files = glob.glob(os.path.join('/Users/byvernault/DATA/PRION_CMIC', 'a*/*-ep2d_diff_MDDW_p2FAD_2.5mm_iso-diffusion*.nii'))
list_files = list(set([files.split('-diffusion')[0] for files in list_files if 'diffusion' in files]))
for fpath in list_files:
    old_nii = glob.glob(fpath+'*.nii.gz')[0]
    if not 'diffusion' in old_nii:
        new_nii = '%s-diffusion%s' % (fpath, old_nii.split(fpath)[1])
        print old_nii, new_nii
        os.rename(old_nii, new_nii)
