#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generate PDF for a spider.
"""

import os
import shutil
import getpass
from dax import XnatUtils


__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = 'Run seg_maths on GIF to generate WHOLEBRAIN mask.'
__version__ = '1.0.0'
__modifications__ = '30 November 2016 - Original write'

BM_ARRAY = [0, 1, 2, 3, 4, 5, 12, 16, 47, 50, 51, 52, 53]


def parse_args():
    """ Parser for arguments """
    from argparse import ArgumentParser
    argp = ArgumentParser(prog='run_b_masking_whole.py',
                          description=__purpose__)
    argp.add_argument('--host', dest='host', default=None,
                      help='Host for XNAT. Default: using $XNAT_HOST.')
    argp.add_argument('-u', '--username', dest='username', default=None,
                      help='Username for XNAT. Default: using $XNAT_USER.')
    argp.add_argument('-p', '--project', dest='project', required=True,
                      help='XNAT project ID')
    argp.add_argument('-s', '--sess', dest='session', default=None,
                      help='Session name.')
    argp.add_argument('-d', '--tmpdir', dest='tmpdir', required=True,
                      help='Path for tmp data.')
    argp.add_argument('-e', '--exe', dest='seg_maths_exe', default="seg_maths",
                      help='Executable for seg_maths.')
    return argp.parse_args()


def generate_bmask_whole(assessor_obj, assessor, tmpdir):
    """ Generating the bmask whole from the assessor outputs."""
    jobsdir = os.path.join(tmpdir, assessor['label'])
    if not os.path.exists(jobsdir):
        os.makedirs(jobsdir)
    else:
        shutil.rmtree(jobsdir)
        os.makedirs(jobsdir)

    files = XnatUtils.download_files_from_obj(jobsdir,
                                              assessor_obj.resource('LABELS'))
    if len(files) != 1:
        raise Exception('Too many niftis downloaded.')
    else:
        input_nii = files[0]
    tiv_files = XnatUtils.download_files_from_obj(jobsdir,
                                                  assessor_obj.resource('TIV'))

    basepath = os.path.dirname(input_nii)
    basename = os.path.basename(input_nii[:-7])
    final_seg_mats_sub_cmd = os.path.join(
                    basepath, "%s_ArtConstruction_0.nii.gz " % basename)
    for index, value in enumerate(BM_ARRAY):
        output_nii = os.path.join(
                basepath, "%s_ArtConstruction_%d.nii.gz " % (basename, index))
        val_min = float(value - 0.5)
        val_max = float(value + 0.5)
        cmd = '%s %s -thr %f -uthr %f -bin %s' % (ARGS.seg_maths_exe,
                                                  input_nii, val_min, val_max,
                                                  output_nii)
        print cmd
        os.system(cmd)
        final_seg_mats_sub_cmd += "-add %s " % output_nii

    # Seg maths add
    to_remove_nii = "%s_ToRemove.nii.gz" % basepath
    cmd = '%s %s -bin %s' % (ARGS.seg_maths_exe, final_seg_mats_sub_cmd,
                             to_remove_nii)
    print cmd
    os.system(cmd)
    # Seg maths remove
    final_brain = "%s_FinalBrain.nii.gz" % basepath
    cmd = '%s %s -sub %s -bin %s' % (ARGS.seg_maths_exe,
                                     ' '.join(tiv_files),
                                     to_remove_nii,
                                     final_brain)
    print cmd
    os.system(cmd)
    return final_brain


if __name__ == '__main__':
    ARGS = parse_args()
    try:
        if ARGS.host:
            HOST = ARGS.host
        else:
            HOST = os.environ['XNAT_HOST']
        if ARGS.username:
            MSG = ("Please provide the password for user <%s> on xnat(%s):"
                   % (ARGS.username, HOST))
            PWD = getpass.getpass(prompt=MSG)
        else:
            PWD = None

        if not os.path.isdir(ARGS.tmpdir):
            os.makedirs(ARGS.tmpdir)
        print 'INFO: connection to xnat <%s>:' % (HOST)
        XNAT = XnatUtils.get_interface(host=ARGS.host, user=ARGS.username,
                                       pwd=PWD)
        li_assessors = XnatUtils.list_project_assessors(XNAT, ARGS.project)
        li_assessors = XnatUtils.filter_list_dicts_regex(
                                li_assessors, 'proctype',
                                ['GIF_Parcellation_v2'])
        li_assessors = XnatUtils.filter_list_dicts_regex(
                                li_assessors, 'procstatus',
                                ['COMPLETE'])
        li_assessors = filter(lambda x: 'WHOLEBRAIN' not in x['resources'],
                              li_assessors)
        li_assessors = sorted(li_assessors, key=lambda k: k['session_label'])
        start = False
        for assessor in li_assessors:
            if ARGS.session:
                if assessor['session_label'] == ARGS.session:
                    start = True
            else:
                start = True
            if start:
                print '\n<-- Assessor: %s -->' % assessor['label']
                assessor_obj = XnatUtils.get_full_object(XNAT, assessor)
                brain = generate_bmask_whole(assessor_obj, assessor,
                                             ARGS.tmpdir)
                XnatUtils.upload_file_to_obj(
                    brain, assessor_obj.resource('WHOLEBRAIN'), removeall=True)

            raw_input()
    finally:
        XNAT.disconnect()
