"""
    Generate csv
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "generate csv."
__version__ = '1.0.0'
__modifications__ = '11 October 2015 - Original write'

import os
#import sys
#import json
import glob
import xlrd
import datetime
from dax import XnatUtils
#import shutil

CSV_TEMPLATE = """scan,{project},{subject},MR,{session},{scan},{type},{series},usable,{resource},{path}"""
CSV_DEMOGRAPHIC = """{project},{subject},{session},{gender},{age},{yob},{education},{genetic},{codon129},{MRC},{geneticstate}"""
CSV_DEMOGRAPHIC2 = """{project},{subject},{dos}"""
EPOCH_DATE = datetime.datetime(1899, 12, 30)

def parse_args():
    """
    Parser for arguments
    """
    from argparse import ArgumentParser
    usage = "Generates csv files from folder."
    argp = ArgumentParser(prog='testing_code', description=usage)
    argp.add_argument('-d', dest='directory',
                      help="Directory where the folders containing the data are stored.")
    argp.add_argument('-e', dest='excelfile',
                      help="Excel xlsx format file containing information.",
                      required=True)
    return argp.parse_args()

def find_subject_date(info_list, slabel, date, label):
    """
        Find the subject from the folder name

        :param info_list: list of information from Excel
        :param slabel: label from the the folder
        :param date: scan date
        :param label: label to check on the csv
        :return: True if the subject was found, False if not and the dict if found
    """
    subjects_list = filter(lambda x: x[label] == slabel, info_list)
    if len(subjects_list) == 0:
        sid = filter(lambda x: x['Hospital ID'] == slabel , INFO_SUBJ)
        if len(sid) > 0:
            subjects_list = filter(lambda x: x[label] == sid[0]['Hospital number'], info_list)
        if len(subjects_list) == 0:
            print '%s not found in the excel spreadsheet for the date %s.' % (slabel, date)
            return False, None
    subject_found = False
    subject_found_dict = None
    for subject_dict in subjects_list:
        if int(get_date(subject_dict['Date of scan'])) ==  int(date):
            subject_found = True
            subject_found_dict = subject_dict.copy()
    if not subject_found:
        if subject_found_dict:
            print '%s not corresponding to date of scan in Excel for %s -- %s' % (date, slabel, subject_found_dict['Hospital ID'])
        else:
            print '%s not corresponding to date of scan in Excel for %s ' % (date, slabel)
    return subject_found, subject_found_dict

def get_date(excel_date):
    """
        Calculate date from excel integer number of days

        :param excel_date: date read from excel
    """
    get_ = datetime.timedelta(excel_date)
    get_col2 = str(EPOCH_DATE + get_)[:10]
    d = datetime.datetime.strptime(get_col2, '%Y-%m-%d')
    get_col = d.strftime('%Y%m%d')
    return get_col

def read_excel():
    """
        Read the excel spreadsheet

        :return: list of dictionaries for the row in excel
    """
    #Read the xlsx file:
    book = xlrd.open_workbook(OPTIONS.excelfile)
    info_list = list()
    for sht in book.sheets():
        if sht.name != 'Subjects_to_Rename':
            header = sht.row_values(0)
            header.append('state')
            prev_row = [None for _ in range(sht.ncols)]
            for row_index in range(1, sht.nrows):
                gstate = ""
                row = list()
                for col_index in range(sht.ncols):
                    value = sht.cell(rowx=row_index, colx=col_index).value
                    if isinstance(value, str) and len(value) == 0:
                        value = prev_row[col_index]
                    if sht.row_values(0)[col_index] == 'Hospital ID' and isinstance(value, float):
                        value = str(int(value))
                    if sht.row_values(0)[col_index] == 'Genetics':
                        if "Asymptomatic" in value:
                            value = value.split("Asymptomatic ")[1].strip()
                            gstate = "Asymptomatic"
                        elif "At risk" in value:
                            value = value.split("At risk ")[1].strip()
                            gstate = "At risk"
                        elif "Symptomatic" in value:
                            value = value.split("Symptomatic ")[1].strip()
                            gstate = "Symptomatic"
                        else:
                            gstate = sht.name
                    row.append(value)
                row.append(gstate)
                prev_row = row
                info_list.append(dict(zip(header, row)))
    return info_list

def read_excel_2():
    """
        Read the excel spreadsheet

        :return: list of dictionaries for the row in excel
    """
    book = xlrd.open_workbook(OPTIONS.excelfile)
    info_list = list()
    for sht in book.sheets():
        if sht.name == 'Subjects_to_Rename':
            header = sht.row_values(0)
            prev_row = [None for _ in range(sht.ncols)]
            for row_index in range(1, sht.nrows):
                row = list()
                for col_index in range(sht.ncols):
                    value = sht.cell(rowx=row_index, colx=col_index).value
                    if isinstance(value, str) and len(value) == 0:
                        value = prev_row[col_index]
                    if isinstance(value, float):
                        value = str(int(value))
                    row.append(value)
                prev_row = row
                info_list.append(dict(zip(header, row)))
    return info_list

def create_upload_data_csv():
    """
        Generate csv file for image data

        :return: list of string to write in a csv string for Xnatupload
    """
    csv_list = list()
    #Gzip the data:
    for filename in glob.glob(os.path.join(OPTIONS.directory, '*', '*MPRAGE*.nii')):
        os.system('gzip '+filename)
    #Read the xlsx file:
    info_list = read_excel()

    for fpath in glob.glob(os.path.join(OPTIONS.directory, '*', '*MPRAGE*.nii.gz')):
        filename = os.path.basename(fpath).rsplit('.nii.gz')[0]
        labels = filename.split('-')
        if len(labels) > 3:
            ss_label = labels[0]
            scan = labels[1]
            stype = labels[2]

            found, subject_dict = find_subject_date(info_list, ss_label.split('_')[0], ss_label.split('_')[1], 'Subject ID')
            if not found:
                if subject_dict:
                    subject = subject_dict['Hospital ID']
                else:
                    subject = ss_label.split('_')[0]
                if isinstance(subject, float) or isinstance(subject, int):
                    subject = str(int(subject))
                session = subject+'_'+ss_label.split('_')[1]
                csvstring = CSV_TEMPLATE.format(project="prion",
                                                subject=subject,
                                                session=session,
                                                scan=scan,
                                                type='MPRAGE',
                                                series=stype,
                                                resource='NIFTI',
                                                path=fpath)
                csv_list.append(csvstring)
            """if found:
                subject = subject_dict['Hospital ID']
                if isinstance(subject, float) or isinstance(subject, int):
                    subject = str(int(subject))
                scan_obj = XnatUtils.select_obj(XNAT, 'prion', subject, subject+'_'+ss_label.split('_')[1], scan)
                if scan_obj.exists():
                    print "Already existing on XNAT: %s/%s/%s " % (subject, subject+'_'+ss_label.split('_')[1], scan)
                else:
                    csvstring = CSV_TEMPLATE.format(project="prion",
                                                    subject=subject,
                                                    session=subject+'_'+ss_label.split('_')[1],
                                                    scan=scan,
                                                    type='MPRAGE',
                                                    series=stype,
                                                    resource='NIFTI',
                                                    path=fpath)
                    csv_list.append(csvstring)
            """
        else:
            print "Error in filename: %s" % (filename)
    return csv_list

def create_upload2_data_csv():
    """
        Generate csv file for image data

        :return: list of string to write in a csv string for Xnatupload
    """
    csv_list = list()
    #Gzip the data:
    for filename in glob.glob(os.path.join(OPTIONS.directory, '*', '*MPRAGE*.nii')):
        os.system('gzip '+filename)
    info_list = read_excel()

    nii_ngz_images = glob.glob(os.path.join(OPTIONS.directory, '*', '*', '*', '*', '*MPRAGE*.nii.gz'))
    for fpath in nii_ngz_images:
        filename = os.path.basename(fpath).rsplit('.nii.gz')[0]
        ss_label, scan, stype, _ = filename.split('-')
        found, subject_dict = find_subject_date(info_list, ss_label.split('_')[0], ss_label.split('_')[1], 'Subject ID')
        if not found:
            if subject_dict:
                subject = subject_dict['Hospital ID']
            else:
                subject = ss_label.split('_')[0]
            if isinstance(subject, float) or isinstance(subject, int):
                subject = str(int(subject))
            session = subject+'_'+ss_label.split('_')[1]
            csvstring = CSV_TEMPLATE.format(project="prion",
                                            subject=subject,
                                            session=session,
                                            scan=scan,
                                            type='MPRAGE',
                                            series=stype,
                                            resource='NIFTI',
                                            path=fpath)
            csv_list.append(csvstring)
        """
        if found:
            subject = subject_dict['Hospital ID']
            if isinstance(subject, float) or isinstance(subject, int):
                subject = str(int(subject))
            csvstring = CSV_TEMPLATE.format(project="prion",
                                            subject=subject,
                                            session=subject+'_'+ss_label.split('_')[1],
                                            scan=scan,
                                            type='MPRAGE',
                                            series=stype,
                                            resource='NIFTI',
                                            path=fpath)
            csv_list.append(csvstring)"""
    return csv_list

def create_upload_demo_csv():
    """
        Generate csv file for demographic data

        :return: list of string to write in a csv string for XnatDemographic
    """
    csv_list = list()
    # Read the xlsx file:
    info_list = read_excel()

    # subject_l = list()
    for sess in XnatUtils.list_sessions(XNAT, 'prion'):
        found, subject_dict = find_subject_date(info_list, sess['subject_label'], sess['date'].replace('-',''), 'Hospital ID')
        if found:
            print sess['session_label']
            date = get_date(subject_dict['DOB'])
            if 'AOS' in subject_dict.keys():
                age = subject_dict['AOS']
            else:
                print subject_dict['Age']
                age = subject_dict['Age']
            csvstring = CSV_DEMOGRAPHIC.format(project="prion",
                                               subject=sess['subject_label'],
                                               session=sess['label'],
                                               gender=subject_dict['Gender'],
                                               yob=date[:4],
                                               education=subject_dict['Education'],
                                               genetic=subject_dict['Genetics'],
                                               codon129=subject_dict['Codon 129'],
                                               age=int(age),
                                               geneticstate=subject_dict['state'],
                                               MRC=subject_dict['MRC score'])
            csv_list.append(csvstring)
            """if 'Date of first symptoms' in subject_dict.keys() and sess['subject_label'] not in subject_l:
                print subject_dict['Date of first symptoms']
                da = get_date(subject_dict['Date of first symptoms'])
                csvstring = CSV_DEMOGRAPHIC2.format(project="prion",
                                                    subject=sess['subject_label'],
                                                    dos=da[:4]+'-'+da[4:6]+'-'+da[6:])
                csv_list.append(csvstring)
                subject_l.append(sess['subject_label'])"""

    return csv_list

def missing_data():
    """
        Check data between XNAT and Excel

        :return: None
    """
    #Read the xlsx files
    info_list = read_excel()

    subject_done = list()
    for sess in XnatUtils.list_sessions(XNAT, 'prion'):
        found, subject_dict = find_subject_date(info_list, sess['subject_label'], sess['date'].replace('-',''), 'Hospital ID')
        if found and not sess['subject_label'] in subject_done:
            subject_done.append(sess['subject_label'])
            print "%s  ==  %s " % (sess['subject_label'], subject_dict['Subject ID'])

    for subject_dict in info_list:
        subject = subject_dict['Hospital ID']
        session = subject +'_'+ get_date(subject_dict['Date of scan'])
        sess_obj = XnatUtils.select_obj(XNAT, 'prion', subject, session)
        if not sess_obj.exists():
            print '%s not found on XNAT. (%s)' % (session, subject_dict['Subject ID'])


if __name__ == '__main__':
    OPTIONS = parse_args()
    try:
        XNAT = XnatUtils.get_interface(host='http://cmic-xnat.cs.ucl.ac.uk')
        INFO_SUBJ = read_excel_2()
        #CSV_LIST = create_upload_data_csv()
        #CSV_LIST = create_upload2_data_csv()
        CSV_LIST = create_upload_demo_csv()
        #missing_data()
        print '\n\nCSV results for upload:'
        print 'project_id,subject_label,session_label,gender,age,yob,education,genetic,codon129,mrc,geneticstate'
        #print 'project_id,subject_label,DateOfFirstSymptoms'
        print '\n'.join(CSV_LIST)

        #info_list = read_excel()

        #Read the xlsx file:
        """
        for idict in info_list:
            print 'Subject: %s' % (idict['Hospital number'])
            subj_obj = XnatUtils.select_obj(XNAT, 'prion', idict['Hospital number'])
            if not subj_obj.exists():
                continue
                #print "  Subject not found on XNAT: %s " % (idict['Hospital number'])
            else:
                print idict['Hospital ID']
                new_subj_obj = XnatUtils.select_obj(XNAT, 'prion', idict['Hospital ID'])
                if not new_subj_obj.exists():
                    print "  Subject converted on XNAT: %s --> %s " % (idict['Hospital number'], idict['Hospital ID'])
                    subj_obj.attrs.set('label', idict['Hospital ID'])
                    subj = idict['Hospital ID']
                    for sess in XnatUtils.list_sessions(XNAT, 'prion', subj):
                        sess_obj = XnatUtils.select_obj(XNAT, 'prion', subj, sess['label'])
                        sess_obj.attrs.set('label', idict['Hospital ID']+'_'+sess['label'].split('_')[1])
                        print "    Session converted on XNAT: %s --> %s " % (sess['label'], idict['Hospital ID']+'_'+sess['label'].split('_')[1])
                else:
                    print "  NEED to reupload sessions for %s " % (idict['Hospital number'])

        """
    finally:
        XNAT.disconnect()
