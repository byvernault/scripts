"""TEST Script for different purpose."""

import os
# import re
import glob
# import fnmatch
import dicom
import re
import dicom.UID
import subprocess as sb
from dicom.sequence import Sequence
from dicom.dataset import Dataset, FileDataset
# import shutil
# import time
import datetime
import nibabel as nib
import numpy as np
# import scipy
# import collections
from dax import XnatUtils
import Ben_functions
# import shlex

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Set the scna types from DICOM header."


def get_adni_id(value):
    reg1 = re.compile('[0-9][0-9][0-9]S[0-9][0-9][0-9][0-9]')
    reg2 = re.compile('[0-9][0-9][0-9]_S_[0-9][0-9][0-9][0-9]')
    result = reg1.findall(value)
    if result:
        return result[0]
    else:
        result = reg2.findall(value)
        if result:
            return result[0]
    return None


def parse_args():
    """Parser for arguments."""
    from argparse import ArgumentParser, RawDescriptionHelpFormatter
    argp = ArgumentParser(prog='Set_types_from_dicom', description=__purpose__,
                          formatter_class=RawDescriptionHelpFormatter)
    argp.add_argument('-p', "--project", dest='project',
                      help='Project ID on XNAT.')
    argp.add_argument('-d', '--directory', dest='directory',
                      help='Directory to store temp data.')
    argp.add_argument('-s', '--session', dest='sessions', default=None,
                      help='Sessions label on XNAT.')
    return argp.parse_args()


def dcm2nii(dicom_fpath):
    """Convert dicom to nifti using dcm2nii.

    :param dicom_fpath: first dicom in the folder
    :return boolean: true if conversion succeeded, false otherwise
    """
    print "   --> convert dcm to nii..."
    dcm2nii_cmd = '''{dcm2nii} \
-a n -e n -d n -g y -f n -n y -p n -v y -x n -r n \
{dicom}'''.format(dcm2nii='dcm2niix', dicom=dicom_fpath)
    try:
        sb.check_output(dcm2nii_cmd.split())
    except sb.CalledProcessError:
        print "    - warning: dcm to nii conversion failed"
        return False

    return True


def get_dicom_list(directory):
    """get the list of DICOMs file from the directory.

    :param directory: directory containing the DICOM files.
    :return list(): list of filepaths that are dicoms in directory
    """
    fnames = os.listdir(directory)
    dicom_paths = list()
    for fname in fnames:
        fpath = os.path.join(directory, fname)
        if is_dicom(fpath):
            dicom_paths.append(fpath)

    return dicom_paths


def check_outputs(nifti_list, bval, bvec):
    """Check that the outputs are right (opening nifti works).

    :param nifti_list: python list of nifti paths
    :param bval: python list of bval paths
    :param bvec: python list of bvec paths
    :return boolean: true if outputs are fine, false otherwise
    """
    for nifti_fpath in nifti_list:
        try:
            nib.load(nifti_fpath)
        except:
            msg = '''    - warning: {file} is not a proper NIFTI'''
            print msg.format(file=os.path.basename(nifti_fpath))
            return False
    if bval or bvec:
        if not os.path.isfile(bval) or not os.path.isfile(bvec):
            print "    - warning: no bval/bvec generated (DTI scan)"
            return False

    return True


def is_dicom(fpath):
    """check if the file is a DICOM medical data.

    :param fpath: path of the file
    :return boolean: true if it's a DICOM, false otherwise
    """
    file_call = '''file {fpath}'''.format(fpath=fpath)
    output = sb.check_output(file_call.split())
    if 'dicom' in output.lower():
        return True

    return False


