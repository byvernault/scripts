"""Delete sessions on XNAT."""

import getpass
from dax import XnatUtils
from datetime import datetime

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Delete sessions on XNAT."


def parse_args():
    """Parser for arguments."""
    from argparse import ArgumentParser, RawDescriptionHelpFormatter
    argp = ArgumentParser(prog='Rename session', description=__purpose__,
                          formatter_class=RawDescriptionHelpFormatter)
    argp.add_argument('--host', dest='host',
                      help='Host for Xnat.')
    argp.add_argument('-u', '--username', dest='username',
                      help='Username for Xnat.')
    argp.add_argument('-p', '--project', dest='project',
                      help='Project ID on Xnat.', required=True)
    argp.add_argument('-s', '--sess', dest='sessions',
                      help='Session labels on Xnat (comma separated).')

    return argp.parse_args()


def get_sessions_list():
    """Extract sessions list from XNAT to be deleted."""
    li_sessions = XnatUtils.list_sessions(XNAT, OPTIONS.project)
    li_sessions = XnatUtils.filter_list_dicts_regex(
                    li_sessions, 'session_label', OPTIONS.sessions.split(','))
    return li_sessions


def print_sessions_list():
    """Print assessors found to be deleted."""
    print '\t%*s' % (-20, 'Session label')
    for session in LI_SESSIONS:
        print '\t%s' % session['label']


def ask_user_delete():
    """Ask user to confirm the deletion."""
    answer = ''
    while answer not in ['Y', 'y', 'n', 'N']:
        answer = raw_input('Do you want to delete all these sessions?(Y/N)\n')
    return answer


def sessions_delete():
    """Delete sessions on XNAT."""
    for session in LI_SESSIONS:
        print ' - deleting session: %s' % session['label']
        # session_obj = XnatUtils.get_full_object(XNAT, session)
        # if session_obj.exists():
        #     try:
        #         session_obj.delete()
        #     except:
        #         print "exception but let's continue"


if __name__ == '__main__':
    OPTIONS = parse_args()
    print 'Deleting sessions for project:\t%s' % OPTIONS.project
    print 'Time: ', str(datetime.now())

    # Connection to Xnat
    try:
        if OPTIONS.username:
            msg = """password for user <%s>:""" % OPTIONS.username
            pwd = getpass.getpass(prompt=msg)
        else:
            pwd = None

        XNAT = XnatUtils.get_interface(host=OPTIONS.host,
                                       user=OPTIONS.username,
                                       pwd=pwd)
        LI_SESSIONS = get_sessions_list()
        if not len(LI_SESSIONS) > 0:
            print 'INFO: No session found. Exit.'
        else:
            print 'INFO: '+str(len(LI_SESSIONS))+' sessions found.'
            # show the list:
            print_sessions_list()

            # ask if it's good to delete:
            answer = ask_user_delete()
            if answer in ['Y', 'y']:
                run = raw_input('Are you sure?(Y/N)\n')
                if run in ['Y', 'y']:
                    print '\nINFO: deleting sessions ...'
                    sessions_delete()
                else:
                    print 'INFO: Delete session CANCELED...'
            else:
                print 'INFO: Delete session CANCELED...'
    finally:
        XNAT.disconnect()
    print '=================================================================\n'
