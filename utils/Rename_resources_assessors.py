#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Renaming a resource for Assessors."""

import os
import sys
from dax import XnatUtils


ASSESSOR_TYPE = 'GIF_Parcellation_v1'
HOST = 'http://cmic-xnat.cs.ucl.ac.uk'
PROJECT = 'Prisma_upgrade'
OLD_RESOURCE = 'VOLUME'
NEW_RESOURCE = 'STATS'
ASSESSOR = None
TMP_DIR = '/Users/byvernault/data/tempGIF/'

try:
    xnat = XnatUtils.get_interface(host=HOST)

    if ASSESSOR:
        li_assessors = [XnatUtils.select_assessor(xnat, ASSESSOR)]
        sys.stdout.write('Renaming resources %s to %s for assessor %s'
                         % (OLD_RESOURCE, NEW_RESOURCE, ASSESSOR))
    else:
        li_assessors = XnatUtils.list_project_assessors(xnat, PROJECT)
        sys.stdout.write('Renaming resources %s to %s for assessor type %s\n'
                         % (OLD_RESOURCE, NEW_RESOURCE, ASSESSOR_TYPE))

    for assessor in li_assessors:
        sys.stdout.write(' - assessor: %s ...\n' % assessor['label'])
        assessors = XnatUtils.get_full_object(xnat, assessor)
        old_res = assessors.resource(OLD_RESOURCE)
        files = None
        if old_res.exists():
            files = XnatUtils.download_files_from_obj(TMP_DIR, old_res)
            if files:
                new_res = assessors.resource(NEW_RESOURCE)
                XnatUtils.upload_files_to_obj(files, new_res)
                if new_res.exists():
                    old_res.delete()
                    sys.stdout.write('   renamed.\n')
                for f in files:
                    os.remove(f)

    print "DONE -- See y'all"
except Exception as e:
    print 'error: %s' % e
finally:
    xnat.disconnect()
