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

DICOM_FIELDS = {"subject":[0x0010,0x0010], "scan":[0x0020,0x0011], "scantype":[0x0008,0x103E], "date":[0x0008,0x0022], "time":[0x0008,0x0032]}

def parse_args():
    """ Parser for arguments """
    from argparse import ArgumentParser
    usage = "Separate DICOM files in a folder by reading the header."
    argp = ArgumentParser(prog='organise_dicomfolder', description=usage)
    argp.add_argument('-d', '--dicomfolder', dest='dicomfolder',
                      help='Directory containing DICOMs.', required=True)
    argp.add_argument('-p', '--project', dest='project',
                      help='Project ID on XNAT.', required=True)
    argp.add_argument('-t', '--sessionType', dest='sessiontype', required=False,
                      help='Session Type for XNAT. By default: MR', default="MR")
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

def read_info_dicom(dicom_path):
    """
        looping through the directory to find dicom and separate them by series

        :param directory: directory containing the dicom.
        :return python list of dict: list of dictionary containing the information for the csv for each dicoms
    """
    dcm_header = dicom.read_file(dicom_path)
    dicom_dict = dict()

    for key, field in DICOM_FIELDS.items():
        #try:
        info = dcm_header[field[0],field[1]].value
        if info:
            dicom_dict[key] = str(info).replace(' ', '_')
        """except:
            print "warning: could not read header tag %s, %s from %s" % (field[0], field[1], dicom_path)
            return None"""

    return dicom_dict

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

def separate_dicoms(args):
    """
        looping through the directory to find dicoms and separate them by series

        :param args: arguments given to the scripts
        :return list: cvs content
    """
    if args.dicomfolder[-1] == '/':
        args.dicomfolder = args.dicomfolder[:-1]
    # list of files/folders in direcory
    ffpaths = os.listdir(args.dicomfolder)
    # csv content:
    csv_content = list()
    # dicom that could not be identified
    unknown_dicom_dir = os.path.join(args.dicomfolder, "unknown_dicoms")
    if not os.path.exists(unknown_dicom_dir):
        os.makedirs(unknown_dicom_dir)
    other_files = os.path.join(args.dicomfolder, "other_files")
    if not os.path.exists(other_files):
        os.makedirs(other_files)
    for name in ffpaths:
        fpath = os.path.join(args.dicomfolder, name)
        if os.path.isfile(fpath) and is_dicom(fpath):
            #open dicom and extract the information needed
            dicom_dict = read_info_dicom(fpath)
            if dicom_dict:
                folder_name = "%s_%s_%s" % (dicom_dict['subject'], dicom_dict['date']+'_'+dicom_dict['time'].split('.')[0], dicom_dict['scan'])
                dfolder = os.path.join(args.dicomfolder, folder_name)
                if not os.path.exists(dfolder):
                    os.makedirs(dfolder)
                shutil.move(fpath, dfolder)
                csv_content.append(get_csv_str(args, dicom_dict, dfolder))
            else:
                shutil.move(fpath, unknown_dicom_dir)
        elif name not in ["other_files", "unknown_dicoms"]:
            shutil.move(fpath, other_files)

    return list(set(csv_content))

if __name__ == '__main__':
    OPTIONS = parse_args()
    print "Separate DICOM in a folder by reading the header."
    print "Time: ", str(datetime.now())

    # Get the folders/files in directory
    CSV_CONTENT = separate_dicoms(OPTIONS)
    print "Csv content for uploading using Xnatupload:"
    print '==================================================================='
    print "\n".join(CSV_CONTENT)
    print '===================================================================\n'
