#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Convert DICOM to NIFTI for a project on XNAT.

Requirements:
    package: nibabel
    file in pythonpath: XnatUtils (see in this project)
    dcm2nii install (last version):
        http://www.mccauslandcenter.sc.edu/mricro/mricron/dcm2nii.html
    dcmtk package (last version) (containing dcmdjpeg):
        http://dicom.offis.de/dcmtk.php.en
"""

import os
import glob
import dicom
import getpass
import numpy as np
import nibabel as nib
import subprocess as sb
from datetime import datetime
from dax import XnatUtils

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Convert DICOM to NIFTI for a project on XNAT."
__version__ = '1.0.0'
__modifications__ = '10 September 2015 - Original write'


def parse_args():
    """Parser for arguments."""
    from argparse import ArgumentParser
    usage = "Convert DICOM to NIFTI for all scans in a project."
    argp = ArgumentParser(prog='dcm2nii_xnat', description=usage)
    argp.add_argument('--host', dest='host',
                      help='Host for Xnat.')
    argp.add_argument('-u', '--username', dest='username',
                      help='Username for Xnat.')
    argp.add_argument('-p', '--project', dest='project',
                      help='Project ID on Xnat.', required=True)
    argp.add_argument('-s', '--sess', dest='sessions',
                      help='Session labels on Xnat (comma separated).')
    argp.add_argument('-d', '--directory', dest='directory',
                      help='Temp directory on your computer.', required=True)
    argp.add_argument('--dcm2nii', dest='dcm2nii', default='dcm2nii',
                      help='Full Path to the executable dcm2nii.')
    argp.add_argument('--dcmdjpeg', dest='dcmdjpeg', default='dcmdjpeg',
                      help='Full Path to the executable of dcmdjpeg.')
    argp.add_argument('-f', '--force', dest='force', action='store_true',
                      help='Force the convertion of NIFTI \
(even if there was NIFTI there).')
    argp.add_argument('-z', '--zip', dest='zip_dicoms', action='store_true',
                      help='ZIP DICOMs if more than one file.')
    argp.add_argument('-c', '--check', dest='check_dcm', action='store_true',
                      help='Checking DICOM using pydicom.')
    return argp.parse_args()


def is_dicom(fpath):
    """check if the file is a DICOM medical data.

    :param fpath: path of the file
    :return boolean: true if it's a DICOM, false otherwise
    """
    file_call = '''file {fpath}'''.format(fpath=fpath)
    output = sb.check_output(file_call.split())
    if 'dicom' in output.lower():
        return True

    return False


def get_dicom_list(directory):
    """get the list of DICOMs file from the directory.

    :param directory: directory containing the DICOM files.
    :return list(): list of filepaths that are dicoms in directory
    """
    fnames = os.listdir(directory)
    dicom_paths = list()
    for fname in fnames:
        fpath = os.path.join(directory, fname)
        if is_dicom(fpath):
            dicom_paths.append(fpath)

    return dicom_paths


def check_duplicate_slices_dicom(dicom_fpaths):
    """Check for duplicate slices in the dicom.

    :param dicom_fpaths: list of dicom files to convert
    :return boolean: true if the dicoms are fine, false otherwise
    """
    # more than one dicom files downloaded in the folder
    if len(dicom_fpaths) > 2:
        new_size = [len(dicom_fpaths), 3]
        orien_mat = np.zeros(new_size)

        for index, dicom_path in enumerate(dicom_fpaths):
            # read the DICOM header
            dcm_header = dicom.read_file(dicom_path)
            try:
                orien_mat[index, ...] = dcm_header[0x0020, 0x0032].value
            except:
                print "    - warning: one dicom could not be read properly \
(no (0020,0032) tag): "+dicom_path
        # Get the axis with the biggest variance = axis used by the scanner
        var_mat = [np.var(orien_mat[:, 0]),
                   np.var(orien_mat[:, 1]),
                   np.var(orien_mat[:, 2])]
        if var_mat[0] == np.max(var_mat):
            col = 0
        elif var_mat[1] == np.max(var_mat):
            col = 1
        else:
            col = 2

        # sort the matrix following the scanner axis
        sorted_orien_mat = orien_mat[orien_mat[:, col].argsort()]
        # compute the matrix of spacing between slices
        diff = sorted_orien_mat[:-1]-sorted_orien_mat[1:]
        spacing_mat = np.sqrt(np.multiply(diff, diff))

        # if this difference is bigger than 0.001, it means that one spacing
        # between two slices is bigger than the spacing between the closest
        # slices ---> some slices are missing
        max_array = [np.max(spacing_mat[:, 0]),
                     np.max(spacing_mat[:, 1]),
                     np.max(spacing_mat[:, 2])]
        min_array = [np.min(spacing_mat[:, 0]),
                     np.min(spacing_mat[:, 1]),
                     np.min(spacing_mat[:, 2])]
        max_spacing_mat = np.subtract(max_array, min_array)
        if max_spacing_mat[col] > 0.001:
            print "    - warning: issues with the dicoms. \
Slices might be missing or duplicated slices."
            return False

    return True


def dcm2nii(dicom_fpath):
    """Convert dicom to nifti using dcm2nii.

    :param dicom_fpath: first dicom in the folder
    :return boolean: true if conversion succeeded, false otherwise
    """
    print "   --> convert dcm to nii..."
    dcm2nii_cmd = '''{dcm2nii} \
-a n -e n -d n -g y -f n -n y -p n -v y -x n -r n \
{dicom}'''.format(dcm2nii=DCM2NII_EXE, dicom=dicom_fpath)
    try:
        sb.check_output(dcm2nii_cmd.split())
    except sb.CalledProcessError:
        print "    - warning: dcm to nii conversion failed"
        return False

    return True


def dcmdjpeg(dcm_dir):
    """Converting the dicom to jpeg dicoms.

    :param dcm_dir: directory containing the dicoms
    """
    print "   --> run dcmdjpeg on the DICOMs to convert \
JPEG DICOM to regular DICOM."
    for number, dicoms in enumerate(os.listdir(dcm_dir)):
        msg = '''{dcmdjpeg} {original_dcm} {new_dcm}'''
        new_dcm = 'final_'+str(number)+'.dcm'
        dcmdjpeg_cmd = msg.format(dcmdjpeg=DCMDJPEG_EXE,
                                  original_dcm=os.path.join(dcm_dir, dicoms),
                                  new_dcm=os.path.join(dcm_dir, new_dcm))
        os.system(dcmdjpeg_cmd)
        os.remove(os.path.join(dcm_dir, dicoms))


def upload_converted_images(dicom_files, dcm_dir, scan_obj):
    """Upload the images after checking them.

    :param dicom_files: list of dicoms files to zip
    :param dcm_dir: directory containing the dicoms
    :param scan_obj: scan pyxnat object from XNAT
    """
    # Local variables
    nifti_list = []
    bval_fpath = ''
    bvec_fpath = ''

    # Get the bvec/bval files and NIFTI from the folder:
    for fpath in glob.glob(os.path.join(dcm_dir, '*')):
        if os.path.isfile(fpath):
            if fpath.lower().endswith('.bval'):
                bval_fpath = fpath
            if fpath.lower().endswith('.bvec'):
                bvec_fpath = fpath
            if fpath.lower().endswith('.nii.gz'):
                nifti_list.append(fpath)
            if fpath.lower().endswith('.nii'):
                os.system('gzip '+fpath)
                nifti_list.append(fpath+'.gz')

    # Check NIFTI:
    good_to_upload = check_outputs(nifti_list, bval_fpath, bvec_fpath)
    # Upload files:
    if good_to_upload:
        if os.path.isfile(bval_fpath) and os.path.isfile(bvec_fpath):
            # BVAL/BVEC
            XnatUtils.upload_file_to_obj(bval_fpath,
                                         scan_obj.resource('BVAL'),
                                         remove=True)
            XnatUtils.upload_file_to_obj(bvec_fpath,
                                         scan_obj.resource('BVEC'),
                                         remove=True)
            # keep the NII with the same name than the BVAL/BVEC
            nifti_list = filter(lambda x: x[:-7] == bval_fpath[:-5],
                                nifti_list)
            XnatUtils.upload_files_to_obj(nifti_list,
                                          scan_obj.resource('NIFTI'),
                                          remove=True)
        else:
            # NII
            XnatUtils.upload_files_to_obj(nifti_list,
                                          scan_obj.resource('NIFTI'),
                                          remove=True)

        # ZIP the DICOM if more than one
        if len(dicom_files) > 1 and OPTIONS.zip_dicoms:
            # Remove the files created before zipping:
            for nii_file in nifti_list:
                os.remove(nii_file)
            if os.path.isfile(bval_fpath) and os.path.isfile(bvec_fpath):
                os.remove(bval_fpath)
                os.remove(bvec_fpath)
            print '   --> more than one dicom file, zipping dicoms.'
            fzip = 'dicoms.zip'
            initdir = os.getcwd()
            # Zip all the files in the directory
            os.chdir(dcm_dir)
            os.system('zip -r '+fzip+' * > /dev/null')
            # return to the initial directory:
            os.chdir(initdir)
            # upload
            if os.path.exists(os.path.join(dcm_dir, fzip)):
                print '   --> uploading zip dicoms'
                scan_obj.resource('DICOM').delete()
                scan_obj.resource('DICOM').put_zip(os.path.join(dcm_dir, fzip),
                                                   overwrite=True,
                                                   extract=False)

        # more than one NIFTI uploaded
        if len(nifti_list) > 1:
            print "    - warning: more than one NIFTI upload"


def check_outputs(nifti_list, bval, bvec):
    """Check that the outputs are right (opening nifti works).

    :param nifti_list: python list of nifti paths
    :param bval: python list of bval paths
    :param bvec: python list of bvec paths
    :return boolean: true if outputs are fine, false otherwise
    """
    for nifti_fpath in nifti_list:
        try:
            nib.load(nifti_fpath)
        except:
            msg = '''    - warning: {file} is not a proper NIFTI'''
            print msg.format(file=os.path.basename(nifti_fpath))
            return False
    if bval or bvec:
        if not os.path.isfile(bval) or not os.path.isfile(bvec):
            print "    - warning: no bval/bvec generated (DTI scan)"
            return False

    return True


def convert_DICOM():
    """Loop through the project scans to convert DICOM to NIFTI."""
    list_scans = XnatUtils.list_project_scans(XNAT, OPTIONS.project)
    # filter the list to keep scans with DICOM and no NIFTI
    if not OPTIONS.force:
        print "Filtering list of scans to keep scans with DICOM but no NIFTI."
        list_scans = filter(
         lambda x: 'DICOM' in x['resources'] and 'NIFTI' not in x['resources'],
         list_scans)
    else:
        print "Filtering list of scans to keep scans with DICOM."
        list_scans = filter(lambda x: 'DICOM' in x['resources'], list_scans)
    # if sessions, filter:
    if OPTIONS.sessions:
        list_scans = filter(
            lambda x: x['session_label'] in OPTIONS.sessions.split(','),
            list_scans)
    number_scans = len(list_scans)
    print "Converting the %s scans found." % (number_scans)
    for index, scan in enumerate(sorted(list_scans,
                                        key=lambda k: k['session_label'])):
        message = ' * {index}/{total} -- Session: {session} -- Scan: {scan}'
        print message.format(index=index+1,
                             total=number_scans,
                             session=scan['session_label'],
                             scan=scan['ID'])
        scan_obj = XnatUtils.get_full_object(XNAT, scan)
        if scan_obj.exists() and \
           len(scan_obj.resource('DICOM').files().get()) > 0:
            print "   --> downloading DICOM ..."
            fpaths = XnatUtils.download_files_from_obj(
                        OPTIONS.directory,
                        scan_obj.resource("DICOM"))
            if not fpaths:
                print '    - warning: DICOM -- no files.'
            else:
                if OPTIONS.force and scan_obj.resource('NIFTI').exists():
                    scan_obj.resource('NIFTI').delete()

                dcm_dir = os.path.join(OPTIONS.directory, 'DICOM')
                if len(fpaths) == 1 and fpaths[0].endswith('.zip'):
                    if not os.path.exists(dcm_dir):
                        os.makedirs(dcm_dir)
                    os.system('unzip -d %s -j %s > /dev/null' % (dcm_dir,
                                                                 fpaths[0]))
                    os.remove(fpaths[0])
                dicom_files = get_dicom_list(dcm_dir)

                if dicom_files:
                    # Check for duplicate dicoms:
                    if OPTIONS.check_dcm:
                        check_duplicate_slices_dicom(dicom_files)
                    # convert dcm to nii
                    conversion_status = dcm2nii(dicom_files[0])

                    if not conversion_status:
                        # Convert dcm via dcmdjpeg
                        dcmdjpeg(dcm_dir)
                        # try again dcm2nii
                        dcm_fpath = os.path.join(dcm_dir, 'final_1.dcm')
                        conversion_status = dcm2nii(dcm_fpath)

                    # Check if Nifti created:
                    nii_li = [f for f in os.listdir(dcm_dir)
                              if f.endswith('.nii.gz') or f.endswith('.nii')]
                    if not nii_li:
                        print "    - warning: dcm to nii failed with \
conversion dcmjpeg. no upload."
                    else:
                        # UPLOADING THE RESULTS
                        upload_converted_images(dicom_files, dcm_dir, scan_obj)

                    # clean tmp folder
                    XnatUtils.clean_directory(OPTIONS.directory)
                else:
                    print "    - ERROR : no proper DICOM files \
found from the resource on XNAT. "

        else:
            print "    - ERROR : issue with resource DICOM: \
no files or resource. "


def executable_exists(executable):
    """Method to check the executable.

    :param executable: executable path
    :param name: name of Executable
    :return: Complete path to the executable
    """
    if os.path.sep not in executable:  # if no separator in executable
        if True in [os.path.isfile(os.path.join(path, executable)) and
                    os.access(os.path.join(path, executable), os.X_OK)
                    for path in os.environ["PATH"].split(os.pathsep)]:
            return True
    else:
        if os.path.isfile(executable):
            return True
    return False


def version_exe(executable):
    """Method to check the executable and it's version.

    :param executable: executable path
    """
    if executable_exists(executable):
        # Print version for Niftyreg - GIFi
        ppath = sb.Popen(['which', executable], stdout=sb.PIPE, stderr=sb.PIPE)
        dcm2nii_path, _ = ppath.communicate()
        pversion = sb.Popen([executable], stdout=sb.PIPE, stderr=sb.PIPE)
        dcm2nii_vers, _ = pversion.communicate()
        msg = 'Executable: %s - version: %s - path: %s'
        print msg % (os.path.basename(executable),
                     dcm2nii_path.strip(),
                     dcm2nii_vers.strip().split('\n')[0])
    else:
        raise Exception('Executable %s not found. Check that the file exists.'
                        % executable)


if __name__ == '__main__':
    OPTIONS = parse_args()
    print 'Converting DICOM to NIFTI for Project:\t%s' % OPTIONS.project
    print 'Time: ', str(datetime.now())

    # Check executables
    DCM2NII_EXE = OPTIONS.dcm2nii
    DCMDJPEG_EXE = OPTIONS.dcmdjpeg
    version_exe(DCM2NII_EXE)
    version_exe(DCMDJPEG_EXE)

    # set a directory where the files are download
    OPTIONS.directory = XnatUtils.makedir(OPTIONS.directory)

    # Connection to Xnat
    try:
        if OPTIONS.username:
            msg = """password for user <%s>:""" % OPTIONS.username
            pwd = getpass.getpass(prompt=msg)
        else:
            pwd = None

        XNAT = XnatUtils.get_interface(host=OPTIONS.host,
                                       user=OPTIONS.username,
                                       pwd=pwd)
        convert_DICOM()
    finally:
        XNAT.disconnect()
    print '=================================================================\n'
