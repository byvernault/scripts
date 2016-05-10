"""Ben functions used locally."""

import os
import csv
import xlrd
import time
import glob
import datetime
import collections
import numpy as np
import nibabel as nib
import dicom
import dicom.UID
import subprocess as sb
from dicom.dataset import Dataset, FileDataset

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Usefull functions to use locally for faster coding"


FUNCTIONS = """List of functions:
    # Read stats files
    read_csv(csv_file, header=None, delimiter=',')
    read_excel(excel_file, header_indexes=None)

    # Images
    is_dicom(fpath)
    order_dicoms(folder)
    find_dicom_in_folder(folder, recursively=True)
    write_dicom(pixel_array, filename, ds_copy, ds_ori, volume_number,\
                series_number, sop_id)
    convert_nifti_2_dicoms(nifti_path, dicom_targets, dicom_source, \
                           output_folder, label=None)
"""


def print_functions():
    """Print the functions in this toolbox."""
    print FUNCTIONS


def read_csv(csv_file, header=None, delimiter=','):
    """Read CSV file (.csv files).

    :param csv_file: path to the csv file
    :param header: list of label for the header, if None, use first line
    :param delimiter: delimiter for the csv, default comma
    :return: list of rows
    """
    if not os.path.isfile(csv_file):
        raise Exception('File not found: %s' % csv_file)
    if not csv_file.endswith('.csv'):
        raise Exception('File format unknown. Need .csv: %s' % csv_file)
    # Read csv
    csv_info = list()
    with open(csv_file, 'rb') as f:
        reader = csv.reader(f, delimiter=delimiter)
        if not header:
            header = next(reader)
        for row in reader:
            if row == header:
                continue
            csv_info.append(dict(zip(header, row)))
    return csv_info


def read_excel(excel_file, header_indexes=None):
    """Read Excel spreadsheet (.xlsx files).

    :param excel_file: path to the Excel file
    :param header_indexes: dictionary with sheet name and header position
                           or use first value
    :return: dictionary of the sheet with the data
    """
    if not os.path.isfile(excel_file):
        raise Exception('File not found: %s' % excel_file)
    if not excel_file.endswith('.xlsx'):
        raise Exception('File format unknown. Need .xlsx: %s' % excel_file)
    # Read the xlsx file:
    book = xlrd.open_workbook(excel_file)
    excel_sheets = dict()
    for sht in book.sheets():
        sheet_info = list()
        if header_indexes:
            header = sht.row_values(int(header_indexes[sht.name]))
            start = int(header_indexes[sht.name])
        else:
            header = sht.row_values(0)
            start = 0
        for row_index in range(start+1, sht.nrows):
            row = list()
            for col_index in range(sht.ncols):
                value = sht.cell(rowx=row_index, colx=col_index).value
                row.append(value)
            sheet_info.append(dict(zip(header, row)))
        excel_sheets[sht.name] = sheet_info

    return excel_sheets


def is_dicom(fpath):
    """Check if the file is a DICOM medical data.

    :param fpath: path of the file
    :return boolean: true if it's a DICOM, false otherwise
    """
    if not os.path.isfile(fpath):
        raise Exception('File not found: %s' % fpath)
    file_call = '''file {fpath}'''.format(fpath=fpath)
    output = sb.check_output(file_call.split())
    if 'dicom' in output.split(':')[1].lower():
        return True

    return False


def order_dicoms(folder):
    """Order the dicoms in a folder by the Slice Location.

    :param folder: path to the folder
    :return: dictionary of the files with the key is the slice location
    """
    if not os.path.isdir(folder):
        raise Exception('Folder not found: %s' % folder)
    dcm_files = dict()
    for dc in glob.glob(os.path.join(folder, '*.dcm')):
        dst = dicom.read_file(dc)
        dcm_files[float(dst.SliceLocation)] = dc
    return collections.OrderedDict(sorted(dcm_files.items()))


def find_dicom_in_folder(folder, recursively=True):
    """Find a dicom file in folder.

    :param folder: path to folder to search
    :param recursively: search sub folder
    :return: list of dicoms
    """
    dicom_list = list()
    if not os.path.isdir(folder):
        raise Exception('Folder not found: %s' % folder)
    for ffname in os.listdir(folder):
        ffpath = os.path.join(folder, ffname)
        if os.path.isfile(ffpath):
            if is_dicom(ffpath):
                dicom_list.append(ffpath)
        elif os.path.isdir(ffpath) and recursively:
            dicom_list.extend(find_dicom_in_folder(ffpath, recursively=True))
    return dicom_list


