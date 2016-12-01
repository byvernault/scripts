"""TEST Script for different purpose."""

import os
# import re
import glob
# import fnmatch
import dicom
import re
import dicom.UID
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


if __name__ == '__main__':
    from pyxnat.core.uriutil import uri_parent
    from pyxnat.core.jsonutil import JsonTable
    import difflib

    args = parse_args()

    xnat = XnatUtils.get_interface(host='http://cmic-xnat.cs.ucl.ac.uk')
    li_sessions = XnatUtils.list_sessions(xnat, 'prion')
    for session in li_sessions:
        sess = XnatUtils.get_full_object(xnat, session)
        """path = 'xnat:mrsessiondata/fields/field\
[name=geneticstate]/field'
        query_str = '?columns=ID,%s' % path
        get_uri = uri_parent(sess.attrs._eobj._uri) + query_str
        print get_uri
        jdata = JsonTable(sess.attrs._intf._get_json(get_uri)
                          ).where(ID=sess.attrs._get_id())
        print jdata

        print jdata.headers()

        header = difflib.get_close_matches(path.split('/')[-1],
                                           jdata.headers())
        print header"""
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

    """csv_file = '/Users/byvernault/data/files/Prion_info.csv'
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
