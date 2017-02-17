#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Separate DICOM files in a folder by reading the header.
"""

import os
import dicom
import shutil
import subprocess as sb
from datetime import datetime


__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Separate DICOM files in a folder by reading the header."
__version__ = '1.0.0'
__modifications__ = '7 October 2015 - Original write'


SUBJECT_IDS = [5, 9, 12, 19, 22, 23, 32, 38, 39, 40, 44]


def parse_args():
    """ Parser for arguments """
    from argparse import ArgumentParser
    usage = "Separate DICOM files in a folder by reading the header."
    argp = ArgumentParser(prog='organise_dicomfolder', description=usage)
    argp.add_argument('-d', '--dicomfolder', dest='dicomfolder',
                      help='Directory containing DICOMs.', required=True)
    argp.add_argument('--onefolder', dest='onefolder',
                      help='One folder containing all DICOMs.',
                      action='store_true')
    return argp.parse_args()


def is_dicom(fpath):
    """
        check if the file is a DICOM medical data

        :param fpath: path of the file
        :return boolean: true if it's a DICOM, false otherwise
    """
    file_call = '''file {fpath}'''.format(fpath=fpath)
    output = sb.check_output(file_call.split())
    if 'dicom' in output.lower():
        return True

    return False


def find_one_dicom(directory):
    """Return the files in subdirectories with the right extension.

    :param directory: directory where the data are located
    :param ext: extension to look for
    :return: python list of files
    """
    for filename in os.listdir(directory):
        fpath = os.path.join(directory, filename)
        if os.path.isfile(fpath):
            if is_dicom(fpath):
                return fpath
            else:
                continue
        elif os.path.isdir(fpath):
            return find_one_dicom(fpath)
    return None


def get_patient_id(dicom_file):
    patient_id = dicom.read_file(dicom_file).PatientID
    if 'patient' in patient_id.lower():
        try:
            pid = int(patient_id.lower().split('patient')[1])
            if pid in SUBJECT_IDS:
                return pid
        except TypeError:
            print 'No patient in ID. Return False.'
    return -1


def find_patient_id(folder):
    '''Extract one dicom file from folder.'''
    dicom_file = find_one_dicom(folder)
    return get_patient_id(dicom_file)


def separate_dicoms():
    """
        looping through the directory to find dicoms and separate them by
        series.
    """
    for folder in os.listdir(OPTIONS.dicomfolder):
        fpath = os.path.join(OPTIONS.dicomfolder, folder)
        if folder.startswith('Patient'):
            continue
        elif os.path.isdir(fpath):
            patient_id = find_patient_id(fpath)
            if patient_id in SUBJECT_IDS:
                print ' - Moving %s' % fpath
                p_folder = os.path.join(OPTIONS.dicomfolder,
                                        'Patient%02d' % patient_id)
                if not os.path.isdir(p_folder):
                    os.makedirs(p_folder)
                new_folder = os.path.join(p_folder, folder)
                shutil.move(fpath, new_folder)


def separate_same_dicoms():
    for name_folder in os.listdir(OPTIONS.dicomfolder):
        fpath1 = os.path.join(OPTIONS.dicomfolder, name_folder)
        if name_folder.startswith('Patient') or name_folder in ['FOREIGN']:
            continue
        elif os.path.isdir(fpath1):
            print 'Looking into folder named: %s' % name_folder
            for serie_folder in os.listdir(fpath1):
                fpath2 = os.path.join(fpath1, serie_folder)
                if os.path.isdir(fpath1):
                    print '  %s' % serie_folder
                    for filename in os.listdir(fpath2):
                        dicom_path = os.path.join(fpath2, filename)
                        if is_dicom(dicom_path):
                            patient_id = get_patient_id(dicom_path)
                            if patient_id in SUBJECT_IDS:
                                print ' - Moving file %s' % dicom_path
                                p_folder = os.path.join(
                                    OPTIONS.dicomfolder,
                                    'Patient%02d' % patient_id,
                                    name_folder, serie_folder)
                                if not os.path.isdir(p_folder):
                                    os.makedirs(p_folder)
                                new_dicom = os.path.join(p_folder, filename)
                                shutil.move(dicom_path, new_dicom)


if __name__ == '__main__':
    OPTIONS = parse_args()
    print "Separate DICOM in a folder by reading the header."
    print "Time: ", str(datetime.now())

    if not OPTIONS.onefolder:
        separate_dicoms()
    else:
        separate_same_dicoms()