def upload_converted_images(dicom_files, dcm_dir, scan_obj):
    """Upload the images after checking them.

    :param dicom_files: list of dicoms files to zip
    :param dcm_dir: directory containing the dicoms
    :param scan_obj: scan pyxnat object from XNAT
    """
    # Local variables
    nifti_list = []
    bval_fpath = ''
    bvec_fpath = ''

    # Get the bvec/bval files and NIFTI from the folder:
    for fpath in glob.glob(os.path.join(dcm_dir, '*')):
        if os.path.isfile(fpath):
            if fpath.lower().endswith('.bval'):
                bval_fpath = fpath
            if fpath.lower().endswith('.bvec'):
                bvec_fpath = fpath
            if fpath.lower().endswith('.nii.gz'):
                nifti_list.append(fpath)
            if fpath.lower().endswith('.nii'):
                os.system('gzip '+fpath)
                nifti_list.append(fpath+'.gz')

    # Check NIFTI:
    good_to_upload = check_outputs(nifti_list, bval_fpath, bvec_fpath)
    # Upload files:
    if good_to_upload:
        if os.path.isfile(bval_fpath) and os.path.isfile(bvec_fpath):
            # BVAL/BVEC
            XnatUtils.upload_file_to_obj(bval_fpath,
                                         scan_obj.resource('BVAL'),
                                         remove=True)
            XnatUtils.upload_file_to_obj(bvec_fpath,
                                         scan_obj.resource('BVEC'),
                                         remove=True)
            # keep the NII with the same name than the BVAL/BVEC
            nifti_list = filter(lambda x: x[:-7] == bval_fpath[:-5],
                                nifti_list)
            XnatUtils.upload_files_to_obj(nifti_list,
                                          scan_obj.resource('NIFTI'),
                                          remove=True)
        else:
            # NII
            XnatUtils.upload_files_to_obj(nifti_list,
                                          scan_obj.resource('NIFTI'),
                                          remove=True)

        # ZIP the DICOM if more than one
        if len(dicom_files) > 1:
            # Remove the files created before zipping:
            for nii_file in nifti_list:
                os.remove(nii_file)
            if os.path.isfile(bval_fpath) and os.path.isfile(bvec_fpath):
                os.remove(bval_fpath)
                os.remove(bvec_fpath)
            print '   --> more than one dicom file, zipping dicoms.'
            zip_path = os.path.join(dcm_dir, 'dicoms.zip')
            zip_files = glob.glob(os.path.join(dcm_dir, '*'))
            zip_list(zip_files, zip_path)

        # more than one NIFTI uploaded
        if len(nifti_list) > 1:
            print "    - warning: more than one NIFTI upload"


def dcmdjpeg(dcm_dir):
    """Converting the dicom to jpeg dicoms.

    :param dcm_dir: directory containing the dicoms
    """
    print "   --> run dcmdjpeg on the DICOMs to convert \
JPEG DICOM to regular DICOM."
    for number, dicoms in enumerate(os.listdir(dcm_dir)):
        msg = '''{dcmdjpeg} {original_dcm} {new_dcm}'''
        new_dcm = 'final_'+str(number)+'.dcm'
        dcmdjpeg_cmd = msg.format(dcmdjpeg='dcmdjpeg',
                                  original_dcm=os.path.join(dcm_dir, dicoms),
                                  new_dcm=os.path.join(dcm_dir, new_dcm))
        os.system(dcmdjpeg_cmd)
        os.remove(os.path.join(dcm_dir, dicoms))


def zip_list(li_files, zip_path, subdir=False):
    """Zip all the files in the list into a zip file.

    :param li_files: python list of files for the zip
    :param zip_path: zip path
    :param subdir: copy the subdirectories as well. Default: False.
    """
    import zipfile
    if not zip_path.lower().endswith('.zip'):
        zip_path = '%s.zip' % zip_path
    with zipfile.ZipFile(zip_path, 'w') as myzip:
        for fi in li_files:
            if subdir:
                myzip.write(fi, compress_type=zipfile.ZIP_DEFLATED)
            else:
                myzip.write(fi, arcname=os.path.basename(fi),
                            compress_type=zipfile.ZIP_DEFLATED)


