"""
    Testing random line of code
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "testing purpose"
__version__ = '1.0.0'
__modifications__ = '11 October 2015 - Original write'

import os
import sys
import json
import glob
import shutil
from dax import XnatUtils

def parse_args():
    """
    Parser for arguments
    """
    from argparse import ArgumentParser
    usage = "Generates bvals/bvecs from json files."
    argp = ArgumentParser(prog='read bvals/bvecs from json', description=usage)
    argp.add_argument('-d', dest='directory',
                      help="Directory where the json files are stored.",
                      required=True)
    return argp.parse_args()

def edit_session_date():
    xnat = XnatUtils.get_interface()

    for session in XnatUtils.list_sessions(xnat, 'prion'):
        date = session['label'].split('_')[1]
        date = date[:4]+'-'+date[4:6]+'-'+date[6:]
        print date
        session_obj = XnatUtils.get_full_object(xnat, session)
        session_obj.attrs.set('date', date)
        #print session
    xnat.disconnect()

def get_T2_scanID(xnat, subject, session):
    scanIDs = list()
    scans_list = XnatUtils.list_scans(xnat, 'PICTURE', subject, session):
    return scanIDs

def organise_folder(xnat, fpath):
    """
        Organize the folder to then generate 4D nifti for the file that need it

        :param fpath: folder path containing the nifti
        :return list(): return list of folder to convert niftis from
    """
    old_scan_name = None
    for niftis in glob.glob(os.path.join(fpath, "*.nii")):
        [session, scan_name, scan_type] = os.path.basename(niftis).split("-")[0:3]
        subject = session.split('_')[0]
        if old_scan_name != scan_name:
            scan_path = os.path.join(fpath, '__'.join([subject, session, scan_name, scan_type]))
            if not os.path.exists(scan_path):
                os.makedirs(scan_path)
            nifti_list.append(scan_path)
            shutil.copy(niftis, scan_path)
            old_scan_name = scan_name
        elif old_scan_name == scan_name:
            shutil.copy(niftis, scan_path)

if __name__ == '__main__':
    try:
        xnat = XnatUtils.get_interface()
        directory = '/Users/byvernault/Downloads/Archive/'
        for filename in os.listdir(directory):
            fpath = os.path.join(directory, filename)
            if os.path.isfile(fpath):
                organise_folder(xnat, fpath)
    finally:
        xnat.disconnect()
