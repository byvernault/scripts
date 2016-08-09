"""TEST Script for different purpose."""

import os
import glob
import dicom
import dicom.UID
import nibabel as nib
import numpy as np
from PIL import Image

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Test Code"


def find_first(item, array):
    """return the index of the first occurence of item in vec."""
    for ind in range(array.shape[0]):
        for jnd in range(array.shape[1]):
            if item == array[ind, jnd]:
                return ind, jnd
    return -1, -1


def change_matrix(array):
    """return the index of the first occurence of item in vec."""
    new_array = np.zeros(shape=array.shape)
    size = array.shape[1]
    for ind in range(array.shape[0]):
        for jnd in range(array.shape[1]):
            new_array[ind, size-jnd-1] = array[ind, jnd]
    return new_array


def order_dcm(folder):
    """return the index of the first occurence of item in vec."""
    dcm_files = dict()
    for dc in glob.glob(os.path.join(folder, '*.dcm')):
        dst = dicom.read_file(dc)
        dcm_files[float(dst.SliceLocation)] = dc
    return dcm_files

if __name__ == '__main__':
    directory = '/Users/byvernault/Downloads/scans_2/'
    # dicom_folder = '/Users/byvernault/Downloads/test_2_nii_TMA183/'
    only_one = True
    for scan in os.listdir(directory):
        if only_one and os.path.isdir(os.path.join(directory, scan)):
            print 'SCAN: %s' % scan
            output_dir = os.path.join(directory, scan, 'PNG')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            dicom_files = glob.glob(os.path.join(directory, scan,
                                                 'DICOM', '*'))[0]

            print dicom_files
            if os.path.exists(os.path.join(directory, scan, 'NIFTI')):
                # Nifti
                nifti_file = glob.glob(os.path.join(
                    directory, scan, 'NIFTI', '*.nii.gz'))[0]
                print 'nii: %s' % nifti_file
                # Load image from NIFTI
                f_img = nib.load(nifti_file)
                f_img_data = f_img.get_data()

                # load the dicom:
                dicom_array = np.zeros(shape=f_img_data.shape)
                # for index in range(f_img_data.shape[2]):
                #    ds = dicom.read_file(dicom_files[index+1])
                index = 0
                issue = False
                if isinstance(dicom_files, dict):
                    for _, dcm in dicom_files.items():
                        ds = dicom.read_file(dcm)
                        d = np.fromstring(ds.PixelData, dtype=np.int16)
                        d = d.reshape((ds.Columns, ds.Rows))
                        # fnii = f_img_data[:,:,index]
                        fnii = np.rot90(f_img_data[:, :, index])
                        # fnii = change_matrix(fnii)
                        # if 'VISTA' in nifti_file or 'DCE' in nifti_file:
                        #     fnii = change_matrix(fnii)
                        """for i in range(d.shape[0]):
                            for j in range(d.shape[1]):
                                print "Indexes (%d,%d): %d -- %d " % (i, j,
                                                                      d[i,j],
                                                                      fnii[i,j])
                                if d[i,j] != fnii[i,j]:
                                    print "  Error"
                                    raw_input()"""
                        dicom_array[:, :, index] = d-fnii
                        index += 1

                    for i in range(dicom_array.shape[2]):
                        if np.amax(dicom_array[:, :, i]) != 0.0 \
                          or np.amin(dicom_array[:, :, i]) != 0.0:
                            print('Issue - Index: %d - Max: %f - Min: %f '
                                  % (i, np.amax(dicom_array[:, :, i]),
                                     np.amin(dicom_array[:, :, i])))
                            issue = True
                        im = Image.fromarray(dicom_array[:, :, i])
                        if im.mode != 'RGB':
                            im = im.convert('RGB')
                        im.save(os.path.join(output_dir,
                                             scan+"_"+str(i)+".png"))
                else:
                    ds = dicom.read_file(dicom_files)
                    d = np.fromstring(ds.PixelData, dtype=np.int16)
                    if len(f_img_data.shape) == 3:
                        d = d.reshape((ds.Columns, ds.Rows,
                                       f_img_data.shape[2]))
                    elif len(f_img_data.shape) == 4:
                        third = ds.NumberOfFrames / f_img_data.shape[2]
                        d = d.reshape((ds.Columns, ds.Rows,
                                       f_img_data.shape[2],
                                       third))
                        if third > f_img_data.shape[3]:
                            d = d[:, :, :, :-1]  # removing last volume (sum)
                            print 'warning: removing last volume.'
                    elif len(f_img_data.shape) == 2:
                        d = d.reshape((ds.Columns, ds.Rows))
                    else:
                        raise Exception('error: dim unknown.')
                    for i in range(f_img_data.shape[3]):
                        for j in range(f_img_data.shape[2]):
                            for b in range(f_img_data.shape[1]):
                                for a in range(f_img_data.shape[0]):
                                    print 'Value: %s  --  %s ' % (d[a, b, j, i],
                                                                  f_img_data[a, b, j, i])
                                    print f_img_data[a, b, j, i]/d[a, b, j, i]
                    dicom_array = d - f_img_data

                    for i in range(dicom_array.shape[3]):
                        for j in range(dicom_array.shape[2]):
                            if np.amax(dicom_array[:, :, j, i]) != 0.0 \
                              or np.amin(dicom_array[:, :, j, i]) != 0.0:
                                print('Issue - Index: %d - Max: %f - Min: %f '
                                      % (i, np.amax(dicom_array[:, :, j, i]),
                                         np.amin(dicom_array[:, :, j, i])))
                                issue = True
                            im = Image.fromarray(dicom_array[:, :, j, i])
                            if im.mode != 'RGB':
                                im = im.convert('RGB')
                            im.save(os.path.join(output_dir,
                                                 scan+"_"+str(i)+".png"))

                if not issue:
                    print 'Good convertion'
