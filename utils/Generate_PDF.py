#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generate PDF for a spider.
"""

import os
import re
import glob
import shutil
import getpass
from dax import XnatUtils
from Spider_GIF_Parcellation_v2_0_0 import Spider_GIF_Parcellation
# from Spider_GIF_Parcellation_v1_0_0 import Spider_GIF_Parcellation


__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = 'Generate PDF for a spider.'
__version__ = '1.0.0'
__modifications__ = '25 November 2016 - Original write'

STATS_EXT = '*.xml'
# STATS_EXT = '*.csv'

RESOURCES = [
    'BIAS_COR',
    'BRAIN',
    'LABELS',
    'PRIOR',
    'SEG',
    'TIV',
    'STATS'
]

labels = {
    '0': 'Bias Corrected',
    '1': 'Brain',
    '2': 'Labels',
    '3': 'Segmentation',
    '4': 'tiv',
    '5': 'prior'
}
cmap = {
    '0': 'gray',
    '1': 'gray',
    '2': None,
    '3': 'gray',
    '4': 'gray',
    '5': None
}


def parse_args():
    """ Parser for arguments """
    from argparse import ArgumentParser
    argp = ArgumentParser(prog='Generate_PDF.py', description=__purpose__)
    argp.add_argument('--host', dest='host', default=None,
                      help='Host for XNAT. Default: using $XNAT_HOST.')
    argp.add_argument('-u', '--username', dest='username', default=None,
                      help='Username for XNAT. Default: using $XNAT_USER.')
    argp.add_argument('-p', '--project', dest='project', required=True,
                      help='XNAT project ID')
    argp.add_argument('-s', '--spider', dest='spider_path', required=True,
                      help='Path to spider.')
    argp.add_argument('-d', '--tmpdir', dest='tmpdir', required=True,
                      help='Path for tmp data.')
    argp.add_argument('-se', '--sess', dest='session', default=None,
                      help='Last session to start from.')
    return argp.parse_args()


def generate_pdf(spider_path, assessor_obj, assessor, tmpdir):
    """ Generating the PDF from the outputs and spider code."""
    jobsdir = os.path.join(tmpdir, assessor['label'])
    if not os.path.exists(jobsdir):
        os.makedirs(jobsdir)
    else:
        shutil.rmtree(jobsdir)
        os.makedirs(jobsdir)
    spider = Spider_GIF_Parcellation(spider_path=spider_path,
                                     jobdir=jobsdir,
                                     xnat_project=assessor['project_id'],
                                     xnat_subject=assessor['subject_label'],
                                     xnat_session=assessor['session_label'],
                                     xnat_scan=None,
                                     xnat_host=None,
                                     xnat_user=None,
                                     xnat_pass=None,
                                     number_core='',
                                     suffix='')

    # Download the outputs form XNAT:
    outputs_dir = os.path.join(jobsdir, 'outputs')
    if not os.path.exists(outputs_dir):
        os.makedirs(outputs_dir)
    for resource in RESOURCES:
        XnatUtils.download_files_from_obj(
                    outputs_dir, assessor_obj.resource(resource))
    # move niftis to outputs folder:
    niftis = glob.glob(os.path.join(outputs_dir, '*', '*.nii.gz'))
    stats = glob.glob(os.path.join(outputs_dir, '*', STATS_EXT))
    for nifti in niftis+stats:
        shutil.move(nifti, outputs_dir)
    spider.make_pdf()

    return spider.pdf_final

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

        script_name = ARGS.spider_path
        if len(script_name.split('/')) > 1:
            script_name = os.path.basename(script_name)
        if script_name.endswith('.py'):
            script_name = script_name[:-3]
        if 'Spider' in script_name:
            script_name = script_name[7:]
        version = script_name.split('_v')[-1].replace('_', '.')
        proctype = re.split("/*_v[0-9]/*",
                            script_name)[0]+'_v'+version.split('.')[0]

        if not os.path.isdir(ARGS.tmpdir):
            os.makedirs(ARGS.tmpdir)
        print 'INFO: connection to xnat <%s>:' % (HOST)
        XNAT = XnatUtils.get_interface(host=ARGS.host, user=ARGS.username,
                                       pwd=PWD)
        li_assessors = XnatUtils.list_project_assessors(XNAT, ARGS.project)
        li_assessors = XnatUtils.filter_list_dicts_regex(
                                li_assessors, 'proctype', [proctype])
        li_assessors = XnatUtils.filter_list_dicts_regex(
                                li_assessors, 'procstatus',
                                ['COMPLETE'])
        li_assessors = sorted(li_assessors, key=lambda k: k['session_label'])
        start = False
        for assessor in li_assessors:
            if ARGS.session:
                if assessor['session_label'] == ARGS.session:
                    start = True
            else:
                start = True
            if start:
                print 'Assessor: %s' % assessor['label']
                assessor_obj = XnatUtils.get_full_object(XNAT, assessor)
                pdf = generate_pdf(ARGS.spider_path, assessor_obj, assessor,
                                   ARGS.tmpdir)
                XnatUtils.upload_file_to_obj(pdf, assessor_obj.resource('PDF'),
                                             removeall=True)
    finally:
        XNAT.disconnect()
