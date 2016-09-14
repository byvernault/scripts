"""TEST number 2 Script for different purpose."""

import os
import time
import glob
import dicom
# from scipy import ndimage
from dicom.sequence import Sequence
import datetime
import numpy as np
import nibabel as nib
from dicom.dataset import Dataset, FileDataset
# import Ben_functions

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Test Code 2"

DEFAULT_MAPS = ['FIT_FobjCamino.nii', 'FIT_R.nii', 'FIT_fEES.nii',
                'FIT_fIC.nii', 'FIT_fVASC.nii', 'FIT_cellularity.nii']
# DICOMs TAG to copy
TAGS_TO_COPY = [0x00185100,  # Patient Position
                0x00180050,  # Slice Thicknes
                0x00180088,  # Spacing Between Slices
                0x00181312,  # In-plane Phase Encoding
                0x00200032,  # Image Position
                0x00200037,  # Image Orientation
                0x00280030]  # Pixel spacing

ORDER_MAPS = ['FIT_fIC', 'FIT_cellularity',
              'FIT_fEES', 'FIT_fVASC', 'FIT_R']
C_RANGE = {'FIT_dir': {'min': 1*10**-10, 'max': 2.9*10**-9},
           'FIT_FobjCamino': {'min': 0, 'max': 50},
           'FIT_Fobj': {'min': 0, 'max': 1},
           'FIT_R': {'min': 0, 'max': 15.10*10**-6},
           'FIT_fIC': {'min': 0, 'max': 1},
           'FIT_cellularity': {'min': 2*10**11, 'max': 1.5*10**14},
           'FIT_fEES': {'min': 0, 'max': 1},
           'FIT_fVASC': {'min': 0, 'max': 1},
           'FIT_R_0-3u': {'min': 0, 'max': 2.67*10**-6},
           'FIT_R_3-6u': {'min': 3.56*10**-6, 'max': 5.34*10**-6},
           'FIT_R_6-9u': {'min': 6.22*10**-6, 'max': 8.89*10**-6},
           'FIT_R_9-12u': {'min': 9.77*10**-6, 'max': 11.55*10**-6},
           'FIT_R_12-15u': {'min': 12.44*10**-6, 'max': 15.10*10**-6},
           'FIT_fIC_0-3u': {'min': 0, 'max': 1},
           'FIT_fIC_3-6u': {'min': 0, 'max': 1},
           'FIT_fIC_6-9u': {'min': 0, 'max': 1},
           'FIT_fIC_9-12u': {'min': 0, 'max': 1},
           'FIT_fIC_12-15u': {'min': 0, 'max': 1},
           'FIT_cell_0-3u': {'min': 3*10**12, 'max': 5*10**16},
           'FIT_cell_3-6u': {'min': 2*10**12, 'max': 3*10**14},
           'FIT_cell_6-9u': {'min': 1*10**12, 'max': 2.5*10**14},
           'FIT_cell_9-12u': {'min': 1*10**12, 'max': 5*10**13},
           'FIT_cell_12-15u': {'min': 2*10**11, 'max': 5.5*10**13},
           'FIT_FobjCamino': {'min': 0, 'max': 50}}


