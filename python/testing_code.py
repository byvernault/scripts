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
import Ben_functions

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Test Code"

EPOCH_DATE = datetime.datetime(1899, 12, 30)


def get_date(excel_date):
    """Calculate date from excel integer number of days.

    :param excel_date: date read from excel
    """
    get_ = datetime.timedelta(excel_date)
    get_col2 = str(EPOCH_DATE + get_)[:10]
    d = datetime.datetime.strptime(get_col2, '%Y-%m-%d')
    get_col = d.strftime('%Y%m%d')
    return get_col


if __name__ == '__main__':
    """host = 'https://qs-controls.cs.ucl.ac.uk'
    user = os.environ['XNAT_USER']
    pwd = os.environ['XNAT_PASS']

    xnat = XnatUtils.get_interface(host=host, user=user, pwd=pwd)

    for scan in XnatUtils.list_project_scans(xnat, projectid='control_DRC'):
        scan_obj = XnatUtils.get_full_object(xnat, scan)
        if scan_obj.exists():
            file_name = scan_obj.resource('NIFTI').files().get()[0]
            print 'control_DRC,%s,%s,%s' % (scan['subject_label'],
                                            scan['session_label'],
                                            file_name.split('.')[0].split('-')[0])"""
    excel_sheets = XnatUtils.read_excel(
                '/Users/byvernault/Downloads/QS_Control_DBinfo_DRC_EG.xlsx')

    name_code = dict()
    for dic in excel_sheets['retrospective cohort']:
        name = dic['Name'].strip().replace(',', '').replace(' ', '').replace('-', '')
        name_code[int(dic['Image code'])] = name

    xnat_mapping = XnatUtils.read_csv('/Users/byvernault/drc.csv',
                                      header=['project_id', 'subject_label',
                                              'session_label', 'image_code'])

    name_gender_yob = dict()
    for dic in excel_sheets['Sheet3']:
        name = '%s%s' % (dic['Surname'].strip().upper().replace(' ', ''),
                         dic['First name'].strip().upper().replace(' ', ''))
        name_gender_yob[name] = [dic['Gender'],
                                 dic['DOB']]

    print [code for code, name in name_code.items() if name == 'GIRLINGCAROLA']
    print 'code,gender,yob'
    for code, name in name_code.items():
        if name in name_gender_yob:
            subject = [s['subject_label'] for s in xnat_mapping
                       if int(s['image_code']) == code][0]
            value = name_gender_yob[name]
            if value[1] != '?':
                print 'control_DRC,%s,%s,%s' % (subject, value[0],
                                                get_date(value[1])[:4])
            else:
                print 'control_DRC,%s,%s,' % (subject, value[0])
        else:
            print '%s not found for %d' % (name, code)

    # check for code - subject unique link:
    subject_name = dict()
    for s in xnat_mapping:
        subject_found = 0
        for code, name in name_code.items():
            if code == int(s['image_code']):
                subject_found = 1
                if name in subject_name:
                    subject_name[name].append(s['subject_label'])
                else:
                    subject_name[name] = [s['subject_label']]

        if not subject_found:
            print 'subject not found %s ' % s

    for code, li in subject_name.items():
        if len(list(set(li))) > 1:
            print code, li
