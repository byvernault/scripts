"""TEST number 2 Script for different purpose.

>>> l='salut'
"""

from datetime import datetime
from dax import spiders, XnatUtils
import glob
from PIL import Image
import matplotlib.pyplot as plt
import nibabel as nib
import nipype.pipeline.engine as pe
import nipype.interfaces.fsl as fsl
import nipype.interfaces.niftyseg as niftyseg
import os
import subprocess

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Test Code 2"


JOB_DIR = '/Users/byvernault/Downloads/'


def make_pdf(session):
    """Method to make the PDF for the spider.

    :return: None
    """
    # tiv = glob.glob(os.path.join(JOB_DIR, 'INPUT', '*', 'TIV', '*.nii.gz'))
    # background = glob.glob(os.path.join(JOB_DIR, '*mul_res.nii.gz'))
    # overlay = glob.glob(os.path.join(JOB_DIR, 'LesionCorrected*.nii.gz'))

    # if not tiv or not background or not overlay:
    #     raise Exception('Missing outputs to generate the PDF.')

    tiv = '/Users/byvernault/Downloads/assessors/DPUK_UCL_E01139/TIV/asyi002_20100218-0002-Sag_MPRAGE-m_tiv.nii.gz'
    background = '/Users/byvernault/data/RESULTS_XNAT_SPIDER/prion-x-009LSF37PC-x-009LSF37PC_20100218-x-BaMoS_v1/INIT/asyi002_20100218-0024-t2_tirm_tra_dark-fluid-m_mul_res.nii.gz'
    overlay = '/Users/byvernault/data/RESULTS_XNAT_SPIDER/prion-x-009LSF37PC-x-009LSF37PC_20100218-x-BaMoS_v1/LESION/LesionCorrected_WS3WT3WC1AC1SP1ST3CL2CIV1_TOT1FLAIR_patient_id_segmentation.nii.gz'
    # Get png images
    # Images
    # flair_im = extract_volume(background, 1)
    flair_im = background
    image_overlay = overlay_images(flair_im, overlay)

    # Indexes for display
    indexes = get_indexes(tiv)
    f_img = nib.load(tiv)
    f_img_data = f_img.get_data()
    nb_slices = f_img_data.shape
    ax_slices = get_slices(indexes[2], nb_slices[2])
    cor_slices = get_slices(indexes[1], nb_slices[1])
    sag_slices = get_slices(indexes[0], nb_slices[0])

    png_slices_sag = slicer(image_overlay, 'x', sag_slices)
    png_slices_cor = slicer(image_overlay, 'y', cor_slices)
    png_slices_ax = slicer(image_overlay, 'z', ax_slices)
    png_wo_slices_sag = slicer(flair_im, 'x', sag_slices, prefix='wo')
    png_wo_slices_cor = slicer(flair_im, 'y', cor_slices, prefix='wo')
    png_wo_slices_ax = slicer(flair_im, 'z', ax_slices, prefix='wo')

    stats = get_stats(overlay)

    # Slices:
    aslices = list()
    cslices = list()
    sslices = list()
    for i in range(0, len(png_wo_slices_ax)):
        aslices.append(png_wo_slices_ax[i])
        aslices.append(png_slices_ax[i])
        cslices.append(png_wo_slices_cor[i])
        cslices.append(png_slices_cor[i])
        sslices.append(png_wo_slices_sag[i])
        sslices.append(png_slices_sag[i])

    # Vmin/Vmax
    vmins = dict()
    vmaxs = dict()
    for v in range(0, 5):
        vmins[2 * v] = 0
        vmins[2 * v + 1] = None
        vmaxs[2 * v] = 255 * 1.50
        vmaxs[2 * v + 1] = None

    orient = 'Axial'
    title = 'BaMoS %s' % orient
    pdf1 = os.path.join(JOB_DIR, 'png_ax.pdf')
    plot_pngs(pdf1, 1, aslices, title, ftitles=get_ftitles(ax_slices),
              number_col=2, vmaxs=vmaxs, vmins=vmins, value=stats)

    orient = 'Coronal'
    title = 'BaMoS %s' % orient
    pdf2 = os.path.join(JOB_DIR, 'png_cor.pdf')
    plot_pngs(pdf2, 2, cslices, title, ftitles=get_ftitles(cor_slices),
              number_col=2, vmaxs=vmaxs, vmins=vmins)

    orient = 'Sagittal'
    title = 'BaMoS %s' % orient
    pdf3 = os.path.join(JOB_DIR, 'png_sag.pdf')
    plot_pngs(pdf3, 3, sslices, title, ftitles=get_ftitles(sag_slices),
              number_col=2, vmaxs=vmaxs, vmins=vmins)

    pdf_final = os.path.join(JOB_DIR, '%s_BaMoS.pdf' % session)
    spiders.merge_pdfs([pdf1, pdf2, pdf3], pdf_final)