def write_dicom(pixel_array, filename, ds_ori,
                series_number, sop_id, series_description,
                subject, session):
    """Write a dicom from a pixel_array (numpy).

    :param pixel_array: 2D numpy ndarray.
                        If pixel_array is larger than 2D, errors.
    :param filename: string name for the output file.
    :param ds_ori: original pydicom object of the pixel_array
    :param volume_number: number of the volume being processed
    :param series_number: number of the series being processed
    :param sop_id: SOPInstanceUID for the DICOM
    :param series_description: series description for Osirix display
    """
    # Set the DICOM dataset
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = 'Secondary Capture Image Storage'
    file_meta.MediaStorageSOPInstanceUID = ds_ori.SOPInstanceUID
    file_meta.ImplementationClassUID = ds_ori.SOPClassUID
    ds = FileDataset(filename, {}, file_meta=file_meta, preamble="\0"*128)

    # Copy the tag from the original DICOM
    for tag, d_obj in ds_ori.items():
        if tag != ds_ori.data_element("PixelData").tag:
            ds[tag] = d_obj

    # Other tags to set
    ds.SeriesNumber = series_number
    ds.PatientName = subject
    ds.PatientID = session
    sop_uid = sop_id + str(datetime.datetime.now()).replace('-', '')\
                                                   .replace(':', '')\
                                                   .replace('.', '')\
                                                   .replace(' ', '')
    ds.SOPInstanceUID = sop_uid[:-1]
    ds.ProtocolName = series_description
    # Set SeriesDate/ContentDate
    now = datetime.date.today()
    ds.SeriesDate = '%d%02d%02d' % (now.year, now.month, now.day)
    ds.ContentDate = '%d%02d%02d' % (now.year, now.month, now.day)
    ds.Modality = 'MR'
    ds.ConversionType = 'WSD'
    ds.StudyDescription = 'INNOVATE'
    ds.SeriesDescription = series_description
    ds.AcquisitionNumber = 1
    ds.SamplesperPixel = 1
    ds.PhotometricInterpretation = 'MONOCHROME2'
    ds.SecondaryCaptureDeviceManufctur = 'Python 2.7.3'
    nb_frames = pixel_array.shape[2]*pixel_array.shape[3]
    ds.NumberOfFrames = nb_frames
    ds.PixelRepresentation = 0
    ds.HighBit = 15
    ds.BitsStored = 8
    ds.BitsAllocated = 8
    ds.SmallestImagePixelValue = pixel_array.min()
    ds.LargestImagePixelValue = pixel_array.max()
    ds.Columns = pixel_array.shape[0]
    ds.Rows = pixel_array.shape[1]

    # Fixing the sequence if the number of frames was less than the original
    # it happens if we remove the last volume for phillips data (mean)
    if ds_ori.NumberOfFrames > nb_frames:
        new_seq = Sequence()
        for i in xrange(0, ds_ori.NumberOfFrames):
            if i % 5 == 0:  # take one slice for each (14)
                new_seq.append(ds_ori[0x5200, 0x9230][i])
        ds[0x5200, 0x9230].value = new_seq

    # Organise the array:
    pixel_array2 = np.zeros((pixel_array.shape[0]*pixel_array.shape[2],
                             pixel_array.shape[1]))
    for i in range(pixel_array.shape[2]):
        pixel_array2[pixel_array.shape[0]*i:pixel_array.shape[0]*(i+1),
                     :] = pixel_array[:, :, i, 0]

    # Set the Image pixel array
    if pixel_array2.dtype != np.uint8:
        pixel_array2 = pixel_array2.astype(np.uint8)

    ds.PixelData = pixel_array2.tostring()
    # Save the image
    ds.save_as(filename)


def convert_niftis_2_dicoms(nifti_folder, sour_obj, output_folder, nbacq):
    """Convert 3D niftis into DICOM files.

    :param nifti_path: path to the nifti file
    :param sour_obj: pydicom object for the source dicom
    :param output_folder: folder where the DICOM files will be saved
    :param nbacq: Acquisition number
    :return: None
    """
    if not os.path.isdir(nifti_folder):
        raise Exception("NIFTY Folder %s not found." % nifti_folder)
    for i, maps_name in enumerate(ORDER_MAPS):
        suffix = 'original'
        # File
        nii_map = os.path.join(nifti_folder, '%s.nii' % maps_name)
        if not os.path.isfile(nii_map):
            raise Exception("NIFTY file %s not found." % nii_map)
        # Naming
        label = os.path.basename(nii_map)[:-4]
        series_description = '%s_%d_%s' % (label, nbacq, suffix)

        # Edit Niftys
        f_img = nib.load(nii_map)
        f_data = f_img.get_data()
        # Rotation 270
        f_data = np.rot90(f_data)
        f_data = np.rot90(f_data)
        f_data = np.rot90(f_data)
        # Normalizing data:
        dmin = C_RANGE[label]['min']
        dmax = C_RANGE[label]['max']
        f_data[f_data < dmin] = dmin
        f_data[f_data > dmax] = dmax
        # Scale numbers to uint8
        f_data = (f_data - dmin)*255.0/(dmax - dmin)

        # Make output_folder:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Series Number and SOP UID
        series_number = 87000 + i
        sop_id = sour_obj.SOPInstanceUID.split('.')
        sop_id = '.'.join(sop_id[:-1])+'.'

        # Write the dicom
        filename = os.path.join(output_folder, '%s.dcm' % series_description)
        write_dicom(f_data, filename, sour_obj,
                    series_number, sop_id, series_description, 'test', 'test')


