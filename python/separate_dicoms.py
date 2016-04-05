"""
    Separate DICOM in a folder by scans following the name pattern (number)
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Separate DICOM in a folder by scans following the name pattern (number)"
__version__ = '1.0.0'
__modifications__ = '11 September 2015 - Original write'

import os
import re
import glob
import subprocess as sb
from datetime import datetime

def parse_args():
    """ Parser for arguments """
    from argparse import ArgumentParser
    usage = "Separate DICOM in a folder by scans following the name pattern (number)"
    argp = ArgumentParser(prog='dcm2nii_xnat', description=usage)
    argp.add_argument('-d', '--directory', dest='directory',
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

def loop_throug_directory(project, directory):
    """
        looping through the directory to find dicom and separate them by scans

        :param directory: directory holding the DICOM
    """
    if directory[-1] == '/':
        directory = directory[:-1]
    subj_name = os.path.basename(directory)
    subjid1 = subj_name.replace('_','')
    subjid2 = subj_name[:-1]+subj_name[-1].lower()
    ffpaths = os.listdir(directory)
    previous_name = None
    count = 1
    csv_text = ''
    for name in ffpaths:
        fpath = os.path.join(directory, name)
        if os.path.isfile(fpath) and is_dicom(fpath):
            csv_str = "scan," + project+','
            if previous_name:
                if int(previous_name[:4]) == int(name[:4]):
                    os.rename(fpath, os.path.join(dcm_dir, name))
                else:
                    # convert to NIFTI and rename the folder and give the csv line:
                    os.system('dcm2nii -a n -e n -d n -g y -f n -n y -p n -v y -x n -r n '+os.path.join(dcm_dir, previous_name))
                    niis_file = glob.glob(os.path.join(dcm_dir, '*.nii.gz'))
                    if niis_file:
                        nii_file_name = niis_file[0].split('/')[-1]
                        exp_name = nii_file_name[:15]
                        try:
                            scan_sd = re.search(exp_name+'(.*)'+subjid1, nii_file_name).group(1)
                            scan_id = re.search(subjid1+'(.*).nii.gz', nii_file_name).group(1)[:5]
                        except:
                            scan_sd = re.search(exp_name+'(.*)'+subjid2, nii_file_name).group(1)
                            scan_id = re.search(subjid2+'(.*).nii.gz', nii_file_name).group(1)[:5]
                        if scan_id[-1] == '0':
                            scan_id = scan_id[1:-1]
                        else:
                            scan_id = scan_id[1:]
                        scan_type = scan_sd
                        csv_str += subj_name+',MR,'+exp_name+','+scan_id+','+scan_type+','+scan_sd+',questionable,'+os.path.abspath(dcm_dir)
                        print "                 PATH = "+csv_str
                        csv_text += '\n'+csv_str
                    # next
                    count +=1
                    dcm_dir = os.path.join(directory, str(count))
                    os.makedirs(dcm_dir)
                    os.rename(fpath, os.path.join(dcm_dir, name))
            else:
                dcm_dir = os.path.join(directory, str(count))
                os.makedirs(dcm_dir)
                os.rename(fpath, os.path.join(dcm_dir, name))

            previous_name = name

    csv_str = "scan," + project+','
    os.system('dcm2nii -a n -e n -d n -g y -f n -n y -p n -v y -x n -r n '+os.path.join(dcm_dir, previous_name))
    niis_file = glob.glob(os.path.join(dcm_dir, '*.nii.gz'))
    if niis_file:
        nii_file_name = niis_file[0].split('/')[-1]
        exp_name = nii_file_name[:15]
        try:
            scan_sd = re.search(exp_name+'(.*)'+subjid1, nii_file_name).group(1)
            scan_id = re.search(subjid1+'(.*).nii.gz', nii_file_name).group(1)[:5]
        except:
            scan_sd = re.search(exp_name+'(.*)'+subjid2, nii_file_name).group(1)
            scan_id = re.search(subjid2+'(.*).nii.gz', nii_file_name).group(1)[:5]
        if scan_id[-1] == 0:
            scan_id = scan_id[1:-1]
        else:
            scan_id = scan_id[1:]
        scan_type = scan_sd
        csv_str += subj_name+',MR,'+exp_name+','+scan_id+','+scan_type+','+scan_sd+',questionable,'+os.path.abspath(dcm_dir)
        print "                 PATH = "+csv_str
        csv_text += '\n'+csv_str

    return csv_text

if __name__ == '__main__':
    OPTIONS = parse_args()
    print "Separate DICOM in a folder by following the name pattern (number)"
    print "Time: ", str(datetime.now())

    # Get the folders/files in directory
    csv_str = loop_throug_directory('PPPX', OPTIONS.directory)
    print csv_str
    print '===================================================================\n'
