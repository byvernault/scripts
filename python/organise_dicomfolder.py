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
import shutil
import subprocess as sb
from datetime import datetime

CVS_STR_TEMPLATE = """{project},{subject},{sessiontype},{session},\
{scan},{scantype},{scandescription},{scanquality},{resource},{fpath}"""

DICOM_FIELDS = {"subject":[0x00100010], "scan":[0x00200011], "scantype":[0x0008103E], "date":[0x00080021], "time":[0x00080032]}

def parse_args():
    """ Parser for arguments """
    from argparse import ArgumentParser
    usage = "Separate DICOM files in a folder by reading the header."
    argp = ArgumentParser(prog='organise_dicomfolder', description=usage)
    argp.add_argument('-d', '--dicomfolder', dest='dicomfolder',
                      help='Directory containing DICOMs.', required=True)
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

def read_info_dicom():
    """
        looping through the directory to find dicom and separate them by study/series

        :return python list of dict: list of dictionary containing the information for the csv for each dicoms
    """
    dicoms_dict = dict()

    # dicom that could not be identified
    #unknown_dicom_dir = os.path.join(DIRECTORY, "unknown_dicoms")
    #if not os.path.exists(unknown_dicom_dir):
    #    os.makedirs(unknown_dicom_dir)
    other_files = os.path.join(DIRECTORY, "other_files")
    if not os.path.exists(other_files):
        os.makedirs(other_files)

    for name in os.listdir(DIRECTORY):
        fpath = os.path.join(DIRECTORY, name)
        if os.path.isfile(fpath) and is_dicom(fpath):
            dcm_header = dicom.read_file(fpath)
            if dcm_header.Modality.upper() == 'PR':
                continue
            else:
                if dcm_header.StudyInstanceUID not in dicoms_dict.keys():
                    dicoms_dict[dcm_header.StudyInstanceUID] = dict()
                else:
                    if dcm_header.SeriesNumber not in dicoms_dict[dcm_header.StudyInstanceUID].keys():
                        dicoms_dict[dcm_header.StudyInstanceUID][dcm_header.SeriesNumber] = {'files':[fpath], 'type':dcm_header.SeriesDescription, 'date':dcm_header.SeriesDate}
                    else:
                        dicoms_dict[dcm_header.StudyInstanceUID][dcm_header.SeriesNumber]['files'].append(fpath)
            #else:
            #    shutil.move(fpath, unknown_dicom_dir)
        elif name not in ["other_files", "unknown_dicoms"]:
            shutil.move(fpath, other_files)

    return dicoms_dict

def get_csv_str(args, dicom_dict, dfolder):
    """
        from arguments and the dicom header, generate the csv line for the scan

        :param args: arguments for the script
        :param dicom_dict: dictionary with the information from header
        :param dfolder: folder containing the dicoms
        :return string: csv string for the scan
    """
    return CVS_STR_TEMPLATE.format(project=args.project,
                                   subject=dicom_dict['subject'],
                                   sessiontype=args.sessiontype,
                                   session=dicom_dict['date']+'_'+dicom_dict['time'].split('.')[0],
                                   scan=dicom_dict['scan'].rstrip('0'),
                                   scantype=dicom_dict['scantype'],
                                   scandescription=dicom_dict['scantype'],
                                   scanquality='questionable',
                                   resource='DICOM',
                                   fpath=dfolder)

def separate_dicoms():
    """
        looping through the directory to find dicoms and separate them by series

    """
    print "1) Reading Dicoms files in the folder %s " % DIRECTORY
    dicoms_info = read_info_dicom()
    print "   Founded %s study(ies)" % len(dicoms_info.keys())
    print "2) Sorting the dicoms into folders in %s " % DIRECTORY
    for study, series in dicoms_info.items():
        studydir = os.path.join(DIRECTORY, study)
        if not os.path.exists(studydir):
            os.makedirs(studydir)

        #Create series folder and move files:
        for serie, info in series.items():
            seriesdir = os.path.join(studydir, "%s-%s.%s" % (serie, info['type'], str(info['date'])))
            if not os.path.exists(seriesdir):
                os.makedirs(seriesdir)
            for fp in info['files']:
                shutil.move(fp, seriesdir)

if __name__ == '__main__':
    OPTIONS = parse_args()
    print "Separate DICOM in a folder by reading the header."
    print "Time: ", str(datetime.now())

    DIRECTORY = OPTIONS.dicomfolder
    if DIRECTORY[-1] == '/':
        DIRECTORY = DIRECTORY[:-1]
    separate_dicoms()
