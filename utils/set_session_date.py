#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setting the date of a session from the session label (after "_")
"""

import os
import getpass
from dax import XnatUtils


__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = 'Setting the date of a session from the session label \
(after "_")'
__version__ = '1.0.0'
__modifications__ = '11 February 2016 - Original write'


def parse_args():
    """ Parser for arguments """
    from argparse import ArgumentParser
    argp = ArgumentParser(prog='set_session_date', description=__purpose__)
    argp.add_argument('--host', dest='host', default=None,
                      help='Host for XNAT. Default: using $XNAT_HOST.')
    argp.add_argument('-u', '--username', dest='username', default=None,
                      help='Username for XNAT. Default: using $XNAT_USER.')
    argp.add_argument('-p', '--project', dest='project', required=True,
                      help='XNAT project ID')
    return argp.parse_args()


def edit_session_date(xnat, session_info):
    date = session_info['label'].split('_')[-1]
    date = '{}-{}-{}'.format(date[:4], date[4:6], date[6:])
    print("%s - %s" % (session_info['label'], date))
    if session_info['date'] == date:
        print ' already set up.'
    else:
        session_obj = XnatUtils.get_full_object(xnat, session_info)
        session_obj.attrs.set('date', date)


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
        for session in XnatUtils.list_sessions(XNAT, ARGS.project):
            edit_session_date(XNAT, session)
    finally:
        XNAT.disconnect()
