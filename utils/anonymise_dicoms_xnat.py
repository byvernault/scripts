#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dicom
from dicom.tag import Tag
from datetime import datetime
import os
import sys
import subprocess as sb


"""
Remove any fields from DICOM header that contains Patient Health
information plus set tags for XNAT.

Probably upgrade for the script if remove other tags:
<--------------------------------------------------->
# Removing more tags
for name in tags:
    if name in dcm:
        dcm.data_element(name).value = ''
    else:
        print "   error: tag %s not found." % (name)
<--------------------------------------------------->
"""


__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Anonymise DICOM header for XNAT."
__version__ = '1.0.0'
__modifications__ = '13 February 2017 - Original write'


# Variables
DEFAULT_HOST = 'https://epinav-xnat.cs.ucl.ac.uk'
COMMENT_TMP = """Project:{project};Subject:{subject};Session:{session}"""
SUBSTITUTE_BY_DEFAULT = {}
REMOVE_BY_DEFAULT_NAME = ('InstitutionAddress',
                          'PatientSex',
                          'PatientAge',
                          'PatientAddress',
                          'MilitaryRank',
                          'Allergies',
                          'AdditionalPatientHistory',
                          'OtherPatientIDs',
                          'PerformingPhysicianName',
                          'OperatorsName',
                          'ReferringPhysicianName',
                          'StudyDate',
                          'StudyDescription',
                          'AcquisitionDate',
                          'AcquisitionNumber',
                          'ContentDate',
                          'AcquisitionDateTime',
                          'ContentTime',
                          'SeriesTime',
                          'AcquisitionTime',
                          'AccessionNumber',
                          'StationName',
                          'StudyID',
                          'RequestingService',
                          'RequestingPhysician',
                          'StudyComments',
                          'PrivateCreatorDataElement',
                          'RequestedProcedureDescription',
                          'CurrentPatientLocation',
                          'ScanningSequence',
                          'SequenceVariant',
                          'ScanOptions')
REMOVE_BY_DEFAULT_TAG = [0x00081048,  # Physician(s) Of Record
                         0x00081040,  # Institutional Department Name
                         0x00081060,  # Name of Physician(s) Reading Study
                         0x0032000A,  # Study Status ID
                         0x0032000C,  # Study Priority ID
                         0x00321030,  # Reason for Study
                         0x00400241,  # Performed Station AE Title
                         0x00400253,  # Performed Procedure Step ID
                         0x00401001,  # Requested Procedure ID
                         0x00400254]  # Performed Procedure Step Description

KEEP_TAG = [(0x0043, 0x102D),
            (0x0043, 0x1081)]


def parse_args():
    """ Parser for arguments """
    from argparse import ArgumentParser
    argp = ArgumentParser(prog='anonymise_dicom', description=__purpose__)
    argp.add_argument('-d', '--directory', dest='dicom_dir', required=True,
                      help='Directory containing the dicom to anonymise.')
    argp.add_argument('--patient', dest='patient', required=True,
                      help='Patient ID in Dicom to edit if several')
    argp.add_argument('--project', dest='project', default='IMPLAN',
                      help='Project ID on XNAT. If not set, prompt user.')
    argp.add_argument('--subject', dest='subject', default=None,
                      help='Subject label on XNAT. If not set, prompt user.')
    helpstr = 'Directory where the dicom will be saved. If None, overwrite \
the original dicom.'
    argp.add_argument('-o', '--out_dir', dest='out_dir', default=None,
                      help=helpstr)
    argp.add_argument('-f', '--force', dest='overwrite', action="store_true",
                      help='Force to overwrite the previous DICOM')
    argp.add_argument('--sendXnat', dest='send_xnat', action="store_true",
                      help='Send the dicom to XNAT at the end.')
    argp.add_argument('--host', dest='host', default=None,
                      help='XNAT host to send the data.')
    argp.add_argument('--exe', dest='exe', default='DicomRemap',
                      help='DicomRemap executable path.')
    return argp.parse_args()


def prompt_user_yes_no(question):
    answer = None
    while answer is None:
        answer = raw_input('%s[Y/N]: ' % question)
        if answer in ['Y', 'y', 'yes', 'Yes', 'YES']:
            return True
        elif answer in ['N', 'n', 'no', 'No', 'NO']:
            return False


