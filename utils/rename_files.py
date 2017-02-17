#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Renaming a file in scans."""

import os
import sys
from dax import XnatUtils


SCAN = 'T2 Axial'
HOST = 'https://prostate-xnat.cs.ucl.ac.uk'
PROJECT = 'PICTURE'
RESOURCE = 'OsiriX'
OLD_FILE = 'mantonelli_Unnamed.rois_series'
NEW_FILE = 'Mrishta_Unnamed.rois_series'
TMP_DIR = '/Users/byvernault/data/temp_roi_upgrade/'

with XnatUtils.get_interface(host=HOST) as xnat:

    li_scans = XnatUtils.list_project_scans(xnat, PROJECT)
    li_scans = XnatUtils.filter_list_dicts_regex(li_scans, 'type', SCAN)
    li_scans = filter(lambda x: RESOURCE in x['resources'], li_scans)
    sys.stdout.write('Renaming file %s to %s for scan type %s\n'
                     % (OLD_FILE, NEW_FILE, SCAN))

    for scan in li_scans:
        sys.stdout.write(' - scan: %s / %s ...\n'
                         % (scan['session_label'], scan['ID']))
        scan_obj = XnatUtils.get_full_object(xnat, scan)
        res_obj = scan_obj.resource(RESOURCE)
        files = None
        if res_obj.exists() and OLD_FILE in res_obj.files().get()[:]:

            # fpath = XnatUtils.download_file_from_obj(TMP_DIR, res_obj,
            #                                          fname=OLD_FILE)
            # if fpath:
            #     upload = XnatUtils.upload_file_to_obj(fpath, res_obj,
            #                                           remove=True,
            #                                           fname=NEW_FILE)
            res_obj.file(OLD_FILE).delete()

    print "DONE -- See y'all"
