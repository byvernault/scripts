"""Separate DICOM files in a folder by reading the header."""

import os
import dicom
import glob
import subprocess as sb
from datetime import datetime
from dax import XnatUtils

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Separate DICOM files in a folder by reading the header."
__version__ = '1.0.0'
__modifications__ = '7 October 2015 - Original write'


PCOMMENT_TEMPLATE = """Project:{project};Subject:{subject};Session:{session}"""
DICOM_FIELDS = {"commentsXnat": [0x0010, 0x4000],
                "subject": [0x0010, 0x0010],
                "serie": [0x0020, 0x0010]}
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


def parse_args():
    """Parser for arguments"""
    from argparse import ArgumentParser
    usage = "Separate DICOM files in a folder by reading the header."
    argp = ArgumentParser(prog='organise_dicomfolder', description=usage)
    argp.add_argument('-d', '--dicomfolder', dest='directory',
                      help='Directory containing DICOMs.', required=True)
    argp.add_argument('-p', '--project', dest='project',
                      help='Project ID on XNAT.', required=True)
    argp.add_argument('-s', '--session', dest='session',
                      help='Last session processed.', default=None)
    return argp.parse_args()

def get_info_file(directory, project):
    """Get the info from directory structure (subject / session)

        :param directory: path for subject dir
        :param project: xnat project ID
        :return dict: dict with info {"scansdir": list of dir, "comment": patient comment}"""
    dicom_dict = dict()
    if len(glob.glob(os.path.join(directory,'*','*')))>0 and is_dicom(glob.glob(os.path.join(directory,'*','*'))[0]):
        dcmfpath = glob.glob(os.path.join(directory,'*','*'))[0]
        ds = dicom.read_file(dcmfpath)
        subject_label = ds.PatientName.replace(' ','')
        try:
            session_label = ds.InstanceCreationDate.replace(' ','')
        except:
            try:
                session_label = ds.AcquisitionDate.replace(' ','')
            except:
                session_label = ds.PerformedProcedureStepEndDate.replace(' ','')
        patient_comment = PCOMMENT_TEMPLATE.format(project=project,
                                                   subject=subject_label,
                                                   session=subject_label+"_"+session_label)
        dicom_dict['comment'] = patient_comment
        print patient_comment
        scans_dir = list()
        for scan in os.listdir(directory):
            fpath = os.path.join(directory, scan)
            if os.path.isdir(fpath):
                scans_dir.append(fpath)

        dicom_dict['scansdir'] = scans_dir
    else:
        print "No dicoms in "+directory

    return dicom_dict

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

def edit_info_dicom(list_dict):
    """
        edit the information of the DICOM for patients comment
    """
    for session_dict in list_dict:
        for scanfolder in session_dict['scansdir']:
            print "Setting field for folder: "+scanfolder+" to "+session_dict['comment']
            set_dicom_field(scanfolder, session_dict['comment'])
            print "------"

def set_dicom_field(dcmfolder, comment):
    """
        edit the information of the DICOM for patients comment

        :param dcmfolder: folder containing the dicoms
        #:param comment: value for the patients comment
    """
    for dcmfile in os.listdir(dcmfolder):
        dicom_path = os.path.join(dcmfolder, dcmfile)
        if os.path.isfile(dicom_path) and is_dicom(dicom_path):
            print "   file: " + dcmfile
            dcm = dicom.read_file(dicom_path)
            # edit the header
            dcm.PatientComments = comment
            dcm.save_as(dicom_path)


def _remove_field(dicom_obj, field):
    _update_field(dicom_obj, field, "")


def _update_field(dicom_obj, field, value):
    if field not in dicom_obj:
        return
    if value is None:
        dicom_obj.__delattr__(field)
    else:
        dicom_obj.__setattr__(field, value)


if __name__ == '__main__':
    OPTIONS = parse_args()
    print "Edit DICOM in a folder/sub folder to upload to XNAT."
    print "Time: ", str(datetime.now())

    # Get the folders/files in directory
    """scan_list = list()
    for subject in os.listdir(os.path.abspath(OPTIONS.directory)):
        subpath = os.path.join(os.path.abspath(OPTIONS.directory), subject)
        if os.path.isdir(subpath):
            if int(subject[:3])>0:
                for session in os.listdir(subpath):
                    sesspath = os.path.join(subpath, session)
                    if os.path.isdir(sesspath):
                        results = get_info_file(sesspath, OPTIONS.project)
                        if results:
                            scan_list.append(results)

    edit_info_dicom(scan_list)
    """

    with XnatUtils.get_interface() as xnat:
        # Scans list
        set_patient_comment = True
        list_subject = list()
        scan_list = XnatUtils.list_project_scans(xnat, OPTIONS.project)
        if list_subject:
            scan_list = filter(lambda x: x['subject_label'] in list_subject,
                               scan_list)

        start_proc = False if OPTIONS.session is not None else True
        for sc in sorted(scan_list, key=lambda k: k['session_label']):
            if OPTIONS.session == sc['session_label']:
                start_proc = True

            if start_proc:
                print("dicoms for session %s / scan %s "
                      % (sc['session_label'], sc['ID']))

                res_obj = XnatUtils.get_full_object(xnat, sc).resource('DICOM')
                if not res_obj.exists():
                    continue
                tmpdir = os.path.join(os.path.abspath(OPTIONS.directory),
                                      sc['session_label'],
                                      sc['ID'])
                if not os.path.exists(tmpdir):
                    os.makedirs(tmpdir)
                else:
                    print '  skip it. already processed.'
                    continue

                dcm_files = XnatUtils.download_files_from_obj(
                    directory=tmpdir, resource_obj=res_obj)
                for dcm_name in dcm_files:
                    # for dicom_path in dicom_files:
                    print "   file: %s " % dcm_name
                    dcm = dicom.read_file(dcm_name)
                    # edit the header
                    dcm.PatientName = sc['subject_label']
                    dcm.PatientID = sc['session_label']

                    # Remove tags
                    for field in REMOVE_BY_DEFAULT_NAME:
                        _remove_field(dcm, field)

                    if set_patient_comment:
                        temp = 'Project:%s;Subject:%s;Session:%s'
                        dcm.PatientComments = temp % (sc['project_id'],
                                                      sc['subject_label'],
                                                      sc['session_label'])
                    # dcm.SeriesDescription = sc['series_description']
                    dcm.save_as(dcm_name)
                XnatUtils.upload_files_to_obj(dcm_files, res_obj, remove=True)
                print "------"
    print "DICOMs read and edited."
    print '==================================================================='
