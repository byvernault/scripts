#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generate PDF for a spider.
"""

import os
import getpass
from dax import XnatUtils


__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = 'Generate PDF for a spider.'
__version__ = '1.0.0'
__modifications__ = '25 November 2016 - Original write'


SNAPSHOTS_ORIGINAL = 'snapshot_original.png'
SNAPSHOTS_PREVIEW = 'snapshot_preview.png'
GS_CMD = """gs -q -o {original} -sDEVICE=pngalpha -dLastPage=1 \
{pdf_path}"""
CONVERT_CMD = """convert {original} -resize x200 {preview}"""


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
    argp.add_argument('-t', '--proctype', dest='proctype', help='Proctype.',
                      default=None)
    argp.add_argument('-d', '--tmpdir', dest='tmpdir', required=True,
                      help='Path for tmp data.')
    return argp.parse_args()


def upload_snapshots(assessor_obj, original, thumbnail):
    """
    Upload snapshots to an assessor

    :param assessor_obj: pyxnat assessor Eobject
    :param resource_path: resource path on the station
    :return: None
    """
    # Remove the previous Snapshots:
    if assessor_obj.out_resource('SNAPSHOTS').exists:
        assessor_obj.out_resource('SNAPSHOTS').delete()
    status = XnatUtils.upload_assessor_snapshots(assessor_obj,
                                                 original,
                                                 thumbnail)
    if status:
        os.remove(original)
        os.remove(thumbnail)
    else:
        print('No snapshots original or preview were uploaded')


def generate_snapshots(assessor_obj, assessor, tmpdir):
    """ Generating the PDF from the outputs and spider code."""
    tmpdir = XnatUtils.makedir(tmpdir)
    jobsdir = os.path.join(tmpdir, assessor['label'])
    if not os.path.exists(jobsdir):
        os.makedirs(jobsdir)

    # Download the outputs form XNAT:
    outputs_dir = os.path.join(jobsdir, 'outputs')
    if not os.path.exists(outputs_dir):
        os.makedirs(outputs_dir)
    pdf_file = XnatUtils.download_file_from_obj(
                    outputs_dir, assessor_obj.resource('PDF'))
    snapshot_original = os.path.join(outputs_dir, SNAPSHOTS_ORIGINAL)
    snapshot_preview = os.path.join(outputs_dir, SNAPSHOTS_PREVIEW)
    print('    +creating original of SNAPSHOTS')
    # Make the snapshots for the assessors with ghostscript
    cmd = GS_CMD.format(original=snapshot_original,
                        pdf_path=pdf_file)
    os.system(cmd)
    # Create the preview snapshot from the original if Snapshots exist :
    if os.path.exists(snapshot_original):
        print('    +creating preview of SNAPSHOTS')
        # Make the snapshot_thumbnail
        cmd = CONVERT_CMD.format(original=snapshot_original,
                                 preview=snapshot_preview)
        os.system(cmd)
    return snapshot_original, snapshot_preview


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

        print 'INFO: connection to xnat <%s>:' % (HOST)
        XNAT = XnatUtils.get_interface(host=ARGS.host, user=ARGS.username,
                                       pwd=PWD)
        li_assessors = XnatUtils.list_project_assessors(XNAT, ARGS.project)
        if ARGS.proctype:
            li_assessors = XnatUtils.filter_list_dicts_regex(
                            li_assessors, 'proctype', ARGS.proctype.split(','))
        li_assessors = XnatUtils.filter_list_dicts_regex(
                            li_assessors, 'procstatus', ['COMPLETE'])
        li_assessors = sorted(li_assessors, key=lambda k: k['session_label'])
        for assessor in li_assessors:
            print 'Assessor: %s' % assessor['label']
            assessor_obj = XnatUtils.get_full_object(XNAT, assessor)
            original, preview = generate_snapshots(assessor_obj,
                                                   assessor,
                                                   ARGS.tmpdir)
            upload_snapshots(assessor_obj, original, preview)
    finally:
        XNAT.disconnect()
