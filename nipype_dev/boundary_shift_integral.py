# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
import os
import nipype.interfaces.utility as niu
import nipype.pipeline.engine as pe
import nipype.interfaces.fsl as fsl
import nipype.interfaces.niftyseg as niftyseg
import nipype.interfaces.niftyreg as niftyreg
from ...interfaces.niftk.filters import N4BiasCorrection, MTPDBiasCorrection, \
                        KMeansWindowWithLinearRegressionNormalisationBSI, \
                        KNDoubleWindowBSI

MNI_TEMPLATE = os.path.join(os.environ['FSLDIR'], 'data', 'standard',
                            'MNI152_T1_2mm.nii.gz')
MNI_TEMPLATE_MASK = os.path.join(os.environ['FSLDIR'], 'data', 'standard',
                                 'MNI152_T1_2mm_brain_mask_dil.nii.gz')


def check_images_validity(images):
    import nibabel as nib
    import numpy as np
    for image in images:
        data = nib.load(image).get_data()
        positives = float(np.count_nonzero(data > 0))
        negatives = float(np.count_nonzero(data < 0))
        if negatives / (positives + negatives) > 0.05:
            return False
    return True


def create_register_two_images_half_way(interpolation='NN',
                                        resample_dil_mask=False,
                                        name='register_half_way'):
    """Workflow to register the two time points images to the half-way."""
    # Create a workflow to process the images
    workflow = pe.Workflow(name=name)
    workflow.base_output_dir = name

    # Input node:
    input_node = pe.Node(interface=niu.IdentityInterface(),
                         name='input_node',
                         fields=['in_files',
                                 'mask_files'])
    # Output node:
    output_node = pe.Node(interface=niu.IdentityInterface(
                          fields=['in_files',
                                  'mask_files',
                                  'aff_file',
                                  'inv_aff_file']),
                          name='output_node')

    # Dilate mask node
    out_dil_mask = pe.Node(interface=niu.IdentityInterface(),
                           name='out_dil_mask',
                           fields=['mask_files'])
    dilate_mask = pe.MapNode(interface=niftyseg.BinaryMaths(
                                            operation='-dil 8 -thr 0.5'),
                             iterfield=['operand_file'],
                             name='dilate_mask')
    workflow.connect(input_node, 'mask_files',
                     dilate_mask, 'operand_file')
    # resample the mask:
    if resample_dil_mask:
        resample_mask = pe.MapNode(interface=niftyreg.RegResample(
                                            inter_val=interpolation),
                                   iterfield=['flo_file', 'ref_file'],
                                   name='resample_mask',)
        workflow.connect([
            (input_node, resample_mask, [('in_files', 'ref_file')]),
            (dilate_mask, resample_mask, [('out_file', 'flo_file')])
                         ])
        # connect outputs
        workflow.connect(resample_mask, 'out_file', out_dil_mask, 'mask_files')
    else:
        workflow.connect(dilate_mask, 'out_file', out_dil_mask, 'mask_files')
    # Dilate mask node END

    # Node to extract
    # Select baseline image and follow_ups
    baseline_im = pe.Node(interface=niu.Select(index=0))
    workflow.connect(input_node, 'in_files', baseline_im, 'inlist')
    follow_up_im = pe.Node(interface=niu.Select(index=1))
    workflow.connect(input_node, 'in_files', follow_up_im, 'inlist')

    # Select dilated baseline mask and follow_ups mask
    dilated_b_mask = pe.Node(interface=niu.Select(index=0))
    workflow.connect(out_dil_mask, 'in_files', dilated_b_mask, 'inlist')
    dilated_f_mask = pe.Node(interface=niu.Select(index=1))
    workflow.connect(out_dil_mask, 'in_files', dilated_f_mask, 'inlist')
    # Node to extract END

    # Node to register the images, from follow-up to baseline
    register_hw = pe.Node(interface=niftyreg.RegAladin(),
                          name='register_images')
    workflow.connect([
        (baseline_im, register_hw, [('out', 'ref_file')]),
        (follow_up_im, register_hw, [('out', 'flo_file')]),
        (dilated_b_mask, register_hw, [('out', 'rmask_file')]),
        (dilated_f_mask, register_hw, [('out', 'fmask_file')])
                     ])
    # Node to register the images END

    # Node to compute the half way transformation matrix and the inverse
    trans_mat = pe.Node(interface=niftyreg.RegTransform(),
                        name='trans_matrix')
    workflow.connect([
        (baseline_im, trans_mat, [('out', 'ref1_file')]),
        (register_hw, trans_mat, [('aff_file', 'half_input')])
                     ])
    inv_trans_mat = pe.Node(interface=niftyreg.RegTransform(),
                            name='inv_trans_mat')
    workflow.connect([
        (baseline_im, inv_trans_mat, [('out', 'ref1_file')]),
        (trans_mat, inv_trans_mat, [('out_file', 'inv_aff_input')])
                     ])
    # Node to compute the half way transformation matrix and the inverse END

    # Resample the data node
    flo_resample = pe.Node(interface=niu.Merge(), name='input_resample')
    workflow.connect([
        (input_node, flo_resample, [('in_files', 'in1')]),
        (input_node, flo_resample, [('mask_files', 'in2')])
                     ])
    # transformation
    trans_resample = pe.Node(interface=niu.Merge(), name='trans_resample')
    workflow.connect([
        (trans_mat, trans_resample, [('out_file', 'in1')]),
        (inv_trans_mat, trans_resample, [('out_file', 'in2')]),
        (trans_mat, trans_resample, [('out_file', 'in3')]),
        (inv_trans_mat, trans_resample, [('out_file', 'in4')])
                     ])
    # set the interpolation for the mask
    interpolations = ['CUB', 'CUB', interpolation, interpolation]
    # Resampling the data
    resample = pe.MapNode(interface=niftyreg.RegResample(), name='resample',
                          iterfield=['flo_file', 'inter_val',
                                     'aff_file'])
    workflow.connect([
        (baseline_im, resample, [('out', 'ref_file')]),
        (flo_resample, resample, [('out', 'flo_file')]),
        (trans_resample, resample, [('out', 'aff_file')]),
                     ])
    resample.inputs.inter_val = interpolations

    # Replace the nans by zeros
    replace_nans = pe.MapNode(interface=fsl.MathsCommand(
                                                    nan2zeros=True),
                              iterfield=['in_file'],
                              name='replace_follow_nans')
    workflow.connect(resample, 'output_file',
                     replace_nans, 'in_file')
    # Resample the data node END

    # Connect the outputs node
    # Divide the outputs
    im_files = pe.Node(interface=niu.Select(index=[0, 1]))
    workflow.connect(replace_nans, 'out_file', im_files, 'inlist')
    mask_files = pe.Node(interface=niu.Select(index=[2, 3]))
    workflow.connect(replace_nans, 'out_file', mask_files, 'inlist')
    workflow.connect([
        (im_files, output_node, [('out', 'in_files')]),
        (mask_files, output_node, [('out', 'mask_files')]),
        (trans_mat, output_node, [('out', 'aff_file')]),
        (inv_trans_mat, output_node, [('out', 'inv_aff_file')]),
                     ])
    # Connect the outputs node END

    return workflow