def ask_user(patient, project=None, subject=None):
    while project is None:
        project = raw_input("Enter Project ID on XNAT: ")
    while subject is None:
        subject = raw_input("Enter Subject label on XNAT: ")
    msg = 'You entered the following information to set for XNAT:'
    msg += '\n\t- patient to edit: %s'
    msg += '\n\t- project: %s'
    msg += '\n\t- subject: %s'
    print msg % (patient, project, subject)

    if not prompt_user_yes_no('Do you want to proceed?'):
        project, subject = ask_user(patient, project, subject)
    return project, subject


def get_dicom_files(folder):
    """
    return all the dicom files from a folder

    :param fpath: path of the file
    :return boolean: true if it's a DICOM, false otherwise
    """
    dicom_files = list()
    for filename in os.listdir(folder):
        fpath = os.path.join(folder, filename)
        if os.path.isfile(fpath) and is_dicom(fpath):
            dicom_files.append(fpath)
        elif os.path.isdir(fpath):
            dicom_files.extend(get_dicom_files(fpath))
    return dicom_files


def is_dicom(fpath):
    """
    check if the file is a DICOM medical data

    :param fpath: path of the file
    :return boolean: true if it's a DICOM, false otherwise
    """
    if 'win' in sys.platform:
        return True
    else:
        file_call = '''file {fpath}'''.format(fpath=fpath)
        output = sb.check_output(file_call.split())
        if 'dicom' in output.lower():
            return True

        return False


def anonymize_file(in_path, out_path, patient_id, xnat_project, xnat_subject,
                   keep=(), remove=(), keep_private_tags=False, **kwargs):
    """
    Anonymize a DICOM file.

    :param in_path: File path to read from.
    :param out_path: File path to write to.
    :param patient_dict: patient dictionary from csv
    :param remove: A list of fields that should be removed in addition to the
                   default ones.
    :param keep: A list of fields that should be kept in the file
                 (takes precedence over all other parameters)
    :param keep_private_tags: If False, all private tags are removed
                              (default: False)
    :param kwargs: Parameters and associated value will be substituted.

    All field names can be given in camel case (like PatientName) or in
    underlined format (like patient_name) to conform with python conventions.
    There are a few fields that are substituted by default and a lot of fields
    that are removed by default.

    """
    try:
        dicom_obj = dicom.read_file(in_path)
    except dicom.InvalidDicomError:
        print 'Warning: %s file is not a dicom. It can not be open with \
pydicom.'
        return

    # Good Patient
    if 'PatientID' in dicom_obj:
        patient = dicom_obj.__getattr__('PatientID')
    else:
        patient = dicom_obj.__getattr__('PatientName')
    if patient != patient_id:
        print ("Warning: ID didn't match for %s instead of %s"
               % (patient_id, patient))
        return

    print "    - Editing %s" % in_path
    comment = None

    if 'SeriesDate' in dicom_obj:
        session = '%s_%s' % (xnat_subject, dicom_obj.__getattr__('SeriesDate'))
    elif 'StudyDate' in dicom_obj:
        session = '%s_%s' % (xnat_subject, dicom_obj.__getattr__('StudyDate'))
    else:
        print 'Date not found ... setting session to subject'
        session = xnat_subject
    comment = COMMENT_TMP.format(project=xnat_project,
                                 subject=xnat_subject,
                                 session=session)

    def _camelize(strg):
        if '_' in strg:
            return ''.join([frag[0].upper() + frag[1:]
                            for frag in strg.split('_')])
        else:
            return strg[0].upper + strg[1:]

    def _delete_field(field):
        _update_field(field, None)

    def _remove_field(field):
        _update_field(field, "")

    def _update_field(field, value):
        if field in keep:
            return
        if field not in dicom_obj:
            return
        if value is None:
            dicom_obj.__delattr__(field)
        else:
            dicom_obj.__setattr__(field, value)

    keep = [_camelize(field) for field in keep]
    substitute = {_camelize(key): value for key, value in kwargs.items()}
    remove = [_camelize(field) for field in remove]

    # Use defaults but the don't remove what user substitutes and vice versa
    remove = list((field for field in REMOVE_BY_DEFAULT_NAME
                   if field not in substitute)) + remove
    for field, value in SUBSTITUTE_BY_DEFAULT.items():
        if field in remove or field in substitute:
            continue
        else:
            if field == 'PatientBirthDate':
                substitute[field] = value[:4]+'0101'
            else:
                substitute[field] = value

    # Set the Patients comments for XNAT:
    if comment:
        dicom_obj.PatientComments = comment
        # set the PatientID to the subjectID:
        dicom_obj.PatientName = xnat_subject
        dicom_obj.PatientID = session

    # Set PatientBirthDate:
    if 'PatientBirthDate' in dicom_obj:
        dicom_obj.PatientBirthDate = dicom_obj.PatientBirthDate[:4]+'0101'

    # Keep tags:
    keeping_tags = dict()
    for tag in KEEP_TAG:
        dcm_tag = Tag(tag)
        if dcm_tag in dicom_obj:
            keeping_tags[dcm_tag] = {
                'value': dicom_obj[dcm_tag].value,
                'sequence': dicom_obj[dcm_tag].VR,
                }
        else:
            print 'Warning: no tag %s for dicom %s' % (dcm_tag, in_path)

    # Remove tags
    for field in remove:
        _remove_field(field)
    for field, value in substitute.items():
        _update_field(field, value)
    for tag in REMOVE_BY_DEFAULT_TAG:
        if tag in dicom_obj:
            dicom_obj[tag].value = ''
    if not keep_private_tags:
        dicom_obj.remove_private_tags()

    # Set tags to keep back:
    for tag, info in keeping_tags.items():
        if tag in dicom_obj:
            dicom_obj[tag].value = info['value']
        else:
            dicom_obj.add_new(tag, info['sequence'], info['value'])

    dicom_obj.save_as(out_path)


