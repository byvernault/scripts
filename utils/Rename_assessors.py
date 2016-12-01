#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Renaming Assessors."""

import os
import sys
from dax import XnatUtils

ASSESSOR_TYPE = 'GIF_Parcellation_v1'
HOST = 'http://cmic-xnat.cs.ucl.ac.uk'
PROJECT = 'prion'
ASSESSOR = None
TMP_DIR = '/Users/byvernault/data/rename_assessors/'

if not os.path.isdir(TMP_DIR):
    os.makedirs(TMP_DIR)

try:
    xnat = XnatUtils.get_interface(host=HOST)

    if ASSESSOR:
        li_assessors = [XnatUtils.select_assessor(xnat, ASSESSOR)]
        sys.stdout.write('Renaming assessors for %s\n'
                         % (ASSESSOR))
    else:
        li_assessors = XnatUtils.list_project_assessors(xnat, PROJECT)
        sys.stdout.write('Renaming assessors for project %s\n'
                         % (PROJECT))

    for assessor in li_assessors:
        sys.stdout.write(' - assessor: %s ...\n' % assessor['label'])
        assessor_obj = XnatUtils.get_full_object(xnat, assessor)
        labels = assessor['label'].split('-x-')
        if labels[1] != assessor['subject_label']:
            new_label = '-x-'.join([
                    assessor['project_id'],
                    assessor['subject_label'],
                    assessor['session_label'],
                    labels[3],
                    labels[4]])
            sys.stdout.write('  + new label: %s \n' % new_label)
            new_assessor_obj = assessor_obj.parent().assessor(new_label)
            if new_assessor_obj.exists:
                sys.stdout.write('  + exists \n')
            else:
                sys.stdout.write('  + creating %s\n' % new_label)
                assessor.create(assessors='proc:genProcData')
                assessor_info = {
                 'proc:genProcData/procstatus': assessor['procstatus'],
                 'proc:genProcData/validation/status': assessor['qcstatus'],
                 'proc:genProcData/proctype': assessor['proctype'],
                 'proc:genProcData/jobstartdate': assessor['jobstartdate'],
                 'proc:genProcData/jobid': assessor['jobid'],
                 'proc:genProcData/date': assessor_obj.attrs.get('date')}
                assessor.attrs.mset(assessor_info)
                sys.stdout.write('  + copying %s\n' % new_label)
                for resource_name in assessor['resources']:
                    asse_dir = os.path.join(TMP_DIR, new_label, resource_name)
                    if not os.path.isdir(asse_dir):
                        os.makedirs(asse_dir)
                    if resource_name != 'SNAPSHOTS':
                        files = XnatUtils.download_files_from_obj(
                                asse_dir, assessor_obj.resource(resource_name))
                        if files:
                            newa_res = new_assessor_obj.resource(resource_name)
                            XnatUtils.upload_files_to_obj(files, newa_res)
                            for f in files:
                                os.remove(f)

    print "DONE -- See y'all"
except Exception as e:
    print 'error: %s' % e
finally:
    xnat.disconnect()
