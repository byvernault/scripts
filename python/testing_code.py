"""TEST Script for different purpose."""

import os
import glob
import dicom
import dicom.UID
from dicom.dataset import Dataset, FileDataset
import shutil
import time
import datetime
import nibabel as nib
import numpy as np
import scipy
import collections
from PIL import Image
from dax import XnatUtils

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Test Code"


def find_first(item, array):
    """return the index of the first occurence of item in vec"""
    for ind in range(array.shape[0]):
        for jnd in range(array.shape[1]):
            if item == array[ind,jnd]:
                return ind,jnd
    return -1, -1

def change_matrix(array):
    new_array = np.zeros(shape=array.shape)
    size = array.shape[1]
    for ind in range(array.shape[0]):
        for jnd in range(array.shape[1]):
            new_array[ind,size-jnd-1] = array[ind,jnd]
    return new_array

def order_dcm(folder):
    dcm_files = dict()
    for dc in glob.glob(os.path.join(folder, '*.dcm')):
        dst = dicom.read_file(dc)
        dcm_files[float(dst.SliceLocation)] = dc
    return dcm_files

if __name__ == '__main__':
    dicom_folder = '/Users/byvernault/Downloads/scans/'
    #dicom_folder = '/Users/byvernault/Downloads/test_2_nii_TMA183/'
    only_one = True
    for scan in os.listdir(dicom_folder):
        if only_one and scan != 'NIFTI' and os.path.isdir(os.path.join(dicom_folder, scan)):
            only_one = True
            print 'SCAN: %s' % scan
            output_dir = os.path.join(dicom_folder, scan, 'PNG')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            dicom_files = order_dcm(os.path.join(dicom_folder, scan))
            #sort:
            dicom_files = collections.OrderedDict(sorted(dicom_files.items()))

            #Nifti
            nifti_file = os.path.join(dicom_folder, 'NIFTI', scan+'.nii.gz')
            print 'nii: %s' % nifti_file
            # Load image from NIFTI
            f_img = nib.load(nifti_file)
            f_img_data = f_img.get_data()

            #load the dicom:
            dicom_array = np.zeros(shape=f_img_data.shape)
            #for index in range(f_img_data.shape[2]):
            #   ds = dicom.read_file(dicom_files[index+1])
            index = 0
            for _, dcm in dicom_files.items():
                ds = dicom.read_file(dcm)
                d = np.fromstring(ds.PixelData, dtype=np.int16)
                d = d.reshape((ds.Columns,ds.Rows))
                #fnii = f_img_data[:,:,index]
                fnii = np.rot90(f_img_data[:,:,index])
                #fnii = change_matrix(fnii)
                #if 'VISTA' in nifti_file or 'DCE' in nifti_file:
                #    fnii = change_matrix(fnii)
                """for i in range(d.shape[0]):
                    for j in range(d.shape[1]):
                        print "Indexes (%d,%d): %d -- %d " % (i, j, d[i,j], fnii[i,j])
                        if d[i,j] != fnii[i,j]:
                            print "  Error"
                            raw_input()"""
                dicom_array[:,:,index] = d-fnii
                index += 1

            issue = False
            for i in range(dicom_array.shape[2]):
                if np.amax(dicom_array[:,:,i]) != 0.0 or np.amin(dicom_array[:,:,i]) != 0.0:
                    print 'Issue - Index: %d - Max: %f - Min: %f ' % (i, np.amax(dicom_array[:,:,i]), np.amin(dicom_array[:,:,i]))
                    issue = True
                im = Image.fromarray(dicom_array[:,:,i])
                if im.mode != 'RGB':
                    im = im.convert('RGB')
                im.save(os.path.join(output_dir, scan+"_"+str(i)+".png"))
            if not issue:
                print 'Good convertion'
