"""TEST number 2 Script for different purpose."""

import os
import glob
import time
import dicom
import scipy
import datetime
import collections
import numpy as np
import nibabel as nib
from dicom.sequence import Sequence
from dicom.dataset import Dataset, FileDataset
from dax import XnatUtils
# import Ben_functions

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Test Code 2"


def parse_args():
    """Parser for arguments."""
    from argparse import ArgumentParser, RawDescriptionHelpFormatter
    argp = ArgumentParser(prog='Rename session', description=__purpose__,
                          formatter_class=RawDescriptionHelpFormatter)
    argp.add_argument('-o', '--old', dest='old', required=True,
                      help='List of sessions to move to new subject.')
    argp.add_argument('-n', '--new', dest='new', required=True,
                      help='New subject.')
    argp.add_argument('-e', '--except', dest='exceptions', default=[],
                      help='Except those sessions.')

    return argp.parse_args()

if __name__ == '__main__':
    xml_file = '/Users/byvernault/20140701_08434709NXRZs006a1001_volumes.xml'
    """import xml.etree.ElementTree
    e = xml.etree.ElementTree.parse(xml_file).getroot()
    print e.attributes()"""

    from xml.dom import minidom
    xmldoc = minidom.parse(xml_file)
    itemlist = xmldoc.getElementsByTagName('item')
    print(len(itemlist))
    for s in itemlist:
        print s

    """args = parse_args()
    xnat = XnatUtils.get_interface(host='http://cmic-xnat.cs.ucl.ac.uk')

    li_sessions = XnatUtils.list_sessions(xnat, 'prion')
    li_sessions = filter(lambda x: x['subject_label'] == args.old, li_sessions)
    for session in li_sessions:
        if session['label'] not in args.exceptions:
            session_obj = XnatUtils.get_full_object(xnat, session)
            if session_obj.exists():
                date = session['label'].split('_')[1]
                new_label = '%s_%s' % (args.new, date)
                print '%s --> %s' % (session['label'], new_label)
                session_obj.attrs.set('label', new_label)"""

    """li_subjs = XnatUtils.list_subjects(xnat, 'prion')
    li_subjs = filter(lambda x: x['subject_label'] == args.old, li_subjs)
    for subject in li_subjs:
        if 'NIFTI' in scan['resources']:
            scan_obj = XnatUtils.get_full_object(xnat, scan)
            resources_file = scan_obj.resource('NIFTI').files().get()[:]
            if len(resources_file) > 1:
                print '%s,%s,%s' % (scan['subject_label'],
                                    scan['session_label'],
                                    scan['ID'])
    xnat.disconnect()
    """
