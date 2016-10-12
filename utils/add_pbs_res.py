#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Adding PBS resource to assessor on XNAT when missing.
"""

import os
import getpass
from dax import XnatUtils

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = 'Adding PBS resource to assessor on XNAT when missing.'
__version__ = '1.0.0'
__modifications__ = '11 February 2016 - Original write'


def parse_args():
    """ Parser for arguments """
    from argparse import ArgumentParser
    argp = ArgumentParser(prog='add_pbs_res.py', description=__purpose__)
    argp.add_argument('--host', dest='host', default=None,
                      help='Host for XNAT. Default: using $XNAT_HOST.')
    argp.add_argument('-u', '--username', dest='username', default=None,
                      help='Username for XNAT. Default: using $XNAT_USER.')
    argp.add_argument('-p', '--project', dest='project', required=True,
                      help='XNAT project ID')
    argp.add_argument('-t', '--proctype', dest='proctype', required=True,
                      help='XNAT Proctype to add PBS resource.')
    return argp.parse_args()


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
        li_assessors = XnatUtils.filter_list_dicts_regex(
                                li_assessors, 'proctype',
                                ARGS.proctype.split(','))
        li_assessors = XnatUtils.filter_list_dicts_regex(
                                li_assessors, 'procstatus',
                                ['COMPLETE'])
        li_assessors = sorted(li_assessors, key=lambda k: k['session_label'])
        for assessor in li_assessors:
            assessor_obj = XnatUtils.get_full_object(XNAT, assessor)
            if not assessor_obj.resource('PBS').exists():
                assessor_obj.resource('PBS').create()
                print 'Resource PBS added to %s.' % assessor['label']

    finally:
        XNAT.disconnect()
