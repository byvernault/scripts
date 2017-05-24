#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Zip all files in a resource as resource.zip
"""

from datetime import datetime
from dax import XnatUtils
import glob
import os


__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__version__ = '1.0.0'
__modifications__ = '28 April 2017 - Original write'
__exe__ = os.path.basename(__file__)
__description__ = "Upload the information for Subj Proc Data."

XSITYPE = 'proc:subjGenProcData'


def parse_args():
    """Parser for arguments."""
    from argparse import ArgumentParser
    argp = ArgumentParser(prog=__exe__, description=__description__)
    argp.add_argument('--host', dest='host',
                      help='Host for Xnat.')
    argp.add_argument('-u', '--username', dest='username',
                      help='Username for Xnat.')
    argp.add_argument('-c', '--csv', dest='csv_file',
                      help='CSV file containing the upload info.',
                      required=True)
    return argp.parse_args()


def create_subjdata(xnat, a_subj_dict):
    """
    Create the assessment on XNAT

    :param xnat: pyxnat interface
    :param a_subj_dict: attributes to set for the assessor
    """
    # select obj:
    uri = '/project/{0}/subject/{1}/experiment/{2}'.format(
        a_subj_dict['project_id'],
        a_subj_dict['subject_label'],
        a_subj_dict['as_label']
    )

    subj_asse_obj = xnat.select(uri)
    # date:
    now = datetime.now()
    today = '{0}{1}{2}'.format(str(now.year), str(now.month), str(now.day))

    kwargs = {
       'experiments': XSITYPE,
       '%s/sessions' % XSITYPE: 's01_1,s01_2,s01_3',
       '%s/procstatus' % XSITYPE: a_subj_dict['as_description'],
       '%s/validation/status' % XSITYPE: 'TEST01',
       '%s/proctype' % XSITYPE: a_subj_dict['as_type'],
       '%s/date' % XSITYPE: today,
    }

    subj_asse_obj.insert(**kwargs)
    print('{0} created.'.format(a_subj_dict['as_label']))

    # Upload Resource:
    upload_path(subj_asse_obj.resource(a_subj_dict['resource']),
                a_subj_dict['resource'], a_subj_dict['fpath'])


def is_file(fpath):
    """
    Verify if the path is a file and if it's a folder,
     if there is only one file in the folder, return the file
    :param fpath: path that need to be check
    :return: True if it's a file or False otherwise, path of the file
    """
    if os.path.isfile(fpath):
        return True, fpath
    else:
        if len(glob.glob(os.path.join(fpath, '*'))) == 1:
            return True, glob.glob(os.path.join(fpath, '*'))[0]
        else:
            if fpath[-1] == '/':
                fpath = fpath[:-1]
            return False, fpath


def upload_path(resource_obj, resource_label, fpath, force=False,
                delete=False, extract=False):
    """
    Upload path to XNAT: either a file or folder
    :param resource_obj: pyxnat resource obj
    :param resource_label: label of the resource
    :param force: force the upload if file exists
    :param delete: delete the resource and all files before uploading
    :param extract: extract the files if it's a zip
    :return: None
    """
    _format_f = '     - File %s: uploading file...'
    _format_p = '     - Folder %s: uploading folder...'
    isfile, fpath = is_file(fpath)
    if isfile:
        print(_format_f % (os.path.basename(fpath)))
        XnatUtils.upload_file_to_obj(
            fpath, resource_obj, remove=force, removeall=delete)
    else:
        print(_format_p % (os.path.basename(fpath)))
        XnatUtils.upload_folder_to_obj(
            fpath, resource_obj, resource_label,
            remove=force, removeall=delete, extract=extract)


def upload_data(args):
    """
    Main function to upload data.

    :param args: arguments from argparser
    """
    biomarkers_info = XnatUtils.read_csv(args.csv_file)

    if args.host:
        host = args.host
    else:
        host = os.environ['XNAT_HOST']

    with XnatUtils.get_interface(host=host, user=args.username) as xnat:
        print('INFO: connection to xnat <%s>:' % (host))
        print('INFO: setting information to XNAT')

        for a_subj_dict in biomarkers_info:
            # Create
            create_subjdata(xnat, a_subj_dict)

            # delete:
            # uri = '/project/{0}/subject/{1}/experiment/{2}'.format(
            #     a_subj_dict['project_id'],
            #     a_subj_dict['subject_label'],
            #     a_subj_dict['session_label']
            # )

            # biomarker_obj = xnat.select(uri)
            # if biomarker_obj.exists():
            #     biomarker_obj.delete()


if __name__ == '__main__':
    args = parse_args()
    print('Uploading information for Wet Biomarkers:')
    print('Time: %s' % str(datetime.now()))

    upload_data(args)

    print('================================================================\n')
