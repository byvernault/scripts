"""TEST number 2 Script for different purpose."""

import os
from dax import XnatUtils

import Ben_functions

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Test Code 2"

HEADER = """object_type,project_id,subject_label,session_type,session_label,as_label,as_type,as_description,quality,resource,fpath"""


if __name__ == '__main__':
    directory = '/Users/byvernault/test_1946/'
    """excel_file = '/Users/byvernault/Downloads/uploaded_05May2016.csv'
    row_excel = Ben_functions.read_csv(excel_file, header=['subject',
                                                           'session'])
    li_sessions = [row['session'].strip() for row in row_excel]

    XNAT = XnatUtils.get_interface(host=os.environ['XN'])

    li_scans = XnatUtils.list_project_scans(XNAT, '1946')
    li_scans = [scan for scan in li_scans
                if scan['type'] == '1946_PET_NAC_DYNAMIC_0_60MIN']

    row = list()
    for scan in li_scans:
        if scan['session_label'] not in li_sessions:
            msg = 'Download scan number %s for session %s'
            print msg % (scan['ID'], scan['session_label'])
            res_obj = XnatUtils.get_full_object(XNAT, scan).resource('DICOM')
            if res_obj.exists() and len(res_obj.files().get()) > 0:
                print ' 1) start download...'
                data_dir = os.path.join(directory, scan['session_label'])
                if not os.path.exists(data_dir):
                    os.makedirs(data_dir)
                dl_files = XnatUtils.download_files_from_obj(data_dir, res_obj)
                print ' 2) Files downloaded: %s' % dl_files
            else:
                print 'Error: no files found for DICOM on XNAT. \
                       Test using curl and check catalog file.'"""

    csv_file = '/Users/byvernault/tempROI/upload_report.csv'
    row_csv = Ben_functions.read_csv(csv_file)
    row_csv = [r for r in row_csv if r['resource'] != 'SNAPSHOTS']
    for row in row_csv:
        r = list()
        for h in HEADER.split(','):
            if h == 'as_label':
                r.append(row.get('resource', '').split('ROI_')[1])
            elif h == 'as_type' or h == 'as_description':
                r.append('')
            elif h == 'quality':
                r.append('usable')
            elif h == 'resource':
                r.append('OsiriX')
            else:
                r.append(row.get(h, None))

        print ','.join(r)
