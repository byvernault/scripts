"""Convert fdf files into DICOM."""

import os
from dicom.dataset import Dataset, FileDataset
import datetime
import time
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
    argp.add_argument('-p', '--project', dest='project', required=True,
                      help='Sessions label on XNAT.')
    argp.add_argument('--subj', dest='subjects', default=None,
                      help='Subjects label on XNAT.')
    argp.add_argument('--sess', dest='sessions', default=None,
                      help='Sessions label on XNAT.')
    argp.add_argument('--force', dest='force', action='store_true',
                      default=False, help='Sessions label on XNAT.')
    argp.add_argument('--zip', dest='zip_fdf', action='store_true',
                      default=False, help='Zip the IMG resource.')
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


def fdf2dicom(fdf_files, fout=None):
    """Function to convert fdf to dicom.

    :param fdf_files: list of fdf files and procpar
    :param fout: name of the nifty output if needed
    :param return: numpy array of the image
                   filename generated
                   dictionary with information on the image
    """
    procpar_file = filter(lambda x: x.endswith('procpar'), fdf_files)
    fdf_files = filter(lambda x: x.endswith('.fdf'), fdf_files)
    dinfo = dict()

    # Read information from the first file:
    with open(fdf_files[0], 'r') as f:
        for line in f:
            if 'roi' in line:
                dinfo['spacing'] = line.split()[3][1:-2].split(',')
            if 'location' in line:
                dinfo['origin'] = line.split()[3][1:-2].split(',')
            if 'orientation' in line:
                dinfo['orientation'] = line.split()[3][1:-2].split(',')
            if 'bits' in line:
                nbits = int(line.split()[3][:-1])
            if 'matrix[]' in line:
                matsize = [int(line.split()[3][1:-1]),
                           int(line.split()[4][:-2])]
                dinfo['matsize'] = matsize
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
    with open(procpar_file[0]) as f:
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
            if isinstance(p_dict['pss'], list):
                val = p_dict['pss'][0]
            else:
                val = float(p_dict['pss'])
            test_affine = [[-1*pix_dim[0], 0, 0,
                            (float(p_dict['lro'])*10-pix_dim[0])/2],
                           [0, pix_dim[1], 0,
                            -1*(float(p_dict['lpe'])*10-pix_dim[1])/2],
                           [0, 0, pix_dim[2],
                            float(val)*10],
                           [0, 0, 0, 1]]
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
    return img_data, fout, dinfo


def get_files_list(directory, extension, add_procpar=False):
    fdf_paths = list()
    for fname in os.listdir(directory):
        fpath = os.path.join(directory, fname)
        if fpath.endswith(extension) or (fname == 'procpar' and add_procpar):
            fdf_paths.append(fpath)
    return fdf_paths


def zipping_files(scan_obj, fdf_dir):
    print '   --> more than one fdf files, zipping IMG resource.'
    fzip = 'fdf.zip'
    initdir = os.getcwd()
    # Zip all the files in the directory
    os.chdir(fdf_dir)
    os.system('zip -r '+fzip+' * > /dev/null')
    fzip_path = os.path.join(fdf_dir, fzip)
    # return to the initial directory:
    os.chdir(initdir)
    # upload
    if os.path.exists(fzip_path):
        print '   --> uploading zip IMG resource'
        scan_obj.resource('IMG').delete()
        scan_obj.resource('IMG').put_zip(fzip_path,
                                         overwrite=True,
                                         extract=False)


