#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Make preview from the NIFTI resources on a project from XNAT.


Requirements:
    package: nibabel/scipy/numpy
    file in pythonpath: XnatUtils (see in this project)
"""

import os
import getpass
import scipy as sp
import numpy as np
import nibabel as nib
from datetime import datetime
from dax import XnatUtils

__author__ = 'byvernault'
__email__ = 'byvernault@gmail.com'
__purpose__ = "Generates snapshots/preview for the scans for all subjects \
in a project."
__version__ = '1.0.0'
__modifications__ = '19 August 2015 - Original write'


def parse_args():
    """Parser for arguments."""
    from argparse import ArgumentParser
    argp = ArgumentParser(prog='make_preview_xnat', description=__purpose__)
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
    argp.add_argument('-r', '--resource', dest='resource',
                      help='Nifti resource name on Xnat.', default='NIFTI')
    argp.add_argument('-f', '--force', dest='force', action='store_true',
                      help='Force the creation of preview.')
    return argp.parse_args()


def make_preview_nifti(xnat, options):
    """generate previewe for a project on XNAT."""
    # make directory
    if not os.path.exists(options.directory):
        os.makedirs(options.directory)

    # list of scans for the project
    list_scans = XnatUtils.list_project_scans(xnat, options.project)
    # filter the list to keep scans with DICOM and no NIFTI
    if not options.force:
        print "Filtering scans to keep scans with NIFTI but no SNAPSHOTS."
        list_scans = filter(lambda x: 'NIFTI' in x['resources'] and
                                      'SNAPSHOTS' not in x['resources'],
                            list_scans)
    # if sessions, filter:
    if options.sessions:
        list_scans = filter(
            lambda x: x['session_label'] in options.sessions.split(','),
            list_scans)
    number_scans = len(list_scans)
    for index, scan in enumerate(sorted(list_scans,
                                        key=lambda k: k['session_label'])):
        message = ' * {index}/{total} -- Session: {session} -- Scan: {scan}'
        print message.format(index=index+1,
                             total=number_scans,
                             session=scan['session_label'],
                             scan=scan['ID'])
        scan_obj = XnatUtils.get_full_object(xnat, scan)

        res_obj = scan_obj.resource(options.resource)
        if res_obj.exists() and len(res_obj.files().get()) > 0:
            if options.force and scan_obj.resource("SNAPSHOTS").exists():
                scan_obj.resource("SNAPSHOTS").delete()
            print "   --> downloading "+options.resource+" ..."
            filename = XnatUtils.download_biggest_file_from_obj(
                                            options.directory, res_obj)
            if not filename:
                print '    - warning: '+options.resource+' -- no files.'
            else:
                if filename.endswith('.nii.gz'):
                    os.system('gzip -d '+filename)
                    filename = filename[:-3]
                fname = os.path.basename(filename).split('.')[0] + "_sm.gif"
                smgif = os.path.join(options.directory, fname)
                fname = os.path.basename(filename).split('.')[0] + "_lg.gif"
                lggif = os.path.join(options.directory, fname)

                status = generate_preview(filename, smgif, lggif)

                if not status:
                    print '   --> GIF FAILED'
                else:
                    if os.path.isfile(smgif):
                        print '   --> GIF Made / upload to XNAT...'
                        scan_obj.resource('SNAPSHOTS').file('snap_t.gif')\
                                .put(smgif, 'GIF', 'THUMBNAIL')
                        scan_obj.resource('SNAPSHOTS').file('snap.gif')\
                                .put(lggif, 'GIF', 'ORIGINAL')
                    else:
                        print '   --> GIF FAILED'

                    if os.path.isfile(smgif):
                        os.remove(smgif)
                        os.remove(lggif)

                if os.path.isfile(filename):
                    os.remove(filename)
        else:
            print("    - ERROR : issue with resource %s: no file or resource. "
                  % (options.resource))


def generate_preview(nifti, smgif, lggif):
    """generate snapshots of the nifti given as parameters.

    :param nifti: path to the nifti file
    :param smgif: path for small gif file
    :param lggif: path for large gif file

    :return boolean: false if fail, true otherwise
    """
    print "   --> Generating snapshots "+nifti
    nii = load_nifti(nifti)

    if nii:
        # fix direction from the nifti to have proper snapshots
        data = get_data(nii)
        if not data.any():
            return False
        size = data.shape
        dtype = str(data.dtype)
        if size[2] > 100:
            # Keep 100 slices from the nifti
            data = resize_100_slices(data)
        # Expanding the matrix
        data = np.expand_dims(data, axis=3)
        # transpose third and fourth dimension
        final_data = np.transpose(data, (0, 1, 3, 2))
        if "float" in dtype.lower():
            # rescale our final data
            final_data = rescale(final_data)
        # Generate our big size1 * size2 numpyArray for snapshots
        size = final_data.shape
        n2 = np.ceil(np.sqrt(size[3]))
        out = np.zeros([n2*size[0], n2*size[1]])
        row = 0
        col = 0
        for i in range(size[3]):
            if col >= n2:
                row += 1
                col = 0

            out[(size[0]*row):(size[0]+size[0]*row),
                (size[1]*col):(size[1]+size[1]*col)] = final_data[:, :, 0, i]
            col += 1

        # Save the images as gif for small and large snapshots:
        sp.misc.imsave(smgif,
                       sp.misc.imresize(np.multiply(out, 255), (512, 512)))
        sp.misc.imsave(lggif, np.multiply(out, 255))
        return True
    else:
        return False


def get_data(nii_obj):
    """Extract the data from the nifti.

    Rotate the images depending on the orientation
    :param nii_obj: nibabel nifti object
    :return: return data from the nifti or null if no data
    """
    try:
        data = nii_obj.get_data()
    except IOError as e:
        print "    - ERROR: can not extract the data from the NIFTI file. \
The traceback is the following:"
        print e
        return None
    # rotating if bitpix is 16 (hack)
    if nii_obj.header['bitpix'] == 16:
        print "   --> Rotating 90 degres slices"
        data = np.rot90(data)

    # Reshape if 4D images
    size = data.shape
    if len(size) == 4:
        # Reshape the numpay array in a 3D array
        # (swap axes to keep matlab standard)
        sl = reduce(lambda x, y: x*y, size[2:])
        data = np.swapaxes(data, 2, 3).reshape((size[0], size[1], sl))
    return data


def load_nifti(nifti):
    """Load nifti as a nibabel object.

    :param nifti: path to the nifti file
    :return: return NIFTI object or None
    """
    if not os.path.exists(nifti):
        print "load_nifti - error - couldn't find the file "+nifti
        return None
    try:
        nii = nib.load(nifti)
        return nii
    except:
        print "load_nifti - error - couldn't open NIFTI "+nifti
        return None


def resize_100_slices(data):
    """Resize array to keep only 100 slices.

    :param data: numpy array of the data
    :return: new array resized [x,y,100]
    """
    print "   --> Limiting to 100 Slices"
    size = data.shape
    slices_list = np.round(np.linspace(0, size[2]-1, num=100))
    new_size = [size[0], size[1], len(slices_list)]
    new_array = np.zeros(new_size)
    # looping through array
    for index, i in enumerate(slices_list):
        new_array[..., index] = data[..., i]

    return new_array


def rescale(data):
    """rescale python Array with user-defined min and max.

    :param data: numpy array
    :return: array rescale
    """
    # Min and Max
    a_max = data.max()
    a_min = data.min()
    # Rescale the data between 0.0 - 1.0
    rescale_array = (data-a_min)/(a_max/2-a_min)
    rescale_array[rescale_array > 1.0] = 1.0

    return rescale_array

if __name__ == '__main__':
    OPTIONS = parse_args()
    print('Making Preview from NIFTI format images for Project:\t%s'
          % OPTIONS.project)
    print 'Time: ', str(datetime.now())

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
        make_preview_nifti(XNAT, OPTIONS)
    finally:
        XNAT.disconnect()
    print '================================================================\n'
