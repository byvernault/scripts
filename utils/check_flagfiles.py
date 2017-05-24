#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Check FlagFiles for dax in result directory.
"""

from datetime import datetime
from dax import DAX_Settings
import glob
import os

DAX_SETTINGS = DAX_Settings()
RESULTS_DIR = DAX_SETTINGS.get_results_dir()
_FLAG_FILES = 'FlagFiles'

__author__ = 'byvernault'
__email__ = 'byvernault@gmail.com'
__purpose__ = "Check FlagFiles for dax in result directory."
__version__ = '1.0.0'
__modifications__ = '19 August 2015 - Original write'


def check_flagfiles():
    """Resize array to keep only 100 slices.

    :param data: numpy array of the data
    :return: new array resized [x,y,100]
    """
    for _flagfile in glob.glob(os.path.join(RESULTS_DIR, _FLAG_FILES, '*')):
        stat = os.stat(_flagfile)
        date = datetime.fromtimestamp(stat.st_mtime)
        # read pid
        print date


if __name__ == '__main__':
    print('Checking DAX Flagfiles in result direcotry.')
    print('Time: %s' % str(datetime.now()))

    check_flagfiles()
