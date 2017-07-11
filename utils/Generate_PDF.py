#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generate PDF for a spider.
"""

from collections import OrderedDict
import os
import glob
import xml.etree.ElementTree as ET
from dax import spiders


__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = 'Generate PDF for a spider.'
__version__ = '1.0.0'
__modifications__ = '25 November 2016 - Original write'


def make_pdf():
    """Method to make the PDF for the spider.

    :return: None
    """
    # PDF pages:
    pdf_pages = {
        '1': os.path.join(JOB_DIR, 'GIF_parcellation_page1.pdf'),
        '2': os.path.join(JOB_DIR, 'GIF_parcellation_page2.pdf')
    }

    # Images outputs:
    bias_corrected = glob.glob(os.path.join(JOB_DIR,
                                            '*bias_corrected.nii.gz'))
    brain = glob.glob(os.path.join(JOB_DIR, '*brain.nii.gz'))
    labels = glob.glob(os.path.join(JOB_DIR, '*labels.nii.gz'))
    prior = glob.glob(os.path.join(JOB_DIR, '*prior.nii.gz'))
    seg = glob.glob(os.path.join(JOB_DIR, '*seg.nii.gz'))
    tiv = glob.glob(os.path.join(JOB_DIR, '*tiv.nii.gz'))
    list_images = [bias_corrected, brain, labels, seg, tiv, prior]

    # Page 1:
    images = []
    for index, image_file in enumerate(list_images):
        if len(image_file) != 1:
            err = '%s output image not found or more than one file found.'
            raise Exception(err % (image_file))
        images.append(image_file[0])

    labels = {
        '0': 'Bias Corrected',
        '1': 'Brain',
        '2': 'Labels',
        '3': 'Segmentation',
        '4': 'tiv',
        '5': 'prior'
    }
    cmap = {
        '0': 'gray',
        '1': 'gray',
        '2': None,
        '3': 'gray',
        '4': 'gray',
        '5': None
    }
    spiders.plot_images(pdf_pages['1'], 1, images,
                        'GIF_Parcellation Pipeline',
                        image_labels=labels, cmap=cmap)

    # Page 2
    # Volumes:
    volumes = glob.glob(os.path.join(JOB_DIR, '*volumes.xml'))
    if len(volumes) != 1:
        err = '%s output csv file with information on volumes not found \
or more than one file found.'
        raise Exception(err % (volumes))
    tree = ET.parse(volumes[0])
    root = tree.getroot()
    di_stats = OrderedDict()
    for tissue in root.findall('tissues'):
        for item in tissue.findall('item'):
            di_stats[item.find('name').text] = item.find('volumeProb').text
    for tissue in root.findall('labels'):
        for item in tissue.findall('item'):
            di_stats[item.find('name').text] = item.find('volumeProb').text

    spiders.plot_stats(pdf_pages['2'], 2, di_stats,
                       'Volumes computed by GIF_Parcellation',
                       columns_header=['Label Name', 'Volume ml'])

    # Join the two pages for the PDF:
    pdf_final = os.path.join(JOB_DIR, 'GIF_parcellation.pdf')
    spiders.merge_pdfs(pdf_pages, pdf_final)


def good_folder():
    bias_corrected = glob.glob(os.path.join(JOB_DIR,
                                            '*bias_corrected.nii.gz'))
    brain = glob.glob(os.path.join(JOB_DIR, '*brain.nii.gz'))
    labels = glob.glob(os.path.join(JOB_DIR, '*labels.nii.gz'))
    prior = glob.glob(os.path.join(JOB_DIR, '*prior.nii.gz'))
    seg = glob.glob(os.path.join(JOB_DIR, '*seg.nii.gz'))
    tiv = glob.glob(os.path.join(JOB_DIR, '*tiv.nii.gz'))
    list_images = [bias_corrected, brain, labels, seg, tiv, prior]
    if [] in list_images:
        return False

    return True


if __name__ == '__main__':
    directory = '/Users/byvernault/data/gifs'
    for folder in os.listdir(directory):
        tmpdirs = glob.glob(os.path.join(directory, folder, 'TempDir_2017_6*'))
        if len(tmpdirs) > 0:
            # Use this dir
            JOB_DIR = tmpdirs[0]
        else:
            JOB_DIR = os.path.join(directory, folder)

        if good_folder():
            print('Creating PDF for {}'.format(JOB_DIR))
            make_pdf()
