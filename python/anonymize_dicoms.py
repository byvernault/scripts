"""Remove any fields from DICOM header that contains Patient Health information.

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

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import sys
import dicom
import subprocess as sb
from datetime import datetime

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Anonymize DICOM header."
__version__ = '1.0.0'
__modifications__ = '15 December 2015 - Original write'

# VARIABLES
CSV_HEADER = ["patient_id", "project_xnat", "subject_xnat", "session_xnat", "folder_path"]
PCOMMENT_TEMPLATE = """Project:{project};Subject:{subject};Session:{session}"""
REPORT_HEADER = ['old_id', 'new_id', 'InstitutionAddress', 'PatientAge', 'MilitaryRank',
                 'Allergies', 'AdditionalPatientHistory', 'OtherPatientIDs',
                 'PerformingPhysicianName', 'OperatorsName', 'ReferringPhysicianName',
                 'StudyDate', 'StudyDescription', 'AcquisitionDate', 'AcquisitionNumber',
                 'ContentDate', 'AcquisitionDateTime', 'ContentTime', 'SeriesTime',
                 'AcquisitionTime', 'AccessionNumber', 'StationName', 'StudyID',
                 'RequestingService', 'RequestingPhysician', 'StudyComments',
                 'PrivateCreatorDataElement', 'RequestedProcedureDescription',
                 'CurrentPatientLocation', 'ScanningSequence', 'SequenceVariant',
                 'ScanOptions', 'PatientName', 'Institutional Department Name',
                 'Name of Physician(s) Reading Study', 'Study Status ID', 'Study Priority ID',
                 'Reason for Study', 'Performed Station AE Title','Performed Procedure Step ID',
                 'Requested Procedure ID', 'Performed Procedure Step Description']
REMOVE_BY_DEFAULT_NAME = ('InstitutionAddress',
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
REMOVE_BY_DEFAULT_TAG = [0x00081048, #Physician(s) Of Record
                         0x00081040, #Institutional Department Name
                         0x00081060, #Name of Physician(s) Reading Study
                         0x0032000A, #Study Status ID
                         0x0032000C, #Study Priority ID
                         0x00321030, #Reason for Study
                         0x00400241, #Performed Station AE Title
                         0x00400253, #Performed Procedure Step ID
                         0x00401001, #Requested Procedure ID
                         0x00400254] #Performed Procedure Step Description

SUBSTITUTE_BY_DEFAULT = {}

DEFAULT_REPORT_NAME = "anonymize_report.csv"

def parse_args():
    """ Parser for arguments """
    from argparse import ArgumentParser
    argp = ArgumentParser(prog='organise_dicomfolder', description=__purpose__)
    argp.add_argument('-c', '--csv', dest='csvfile', required=True,
                      help='CSV file containing the patient/path information. header: patient_id,project_xnat,subject_xnat,session_xnat,folder_path.')
    argp.add_argument('-d', '--directory', dest='out_dir', default=None,
                      help='Directory where the dicom will be saved. If None, overwrite the original dicom.')
    argp.add_argument('-x', '--xnat', dest='set_xnat', action="store_true",
                      help='Setting PatientsComment in DICOM header for XNAT using project/patient_id/patient_id_date')
    argp.add_argument('-a', '--addStudyDate', dest='add_date', action="store_true",
                      help='Add the StudyDate at the end of the session id')
    argp.add_argument('-r', '--removeFields', dest='remove_fields',
                      help='Remove fields specified by this option: E.G: PatientName,PatientID', default=None)
    argp.add_argument('-f', '--force', dest='overwrite', action="store_true",
                      help='Force to overwrite the previous DICOM', default=None)
    argp.add_argument('-p', '--startingPatient', dest='first_patient',
                      help='When restarting the process, patient id to start from', default=None)
    argp.add_argument('--sendXnat', dest='send_xnat', action="store_true",
                      help='Send the dicom to XNAT at the end.')
    return argp.parse_args()

def read_csv():
    """
    Reading the csv from options

    :return: list of patient dictionaries describing the data to edit
    """
    patients_list = list()
    if os.path.exists(OPTIONS.csvfile):
        with open(OPTIONS.csvfile,'rb') as csvfileread:
            csvreader = csv.reader(csvfileread, delimiter=',')
            for row in csvreader:
                if row[0] == "patient_id":
                    continue
                patients_list.append(dict(zip(CSV_HEADER, row)))
    else:
        raise Exception('file %s not found. Check if the file exists.' % (OPTIONS.csvfile))

    return sorted(patients_list, key=lambda k: k['patient_id'])

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
    file_call = '''file {fpath}'''.format(fpath=fpath)
    output = sb.check_output(file_call.split())
    if 'dicom' in output.lower():
        return True

    return False

def anonymize_file(in_path, out_path, patient_dict, keep=(), remove=(), keep_private_tags=False, **kwargs):
    '''Anonymize a DICOM file.
    :param in_path: File path to read from.
    :param out_path: File path to write to.
    :param patient_dict: patient dictionary from csv
    :param remove: A list of fields that should be removed in addition to the default ones.
    :param keep: A list of fields that should be kept in the file (takes precedence over all other parameters)
    :param keep_private_tags: If False, all private tags are removed (default: False)
    :param kwargs: Parameters and associated value will be substituted.
    All field names can be given in camel case (like PatientName) or in underlined format (like patient_name)
    to conform with python conventions.
    There are a few fields that are substituted by default and a lot of fields that are removed by default.
    '''
    row = list()
    f = dicom.read_file(in_path)

    #Good Patient
    if 'PatientID' in f:
        patient = f.__getattr__('PatientID')
    else:
        patient = f.__getattr__('PatientName')
    if patient != patient_dict['patient_id']:
        print "Warning: ID didn't match for %s instead of %s" % (patient_dict['patient_id'], patient)
        return

    print "    - Editing %s" % in_path
    #Directory
    if OPTIONS.out_dir:
        o_dir = os.path.join(os.path.dirname(out_path), patient_dict['subject_xnat'])
        if not os.path.exists(o_dir):
            os.makedirs(o_dir)
        out_path = os.path.join(o_dir, os.path.basename(out_path))

    #For report:
    row.append(patient_dict['patient_id'])
    row.append(patient_dict['subject_xnat'])
    for field in REMOVE_BY_DEFAULT_NAME:
        if field in f:
            row.append(f.__getattr__(field))
        else:
            row.append('')
    for field in SUBSTITUTE_BY_DEFAULT.keys():
        if field in f:
            row.append(f.__getattr__(field))
    for tag in REMOVE_BY_DEFAULT_TAG:
        if tag in f:
            row.append(f[tag].value)
    if not row in ROW_LIST:
        ROW_LIST.append(row)

    comment = None
    if OPTIONS.set_xnat:
        if patient_dict["session_xnat"]:
            session = patient_dict["session_xnat"]
        else:
            if OPTIONS.add_date:
                if 'SeriesDate' in f:
                    session = patient_dict["subject_xnat"]+'_'+f.__getattr__('SeriesDate')
                elif 'StudyDate' in f:
                    session = patient_dict["subject_xnat"]+'_'+f.__getattr__('StudyDate')
                else:
                    print 'Date not found ... setting session to subject'
                    session = patient_dict["subject_xnat"]
            else:
                session = patient_dict["subject_xnat"]
        comment = PCOMMENT_TEMPLATE.format(project=patient_dict["project_xnat"],
                                           subject=patient_dict["subject_xnat"],
                                           session=session)

    def _camelize(strg):
        if '_' in strg:
            return ''.join([ frag[0].upper() + frag[1:] for frag in strg.split('_') ])
        else:
            return strg[0].upper + strg[1:]

    #def _delete_field(field):
    #    _update_field(field, None)

    def _remove_field(field):
        _update_field(field, "")

    def _update_field(field, value):
        if field in keep:
            return
        if not field in f:
            return
        if value is None:
            f.__delattr__(field)
        else:
            f.__setattr__(field, value)

    keep = [_camelize(field) for field in keep]
    substitute = {_camelize(key) : value for key, value in kwargs.items()}
    remove = [_camelize(field) for field in remove]

    # Use defaults but the don't remove what user substitutes and vice versa
    remove = list((field for field in REMOVE_BY_DEFAULT_NAME if not field in substitute)) + remove
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
        f.PatientComments = comment
        # set the PatientID to the subjectID:
        f.PatientName = patient_dict["subject_xnat"]
        f.PatientID = patient_dict["subject_xnat"]

    # Set PatientBirthDate:
    if 'PatientBirthDate' in f:
        f.PatientBirthDate = f.PatientBirthDate[:4]+'0101'

    for field in remove:
        _remove_field(field)
    for field, value in substitute.items():
        _update_field(field, value)
    for tag in REMOVE_BY_DEFAULT_TAG:
        if tag in f:
            f[tag].value = ''
    if not keep_private_tags:
        f.remove_private_tags()

    if not os.path.exists(out_path) or \
       os.path.exists(out_path) and OPTIONS.overwrite:
        f.save_as(out_path)

if __name__ == '__main__':
    #Get args
    OPTIONS = parse_args()
    ROW_LIST = list()

    if OPTIONS.out_dir:
        if not os.path.exists(os.path.abspath(OPTIONS.out_dir)):
            raise Exception('%s ouput directory not found.' % (os.path.abspath(OPTIONS.out_dir)))
    elif not OPTIONS.overwrite:
        wrong_answer = True
        while wrong_answer:
            answer = raw_input("-d/--directory not set, the changes on the DICOM tags will be saved on the original dicom files. Do you agree (Y/N)?")
            if answer in ['Y', 'y', 'yes', 'Yes', 'YES']:
                wrong_answer = False
                OPTIONS.overwrite = True
            elif answer in ['N', 'n', 'no', 'No', 'NO']:
                print 'Exiting the script.'
                sys.exit()
            else:
                wrong_answer = True

    # Script starting
    print "Edit DICOM in a folder/sub folders to anonymize the data."
    print "Time: ", str(datetime.now())

    # Read csv file:
    PATIENTS_LIST = read_csv()

    if not PATIENTS_LIST:
        print "WARNING: no patients found in the csv given. Please provide a csv following the help header: patient_id,new_patient_id,folder_path"
    else:
        if OPTIONS.out_dir:
            report_file = os.path.join(OPTIONS.out_dir, DEFAULT_REPORT_NAME)
        else:
            report_file = os.path.join(os.environ['HOME'], DEFAULT_REPORT_NAME)

        if os.path.exists(report_file):
            wrong_answer = True
            while wrong_answer:
                answer = raw_input("The report file %s already exists. Do you want to overwrite it (Y/N)?" % report_file)
                if answer in ['Y', 'y', 'yes', 'Yes', 'YES']:
                    wrong_answer = False
                elif answer in ['N', 'n', 'no', 'No', 'NO']:
                    print 'Exiting the script.'
                    sys.exit()
                else:
                    wrong_answer = True

        with open(report_file, 'wb') as csvfilewrite:
            CSVWRITER = csv.writer(csvfilewrite, delimiter=',')
            #Today date
            CSVWRITER.writerow(['Anonymized date = %s' % ('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()))])
            CSVWRITER.writerow(REPORT_HEADER)
            # Called the function for each patient folder containing dicom
            previous_patient = None
            scan_count = 0
            index = 0
            total_subject = len(set([p['patient_id'] for p in PATIENTS_LIST]))
            if OPTIONS.first_patient:
                patient_start_found = False
            else:
                patient_start_found = True

            for p_dict in PATIENTS_LIST:
                if OPTIONS.first_patient and p_dict['patient_id'] == OPTIONS.first_patient:
                    patient_start_found = True
                if previous_patient != p_dict['patient_id']:
                    scan_count = 0
                    index = index + 1
                    if patient_start_found:
                        print " - Patient %s/%s info: %s " % (str(index), str(total_subject), p_dict['patient_id'])
                    previous_patient = p_dict['patient_id']
                if patient_start_found:
                    # Print statement
                    print "   + anonymizing %s folder" % (str(scan_count+1))
                    # get dicom files from folder
                    dicoms_list = get_dicom_files(p_dict["folder_path"])

                    # anonymize the dicoms:
                    for dicom_file in dicoms_list:
                        if OPTIONS.out_dir:
                            out_dcm_path = os.path.join(os.path.abspath(OPTIONS.out_dir), os.path.basename(dicom_file))
                        else:
                            out_dcm_path = dicom_file
                        if OPTIONS.remove_fields:
                            remove_fields = OPTIONS.remove_fields.split(',')
                        else:
                            remove_fields = ()
                        anonymize_file(dicom_file, out_dcm_path, p_dict, remove=remove_fields)
                    scan_count = scan_count+1

            for csv_row in ROW_LIST:
                CSVWRITER.writerow(csv_row)
