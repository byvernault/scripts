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
import glob
import xlrd

CSV_TEMPLATE = """scan,{project},{subject},MR,{session},{scan},{type},{series},usable,{resource},{path}"""

def parse_args():
    """
    Parser for arguments
    """
    from argparse import ArgumentParser
    usage = "Generates csv to upload prion data to XNAT."
    argp = ArgumentParser(prog='Generate CSV', description=usage)
    argp.add_argument('-d', dest='directory',
                      help="Directory where the json files are stored.",
                      required=True)
    argp.add_argument('-e', dest='excelfile',
                      help="Excel file with the subject names/IDs.",
                      required=True)
    return argp.parse_args()

def create_csv(directory):
    """
        Generate csv file

        :param directory: directory where data are
    """
    for folder in os.listdir(directory):
        if len(folder.split('__')) == 5:

            """if len(glob.glob(os.path.join(directory, folder, '*.nii'))) == 1:
                os.system('gzip '+glob.glob(os.path.join(directory, folder, '*.nii'))[0])
                print folder"""
            [subject, session, scan, stype, resource] = folder.split('__')
            '''if 'MPRAGE' in stype:
                csvstring = CSV_TEMPLATE.format(project="prion",
                                                subject=subject,
                                                session=session,
                                                scan=scan,
                                                type='MPRAGE',
                                                series=stype,
                                                resource=resource,
                                                path=os.path.abspath(os.path.join(directory, folder)))
                print csvstring
'''
            if stype == 'ep2d_diff_MDDW_p2FAD_2.5mm_iso' and session == 'aaco001_20090917':
                csvstring = CSV_TEMPLATE.format(project="prion",
                                                subject=subject,
                                                session=session,
                                                scan=scan,
                                                type='DIFF',
                                                series=stype,
                                                resource=resource,
                                                path=os.path.abspath(os.path.join(directory, folder)))
                print csvstring
            elif stype == 'ep2d_diff_MDDW_p2FAD_2.5mm_iso_B0' and session == 'aaco001_20090917':
                csvstring = CSV_TEMPLATE.format(project="prion",
                                                subject=subject,
                                                session=session,
                                                scan=scan,
                                                type='B0',
                                                series=stype,
                                                resource=resource,
                                                path=os.path.abspath(os.path.join(directory, folder)))
                print csvstring
        else:
            pass
            #print "Check folder: "+folder

def read_excel():
    """
        Read the excel spreadsheet

        :return: list of dictionaries for the row in excel
    """
    #Read the xlsx file:
    book = xlrd.open_workbook(ARGS.excelfile)
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
    book = xlrd.open_workbook(ARGS.excelfile)
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

def create_csv_xnat():
    """
        Generate csv file

    """
    resource = 'NIFTI'
    for nifti in glob.glob(os.path.join(ARGS.directory, '*', '*.nii.gz')):
        if not "MPRAGE" in nifti:
            labels = os.path.basename(nifti).split('.nii.gz')[0].split('-')
            [session, scan, stype] = labels[0:3]
            if stype[-3:] == '_4D':
                stype = stype[:-3]
            subject = session.split('_')[0]
            new_subj = list(set([s['Hospital ID'] for s in RENAME if s['Subject ID'] == subject]))
            if len(new_subj) > 1:
                raise Exception("more than one subject found with the ID %s" % subject)
            elif len(new_subj) == 1:
                subject = new_subj[0]
            else:
                new_subj = list(set([s['Hospital ID'] for s in INFO if s['Subject ID'] == subject]))
                if len(new_subj)>1:
                    raise Exception("more than one subject found with the ID %s" % subject)
                subject = new_subj[0]
            session = "%s_%s" % (subject, session.split('_')[1])
            #CHANGE subject/session
            csvstring = CSV_TEMPLATE.format(project="prion",
                                            subject=subject,
                                            session=session,
                                            scan=scan,
                                            type=stype,
                                            series=stype,
                                            resource=resource,
                                            path=nifti)
            print csvstring

    for resources in ['BVAL', 'BVEC', 'NEGYBVEC']:
        if resources != 'NEGYBVEC':
            resource_ext = resources.lower()
        else:
            resource_ext = 'negYbvec'
        for files in glob.glob(os.path.join(ARGS.directory, '*', '*.'+resource_ext)):
            session = os.path.basename(files).split('_index')[0]
            subject = session.split('_')[0]
            new_subj = list(set([s['Hospital ID'] for s in RENAME if s['Subject ID'] == subject]))
            if len(new_subj) > 1:
                raise Exception("more than one subject found with the ID %s" % subject)
            elif len(new_subj) == 1:
                subject = new_subj[0]
            else:
                new_subj = list(set([s['Hospital ID'] for s in INFO if s['Subject ID'] == subject]))
                if len(new_subj)>1:
                    raise Exception("more than one subject found with the ID %s" % subject)
                subject = new_subj[0]
            new_session = "%s_%s" % (subject, session.split('_')[1])
            scan = ''
            stype = ''
            for fnii in glob.glob(os.path.join(ARGS.directory, session, '*.nii.gz')):
                filename = os.path.basename(fnii).split('.nii.gz')[0]
                if 'b0' not in filename.lower() and 'ep2d_diff' in filename.lower():
                    [_, scan, stype] = filename.split('.nii.gz')[0].split('-')[0:3]
            #CHANGE subject/session
            csvstring = CSV_TEMPLATE.format(project="prion",
                                            subject=subject,
                                            session=new_session,
                                            scan=scan,
                                            type=stype,
                                            series=stype,
                                            resource=resources,
                                            path=files)
            print csvstring

"""
bash command to copy data:

for i in aa*;do mkdir ../upload/${i:0:7}__${i:0:16}__0016__ep2d_diff_MDDW_p2FAD_2.5mm_iso__bval && cp $i/*.bval ../upload/${i:0:7}__${i:0:16}__0016__ep2d_diff_MDDW_p2FAD_2.5mm_iso__bval;done
for i in aa*;do mkdir ../upload/${i:0:7}__${i:0:16}__0016__ep2d_diff_MDDW_p2FAD_2.5mm_iso__bvec && cp $i/*.bvec ../upload/${i:0:7}__${i:0:16}__0016__ep2d_diff_MDDW_p2FAD_2.5mm_iso__bvec;done
for i in aa*;do mkdir ../upload/${i:0:7}__${i:0:16}__0016__ep2d_diff_MDDW_p2FAD_2.5mm_iso__negYbvec && cp $i/*.negYbvec ../upload/${i:0:7}__${i:0:16}__0016__ep2d_diff_MDDW_p2FAD_2.5mm_iso__negYbvec;done
for i in aa*;do mkdir ../upload/${i:0:7}__${i:0:16}__json && cp $i/*.json ../upload/${i:0:7}__${i:0:16}__json;done
for i in aa*/aa*__aa*;do cp -r $i ../upload/${i:17}__NIFTI;done
"""

if __name__ == '__main__':
    ARGS = parse_args()

    INFO = read_excel()
    RENAME = read_excel_2()
    create_csv_xnat()