def write_dicom(pixel_array, filename, series_number, fdf_info,
                series_description, project, subject, session):
    """Write a dicom from a pixel_array (numpy).

    :param pixel_array: 2D numpy ndarray.
                        If pixel_array is larger than 2D, errors.
    :param filename: string name for the output file.
    :param ds_ori: original pydicom object of the pixel_array
    :param series_number: number of the series being processed
    :param series_description: series description for Osirix display
    :param project: XNAT Project ID
    :param subject: XNAT Subject label
    :param session: XNAT Session label
    """
    # Variables
    pixel_array = np.rot90(pixel_array)
    pixel_array = np.rot90(pixel_array)
    pixel_array = np.rot90(pixel_array)
    # less than zero
    # pixel_array[pixel_array < 0] = 0
    now = datetime.datetime.now()
    date = '%d%02d%02d' % (now.year, now.month, now.day)
    sop_id = '1.2.840.10008.5.1.4.1.1.4.%s' % date
    ti = str(time.time())
    uid = sop_id + ti
    # Other tags to set
    sop_uid = sop_id + str(now).replace('-', '')\
                               .replace(':', '')\
                               .replace('.', '')\
                               .replace(' ', '')
    # Number of frames
    size = pixel_array.shape
    nb_frames = None
    if len(size) == 3:
        nb_frames = size[2]
    elif len(size) == 4:
        nb_frames = size[2]*size[3]

    # Create the ds object
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = 'Secondary Capture Image Storage'
    file_meta.MediaStorageSOPInstanceUID = sop_id
    file_meta.ImplementationClassUID = '1.2.840.10008.5.1.4.1.1.4'
    ds = FileDataset(filename, {}, file_meta=file_meta, preamble="\0"*128)

    ds.SeriesDate = '%d%02d%02d' % (now.year, now.month, now.day)
    ds.ContentDate = '%d%02d%02d' % (now.year, now.month, now.day)
    ds.ContentTime = str(time.time())  # milliseconds since the epoch
    ds.StudyInstanceUID = uid
    ds.SeriesInstanceUID = uid
    # Other tags to set
    ds.SOPInstanceUID = sop_uid[:-1]
    ds.SOPClassUID = 'Secondary Capture Image Storage'
    ds.SecondaryCaptureDeviceManufctur = 'Python 2.7.3'

    # These are the necessary imaging components of the FileDataset object.
    ds.Modality = 'MR'
    ds.ConversionType = 'WSD'
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelRepresentation = 0
    ds.HighBit = 15
    ds.BitsStored = 16
    ds.BitsAllocated = 16
    ds.Columns = pixel_array.shape[0]
    ds.Rows = pixel_array.shape[1]
    ds.ProtocolName = '%s 9.4T' % series_description
    ds.StudyDescription = project
    ds.PatientsName = subject
    ds.PatientID = session
    ds.SeriesDescription = series_description
    ds.SeriesNumber = 1
    ds.SmallestImagePixelValue = pixel_array.min()
    ds.LargestImagePixelValue = pixel_array.max()
    ds.AcquisitionNumber = 1
    ds.SamplesperPixel = 1
    ds.PixelSpacing = '%s\%s' % (fdf_info['spacing'][0],
                                 fdf_info['spacing'][1])
    ds.SpacingBetweenSlices = float(fdf_info['spacing'][2])
    ds.ImageOrientation = '\\'.join(fdf_info['orientation'])
    ds.PatientPosition = '\\'.join(fdf_info['origin'])
    if nb_frames:
        ds.NumberOfFrames = nb_frames

    # Organise the array:
    if len(size) == 3:
        pixel_array2 = np.zeros((size[0]*size[2], size[1]))
        for i in range(size[2]):
            pixel_array2[size[0]*i:size[0]*(i+1), :] = pixel_array[:, :, i]
    elif len(size) > 3:
        pixel_array2 = np.zeros((size[0]*size[2]*size[3], size[1]))
        for i in range(size[2]):
            for j in range(size[3]):
                pixel_array2[size[0]*j+i*size[3]*size[0]:
                             size[0]*(j+1)+i*size[3]*size[0],
                             :] = pixel_array[:, :, i, j]
    else:
        pixel_array2 = pixel_array

    # Set the Image pixel array
    if pixel_array2.dtype != np.uint16:
        pixel_array2 = pixel_array2.astype(np.uint16)
        print pixel_array2.max()
        print pixel_array2.min()

    ds.PixelData = pixel_array2.tostring()
    # Save the image
    ds.save_as(filename)

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
        li_scans = sorted(li_scans, key=lambda k: k['session_label'])
        for scan_d in li_scans:
            if scan_d['ID'] == 'n004':
                print (' -> converting session: %s /scan: %s'
                       % (scan_d['session_label'], scan_d['ID']))
                if 'IMG' in scan_d['resources']:
                    if 'NIFTI' not in scan_d['resources'] or args.force:
                        tmp_dir = os.path.join(args.directory,
                                               scan_d['session_label'],
                                               scan_d['ID'])
                        if not os.path.isdir(tmp_dir):
                            os.makedirs(tmp_dir)
                        scan_obj = XnatUtils.get_full_object(xnat, scan_d)
                        # Download:
                        files = XnatUtils.download_files_from_obj(
                                                tmp_dir, scan_obj.resource('IMG'))
                        if len(files) > 1 and args.zip_fdf:
                            zipping_files(scan_obj, os.path.dirname(files[0]))

                        if len(files) == 1 and files[0].endswith('.zip'):
                            fdf_dir = os.path.dirname(files[0])
                            os.system('unzip -d %s -j %s > /dev/null'
                                      % (fdf_dir, files[0]))
                            os.remove(files[0])
                            files = get_files_list(fdf_dir, '.fdf',
                                                   add_procpar=True)

                        # Convert:
                        fdf_files = filter(lambda x: x.endswith('.fdf'), files)
                        nii_file = os.path.join(
                           tmp_dir,
                           ('%s.nii'
                            % os.path.basename(fdf_files[0]).split('.')[0]))
                        img_data, nii_file, dinfo = fdf2dicom(files, fout=nii_file)

                        # Upload:
                        if os.path.isfile(nii_file):
                            # XnatUtils.upload_file_to_obj(
                            #        nii_file, scan_obj.resource('NIFTI'),
                            #        remove=True)
                            # Convert to dicom:
                            write_dicom(img_data, nii_file[:-3]+'dcm',
                                        scan_d['ID'],
                                        dinfo,
                                        scan_d['series_description'],
                                        args.project,
                                        scan_d['subject_label'],
                                        scan_d['session_label'])

                            if os.path.isfile(nii_file[:-3]+'dcm'):
                                print 'YEAH DICOM'
                                # XnatUtils.upload_file_to_obj(
                                #        nii_file[:-3]+'dcm',
                                #        scan_obj.resource('DICOM'),
                                #        remove=True)
                        else:
                            print '  error: no nifti created.'
                    else:
                        print '  warning: NIFTI already generated. Skipping.'
                else:
                    print '  warning: no IMG resources found. Skipping.'
    finally:
        xnat.disconnect()
