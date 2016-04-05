"""
    Separate DICOM files in a folder by reading the header.
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Separate DICOM files in a folder by reading the header."
__version__ = '1.0.0'
__modifications__ = '7 October 2015 - Original write'

import os
import dicom
import glob
import subprocess as sb
from datetime import datetime

PCOMMENT_TEMPLATE = """Project:{project};Subject:{subject};Session:{session}"""

DICOM_FIELDS = {"commentsXnat":[0x0010,0x4000], "subject":[0x0010,0x0010], "serie":[0x0020,0x0010]}

def parse_args():
    """ Parser for arguments """
    from argparse import ArgumentParser
    usage = "Separate DICOM files in a folder by reading the header."
    argp = ArgumentParser(prog='organise_dicomfolder', description=usage)
    argp.add_argument('-d', '--dicomfolder', dest='directory',
                      help='Directory containing DICOMs.', required=True)
    argp.add_argument('-p', '--project', dest='project',
                      help='Project ID on XNAT.', required=True)
    return argp.parse_args()

def get_info_file(directory, project):
    """
        Get the info from directory structure (subject / session)

        :param directory: path for subject dir
        :param project: xnat project ID
        :return dict: dict with info {"scansdir": list of dir, "comment": patient comment}
    """
    dicom_dict = dict()
    if len(glob.glob(os.path.join(directory,'*','*')))>0 and is_dicom(glob.glob(os.path.join(directory,'*','*'))[0]):
        dcmfpath = glob.glob(os.path.join(directory,'*','*'))[0]
        ds = dicom.read_file(dcmfpath)
        subject_label = ds.PatientName.replace(' ','')
        try:
            session_label = ds.InstanceCreationDate.replace(' ','')
        except:
            try:
                session_label = ds.AcquisitionDate.replace(' ','')
            except:
                session_label = ds.PerformedProcedureStepEndDate.replace(' ','')
        patient_comment = PCOMMENT_TEMPLATE.format(project=project,
                                                   subject=subject_label,
                                                   session=subject_label+"_"+session_label)
        dicom_dict['comment'] = patient_comment
        print patient_comment
        scans_dir = list()
        for scan in os.listdir(directory):
            fpath = os.path.join(directory, scan)
            if os.path.isdir(fpath):
                scans_dir.append(fpath)

        dicom_dict['scansdir'] = scans_dir
    else:
        print "No dicoms in "+directory

    return dicom_dict

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

def edit_info_dicom(list_dict):
    """
        edit the information of the DICOM for patients comment
    """
    for session_dict in list_dict:
        for scanfolder in session_dict['scansdir']:
            print "Setting field for folder: "+scanfolder+" to "+session_dict['comment']
            set_dicom_field(scanfolder, session_dict['comment'])
            print "------"

def set_dicom_field(dcmfolder, comment):
    """
        edit the information of the DICOM for patients comment

        :param dcmfolder: folder containing the dicoms
        :param comment: value for the patients comment
    """
    for dcmfile in os.listdir(dcmfolder):
        dicom_path = os.path.join(dcmfolder, dcmfile)
        if os.path.isfile(dicom_path) and is_dicom(dicom_path):
            print "   file: "+dcmfile
            dcm = dicom.read_file(dicom_path)
            # edit the header
            dcm.PatientComments = comment
            dcm.save_as(dicom_path)

if __name__ == '__main__':
    OPTIONS = parse_args()
    print "Edit DICOM in a folder/sub folder to upload to XNAT."
    print "Time: ", str(datetime.now())

    # Get the folders/files in directory
    scan_list = list()
    for subject in os.listdir(os.path.abspath(OPTIONS.directory)):
        subpath = os.path.join(os.path.abspath(OPTIONS.directory), subject)
        if os.path.isdir(subpath):
            if int(subject[:3])>0:
                for session in os.listdir(subpath):
                    sesspath = os.path.join(subpath, session)
                    if os.path.isdir(sesspath):
                        results = get_info_file(sesspath, OPTIONS.project)
                        if results:
                            scan_list.append(results)

    edit_info_dicom(scan_list)
    print "DICOMs read and edited."
    print '==================================================================='
