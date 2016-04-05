#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import numpy as np
import nibabel as nib
import matplotlib.cm as cm
import matplotlib.pyplot as plt

# PDF path:
output_dir = '/Users/byvernault/outputs'
pdf_page1 = 'GIF_parcellation_page1.pdf'
pdf_page2 = 'GIF_parcellation_page2.pdf'
pdf_final = 'GIF_parcellation.pdf'

# Images outputs:
bias_corrected = os.path.join(output_dir, 'asyi017_20101007-0002-Sag_MPRAGE-m_bias_corrected.nii.gz')
brain = os.path.join(output_dir, 'asyi017_20101007-0002-Sag_MPRAGE-m_brain.nii.gz')
labels = os.path.join(output_dir, 'asyi017_20101007-0002-Sag_MPRAGE-m_labels.nii.gz')
prior = os.path.join(output_dir, 'asyi017_20101007-0002-Sag_MPRAGE-m_prior.nii.gz')
seg = os.path.join(output_dir, 'asyi017_20101007-0002-Sag_MPRAGE-m_seg.nii.gz')
tiv = os.path.join(output_dir, 'asyi017_20101007-0002-Sag_MPRAGE-m_tiv.nii.gz')

# Volumes:
volumes = os.path.join(output_dir, 'asyi017_20101007-0002-Sag_MPRAGE-m_volumes.csv')

print "--Page 1--"
# fig
fig = plt.figure(figsize=(15,14))
list_images = [bias_corrected, brain, labels, seg, tiv, prior]
y_labels = ['Bias Corrected', 'Brain', 'labels', 'Segmentation', 'tiv', 'prior']
list_cmaps = [cm.Greys_r, cm.Greys_r, None, cm.Greys_r, cm.Greys_r, None]

print "Number of images: ", len(list_images)
print "Number of images per line:",3

for index, image_file in enumerate(list_images):
    # Open niftis with nibabel
    f_img = nib.load(image_file)
    f_img_data = f_img.get_data()

    # Draw
    if len(f_img_data.shape) == 3:
        ax = fig.add_subplot(len(list_images),3,3*index+1)
        ax.imshow(np.rot90(f_img_data[:,:,f_img_data.shape[2]/2]), cmap = list_cmaps[index])
        if index == 0:
            ax.set_title('Axial', fontsize=10)
        ax.set_ylabel(y_labels[index])
        ax.set_xticks([])
        ax.set_yticks([])
        #ax.set_axis_off()
        ax = fig.add_subplot(len(list_images),3,3*index+2)
        ax.imshow(np.rot90(f_img_data[:,f_img_data.shape[1]/2,:]), cmap = list_cmaps[index])
        if index == 0:
            ax.set_title('Coronal', fontsize=10)
        ax.set_axis_off()
        ax = fig.add_subplot(len(list_images),3,3*index+3)
        ax.imshow(np.rot90(f_img_data[f_img_data.shape[0]/2,:,:]), cmap = list_cmaps[index])
        if index == 0:
            ax.set_title('Sagittal', fontsize=10)
        ax.set_axis_off()
    elif len(f_img_data.shape) == 4:
        ax = fig.add_subplot(len(list_images),3,3*index+1)
        ax.imshow(np.rot90(f_img_data[:,:,f_img_data.shape[2]/2,f_img_data.shape[3]/2]), cmap = list_cmaps[index])
        if index == 0:
            ax.set_title('Axial', fontsize=10)
        ax.set_ylabel(y_labels[index])
        ax.set_xticks([])
        ax.set_yticks([])
        #ax.set_axis_off()
        ax = fig.add_subplot(len(list_images),3,3*index+2)
        ax.imshow(np.rot90(f_img_data[:,f_img_data.shape[1]/2,:,f_img_data.shape[3]/2]), cmap = list_cmaps[index])
        if index == 0:
            ax.set_title('Coronal', fontsize=10)
        ax.set_axis_off()
        ax = fig.add_subplot(len(list_images),3,3*index+3)
        ax.imshow(np.rot90(f_img_data[f_img_data.shape[0]/2,:,:,f_img_data.shape[3]/2]), cmap = list_cmaps[index])
        if index == 0:
            ax.set_title('Sagittal', fontsize=10)
        ax.set_axis_off()

# Print on a PDF:
plt.subplots_adjust(wspace=1, hspace=1)
plt.show()
fig.savefig(os.path.join(output_dir, pdf_page1), transparent=True, orientation='portrait', dpi=300)

print "--Page 2--"
# CSV:
#volumes_info = list()
fig.clf()
with open(volumes, 'rb') as csvfileread:
    csvreader = csv.reader(csvfileread, delimiter=',')
    list_labels_name = csvreader.next()
    list_labels_volume = csvreader.next()
    #for index, name in enumerate(list_labels_name):
    #    volumes_info.append(dict(zip(['Label Name', "Volume"], [name, list_labels_volume[index]])))

#do the table
print len(list_labels_volume)
print len(list_labels_name)
print len(['Volume'])
the_table = plt.table(cellText=list_labels_volume,
                      rowLabels=list_labels_name,
                      colLabels=['Volume'],
                      loc='bottom')
plt.title('Volumes')
plt.show()
fig.savefig(os.path.join(output_dir, pdf_page2), transparent=True, orientation='portrait', dpi=300)