def plot_pngs(pdf_path, page_index, png_images, title,
              ftitles=None, number_col=3, time_writer=None,
              vmaxs=dict(), vmins=dict(), value=None):
    plt.ioff()
    print('INFO: generating pdf page %d with PNG images.' % page_index)
    number_png = len(png_images)
    number_row = int(round(float(number_png) / number_col))
    fig, axs = plt.subplots(number_row, number_col, figsize=(7.5, 10))

    if isinstance(png_images, str):
        png_images = [png_images]
    elif isinstance(png_images, list):
        pass
    else:
        raise ValueError('Error in plot_pngs: Wrong format for png_images.')

    if isinstance(ftitles, dict):
        pass
    else:
        raise ValueError('Error in plot_pngs: Wrong format for ftitles (dict(): \
key -> image ind (starting from 1), value -> title.')

    for index, png in enumerate(png_images):
        img = Image.open(png)
        l_ind = int(index / number_col)
        c_ind = index % number_col
        stitle = ftitles.get(index, None)
        vmax = vmaxs.get(index, None)
        vmin = vmins.get(index, None)
        if vmax or vmin:
            gray = img.convert('L')
            axs[l_ind, c_ind].imshow(gray, cmap=plt.get_cmap('gray'),
                                     vmax=vmax, vmin=vmin)
        else:
            axs[l_ind, c_ind].imshow(img)
        if stitle:
            axs[l_ind, c_ind].set_title(stitle, fontsize=9)
        axs[l_ind, c_ind].set_axis_off()

    fig.tight_layout()
    date = datetime.now()
    # Titles page
    left = 0.05
    bottom = 0.05
    width = 0.9
    height = 0.9
    plt.subplots_adjust(left=left,
                        bottom=bottom,
                        right=width,
                        top=height)
    plt.figtext(0.5, 0.985, '-- %s PDF report --' % title,
                horizontalalignment='center', fontsize=10)
    plt.figtext(0.5, 0.015, 'Date: %s -- page %d' % (str(date), 1),
                horizontalalignment='center', fontsize=8)
    if value:
        plt.figtext(0.5, 0.938, 'Seg-stats lesion -v: %s' % value,
                    horizontalalignment='right', fontsize=10)
    fig.savefig(pdf_path, transparent=True, orientation='portrait',
                dpi=100)
    plt.close(fig)


def get_ftitles(slices):
    ftitles = dict()
    for ind, slice_nb in enumerate(slices):
        ftitles[2 * ind] = 'FLAIR - %s' % slice_nb
        ftitles[2 * ind + 1] = 'FLAIR with lesions - %s' % slice_nb
    return ftitles


def get_stats(lesion_file):
    cmd = 'seg_stats %s -vp' % lesion_file
    proc = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE)
    output, error = proc.communicate()
    return output


def get_image_slices(labels):
    fslices = dict()
    for i in range(1, len(labels) + 1):
        fslices[str(2 * (i - 1) + 1)] = int(labels[i - 1].split('slice ')[1])
    return fslices


def get_indexes(image):
    cmd = 'seg_stats %s -c' % image
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.split()


def extract_volume(in_file, volume, out_file=None):
    if not out_file:
        # File name
        flabel = os.path.basename(in_file).split('.')
        image_name = '%s_vol_%d.%s' % (flabel[0], volume, '.'.join(flabel[1:]))
        out_file = os.path.join(os.path.dirname(in_file), image_name)
    extractor = pe.Node(interface=niftyseg.BinaryMathsInteger(operation='tp'),
                        name='extractor')
    extractor.inputs.in_file = in_file
    extractor.inputs.operand_value = volume
    extractor.inputs.out_file = out_file
    extractor.run()
    return out_file


def overlay_images(in_file, overlay_file, out_file=None):
    if not out_file:
        flabel = os.path.basename(in_file).split('.')
        image_name = '%s_overlay.%s' % (flabel[0], '.'.join(flabel[1:]))
        out_file = os.path.join(os.path.dirname(in_file), image_name)
    overlay_node = pe.Node(interface=fsl.Overlay(transparency=False,
                                                 out_type='float',
                                                 auto_thresh_bg=True),
                           name='overlay_node')
    overlay_node.inputs.background_image = in_file
    overlay_node.inputs.stat_image = overlay_file
    overlay_node.inputs.stat_thresh = (1.0, 1.0)
    overlay_node.inputs.out_file = out_file
    overlay_node.run()
    return out_file


def slicer(image, axe, n_slices, prefix=None, threshold=None):
    path = os.path.dirname(image)
    out_files = [os.path.join(path, '%sslicer_out_%s_%s.png'
                                    % ('%s_' % prefix if prefix else '',
                                       axe, islice))
                 for islice in n_slices]
    slicer = pe.MapNode(interface=fsl.Slicer(scaling=1),
                        iterfield=['slice_number', 'out_file'],
                        name='slicer_%s' % axe)
    slicer.inputs.in_file = image
    slicer.inputs.slice_number = n_slices
    slicer.inputs.single_slice = axe
    if threshold:
        print('USING TRESHOLD')
        slicer.inputs.intensity_range = threshold
    slicer.inputs.out_file = out_files
    slicer.run()
    return out_files


def get_slices(ind_slice, nb_slices):
    ind_slice = int(float(ind_slice))
    percent1 = int(1 * nb_slices / 100)
    percent3 = int(3 * nb_slices / 100)
    slices = [ind_slice - percent3, ind_slice - percent1, ind_slice,
              ind_slice + percent1, ind_slice + percent3]
    return slices


if __name__ == '__main__':
    """with XnatUtils.get_interface(host=os.environ['XP']) as xnat:
        scans = XnatUtils.list_project_scans(xnat, 'MASTER_MM')
        for scan in scans:
            if scan['resources'] == ['secondary'] and \
               scan['ID'].startswith('0-'):
                print('Scan: {}  --  {}'.format(scan['ID'], scan['type']))
                obj = XnatUtils.get_full_object(xnat, scan)
                if obj.exists():
                    obj.delete()
                    print('  deleted')"""


    make_pdf('session')
