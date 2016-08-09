"""TEST number 2 Script for different purpose."""

import os
import argparse
import sys
import zipfile
# from dax import XnatUtils

# import Ben_functions

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Test Code 2"


def find_files(directory, ext):
    """Return the files in subdirectories witht the right extension.

    :param directory: directory where the data are located
    :param ext: extension to look for
    :return: python list of files
    """
    li_files = list()
    for root, _, filenames in os.walk(directory):
        li_files.extend([os.path.join(root, f) for f in filenames
                         if f.lower().endswith(ext.lower())])
    return li_files


def zip_list(li_files, zip_path, subdir=False):
    """Zip all the files in the list into a zip file.

    :param li_files: python list of files for the zip
    :param zip_path: zip path
    :param subdir: copy the subdirectories as well. Default: False.
    """
    if not zip_path.lower().endswith('.zip'):
        zip_path = '%s.zip' % zip_path
    with zipfile.ZipFile(zip_path, 'w') as myzip:
        for fi in li_files:
            if subdir:
                myzip.write(fi, compress_type=zipfile.ZIP_DEFLATED)
            else:
                myzip.write(fi, arcname=os.path.basename(fi),
                            compress_type=zipfile.ZIP_DEFLATED)


def unzip_list(zip_path, directory):
    """Unzip all the files from the zip file and give the list of files.

    :param zip_path: zip path
    :param directory: directory where to extract the data
    :return: python list of files
    """
    li_files = list()
    if not os.path.exists(directory):
        raise Exception('Folder %s does not exist.')
    with zipfile.ZipFile(zip_path, 'r') as myzip:
        for member in myzip.infolist():
            path = directory
            words = member.filename.split('/')
            for word in words[:-1]:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word in (os.curdir, os.pardir, ''):
                    continue
                path = os.path.join(path, word)
            myzip.extract(member, path)
            li_files.append(path)
    return li_files


if __name__ == '__main__':
    li_files = ['/Users/byvernault/Downloads/mr_240114_Pros-001/inputs/1101-DTI_iso/xDTIisoSENSE.bval',
                '/Users/byvernault/Downloads/mr_240114_Pros-001/inputs/1101-DTI_iso/xDTIisoSENSE.bvec',
                '/Users/byvernault/Downloads/mr_240114_Pros-001/inputs/1101-DTI_iso/xDTIisoSENSE.nii.gz']
    zip_path = '/Users/byvernault/test.zip'
    zip_list(li_files, zip_path)

    raw_input('decompress?')
    li_files2 = unzip_list(zip_path, '/Users/byvernault/testunzip/')
    print "LIST OF FILES: %s" % li_files2