def create_boundary_shift_integral_two_images(lesion_masks=None,
                                              roi_masks=None,
                                              iso=False,
                                              norm=False,
                                              bsi_method=0,
                                              sub_lesion=False,
                                              fill_lesion=False,
                                              dil_sub=1,
                                              dil_fill=0,
                                              single_window=True,
                                              t2_mode=False,
                                              dil_kmeans=3,
                                              tkn=3,
                                              name='bsi_on_two_images'):
    """Main Workflow to compute boundary shift integral.

    Nipype workflow as input_node:
        - in_files, python list (baseline, follow up)
        - mask_files, python list (baseline, follow up)

    Ouput_node:
        - ...

    Arguments:
    :param lesion_masks: list of masks for lesion (baseline, follow up)
    :param roi_mask: list of masks for ROI (baseline, follow up)
    :param iso: convert all the files to 1mm ISO voxel
    :param norm: normalized images
    :param bsi_method: method for BSI
        GBSI: computes BSI using generalized BSI by ...
        KN-BSI: computes BSI using K-means BSI by Leung et al. Neuroimage 2010
        PBSI: computes BSI using probabilistic BSI by Ledig et al. MICCAI 2012
        PBSIg: computes BSI using probabilistic BSI with gamma=1 as in Ledig
               et al. MICCAI 2012
    :param sub_lesion: Substract/remove lesions mask from the brain mask
         for BSI calculation
    :param fill_lesion: Activates filling lesions script Declan T. Chard
         et al. JMRI 2010
    :param dil_sub: Number of dilations for lesion masks, useful for lesion
         substraction, recommended value: 1
    :param dil_fill: Number of dilations for lesion masks, useful for lesion
         filling, recommended value: 0
    :param single_window: single window BSI, CSF-GM, Freeborough
         et al. 1997 TMI [DEFAULT] else applies double window BSI, it computes
         BSI between CSF-GM and WM-GM as in Leung et al. Neuroimage 2010
    :param t2_mode: bool to compute BSI taking into account that we are using
         T2 images as input data
    :param dil_kmeans: number of dilations for K-Means [0-4, by default 3]
    :param tkn: number of classes for K-Means [2 or 3, by default 3]
    :param name: name for the nipype workflow
    """
    # Set interpolation
    if bsi_method == 1 or bsi_method == 3:
        interpolation = 'LIN'
    else:
        interpolation = 'NN'

    # Create a workflow to process the images
    workflow = pe.Workflow(name=name)
    workflow.base_output_dir = name

    # Input node:
    input_node = pe.Node(interface=niu.IdentityInterface(),
                         name='input_node',
                         fields=['in_files',
                                 'masks_files'])
    # Output node:
    output_node = pe.Node(interface=niu.IdentityInterface(
                          fields=['out_img_files']),
                          name='output_node')

    # Node to Copy geometry for mask, roi mask and lesion mask:
    cpgeom_mask = pe.MapNode(interface=fsl.CopyGeom(),
                             iterfield=['in_file', 'dest_file'],
                             name='copy_geometry_mask')
    workflow.connect([
        (input_node, cpgeom_mask, [('in_files', 'in_file')]),
        (input_node, cpgeom_mask, [('mask_files', 'dest_file')])
                     ])
    if roi_masks:
        cpgeom_roi_mask = pe.MapNode(interface=fsl.CopyGeom(),
                                     iterfield=['in_file', 'dest_file'],
                                     name='copy_geometry_roi')
        cpgeom_roi_mask.inputs.dest_file = roi_masks
        workflow.connect(input_node, 'in_files', cpgeom_roi_mask, 'in_file')

    if lesion_masks:
        cpgeom_les_mask = pe.MapNode(interface=fsl.CopyGeom(),
                                     iterfield=['in_file', 'dest_file'],
                                     name='copy_geometry_lesion')
        cpgeom_les_mask.inputs.dest_file = lesion_masks
        workflow.connect(input_node, 'in_files', cpgeom_roi_mask, 'in_file')
    # Node to Copy geometry END

    # Node to convert all the files to 1mm ISO voxel via flirt
    # input iso with images baseline and follow up, masks baseline and
    # follow up, roi masks, lesion masks
    input_iso = pe.Node(interface=niu.Merge(), name='input_iso')
    workflow.connect([
        (input_node, input_iso, [('in_files', 'in1')]),
        (cpgeom_mask, input_iso, [('out_file', 'in2')]),
                     ])
    ind = 3
    if roi_masks:
        workflow.connect(cpgeom_roi_mask, 'out_file', input_iso, 'in%d' % ind)
        ind += 1
    if lesion_masks:
        workflow.connect(cpgeom_les_mask, 'out_file', input_iso, 'in%d' % ind)
    # output node for iso
    output_iso = pe.Node(interface=niu.IdentityInterface(),
                         name='output_iso',
                         fields=['in_files', 'mask_files',
                                 'roi_masks', 'lesion_masks'])
    if iso:
        # iso node
        resolution = (1.0, 1.0, 1.0)
        iso_node = pe.MapNode(interface=niftyreg.RegTools(
                                                chg_res_val=resolution,
                                                iso_flag=True),
                              iterfield=['in_file'],
                              name='iso_node')
        workflow.connect([
            (input_iso, iso_node, [('in_files', 'in_file')]),
            (input_iso, iso_node, [('in_files', 'reference')])
                         ])
        # Extract the output
        iso_in_files = pe.Node(interface=niu.Select(index=[0, 1]))
        workflow.connect(iso_node, 'out_file', iso_in_files, 'inlist')
        iso_mask_files = pe.Node(interface=niu.Select(index=[2, 3]))
        workflow.connect(iso_node, 'out_file', iso_mask_files, 'inlist')
        # connect:
        workflow.connect([
            (iso_in_files, output_iso, [('out', 'in_files')]),
            (iso_mask_files, output_iso, [('out', 'mask_files')])
                         ])
        # Roi and lesion
        ind = 0
        if roi_masks:
            ind = 2
            iso_roi_masks = pe.Node(interface=niu.Select(index=[4, 5]))
            workflow.connect(iso_node, 'out_file', iso_roi_masks, 'inlist')
            # Connect:
            workflow.connect(iso_roi_masks, 'out', output_iso, 'roi_masks')
        else:
            output_iso.outputs.roi_masks = None
        if lesion_masks:
            iso_lesion_masks = pe.Node(interface=niu.Select(index=[4+ind,
                                                                   5+ind]))
            workflow.connect(iso_node, 'out_file', iso_lesion_masks, 'inlist')
            # Connect:
            workflow.connect(iso_lesion_masks, 'out',
                             output_iso, 'lesion_masks')
        else:
            output_iso.outputs.lesion_masks = None
    else:
        # If no iso connect the output
        workflow.connect([
            (input_node, output_iso, [('in_files', 'in_files')]),
            (input_node, output_iso, [('mask_files', 'mask_files')])
                         ])
        if roi_masks:
            workflow.connect(cpgeom_roi_mask, 'out_file',
                             output_iso, 'roi_masks')
        else:
            output_iso.outputs.roi_masks = None
        if lesion_masks:
            workflow.connect(cpgeom_les_mask, 'out_file',
                             output_iso, 'lesion_masks')
        else:
            output_iso.outputs.lesion_masks = None
    # Node iso END

    # Node fill_lesions
    if output_iso.outputs.lesion_masks:
        # fill lesions
        fill_lesions = pe.MapNode(interface=niftyseg.FillLesions(
                                            dilation=dil_fill),
                                  iterfield=['in_file', 'lesion_mask',
                                             'bin_mask'],
                                  name='fill_lesions')
        workflow.connect([
            (output_iso, fill_lesions, [('in_files', 'in_file')]),
            (output_iso, fill_lesions, [('lesion_masks', 'lesion_mask')]),
            (output_iso, fill_lesions, [('mask_files', 'bin_mask')]),
                         ])
        # Copy geometry:
        cpgeom_les = pe.MapNode(interface=fsl.CopyGeom(),
                                iterfield=['in_file', 'dest_file'],
                                name='copy_geometry_les')
        workflow.connect([
            (input_node, cpgeom_les, [('in_files', 'in_file')]),
            (fill_lesions, cpgeom_les, [('out_file', 'dest_file')])
                         ])
    # Node fill_lesions END

    # Node to normalized images
    # N4 Normalization of the intensity for each image
    output_norm = pe.Node(interface=niu.IdentityInterface(),
                          name='output_norm_node',
                          fields=['in_files',
                                  'mask_files',
                                  'roi_masks',
                                  'lesion_masks'])
    workflow.connect([
        (output_iso, output_norm, [('mask_files', 'mask_files')]),
        (output_iso, output_norm, [('roi_masks', 'roi_masks')]),
        (output_iso, output_norm, [('lesion_masks', 'lesion_masks')])
                     ])
    if norm:
        norm_bias_n4 = pe.MapNode(interface=N4BiasCorrection(
                                            mask_file=MNI_TEMPLATE_MASK),
                                  iterfield=['in_file', 'reference'],
                                  name='n4_bias_correction')
        workflow.connect([
            (output_iso, norm_bias_n4, [('in_files', 'in_file')]),
            (output_iso, norm_bias_n4, [('mask_files', 'mask_file')])
                         ])
        copygeom_norm = pe.MapNode(interface=fsl.CopyGeom(),
                                   iterfield=['in_file', 'dest_file'],
                                   name='copy_geometry_norm')
        workflow.connect([
            (output_iso, copygeom_norm, [('in_files', 'in_file')]),
            (norm_bias_n4, copygeom_norm, [('out_file', 'dest_file')])
                         ])
        workflow.connect(norm_bias_n4, 'out_file',
                         output_norm, 'in_files')
    else:
        workflow.connect(output_iso, 'in_files',
                         output_norm, 'in_files')
    # Node to normalized images END

    # Node to register half-way the images/masks and roi_masks if define
    reg_hw_images = create_register_two_images_half_way(
                                        interpolation=interpolation,
                                        name='register_hw_images')
    workflow.connect([
        (output_norm, reg_hw_images, [('in_files', 'in_files')]),
        (output_norm, reg_hw_images, [('mask_files', 'mask_files')])
                     ])
    if roi_masks:
        reg_hw_roi = create_register_two_images_half_way(
                                        interpolation=interpolation,
                                        name='reg_hw_roi')
        workflow.connect([
            (output_norm, reg_hw_roi, [('in_files', 'in_files')]),
            (output_norm, reg_hw_roi, [('roi_masks', 'mask_files')])
                         ])
    if sub_lesion:
        baseline_im = pe.Node(interface=niu.Select(index=0))
        workflow.connect(reg_hw_images, 'in_files', baseline_im, 'inlist')
        resample_les = pe.MapNode(interface=niftyreg.RegResample(
                                    interpolation='NN'),
                                  name='resample_les',
                                  iterfield=['flo_file', 'aff_file'])
        workflow.connect([
            (baseline_im, resample_les, [('out', 'ref_file')]),
            (output_norm, resample_les, [('lesion_masks', 'flo_file')]),
                         ])
        resample_les.inputs.aff_file = [reg_hw_images.outputs.inv_aff_file,
                                        reg_hw_images.outputs.aff_file]
        # Replace the nans by zeros
        sub_lesion_masks = pe.MapNode(interface=fsl.MathsCommand(
                                                        nan2zeros=True),
                                      iterfield=['in_file'],
                                      name='replace_nans_les')
        workflow.connect(resample_les, 'output_file',
                         sub_lesion_masks, 'in_file')
    # Node to register half-way END

    # Bias correction node
    # correct the differential bias correction between baseline and follow up
    bias_corr = pe.Node(interface=MTPDBiasCorrection(),
                        name='bias_correction')
    workflow.connect([
        (reg_hw_images, bias_corr, [('in_files', 'in_files')]),
        (reg_hw_images, bias_corr, [('mask_files', 'mask_files')]),
                     ])
    # keep geometry after the bias correction step
    copygeom_bias = pe.MapNode(interface=fsl.CopyGeom(),
                               iterfield=['in_file', 'dest_file'],
                               name='copygeom_bias')
    workflow.connect([
        (reg_hw_images, copygeom_bias, [('in_files', 'in_file')]),
        (bias_corr, copygeom_bias, [('out_files', 'dest_file')])
                     ])
    # Bias correction node END

    # Removing tissue node
    # Calculate the mask with the tissue to be removed or not
    output_rm_tissue_node = pe.Node(interface=niu.IdentityInterface(),
                                    name='output_rm_tissue_node',
                                    fields=['mask_files',
                                            'roi_masks',
                                            'tissue_file'])
    if sub_lesion:
        calculate_tissue = pe.Node(interface=niu.IdentityInterface(
                                   fields=['out_file']),
                                   name='calculate_tissue')
        # Select dilated and resampled baseline mask and follow_ups mask
        bsi_b_mask = pe.Node(interface=niu.Select(index=0))
        workflow.connect(sub_lesion_masks, 'out_file', bsi_b_mask, 'inlist')
        bsi_f_mask = pe.Node(interface=niu.Select(index=1))
        workflow.connect(sub_lesion_masks, 'out_file', bsi_f_mask, 'inlist')
        # Calculate tissue to be removed:
        add_lesion_masks = pe.MapNode(interface=niftyseg.BinaryMaths(
                                                operation='add',
                                                output_datatype='char'),
                                      name='add_lesion_masks')
        workflow.connect([
            (bsi_b_mask, add_lesion_masks, [('out', 'in_file')]),
            (bsi_f_mask, add_lesion_masks, [('out', 'operand_file')])
                         ])
        if dil_sub > 0:
            dil_lesion_masks = pe.MapNode(interface=niftyseg.BinaryMaths(
                                                    operation='dil',
                                                    output_datatype='char'),
                                          name='dil_lesion_masks')

            dil_lesion_masks.inputs.operand_value = dil_sub
            workflow.connect(add_lesion_masks, 'out_file',
                             dil_lesion_masks, 'in_file')
            # connect outputs
            workflow.connect(dil_lesion_masks, 'out_file',
                             calculate_tissue, 'out_file')
        else:
            workflow.connect(add_lesion_masks, 'out_file',
                             calculate_tissue, 'out_file')
        # Generate tissue_inv file
        # seg_matsh -sub
        sub_node = pe.MapNode(interface=niftyseg.BinaryMaths(
                                                operation='sub',
                                                output_datatype='char'),
                              name='subtract')
        sub_node.inputs.operand_value = 1
        workflow.connect(calculate_tissue, 'out_file', sub_node, 'in_file')
        # seg_matsh -abs
        abs_node = pe.MapNode(interface=niftyseg.UnaryMaths(
                                                operation='abs',
                                                output_datatype='char'),
                              name='abs')
        workflow.connect(sub_node, 'out_file', abs_node, 'in_file')
        # Copy geometry:
        tissue_inv = pe.MapNode(interface=fsl.CopyGeom(),
                                name='copygeom_1')
        workflow.connect([
            (input_node, tissue_inv, [('tissue_file', 'in_file')]),
            (abs_node, tissue_inv, [('out_file', 'dest_file')])
                         ])

        # Remove tissue from mask
        input_rm = pe.Node(interface=niu.Merge(), name='input_iso')
        workflow.connect(reg_hw_images, 'mask_files', input_rm, 'in1')
        if roi_masks:
            workflow.connect(reg_hw_roi, 'mask_files', input_rm, 'in2')
        # seg_maths -mul
        mul_node = pe.MapNode(interface=niftyseg.BinaryMaths(operation='mul'),
                              iterfield=['in_file'],
                              name='multiply')
        workflow.connect([
            (input_rm, mul_node, [('in_files', 'in_file')]),
            (tissue_inv, mul_node, [('out_file', 'operand_file')])
                         ])
        # seg_maths -thr
        thr_node = pe.MapNode(interface=niftyseg.BinaryMaths(operation='thr'),
                              iterfield=['in_file'],
                              name='multiply')
        thr_node.inputs.operand_value = 0
        workflow.connect(mul_node, 'in_file', thr_node, 'in_file')
        # Copy geometry:
        copygeom_2 = pe.MapNode(interface=fsl.CopyGeom(),
                                iterfield=['in_file', 'dest_file'],
                                name='copy_geometry')
        workflow.connect([
            (input_node, copygeom_2, [('in_files', 'in_file')]),
            (thr_node, copygeom_2, [('out_file', 'dest_file')])
                         ])

        # Connect to the output:
        workflow.connect(calculate_tissue, 'tissue_file',
                         output_rm_tissue_node, 'tissue_file')
        select_masks = pe.Node(interface=niu.Select(index=[0, 1]))
        workflow.connect(copygeom_2, 'out_file', select_masks, 'inlist')
        workflow.connect(select_masks, 'out_file',
                         output_rm_tissue_node, 'mask_files')
        if roi_masks:
            select_roi = pe.Node(interface=niu.Select(index=[2, 3]))
            workflow.connect(copygeom_2, 'out_file', select_roi, 'inlist')
            workflow.connect(select_roi, 'out',
                             output_rm_tissue_node, 'roi_files')
        else:
            output_rm_tissue_node.inputs.roi_files = None
    else:
        # connect output
        output_rm_tissue_node.inputs.tissue_file = 'dummy'
        workflow.connect(reg_hw_images, 'mask_files',
                         output_rm_tissue_node, 'mask_files')
        if roi_masks:
            workflow.connect(output_norm, 'out_file',
                             output_rm_tissue_node, 'roi_masks')
        else:
            output_rm_tissue_node.inputs.roi_files = None
    # Removing tissue node END

    # BSI calculation
    # Binarize probabilistic mask for calculating volumes
    binarize_mask = pe.MapNode(interface=niftyseg.BinaryMaths(
                                            operation='thr',
                                            output_datatype='char'),
                               name='binarize_mask')
    binarize_mask.inputs.operand_value = 0.5
    workflow.connect(output_rm_tissue_node, 'mask_files',
                     binarize_mask, 'in_file')

    # Select inputs for signle window
    # Images
    corr_base_im = pe.Node(interface=niu.Select(index=0))
    workflow.connect(copygeom_bias, 'in_files', corr_base_im, 'inlist')
    corr_follow_im = pe.Node(interface=niu.Select(index=1))
    workflow.connect(copygeom_bias, 'in_files', corr_follow_im, 'inlist')
    # Binary Masks
    b_mask_bin = pe.Node(interface=niu.Select(index=0))
    workflow.connect(binarize_mask, 'out_file', b_mask_bin, 'inlist')
    f_mask_bin = pe.Node(interface=niu.Select(index=1))
    workflow.connect(binarize_mask, 'out_file', f_mask_bin, 'inlist')
    # BSI masks:
    bsi_b_mask_bin = pe.Node(interface=niu.Select(index=0))
    workflow.connect(output_rm_tissue_node, 'mask_files',
                     b_mask_bin, 'inlist')
    bsi_f_mask_bin = pe.Node(interface=niu.Select(index=1))
    workflow.connect(output_rm_tissue_node, 'mask_files',
                     f_mask_bin, 'inlist')
    # Stats
    input_stats = pe.Node(interface=niu.IdentityInterface(),
                          name='input_volume', fields=['volume'])

    if roi_masks:
        binarize_roi = pe.Node(interface=niftyseg.BinaryMaths(
                                                operation='thr',
                                                output_datatype='uchar'),
                               name='binarize_mask')
        binarize_roi.inputs.operand_value = 0.5
        workflow.connect(output_rm_tissue_node, 'mask_files',
                         binarize_roi, 'in_file')
        # Select baseline roi mask
        b_roi_bin = pe.Node(interface=niu.Select(index=0))
        workflow.connect(binarize_roi, 'out_file', b_roi_bin, 'inlist')
        f_roi_bin = pe.Node(interface=niu.Select(index=1))
        workflow.connect(binarize_roi, 'out_file', f_roi_bin, 'inlist')
        workflow.connect(b_roi_bin, 'out', input_stats, 'volume')
    else:
        workflow.connect(b_mask_bin, 'out', input_stats, 'volume')

    # Single window
    if single_window:
        single_window = pe.Node(
                interface=KMeansWindowWithLinearRegressionNormalisationBSI(
                                in_t2_images=1 if t2_mode else 0,
                                in_bsi_method=bsi_method,
                                in_dilation_kmeans=dil_kmeans,
                                in_nb_kmeans_class=tkn),
                name='single_window')
        workflow.connect([
            (corr_base_im, single_window, [('out', 'baseline_image')]),
            (b_mask_bin, single_window, [('out', 'baseline_mask')]),
            (corr_follow_im, single_window, [('out', 'repeat_image')]),
            (f_mask_bin, single_window, [('out', 'repeat_mask')]),
            (corr_base_im, single_window, [('out', 'bsi_image')]),
            (bsi_b_mask_bin, single_window, [('out', 'bsi_mask')]),
            (corr_follow_im, single_window, [('out', 'bsi_repeat_image')]),
            (bsi_f_mask_bin, single_window, [('out', 'bsi_repeat_mask')]),
            (output_rm_tissue_node, single_window, [('tissue_file',
                                                     'in_lesions_mask')])
                         ])

        # Copy geometry for all outputs file:
        input_cpgeom = pe.Node(interface=niu.Merge(), name='input_cpgeom')
        workflow.connect([
            (corr_base_im, input_cpgeom, [('out', 'in1')]),
            (corr_base_im, input_cpgeom, [('out', 'in2')]),
            (corr_base_im, input_cpgeom, [('out', 'in3')]),
            (corr_follow_im, input_cpgeom, [('out', 'in4')]),
            (corr_follow_im, input_cpgeom, [('out', 'in5')])
                         ])
        dest_cpgeom = pe.Node(interface=niu.Merge(), name='dest_cpgeom')
        workflow.connect([
            (single_window, dest_cpgeom, [('out_bsi_image', 'in1')]),
            (single_window, dest_cpgeom, [('out_xor_mask', 'in2')]),
            (single_window, dest_cpgeom, [('out_class_image', 'in3')]),
            (single_window, dest_cpgeom, [('out_repeat_class_image', 'in4')]),
            (single_window, dest_cpgeom, [('out_normalised_repeat_image',
                                           'in5')])
                         ])
        final_cpgeom = pe.MapNode(interface=fsl.CopyGeom(),
                                  iterfield=['in_file', 'dest_file'],
                                  name='final_cpgeom')
        workflow.connect([
            (input_cpgeom, final_cpgeom, [('out', 'in_file')]),
            (dest_cpgeom, final_cpgeom, [('out', 'dest_file')])
                         ])

    # Double window mode
    else:
        double_window = pe.Node(
                interface=KNDoubleWindowBSI(
                                in_t2_images=1 if t2_mode else 0,
                                in_bsi_method=bsi_method,
                                in_dilation_kmeans=dil_kmeans,
                                in_nb_kmeans_class=tkn),
                name='single_window')
        workflow.connect([
            (corr_base_im, double_window, [('out', 'baseline_image')]),
            (b_mask_bin, double_window, [('out', 'baseline_mask')]),
            (corr_follow_im, double_window, [('out', 'repeat_image')]),
            (f_mask_bin, double_window, [('out', 'repeat_mask')]),
            (corr_base_im, double_window, [('out', 'bsi_image')]),
            (bsi_b_mask_bin, double_window, [('out', 'bsi_mask')]),
            (corr_follow_im, double_window, [('out', 'bsi_repeat_image')]),
            (bsi_f_mask_bin, double_window, [('out', 'bsi_repeat_mask')]),
            (output_rm_tissue_node, double_window, [('tissue_file',
                                                     'in_lesions_mask')]),
            (b_roi_bin, double_window, [('out', 'gm_mask')]),
            (f_roi_bin, double_window, [('out', 'repeat_gm_mask')]),
                         ])

        # Copy geometry for all outputs file:
        dest_cpgeom = pe.Node(interface=niu.Merge(), name='dest_cpgeom')
        workflow.connect([
            (double_window, dest_cpgeom, [('out_bsi_image', 'in1')]),
            (double_window, dest_cpgeom, [('out_xor_mask', 'in2')]),
            (double_window, dest_cpgeom, [('out_csf_gm', 'in3')]),
            (double_window, dest_cpgeom, [('out_gm_wm', 'in4')])
                         ])
        final_cpgeom = pe.MapNode(interface=fsl.CopyGeom(),
                                  iterfield=['dest_file'],
                                  name='final_cpgeom')
        workflow.connect([
            (corr_base_im, final_cpgeom, [('out', 'in_file')]),
            (dest_cpgeom, final_cpgeom, [('out', 'dest_file')])
                         ])

    # Stats node:
    stats_node = pe.MapNode(interface=niftyseg.UnaryStats(
                                            operation='V'),
                            name='stats_node')
    workflow.connect(input_stats, 'volume', stats_node, 'in_file')
    # BSI calculation END

    # Write the outputs:
    # Values to return:
    """with open(single_window.outputs.out_bsi_values, 'rb') as f:
        reader = csv.reader(f, delimiter=delimiter)
        if not header:
            header = next(reader)
        for row in reader:
            if row == header:
                continue
        bsi=output.split('DW BSI,')[1]
	bsi=bsi.split(',')[0]
	bsi=float(bsi)
    v1 = float(stats_node.outputs.output)
    pbvc = - 100 * bsi * 1000 / v1"""

    # Generate Report
    # compute volumes:
    stats_report = pe.MapNode(interface=niftyseg.UnaryStats(
                                            operation='V'),
                              name='stats_report')
    workflow.connect(binarize_mask, 'out', stats_report, 'in_file')
    # generate png

    # Generating segmentation overlayed images

    # Generate Report END

    return workflow
