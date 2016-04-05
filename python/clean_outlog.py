#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Author:         Benjamin Yvernault
    contact:        b.yvernault@ucl.ac.uk
    Purpose:        Clean OUTLOG that are empty
'''

__author__ = "Benjamin Yvernault"
__email__ = "b.yvernault@ucl.ac.uk"
__purpose__ = "Clean OUTLOG that are empty"

import os
import glob
from dax import RESULTS_DIR

for fpath in glob.glob(os.path.join(RESULTS_DIR, 'OUTLOG', '*.output')):
    if os.path.isfile(fpath) and os.path.getsize(fpath) == 0:
        print 'delete file %s ' % (fpath)
