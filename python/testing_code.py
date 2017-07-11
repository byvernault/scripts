"""TEST Script for different purpose."""

import os
from collections import OrderedDict
# import re
import glob
# import fnmatch
import dicom
import re
import shutil
import xml.etree.ElementTree as ET
# import time
import datetime
import nibabel as nib
import numpy as np
# import scipy
# import collections
from dax import XnatUtils, DAX_Settings, spiders
# import shlex

DAX_SETTINGS = DAX_Settings()
RESULTS_DIR = DAX_SETTINGS.get_results_dir()
__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'


# def write_files(nii_file, bval):
#     basedir = os.path.dirname(nii_file)
#     basename = os.path.basename(nii_file).split('.')[0]
#     bval_file = os.path.join(basedir, '{}.bval'.format(basename))
#     bvec_file = os.path.join(basedir, '{}.bvec'.format(basename))
#     with open(bval_file, 'w') as _bval:
#         _bval.write(' '.join(bval))
#     with open(bvec_file, 'w') as _bvec:
#         _bvec.write(' '.join(bval) + '\n')
#         _bvec.write(' '.join(bval) + '\n')
#         _bvec.write(' '.join(bval))
#     return bval_file, bvec_file


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


if __name__ == "__main__":
    directory = '/cluster/project0/DAX/jobsdir'
    for folder in os.listdir(directory):
        print('Assessor: {}'.format(folder))
        asr_label = folder
        if not asr_label.endswith('GIF_Parcellation_v3'):
            continue

        tmpdirs = glob.glob(os.path.join(directory, folder, 'TempDir_2017_6*'))
        if len(tmpdirs) > 0:
            # Use this dir
            JOB_DIR = tmpdirs[0]
        else:
            JOB_DIR = os.path.join(directory, folder)

        if good_folder():
            print('  creating PDF')
            make_pdf()

            pdf = os.path.join(JOB_DIR, 'GIF_parcellation.pdf')
            if not os.path.exists(pdf):
                print('  Failed to create PDF.')
                continue

            bias_corrected = glob.glob(os.path.join(JOB_DIR,
                                       '*bias_corrected.nii.gz'))
            brain = glob.glob(os.path.join(JOB_DIR, '*brain.nii.gz'))
            labels = glob.glob(os.path.join(JOB_DIR, '*labels.nii.gz'))
            prior = glob.glob(os.path.join(JOB_DIR, '*prior.nii.gz'))
            seg = glob.glob(os.path.join(JOB_DIR, '*seg.nii.gz'))
            tiv = glob.glob(os.path.join(JOB_DIR, '*tiv.nii.gz'))

            asr_dir = os.path.join(RESULTS_DIR, asr_label)
            if not os.path.exists(asr_dir):
                print('  Copy data for {}'.format(asr_label))
                os.makedirs(asr_dir)
                res_dir = os.path.join(asr_dir, 'PDF')
                os.makedirs(res_dir)
                shutil.move(pdf, res_dir)
                res_dir = os.path.join(asr_dir, 'BIAS_COR')
                os.makedirs(res_dir)
                shutil.move(bias_corrected[0], res_dir)
                res_dir = os.path.join(asr_dir, 'BRAIN')
                os.makedirs(res_dir)
                shutil.move(brain[0], res_dir)
                res_dir = os.path.join(asr_dir, 'LABELS')
                os.makedirs(res_dir)
                shutil.move(labels[0], res_dir)
                res_dir = os.path.join(asr_dir, 'PRIOR')
                os.makedirs(res_dir)
                shutil.move(prior[0], res_dir)
                res_dir = os.path.join(asr_dir, 'SEG')
                os.makedirs(res_dir)
                shutil.move(seg[0], res_dir)
                res_dir = os.path.join(asr_dir, 'TIV')
                os.makedirs(res_dir)
                shutil.move(tiv[0], res_dir)
                fname = os.path.join(asr_dir, 'READY_TO_UPLOAD.txt')
                with open(fname, 'a'):  # Create file if does not exist
                    os.utime(fname, None)
