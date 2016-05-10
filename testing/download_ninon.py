"""Download For Ninon."""


import os
import csv
from dax import XnatUtils


__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Download for Ninon"


CCMD = """curl -o {path}/DICOM.zip \
{host}/data/archive/projects/{project}/subjects/{subject}\
/experiments/{session}/scans/${type}/files?format=zip\
 -u $XNAT_USER:$XNAT_PASS"""
HOST = 'https://nimg1946.cs.ucl.ac.uk'


def read_csv(csv_file, header=None, delimiter=','):
    """Read CSV file (.csv files).

    :param csv_file: path to the csv file
    :param header: list of label for the header, if None, use first line
    :param delimiter: delimiter for the csv, default comma
    :return: list of rows
    """
    if not os.path.isfile(csv_file):
        raise Exception('File not found: %s' % csv_file)
    if not csv_file.endswith('.csv'):
        raise Exception('File format unknown. Need .csv: %s' % csv_file)
    # Read csv
    csv_info = list()
    with open(csv_file, 'rb') as f:
        reader = csv.reader(f, delimiter=delimiter)
        if not header:
            header = next(reader)
        for row in reader:
            if row == header:
                continue
            csv_info.append(dict(zip(header, row)))
    return csv_info


def parse_args():
    """Parser for arguments."""
    from argparse import ArgumentParser
    usage = "Download 1946 data for Ninon."
    argp = ArgumentParser(prog='download_ninon.py', description=usage)
    argp.add_argument('-d', dest='directory',
                      help="Directory where the json files are stored.",
                      required=True)
    argp.add_argument('-c', dest='csv',
                      help="Csv file containing the subject that where already\
                            downloaded.",
                      required=True)
    return argp.parse_args()

if __name__ == '__main__':
    args = parse_args()
    row_excel = read_csv(args.csv, header=['subject', 'session'])
    li_sessions = [row['session'].strip() for row in row_excel]

    XNAT = XnatUtils.get_interface(host=HOST)

    li_scans = XnatUtils.list_project_scans(XNAT, '1946')
    li_scans = [scan for scan in li_scans
                if scan['type'] == '1946_PET_NAC_DYNAMIC_0_60MIN']

    row = list()
    for scan in li_scans:
        if scan['session_label'] not in li_sessions:
            msg = 'Download scan number %s for session %s'
            print msg % (scan['ID'], scan['session_label'])
            # data_dir = os.path.join(args.directory, scan['subject_label'],
            #                        scan['session_label'], 'scans',
            #                        '1946_PET_NAC_DYNAMIC_0_60MIN')
            data_dir = os.path.join(args.directory, scan['session_label'])
            if os.path.exists(data_dir):
                print ' --> Folder present. Already downloaded?'
            else:
                scan_obj = XnatUtils.get_full_object(XNAT, scan)
                res_obj = scan_obj.resource('DICOM')
                if not res_obj.exists():
                    print ' Error: No DICOM Resources found for scan.'
                else:
                    if len(res_obj.files().get()) > 0:
                        print ' 1) start download...'
                        os.makedirs(data_dir)
                        dl_files = XnatUtils.download_files_from_obj(data_dir,
                                                                     res_obj)
                        print ' 2) Files downloaded'
                    else:
                        os.makedirs(data_dir)
                        curl = CCMD.format(path=data_dir,
                                           host=HOST,
                                           project='1946',
                                           subject=scan['subject_label'],
                                           session=scan['session_label'],
                                           type='1946_PET_NAC_DYNAMIC_0_60MIN')
                        print 'Pyxnat failed. Trying curl: %s' % curl
                        try:
                            os.system(curl)
                            dcm_zip = os.path.join(data_dir, 'DICOM.zip')
                            if os.path.exists(dcm_zip):
                                os.system('unzip -o -d %s %s' %
                                          (data_dir, dcm_zip))
                            else:
                                print 'Error: download failed with pyxnat and curl. \
                                       Check catalog file on XNAT.'
                        except:
                            print 'Error: download failed with pyxnat and curl. \
                                   Check catalog file on XNAT.'