def write_dicom(pixel_array, filename, ds_copy, ds_ori, volume_number,
                series_number, sop_id):
    """Write data in dicom file and copy the header from different dicoms.

    :param pixel_array: data to write in a dicom
    :param filename: file name for the dicom
    :param ds_copy: pydicom object of the dicom to copy info from
    :param ds_ori: pydicom object of the dicom where the array comes from
    :param volume_number: numero of volume being processed
    :param series_number: number of the series being written
    :param sop_id: SOPID for the dicom
    :return: None
    """
    # Set to zero negatives values in the image:
    pixel_array[pixel_array < 0] = 0

    # Set the DICOM dataset
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = 'Secondary Capture Image Storage'
    file_meta.MediaStorageSOPInstanceUID = ds_ori.SOPInstanceUID
    file_meta.ImplementationClassUID = ds_ori.SOPClassUID
    ds = FileDataset(filename, {}, file_meta=file_meta, preamble="\0"*128)

    # Copy the tag from the original DICOM
    for tag, value in ds_ori.items():
        if tag != ds_ori.data_element("PixelData").tag:
            ds[tag] = value

    # Other tags to set
    ds.SeriesNumber = series_number
    ds.SeriesDescription = ds_ori.SeriesDescription + ' reg_f3d'
    sop_uid = sop_id + str(datetime.datetime.now()).replace('-', '')\
                                                   .replace(':', '')\
                                                   .replace('.', '')\
                                                   .replace(' ', '')
    ds.SOPInstanceUID = sop_uid[:-1]
    ds.ProtocolName = ds_ori.ProtocolName
    ds.InstanceNumber = volume_number+1

    # Copy from T2 the orientation tags:
    ds.PatientPosition = ds_copy.PatientPosition
    ds[0x18, 0x50] = ds_copy[0x18, 0x50]  # Slice Thicknes
    ds[0x18, 0x88] = ds_copy[0x18, 0x88]  # Spacing Between Slices
    ds[0x18, 0x1312] = ds_copy[0x18, 0x1312]  # In-plane Phase Encoding
    ds[0x20, 0x32] = ds_copy[0x20, 0x32]  # Image Position
    ds[0x20, 0x37] = ds_copy[0x20, 0x37]  # Image Orientation
    ds[0x20, 0x1041] = ds_copy[0x20, 0x1041]  # Slice Location
    ds[0x28, 0x10] = ds_copy[0x28, 0x10]  # rows
    ds[0x28, 0x11] = ds_copy[0x28, 0x11]  # columns
    ds[0x28, 0x30] = ds_copy[0x28, 0x30]  # Pixel spacing

    # Set the Image pixel array
    if pixel_array.dtype != np.uint16:
        pixel_array = pixel_array.astype(np.uint16)
    ds.PixelData = pixel_array.tostring()

    # Save the image
    ds.save_as(filename)


def convert_nifti_2_dicoms(nifti_path, dicom_targets, dicom_source,
                           output_folder, label=None):
    """Convert 4D niftis generated by reg_f3d into DICOM files.

    :param nifti_path: path to the nifti file
    :param dicom_target: list of dicom files from the target
     for the registration for header info
    :param dicom_source: one dicom file from the source
     for the registration for header info
    :param output_folder: folder where the DICOM files will be saved
    :param label: name for the output dicom files
    :return: None
    """
    if not os.path.isfile(nifti_path):
        raise Exception("NIFTI File %s not found." % nifti_path)
    # Load image from NIFTI
    f_img = nib.load(nifti_path)
    f_img_data = f_img.get_data()

    # Load dicom headers
    if not os.path.isfile(dicom_source):
        raise Exception("DICOM File %s not found ." % dicom_source)
    adc_dcm_obj = dicom.read_file(dicom_source)

    # Make output_folder:
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Series Number and SOP UID
    ti = time.time()
    series_number = 86532 + int(str(ti)[2:4]) + int(str(ti)[4:6])
    sop_id = adc_dcm_obj.SOPInstanceUID.split('.')
    sop_id = '.'.join(sop_id[:-1])+'.'

    # Sort the DICOM T2 to create the ADC registered DICOMs
    dcm_obj_sorted = dict()
    for dcm_file in dicom_targets:
        # Load dicom headers
        if not os.path.isfile(dcm_file):
            raise Exception("DICOM File %s not found." % dcm_file)
        t2_dcm_obj = dicom.read_file(dcm_file)
        dcm_obj_sorted[t2_dcm_obj.InstanceNumber] = t2_dcm_obj

    for vol_i in range(f_img_data.shape[2]):
        if f_img_data.shape[2] > 100:
            filename = os.path.join(output_folder, '%s_%03d.dcm' % (label,
                                                                    vol_i+1))
        elif f_img_data.shape[2] > 10:
            filename = os.path.join(output_folder, '%s_%02d.dcm' % (label,
                                                                    vol_i+1))

        else:
            filename = os.path.join(output_folder, '%s_%d.dcm' % (label,
                                                                  vol_i+1))

        write_dicom(np.rot90(f_img_data[:, :, vol_i]), filename,
                    dcm_obj_sorted[vol_i+1], adc_dcm_obj, vol_i,
                    series_number, sop_id)