def send_to_xnat(exe, dicom_folder, host):
    print 'Sending dicoms from folder: %s' % (dicom_folder)
    if not executable_exists(exe):
        raise Exception('Executable not found: %s' % exe)

    host_str = host
    if host_str.startswith('http'):
        host_str = 'dicom%s' % host_str[5:]
    elif host_str.startswith('https'):
        host_str = 'dicom%s' % host_str[6:]

    cmd = '%s -o %s:8104/XNAT %s' % (exe, host_str, dicom_folder)
    print '  --> Running command: %s' % cmd
    os.system(cmd)


def executable_exists(executable):
    """ Return True if the executable exists.

    If the full path is given, check that it's an executable.
    Else check in PATH for the file.
    """
    if '/' in executable and os.path.isfile(executable):
        return os.access(os.path.abspath(executable), os.X_OK)
    else:
        if True in [os.path.isfile(os.path.join(path, executable)) and
                    os.access(os.path.join(path, executable), os.X_OK)
                    for path in os.environ["PATH"].split(os.pathsep)]:
            return True
    return False


def main_fct():
    args = parse_args()

    # Script starting
    print "Edit DICOM in a folder/sub folders to anonymize the data."
    print "Time: ", str(datetime.now())

    # Ask user for project and subject on XNAT:
    project, subject = ask_user(args.patient, args.project, args.subject)

    if args.out_dir:
        out_dir = args.out_dir
    else:
        out_dir = os.path.join(os.path.dirname(args.dicom_dir),
                               '%s_ano' % subject)

    out_dir = os.path.abspath(out_dir)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    print "Anonymizing dicoms from folder: %s" % (args.dicom_dir)
    # get dicom files from folder
    dicoms_list = get_dicom_files(args.dicom_dir)

    # anonymize the dicoms:
    for dicom_file in dicoms_list:
        out_dcm_path = os.path.join(os.path.abspath(out_dir),
                                    os.path.basename(dicom_file))
        anonymize_file(dicom_file, out_dcm_path, args.patient, project,
                       subject)

    if args.send_xnat:
        host = args.host
        if not host:
            host = os.environ.get('XNAT_HOST', DEFAULT_HOST)
        send_to_xnat(args.exe, out_dir, host)


if __name__ == '__main__':
    main_fct()
