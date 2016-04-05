"""
    Generate 4D nifti from 3D
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Extract bvals and bvecs from json file."
__version__ = '1.0.0'
__modifications__ = '11 October 2015 - Original write'

import os
import glob
from dax import XnatUtils

MATLAB_SCRIPT_TEMPLATE = """
addpath(genpath('/Users/byvernault/home-local/masimatlab/trunk/xnatspiders/matlab/ext'));
addpath('/Users/byvernault/Documents/MATLAB');
dirpath = '{dirpath}';
convert3Dto4DNII(dirpath);
"""

def parse_args():
    """
    Parser for arguments
    """
    from argparse import ArgumentParser
    usage = "Generates 4D niftis from 3D."
    argp = ArgumentParser(prog='read bvals/bvecs from json', description=usage)
    argp.add_argument('-d', dest='directory',
                      help="Directory where the folder containing the nifti files is.",
                      required=False)
    argp.add_argument('-f', dest='filepath',
                      help="File containing the name of the folder containing nifti in directory.",
                      default=None, required=False)
    argp.add_argument('-t', dest='untouch', action='store_false',help="Load nifti with orientation (not advise to do so)")
    argp.add_argument('-o', dest='onedti', action='store_true',help="Incorporate all the b0 with the dti (first volumes).")
    return argp.parse_args()

def generate_4D_nifti(folder_path):
    """
        Generate a 4D nifti from 3D nifti

        :param folder_path: folder containing the .nii files
    """
    nii_dict = organise_niftis(fpath)
    print "Converting 3D niftis into 4D nifti for folder %s ." % folder_path
    matlab_script = os.path.join(folder_path, 'convert3Din4D.m')
    f = open(matlab_script, "w")
    try:
        prefix_str = "{"
        for key in nii_dict.keys():
            prefix_str += "'%s'," % key
        prefix_str = prefix_str[:-1] + "}"
        lines = [ "% Matlab Script to call vufMRIQAGUI function\n",
                  "addpath(genpath('/Users/byvernault/home-local/masimatlab/trunk/xnatspiders/matlab/ext'));\n",
                  "addpath('/Users/byvernault/Documents/MATLAB');\n",
                  "folder_niis = '%s';\n" % folder_path,
                  "prefix = %s;\n" % prefix_str,
                  "dti = %s;\n" % (1 if ARGS.onedti else 0),
                  "untouch = %s;\n" % (1 if ARGS.untouch else 0),
                  "convert3Dto4DNII(folder_niis, prefix, dti, untouch);\n"]
        f.writelines(lines)
    finally:
        f.close()

    for key, nii_list in nii_dict.items():
        filename = os.path.join(folder_path, "%s_4D.nii.gz" % key)
        if os.path.isfile(filename):
            print"INFO: NIFTI already created. Skipping ... "
            return

    #Running Matlab script:
    XnatUtils.run_matlab(matlab_script, True)

    for key, nii_list in nii_dict.items():
        filename = os.path.join(folder_path, "%s_4D.nii" % key)
        if not os.path.isfile(filename):
            print"ERROR: NO NIFTI CREATED ... "
        else:
            # copying with fsl the header:
            print "Copying geometry from 3D nifti and gzipping the nifti for %s" % filename
            cmd = "fslcpgeom %s %s -d" % (nii_list[0], filename)
            os.system(cmd)
            os.system("gzip %s " % filename)

def organise_niftis(folder_path):
    """
    Read the niftis from the folder

    :param fpath: folder path to query
    :return: dictionary with nii_filename and all files to convert
    """
    niis = dict()
    for nii_file in glob.glob(os.path.join(folder_path, '*.nii')):
        nii_key = os.path.basename(nii_file).split('.')[0].split('-m-')[0]
        if nii_key in niis.keys():
            niis[nii_key].append(nii_file)
        else:
            niis[nii_key] = [nii_file]

    for key, item in niis.items():
        if len(item) == 1:
            os.system("gzip %s " % item[0])
            del niis[key]

    return niis

if __name__ == '__main__':
    ARGS = parse_args()
    print "INFO: Converting 3D nifti from a folder into a 4D nifti. Please be sure the nifti are not gzip."

    fpath_list = list()
    if not ARGS.filepath:
        for folder in os.listdir(ARGS.directory):
            fpath = os.path.abspath(os.path.join(ARGS.directory, folder))
            if os.path.isdir(fpath):
                if len(glob.glob(os.path.join(fpath, '*.nii'))) > 1:
                    fpath_list.append(fpath)
    else:
        for line in open(ARGS.filepath, 'r'):
            fpath = line.strip()
            if os.path.exists(fpath):
                if len(glob.glob(os.path.join(fpath, '*.nii')))>1:
                    fpath_list.append(fpath)
            else:
                print"error: path does not exist: %s" % fpath

    print("INFO: Press Enter to proceed with the convertion 3D to 4D nifti ....")
    for fpath in fpath_list:
        generate_4D_nifti(fpath)
