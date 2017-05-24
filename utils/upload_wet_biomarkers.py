#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Zip all files in a resource as resource.zip
"""

import os
from datetime import datetime
from dax import XnatUtils

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__version__ = '1.0.0'
__modifications__ = '27 April 2017 - Original write'
__exe__ = os.path.basename(__file__)
__description__ = "Upload the information for WetBiomarkers."

XSITYPE = 'cx:bioMarkersData'


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


def validate(date_text):
    """
    Validate the date.
    """
    try:
        datetime.strptime(date_text, '%Y%m%d')
        return '{0}-{1}-{2}'.format(date_text[0:4],
                                    date_text[4:6],
                                    date_text[6:])
    except ValueError:
        print("Incorrect data format, should be YYYYMMDD. Using today date.")
        now = datetime.now()
        today = '{0}{1}{2}'.format(str(now.year), str(now.month), str(now.day))
        return today


def is_float(val):
    """
    Check if tag is a float.
    """
    try:
        float(val)
    except ValueError:
        return False
    return True


def create_biomarker(xnat, biomarker_dict):
    """
    Create the assessment on XNAT

    :param xnat: pyxnat interface
    :param biomarker_dict: attributes to set for the assessors
    """
    # select obj:
    uri = '/project/{0}/subject/{1}/experiment/{2}'.format(
        biomarker_dict['project_id'],
        biomarker_dict['subject_label'],
        biomarker_dict['session_label']
    )

    biomarker_obj = xnat.select(uri)
    if not biomarker_obj.exists():
        # date:
        date = validate(biomarker_dict.get('session_label').split('_')[-1])

        kwargs = {'experiments': XSITYPE,
                  '%s/date' % XSITYPE: date,
                  '%s/editor' % XSITYPE: xnat.user}
        if is_float(biomarker_dict['wetbiomarkerAB_norm']):
            kwargs['%s/norm/amyloidbeta' % XSITYPE] = \
                float(biomarker_dict['wetbiomarkerAB_norm'])
        if is_float(biomarker_dict['wetbiomarkerT_norm']):
            kwargs['%s/norm/tauprotein' % XSITYPE] = \
                float(biomarker_dict['wetbiomarkerT_norm'])
        if is_float(biomarker_dict['wetbiomarkerPT_norm']):
            kwargs['%s/norm/phosphorylated' % XSITYPE] = \
                float(biomarker_dict['wetbiomarkerPT_norm'])
        if is_float(biomarker_dict['wetbiomarkerAB_raw']):
            kwargs['%s/raw/amyloidbeta' % XSITYPE] = \
                float(biomarker_dict['wetbiomarkerAB_raw'])
        if is_float(biomarker_dict['wetbiomarkerT_raw']):
            kwargs['%s/raw/tauprotein' % XSITYPE] = \
                float(biomarker_dict['wetbiomarkerT_raw'])
        if is_float(biomarker_dict['wetbiomarkerPT_raw']):
            kwargs['%s/raw/phosphorylated' % XSITYPE] = \
                float(biomarker_dict['wetbiomarkerPT_raw'])

        biomarker_obj.insert(**kwargs)
        print('{0} created.'.format(biomarker_dict['session_label']))


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

        for biomarker_dict in biomarkers_info:
            # Create
            create_biomarker(xnat, biomarker_dict)

            # delete:
            # uri = '/project/{0}/subject/{1}/experiment/{2}'.format(
            #     biomarker_dict['project_id'],
            #     biomarker_dict['subject_label'],
            #     biomarker_dict['session_label']
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
