"""TEST number 2 Script for different purpose."""

import os
import time
import glob
import dicom
import datetime
import numpy as np
import nibabel as nib
from dax import XnatUtils
from scipy import ndimage
from dicom.sequence import Sequence
from dicom.dataset import Dataset, FileDataset

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Test Code 2"


if __name__ == '__main__':
    pdf_title = 'Registration Verdict - acquisition %d'
    list_slices = [3, 6, 9, 12]
    slices = {'0': list_slices,
              '1': list_slices,
              '2': list_slices,
              '3': list_slices,
              '4': list_slices}
    labels = {'0': 'b3000',
              '1': 'b2000',
              '2': 'b1500',
              '3': 'b500',
              '4': 'b90'}
    images = ['/Users/byvernault/data/registration_INN-004/inputs/901/1.2.826.0.1.1817913.212.1.1.1.53906756-901-1-139a03t.nii.gz',
              '/Users/byvernault/data/registration_INN-004/outputs/1001/1001_b2000_vx1.3_1_reg.nii',
              '/Users/byvernault/data/registration_INN-004/outputs/1101/1101_b2000_vx1.3_1_reg.nii',
              '/Users/byvernault/data/registration_INN-004/outputs/1201/1201_b1500_vx1.3_1_reg.nii',
              '/Users/byvernault/data/registration_INN-004/outputs/1301/1301_b500_vx1.3_1_reg.nii']
    for im in images:
        images = list()
        labels = dict()
        sorted_list = sorted(self.acquisitions[i],
                             key=lambda k: int(k['ID']))
        for index, scan_info in enumerate(sorted_list):
            labels[str(index)] = scan_info['type']
            images.append(self.acquisitions[i][index]['reg'])

    # Saved pages:
    pdf_page = os.path.join(self.jobdir, 'registration_page_%d.pdf'
                                         % page_number)

    self.plot_images_page(pdf_page, 1, images,
                          pdf_title % (1), image_labels=labels,
                          slices=slices, volume_ind=0)
    pdf_pages[page_number] = pdf_page
    # Merge pages:
    self.merge_pdf_pages(pdf_pages, self.pdf_final)
