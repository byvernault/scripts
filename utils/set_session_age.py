#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setting the age of a session by using yob and sessiond date.
"""

import os
import getpass
from dax import XnatUtils
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = 'Setting the age of a session by using yob and sessiond date'
__version__ = '1.0.0'
__modifications__ = '11 February 2016 - Original write'


def parse_args():
    """Parser for arguments."""
    from argparse import ArgumentParser
    argp = ArgumentParser(prog='set_session_date', description=__purpose__)
    argp.add_argument('--host', dest='host', default=None,
                      help='Host for XNAT. Default: using $XNAT_HOST.')
    argp.add_argument('-u', '--username', dest='username', default=None,
                      help='Username for XNAT. Default: using $XNAT_USER.')
    argp.add_argument('-p', '--project', dest='project', required=True,
                      help='XNAT project ID')
    argp.add_argument('--force', dest='force', action='store_true',
                      help='force setting the age even if it already exists.')
    return argp.parse_args()


def years_between(start_date, end_date):
    """Difference between two dates."""
    dsinfo = start_date.split('-')
    start_date = date(int(dsinfo[0]), int(dsinfo[1]), int(dsinfo[2]))
    deinfo = end_date.split('-')
    end_date = date(int(deinfo[0]), int(deinfo[1]), int(deinfo[2]))
    rd = relativedelta(end_date, start_date)
    return rd.years + rd.months/12.0 + rd.days/365.2425


def set_session_age(session_info):
    """Set age for session."""
    if not session_info['age'] or ARGS.force:
        session_obj = XnatUtils.get_full_object(XNAT, session_info)
        xsitype_sess = session_obj.attrs.get('xsiType')
        yob = session_obj.parent().attrs.get('yob')
        if not yob:
            print 'Skipping the session because yob not set.'
        else:
            yob = "%s-01-01" % yob
            years = years_between(yob, session_info['date'])
            age = '%.2f' % years
            session_obj.attrs.set('%s/%s' % (xsitype_sess, 'age'), age)
            print 'Age set to %s for %s.' % (age, session['label'])
    else:
        print 'Already set to %s for %s' % (session_info['age'],
                                            session['label'])

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
        XNAT = XnatUtils.get_interface(host=ARGS.host,
                                       user=ARGS.username,
                                       pwd=PWD)
        for session in XnatUtils.list_sessions(XNAT, ARGS.project):
            set_session_age(session)
    finally:
        XNAT.disconnect()
