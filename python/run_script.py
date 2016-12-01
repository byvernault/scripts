"""TEST number 2 Script for different purpose."""

import os
import time
import glob
import dicom
import datetime
import numpy as np
import nibabel as nib
from dax import XnatUtils
from scipy import ndimage
from dicom.sequence import Sequence
from dicom.dataset import Dataset, FileDataset
from lxml import etree

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Test Code 2"


def parse_args():
    """Parser for arguments."""
    from argparse import ArgumentParser, RawDescriptionHelpFormatter
    argp = ArgumentParser(prog='Set_types_from_dicom', description=__purpose__,
                          formatter_class=RawDescriptionHelpFormatter)
    argp.add_argument('-s', '--subj', dest='suject_to_do',
                      help='Sessions label on XNAT.')
    argp.add_argument('-d', '--date', dest='dateb',
                      help='Date of birth.')
    argp.add_argument('-g', '--gender', dest='gender',
                      help='Gender.')

    return argp.parse_args()


if __name__ == '__main__':
    args = parse_args()
    xnat = XnatUtils.get_interface(host='https://qs-controls.cs.ucl.ac.uk')

    subj = xnat.select('/project/control_PRION/subject/%s' % args.suject_to_do)
    if subj.exists():
        dic = {'yob': args.dateb,
               'gender': args.gender}
        subj.attrs.mset(dic)

    """li_subjects = XnatUtils.list_subjects(xnat, 'prion')
    li_subjects = sorted(li_subjects, key=lambda k: k['label'])
    li_su = []
    for subject in li_subjects:
        subj_obj = XnatUtils.get_full_object(xnat, subject)
        genetic = subj_obj.attrs.get('xnat:subjectData/fields/field\
[name=genetic]/field')
        # print genetic
        if 'Control' in genetic:
            li_su.append(subject['label'])

    print ','.join(li_su)"""

    """li_assessors = XnatUtils.list_project_assessors(xnat, 'prion')
    li_assessors = sorted(li_assessors, key=lambda k: k['session_label'])
    # li_su = []
    for assessor in li_assessors:
        labels = assessor['label'].split('-x-')
        if labels[1] != assessor['subject_label']:
            print 'Deleting: %s' % (assessor['label'])
            assessor_obj = XnatUtils.get_full_object(xnat, assessor)
            if assessor_obj.exists:
                assessor_obj.delete()
                print ' next...'"""

            # li_su.append(assessor['subject_label'])
            # print 'Changing: %s --> %s' % (assessor['label'],
            #                                new_label)
    # print ','.join(list(set(li_su)))
    """
    li_sessions = XnatUtils.list_sessions(xnat, 'prion')
    li_sessions = sorted(li_sessions, key=lambda k: k['session_label'])
    subject_changed = False
    for session in li_sessions:
        label = session['label'].split('_')[0]
        if label == args.suject_to_do and not subject_changed:
            if session['subject_label'] != label:
                print 'Wrong subject: %s --> %s' % (session['subject_label'],
                                                    label)
                new_subj = xnat.select('/project/prion/subject/%s' % label)
                if new_subj.exists():
                    print 'Error: subject exists %s' % label
                subject = XnatUtils.get_full_object(xnat, session).parent()
                if subject.exists():
                    subject.attrs.set('label', label)
                    subject_changed = True
                    print ('Subject changed for %s --> %s'
                           % (session['subject_label'], label))
    """
    xnat.disconnect()