if __name__ == '__main__':
    OPTIONS = parse_args()
    directory = XnatUtils.makedir(OPTIONS.directory)
    type_scans = ['fl3d-cor_bh_15fadynamic', 'fl3d-cor_bh_15fa_dynamic_50meas',
                  'fl3d-cor_15fa_dynamic_50meas', 'fl3d-cor_bh_15fadynamic']

    XNAT = XnatUtils.get_interface(host='https://prostate-xnat.cs.ucl.ac.uk')

    list_scans = XnatUtils.list_project_scans(XNAT, OPTIONS.project)
    if OPTIONS.sessions:
        list_scans = filter(
            lambda x: x['session_label'] in OPTIONS.sessions.split(','),
            list_scans)
    list_scans = filter(lambda x: 'NIFTI' not in x['resources'], list_scans)
    number_scans = len(list_scans)
    print "Converting the %s scans found." % (number_scans)
    for index, scan in enumerate(sorted(list_scans,
                                        key=lambda k: k['session_label'])):
        message = ' * {index}/{total} -- Session: {session} -- Scan: {scan}'
        print message.format(index=index+1,
                             total=number_scans,
                             session=scan['session_label'],
                             scan=scan['ID'])
        if scan['type'] in type_scans:
            scan_obj = XnatUtils.get_full_object(XNAT, scan)
            if scan_obj.exists() and \
               len(scan_obj.resource('DICOM').files().get()) > 0:
                print "   --> downloading DICOM ..."
                tmp_dir = os.path.join(directory, scan['session_label'],
                                       scan['ID'])
                os.makedirs(tmp_dir)
                fpaths = XnatUtils.download_files_from_obj(
                            tmp_dir,
                            scan_obj.resource("DICOM"))
                if not fpaths:
                    print '    - warning: DICOM -- no files.'
                else:
                    dcm_dir = os.path.join(tmp_dir, 'DICOM')
                    if len(fpaths) == 1 and fpaths[0].endswith('.zip'):
                        if not os.path.exists(dcm_dir):
                            os.makedirs(dcm_dir)
                        os.system('unzip -d %s -j %s > /dev/null'
                                  % (dcm_dir, fpaths[0]))
                        os.remove(fpaths[0])
                    dicom_files = get_dicom_list(dcm_dir)

                    if dicom_files:
                        # convert dcm to nii
                        conversion_status = dcm2nii(dicom_files[0])

                        if not conversion_status:
                            # Convert dcm via dcmdjpeg
                            dcmdjpeg(dcm_dir)
                            # try again dcm2nii
                            dcm_fpath = os.path.join(dcm_dir, 'final_1.dcm')
                            conversion_status = dcm2nii(dcm_fpath)

                        # Check if Nifti created:
                        nii_li = [f for f in os.listdir(dcm_dir)
                                  if f.endswith('.nii.gz') or f.endswith('.nii')]
                        if not nii_li:
                            print "    - warning: dcm to nii failed with \
conversion dcmjpeg. no upload."
                        else:
                            # UPLOADING THE RESULTS
                            upload_converted_images(dicom_files, dcm_dir,
                                                    scan_obj)

                        # clean tmp folder
                        # XnatUtils.clean_directory(directory)
                    else:
                        print "    - ERROR : no proper DICOM files \
found from the resource on XNAT. "

            else:
                print "    - ERROR : issue with resource DICOM: \
no files or resource. "

    XNAT.disconnect()

    """xnat = XnatUtils.get_interface(host='http://cmic-xnat.cs.ucl.ac.uk')
    li_sessions = XnatUtils.list_sessions(xnat, 'prion')
    for session in li_sessions:
        sess = XnatUtils.get_full_object(xnat, session)
        geneticstate = sess.xpath("/xnat:MRSession/xnat:fields/xnat:\
field[@name='geneticstate']/text()[2]")
        if not geneticstate:
            other_sess = sess.parent().experiments()[0]
            other_geneticstate = other_sess.xpath("/xnat:MRSession/xnat:fields/xnat:\
field[@name='geneticstate']/text()[2]")
            other_mrc = other_sess.xpath("/xnat:MRSession/xnat:fields/xnat:\
field[@name='mrc']/text()[2]")
            print session['label'], other_sess.label(), other_geneticstate, other_mrc
            if other_geneticstate:
                mset_dict = dict()
                xsitype_sess = sess.attrs.get('xsiType')
                mset_dict[xsitype_sess+"/fields/field[name=geneticstate]/field"] = other_geneticstate[0]
                mset_dict[xsitype_sess+"/fields/field[name=mrc]/field"] = other_mrc[0]
                sess.attrs.mset(mset_dict)
        # print "Value:", sess.parent().xpath("/xnat:Subject/xnat:fields/xnat:field[@name='geneticstate']/text()[2]")[0]

        # if not geneticstate:
        #    print session['label']

    csv_file = '/Users/byvernault/data/files/Prion_info.csv'
    csv_info = Ben_functions.read_csv(csv_file)
    csv_info = sorted(csv_info, key=lambda k: k['session'])
    di = dict()
    for info in csv_info:
        di[info['nifti'].split('_')[0]] = info['subject']

    flair_dir = '/Users/byvernault/Downloads/FLAIR_369_20161122'
    flair_files = glob.glob(os.path.join(flair_dir, '*', '*.nii.gz'))
    for nifti in flair_files:
        basename = os.path.basename(nifti)
        labels = basename.split('-')
        prion_code = labels[0].split('_')[0]
        date = labels[0].split('_')[1]
        subject_label = di[prion_code]
        session_label = '%s_%s' % (subject_label, date)
        print 'scan,prion,%s,MR,%s,%s,FLAIR,t2_tirm_tra_dark-fluid,usable,\
NIFTI,%s' % (subject_label, session_label, labels[1], nifti)

    directory = os.path.abspath(args.directory)
    if not os.path.isdir(directory):
        os.makedirs(directory)

    # Scans on XNAT:
    try:
        xnat = XnatUtils.get_interface()
        li_scans = XnatUtils.list_project_scans(xnat, args.project)
        if args.sessions:
            li_scans = XnatUtils.filter_list_dicts_regex(
                li_scans, 'session_label', args.sessions.split(','))
        li_scans = sorted(li_scans, key=lambda k: k['session_label'])
        for scan_d in li_scans:
            if 'DICOM' in scan_d['resources']:
                print (" - setting tags for %s/%s"
                       % (scan_d['session_label'], scan_d['ID']))
                tmp_dir = os.path.join(directory, scan_d['session_label'],
                                       scan_d['ID'])
                if not os.path.isdir(tmp_dir):
                    os.makedirs(tmp_dir)
                # Download the dicom and read the header:
                scan_obj = XnatUtils.get_full_object(xnat, scan_d)
                dicom_files = XnatUtils.download_files_from_obj(
                                tmp_dir, scan_obj.resource('DICOM'))
                if len(dicom_files) > 1:
                    # for dicom_path in dicom_files:
                    for dicom_file in dicom_files:
                        dcm = dicom.read_file(dicom_file)
                        dcm.remove_private_tags()
                        dcm.save_as(dicom_file)

                    print '  removing tags done ...'
                    print '   --> more than one dicom file, zipping dicoms.'
                    fzip = 'dicoms.zip'
                    initdir = os.getcwd()
                    tmp_dir = os.path.join(tmp_dir, 'DICOM')
                    # Zip all the files in the directory
                    os.chdir(tmp_dir)
                    os.system('zip -r '+fzip+' * > /dev/null')
                    # return to the initial directory:
                    os.chdir(initdir)
                    # upload
                    if os.path.exists(os.path.join(tmp_dir, fzip)):
                        print '   --> uploading zip dicoms'
                        scan_obj.resource('DICOM').delete()
                        scan_obj.resource('DICOM').put_zip(
                            os.path.join(tmp_dir, fzip),
                            overwrite=True, extract=False)
                    print '  upload done ...'
                else:
                    print '  skipping ... '

    finally:
        xnat.disconnect()

    xnat = XnatUtils.get_interface(host='http://cmic-xnat.cs.ucl.ac.uk')
    li_scans = XnatUtils.list_project_scans(xnat, 'prion')
    li_scans = sorted(li_scans, key=lambda k: k['subject_label'])
    print 'subject,session,scan,nifti'
    for scan in li_scans:
        if 'NIFTI' in scan['resources']:
            scan_obj = XnatUtils.get_full_object(xnat, scan)
            resources_file = scan_obj.resource('NIFTI').files().get()[:]
            print '%s,%s,%s,%s' % (scan['subject_label'],
                                   scan['session_label'],
                                   scan['ID'],
                                   ' '.join(resources_file))

    xnat.disconnect()
    # args = parse_args()
    # adni_id = args.sessions
    DEFAULT_CSV_LIST = [
             'object_type', 'project_id', 'subject_label', 'session_type',
             'session_label', 'as_label', 'as_type', 'as_description',
             'quality', 'resource', 'fpath']
    csv_file = '/Users/byvernault/data/prion_asses/download_report.csv'
    csv_file = '/Users/byvernault/data/files/Prion_info.csv'
    csv_info = Ben_functions.read_csv(csv_file)
    csv_info = sorted(csv_info, key=lambda k: k['session'])
    di = dict()
    for info in csv_info:
        if not info['subject'] in di:
            di[info['subject']] = info['nifti'].split('-')[0].split('_')[0]

    csv_info = sorted(csv_info, key=lambda k: k['session'])
    for key in sorted(di.keys(), key=lambda x: di[x]):
        print key, di[key]

    for index, info in enumerate(csv_info):
        labels = info['as_label'].split('-x-')
        if labels[1] != info['as_label']:
            new_label = '-x-'.join([
                    info['project_id'],
                    info['subject_label'],
                    info['session_label'],
                    labels[3],
                    labels[4]])
            print new_label
            info['as_label'] = new_label
            csv_info[index] = info

    tmp = '{object_type},{project_id},{subject_label},{session_type},\
{session_label},{as_label},{as_type},{as_description},{quality},{resource},\
{fpath}'
    print ','.join(DEFAULT_CSV_LIST)
    for info in csv_info:
        print tmp.format(
                object_type=info['object_type'],
                project_id=info['project_id'],
                subject_label=info['subject_label'],
                session_type=info['session_type'],
                session_label=info['session_label'],
                as_label=info['as_label'],
                as_type=info['as_type'],
                as_description=info['as_description'],
                quality=info['quality'],
                resource=info['resource'],
                fpath=info['fpath'],
                )

    previous_subject = ''
    previous_adni_id = ''
    for nifti in csv_info:
        if previous_subject != nifti['subject']:
            print 'Subject: %s / session: %s' % (nifti['subject'],
                                                 nifti['session'])
            previous_subject = nifti['subject']
            previous_adni_id = get_adni_id(nifti['nifti'])
        else:
            adni_id = get_adni_id(nifti['nifti'])
            if not adni_id:
                print '  id not found'
            elif not previous_adni_id:
                print '  previous id not found'
                previous_adni_id = adni_id
            elif adni_id != previous_adni_id and \
                 adni_id != previous_adni_id.replace('_', ''):
                print ('  error: two different ids: %s -- %s '
                       % (previous_adni_id,  adni_id))

    niftis = filter(lambda x: adni_id in x['nifti'], csv_info)
    for n in niftis:
        print n['session'], n['nifti']"""
