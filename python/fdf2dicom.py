"""Convert fdf files into DICOM."""

import os
import dicom
import scipy
import nibabel as nib
import numpy as np
from dax import XnatUtils


__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Convert fdf files into DICOM."

HEADER_INFO = ['comment', 'tDELTA', 'tdelta', 'gdiff', 'dro', 'dpe', 'dsl',
               'te', 'tr', 'lro', 'lpe', 'thk', 'gap', 'pss', 'nt', 'max_bval']


def parse_args():
    """Parser for arguments."""
    from argparse import ArgumentParser, RawDescriptionHelpFormatter
    argp = ArgumentParser(prog='fdf2dicom', description=__purpose__,
                          formatter_class=RawDescriptionHelpFormatter)
    argp.add_argument('-d', "--directory", dest='directory', required=True,
                      help='Temp directory to store data.')
    argp.add_argument('-p', '--project', dest='projects', required=True,
                      help='Sessions label on XNAT.')
    argp.add_argument('--subj', dest='subjects', required=True,
                      help='Subjects label on XNAT.')
    argp.add_argument('--sess', dest='sessions', required=True,
                      help='Sessions label on XNAT.')
    return argp.parse_args()


def type_it(parval):
    parval = parval.split()[1:]  # first is length of parameter
    for pct, p in enumerate(parval):
        try:
            parval[pct] = int(p)
        except ValueError:
            try:
                parval[pct] = float(p)
            except ValueError:  # string case
                pass
    if len(parval) == 1:
        parval = parval[0]
    return parval


def fdf2dicom(fdf_files, fout):
    """Function to convert fdf to dicom.
    """
    with open(fdf_files[0], 'r') as f:
        for line in f:
            if 'bits' in line:
                nbits = int(line.split()[3][:-1])
            if 'matrix[]' in line:
                matsize = [int(line.split()[3][1:-1]),
                           int(line.split()[4][:-2])]
            if 'bigendian' in line:
                endflag = int(line.split()[3][:-1])
                endstr = '<' if endflag == 0 else '>'

    img_data = np.zeros([matsize[0], matsize[1], len(fdf_files)])
    for fct, fname in enumerate(fdf_files):
        with open(fname, 'rb') as f:
            imgtmp = np.frombuffer(f.read(), '%sf' % endstr)
            img_data[:, :, fct] = np.reshape(imgtmp[(-matsize[0]*matsize[1]):],
                                             [matsize[0], matsize[1]]).T

    p_dict = dict()
    with open('procpar') as f:
        for line in f:
            for vname in HEADER_INFO:
                # see variable name definitions in fdf_info
                if line.split()[0] == vname:
                    p_dict[vname] = type_it(f.next())
                    # want to pass in the next line with the variable value
                    # to read, not the line with the variable name
    if fout is not None:
        if fout.endswith('.nii') or fout.endswith('.nii.gz'):
            try:
                len_b = len(p_dict['dro'])
            except TypeError:  # only one diffusion direction
                len_b = 1
            except KeyError:  # not a diffusion sequence
                len_b = 1
            if len_b > 1:
                new_data = [img_data.shape[0], img_data.shape[1],
                            img_data.shape[2]/len_b, len_b]
                img_data = np.reshape(img_data, new_data)
            pix_dim = [float(p_dict['lro'])*10/img_data.shape[0],
                       float(p_dict['lpe'])*10/img_data.shape[1],
                       p_dict['thk']+10*float(p_dict['gap'])]
            test_affine = r_[c_[-1*pix_dim[0], 0, 0,
                                (float(p_dict['lro'])*10-pix_dim[0])/2],
                             c_[0, pix_dim[1], 0,
                                -1*(float(p_dict['lpe'])*10-pix_dim[1])/2],
                             c_[0, 0, pix_dim[2],
                                p_dict['pss'][0]*10],
                             c_[0, 0, 0, 1]]
            img_nii = nib.Nifti1Image(img_data, test_affine)
            try:
                fout = fout[:-7]+'_b'+str(int(p_dict['max_bval']))+fout[-7:]
                # add b-value to filename if diffusion sequence
            except KeyError:
                print "Not a diffusion sequence; filename stays as fout"
            nib.save(img_nii, fout)
        elif fout.endswith('.mat'):
            img_dict = p_dict
            img_dict['imgData'] = img_data
            try:
                fout = fout[:-7]+'_b'+str(int(p_dict['max_bval']))+fout[-7:]
                # add b-value to filename if diffusion sequence
            except KeyError:
                print "Not a diffusion sequence; filename stays as fout"
            scipy.io.savemat(fout, img_dict)
    return img_data


if __name__ == '__main__':
    args = parse_args()

    # Scans on XNAT:
    try:
        xnat = XnatUtils.get_interface()
        li_scans = XnatUtils.list_project_scans(xnat, args.project)
        # Filter:
        if args.sessions:
            li_scans = XnatUtils.filter_list_dicts_regex(
                           li_scans, 'session_label', args.sessions.split(','))
        if args.subjects:
            li_scans = XnatUtils.filter_list_dicts_regex(
                           li_scans, 'subject_label', args.subjects.split(','))
        li_scans = XnatUtils.filter_list_dicts_regex(
                       li_scans, 'resources', args.subjects.split(','))
        li_scans = sorted(li_scans, key=lambda k: k['session_label'])
        for scan_d in li_scans:
            if 'IMG' in scan_d['resources']:
                scan_obj = XnatUtils.get_full_object(xnat, scan_d)
                # Download:
                files = XnatUtils.download_files_from_obj(
                                        xnat, scan_obj.resource('IMG'))
                # Convert:
                fdf2dicom(files, dicomdir)
                # Upload:

    finally:
        xnat.disconnect()
