"""Set the scna types from DICOM header."""

import os
import dicom
from dax import XnatUtils

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Set the scna types from DICOM header."


def parse_args():
    """Parser for arguments."""
    from argparse import ArgumentParser, RawDescriptionHelpFormatter
    argp = ArgumentParser(prog='Set_types_from_dicom', description=__purpose__,
                          formatter_class=RawDescriptionHelpFormatter)
    argp.add_argument('-p', "--project", dest='project', required=True,
                      help='Project ID on XNAT.')
    argp.add_argument('-d', '--directory', dest='directory', required=True,
                      help='Directory to store temp data.')
    argp.add_argument('-s', '--session', dest='sessions', required=True,
                      help='Sessions label on XNAT.')

    return argp.parse_args()


if __name__ == '__main__':
    args = parse_args()

    directory = os.path.abspath(args.directory)
    if not os.path.isdir(directory):
        os.makedirs(directory)

    # Scans on XNAT:
    try:
        xnat = XnatUtils.get_interface()
        li_scans = XnatUtils.list_project_scans(xnat, args.project)
        li_scans = XnatUtils.filter_list_dicts_regex(li_scans, 'session_label',
                                                     args.sessions.split(','))
        li_scans = sorted(li_scans, key=lambda k: k['session_label'])
        for scan_d in li_scans:
            # If type is unknown or empty, run:
            if scan_d['type'] == 'unknown' or not scan_d['type']:
                if 'DICOM' in scan_d['resources']:
                    print (" - setting type for %s/%s"
                           % (scan_d['session_label'], scan_d['ID']))
                    tmp_dir = os.path.join(directory, scan_d['session_label'],
                                           scan_d['ID'])
                    if not os.path.isdir(tmp_dir):
                        os.makedirs(tmp_dir)
                    # Download the dicom and read the header:
                    scan_obj = XnatUtils.get_full_object(xnat, scan_d)
                    dicom_file = XnatUtils.download_file_from_obj(
                                    tmp_dir, scan_obj.resource('DICOM'))
                    # for dicom_path in dicom_files:
                    print "   file: %s " % dicom_file
                    dcm = dicom.read_file(dicom_file)
                    # Get the protocol name
                    protocol = dcm.ProtocolName
                    # Set it to the scan
                    scan_obj.attrs.mset({'type': protocol,
                                         'series_description': protocol})

    finally:
        xnat.disconnect()