def convert_nifti_2_dicoms(nifti_path, sour_obj, output_folder,
                           series_description, label=None):
    """Convert 3D niftis into DICOM files.

    :param nifti_path: path to the nifti file
    :param sour_obj: pydicom object for the source dicom
    :param output_folder: folder where the DICOM files will be saved
    :param series_description: series description for the scan
    :param label: name for the output dicom files
    :return: None
    """
    if not os.path.isfile(nifti_path):
        raise Exception("NIFTY File %s not found." % nifti_path)
    # Load image from NIFTI
    f_img = nib.load(nifti_path)
    f_data = f_img.get_data()
    # Rotation 270
    f_data = np.rot90(f_data)
    f_data = np.rot90(f_data)
    f_data = np.rot90(f_data)
    # Normalizing data:
    dmin = C_RANGE[label]['min']
    dmax = C_RANGE[label]['max']
    f_data[f_data < dmin] = dmin
    f_data[f_data > dmax] = dmax
    # Scale numbers to uint8
    f_img_data = (f_data - dmin)*255.0/(dmax - dmin)

    # Make output_folder:
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Series Number and SOP UID
    str_ti = "%f" % time.time()
    series_number = 86532 + int(str_ti[-4:-2]) + int(str_ti[-2:])
    sop_id = sour_obj.SOPInstanceUID.split('.')
    sop_id = '.'.join(sop_id[:-1])+'.'

    filename = os.path.join(output_folder, '%s.dcm' % label)
    write_dicom(f_img_data, filename, sour_obj,
                series_number, sop_id, series_description,
                'INN-001-KRE', 'INN-001-KRE_20160101')


def subtract_obj_to_map(nii_folder, sour_obj, output_folder):
    if not os.path.isdir(nii_folder):
        raise Exception("NIFTY Folder %s not found." % nii_folder)

    nii_mapobj = os.path.join(nii_folder, 'FIT_FobjCamino.nii')
    if not os.path.isfile(nii_mapobj):
        raise Exception("NIFTY file OBJ %s not found." % nii_mapobj)

    # Load image from NIFTI
    f_img_mobj = nib.load(nii_mapobj)
    f_data_obj = f_img_mobj.get_data()
    # Rotation 270
    f_data_obj = np.rot90(f_data_obj)
    f_data_obj = np.rot90(f_data_obj)
    f_data_obj = np.rot90(f_data_obj)
    mask = f_data_obj > C_RANGE['FIT_FobjCamino']['max']

    for index, map_name in enumerate(ORDER_MAPS):
        # File
        nii_map = os.path.join(nii_folder, '%s.nii' % map_name)
        if not os.path.isfile(nii_map):
            raise Exception("NIFTY file %s not found." % nii_map)
        # Load image from NIFTI
        f_img = nib.load(nii_map)
        f_data = f_img.get_data()
        # Rotation 270
        f_data = np.rot90(f_data)
        f_data = np.rot90(f_data)
        f_data = np.rot90(f_data)
        # Normalizing data:
        dmin = C_RANGE[map_name]['min']
        dmax = C_RANGE[map_name]['max']
        f_data[f_data < dmin] = dmin
        f_data[f_data > dmax] = dmax

        # Scale numbers to uint8
        f_data = (f_data - dmin)*255.0/(dmax - dmin)

        # Subtract:
        f_data[mask] = np.nan

        # Make output_folder:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Series Number and SOP UID
        series_number = 87000 + 5 + index
        sop_id = sour_obj.SOPInstanceUID.split('.')
        sop_id = '.'.join(sop_id[:-1])+'.'

        filename = os.path.join(output_folder, '%s_subtracted.dcm' % map_name)
        write_dicom(f_data, filename, sour_obj,
                    series_number, sop_id, map_name,
                    'test', 'test')


if __name__ == '__main__':
    outdir = '/Users/byvernault/Downloads/assessors/\
prostate_xnat_E01281/RMAPS1'
    osirix_folder = os.path.join(outdir, 'OsiriX')
    # Generate Dicom for OsiriX
    nb_acq = 1
    # Load dicom headers
    dc = '/Users/byvernault/Downloads/1.3.46.670589.11.3228500564.4293032899\
.1892417991.1469747517-801-1-9w4d66.dcm'
    if not os.path.isfile(dc):
        err = "DICOM File %s not found."
        raise Exception(err % dc)
    sour_obj = dicom.read_file(dc)
    convert_niftis_2_dicoms(outdir, sour_obj, osirix_folder, 1)
    """for maps in glob.glob(os.path.join(outdir, '*.nii')):
        print 'Converting: %s' % maps
        nii = os.path.join(outdir, maps)
        convert_nifti_2_dicoms(
            nii,
            sour_obj,
            osirix_folder,
            os.path.basename(nii)[:-4],
            label=os.path.basename(nii)[:-4])"""
    subtract_obj_to_map(outdir, sour_obj, osirix_folder)
