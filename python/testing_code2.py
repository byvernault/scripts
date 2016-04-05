"""
    TEST Script for different purpose
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Test Code"

import os

def parse_args():
    """
    Parser for arguments
    """
    from argparse import ArgumentParser
    usage = "Generates csv files from folder."
    argp = ArgumentParser(prog='testing_code', description=usage)
    argp.add_argument('-d', dest='directory',
                      help="Directory where the folders containing the data are stored.")
    return argp.parse_args()

def make_csv():
    """
        make csv
    """
    print 'patient_id,project_xnat,subject_xnat,session_xnat,folder_path'
    for labels in os.listdir(OPTIONS.directory):
        if os.path.isdir(os.path.join(OPTIONS.directory, labels)):
            las = labels.split('-')
            str_code = ''
            int_code = ''
            for c in list(las[0]):
                try:
                    _ = int(c)
                    int_code += c
                except:
                    str_code += c
            subject = '%s%s' % (str_code.upper(), int_code)
            for folder in os.listdir(os.path.abspath(os.path.join(OPTIONS.directory, labels))):
                spath = os.path.abspath(os.path.join(OPTIONS.directory, labels, folder))
                for scan_folder in os.listdir(spath):
                    print "%s%s,PICTURE,%s,,%s" % (str_code, int_code, subject, os.path.join(spath, scan_folder))

if __name__ == '__main__':
    OPTIONS = parse_args()
    make_csv()
