#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""TEST Script for different purpose."""

import pyxnat
import shutil
import os
import glob
import sys
import time
import dicom
import csv
import datetime
import numpy as np
import nibabel as nib
import subprocess as sb
import matplotlib.pyplot as plt
from dicom.dataset import Dataset, FileDataset
# import Ben_functions
from dax import XnatUtils

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Test Code"
FILES = ['Mrishta_Unnamed.rois_series',
         'rmhaohn_Unnamed.rois_series',
         'ROI_2015.rois_series']


def check_files(files):
    if len(files) != len(FILES):
        return False

    for val in files:
        if val not in FILES:
            return False

    return True


if __name__ == '__main__':
    res_dir = '/Users/byvernault/data/tmp_rois/'
    project = 'PICTURE'
    XNAT = XnatUtils.get_interface()
    li_t2 = XnatUtils.list_project_scans(XNAT, project)
    li_t2 = XnatUtils.filter_list_dicts_regex(li_t2, 'type', ['T2 Axial'])

    for scan in li_t2:
        if 'OsiriX' in scan['resources']:
            scan_obj = XnatUtils.get_full_object(XNAT, scan)
            files = scan_obj.resource('OsiriX').files()
            list_files = files.get()
            if not check_files(list_files):
                print ('Session %s does not have the files required: %s'
                       % (scan['session_label'], list_files))
            
            # f_obj.delete()
            # print ('ROI.rois_series deleted for %s / %s'
            #        % (scan['session_label'], scan['ID']))

            """
            ndir = os.path.join(res_dir, scan['session_label'], scan['ID'])
            if not os.path.exists(ndir):
                os.makedirs(ndir)
                scan_obj = XnatUtils.get_full_object(XNAT, scan)
                f_obj = scan_obj.resource('OsiriX').file('ROI.rois_series')
                if f_obj.exists():
                    fpath = XnatUtils.download_file_from_obj(
                                ndir, scan_obj.resource('OsiriX'),
                                fname='ROI.rois_series')
                    XnatUtils.upload_file_to_obj(
                            fpath, scan_obj.resource('OsiriX'),
                            fname='ROI_2015.rois_series', remove=True)
                    print 'reuploaded for %s / %s' % (scan['session_label'],
                                                      scan['ID'])"""
