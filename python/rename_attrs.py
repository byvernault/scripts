"""
    Renaming attrs for xnat object
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Renaming attrs for xnat object"
__version__ = '1.0.0'
__modifications__ = '11 September 2015 - Original write'

import os
import re
import glob
import subprocess as sb
from datetime import datetime
from dax import XnatUtils

if __name__ == '__main__':
