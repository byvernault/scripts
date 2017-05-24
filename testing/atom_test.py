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


site = 'austin'
site_nb = '01'


def check_folder(folder, pid=1):
    _p = os.path.join(folder, str(pid))
    if os.path.exists(_p):
        pid += 1
        _p = check_folder(folder, pid)

    return _p


if __name__ == '__main__':
    temp_dir = '/Users/byvernault/Documents/PROPS_data'
    new_dir = '/Users/byvernault/data/PROPS_upload'

    paths = glob.glob(os.path.join(temp_dir, '*', '*Austin*'))
    for folder in paths:
        for patient in os.listdir(folder):
            _p = os.path.join(folder, patient)
            if os.path.isdir(_p):
                new_patient = patient.replace('-', '')\
                                     .replace('_', '')\
                                     .replace(' ', '')
                _dir = os.path.join(new_dir, new_patient)
                if not os.path.exists(new_dir):
                    os.makedirs(new_dir)
                _newp = check_folder(_dir)
                # os.makedirs(_newp)
                # copy:
                print 'Copying %s to %s' % (_p, _newp)
                shutil.copytree(_p, _newp)
