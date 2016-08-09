#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""TEST Script for different purpose."""

import pyxnat
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

if __name__ == '__main__':
    res_dir = '/Users/byvernault/RESULTS_XNAT_SPIDER/'
    xnat = XnatUtils.get_interface()
    for assessor in XnatUtils.list_project_assessors(xnat, 'PICTURE'):
        if assessor['procstatus'] == 'COMPLETE':
            print assessor['label']
            asse = XnatUtils.get_full_object(xnat, assessor)
            for resource in XnatUtils.list_assessor_out_resources(xnat, assessor['project_id'], assessor['subject_label'], assessor['session_label'], assessor['label']):
                if resource['label'].isdigit():
                    print '  - %s ' % resource['label']
                    res = asse.resource(resource['label'])
                    if res.exists():
                        res.delete()
                        print '    deleted...'
