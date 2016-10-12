# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
import os
from PIL import Image
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
HTML_TEMPLATE = """
<html>
<head>
<link href="http://cmictig.cs.ucl.ac.uk/templates/design_control/favicon.ico" \
rel="shortcut icon" type="image/x-icon">
<title>BSI - Id: {patient}</title>
<style>
body {
    font-family:"Tahoma",Helvetica,Sans-serif;
}
p { font-family:"Tahoma",Helvetica,Sans-serif; }
td { font-family:"Tahoma",Helvetica,Sans-serif; }
.title {
    background:#E0E0E0;
    border-top:solid 1px #EEEDED;
    border-bottom:solid 1px #EEEDED;
    width:100% !important;
    max-width:100% !important;
    height:40x;
    padding-top:5px;
    padding-left:5px;
    padding-bottom:5px;
    z-index:3
}
</style>
</head>
<body>
<div><a href="http://cmictig.cs.ucl.ac.uk/" target="a"><img border \
src="http://cmictig.cs.ucl.ac.uk/templates/design_control/images/s5_logo.png">\
</a></div>
<br>
<div><h3>Atrophy report: {patient}</h3></div>
<div class="title"><b>Brain extraction results</b></div>
<p>These images show the tissue segmentation used to find the brain/non-brain \
boundary.</p>
<p><i>Baseline:</i> {b_mask} <br><i>Volume:</i> {vol1} mm^3<br><img border=0 \
width="100%" src="{f_b_mask}"></p>
<p><i>Follow-up:</i> {f_mask} <br><i>Volume:</i> {vol2} mm^3<br><img border=0 \
width="100%" src="{f_f_mask}"></p>
<br>
<div class="title"><b>Brain extraction comparation between two time-points</b>\
</div>
<p><img border=0 width="100%" src="{seg}"></p>
<br>
<div class="title"><b>Baseline to follow-up registration results</b></div>
<p><img border=0 width="100%" src="{reg}"></p>
<br>
<div class="title"><b>XOR region where BSI is computed</b></div>
<p>Probability 0 <IMG SRC="http://cmictig.cs.ucl.ac.uk/softweb/img/orange.gif"\
> 1
<p><img border=0 width="100%" src="{xor}"></p>
<br>
<div class="title"><b>Final brain edge movement image results</b></div>
<p>Atrophy <IMG SRC="http://cmictig.cs.ucl.ac.uk/softweb/img/blue.gif"> 0 \
<IMG SRC="http://cmictig.cs.ucl.ac.uk/softweb/img/orange.gif"> Growth</p>
<p><img border=0 width="100%" src="{bsi}"></p>
<br>
<div class="title"><b>Estimated BSI and PBVC</b></div>
<p><font face="courier" size="3">BSI (ml)= {bsi_val}<br>PBVC (%)= {pbvc_val}\
<br>ATROPHY (%)= {atrophy}<br>GROWTH (%)= {growth}</font></p>
<div class="title"><b>Executed command line:</b></div>
<p><font face="courier" size="-1">{cmd}</font></p>
<div class="title"><b>Referencing this work</b></div>
<p>Two-timepoint percentage brain volume change was estimated with GBSI \
[Prados et al. 2014], part of NifTK software tools
[URL:<a href="http://cmictig.cs.ucl.ac.uk/research/software/" target="a">\
http://cmictig.cs.ucl.ac.uk/research/software</a>].</p>
<b>GBSI method</b>
<font size="-1"><em>
<p>[Prados 2014] Prados, F., Cardoso, M. J., Leung, K. K., Cash, D. M., \
Modat, M., Fox, N. C., Wheeler-Kingshott, C. A. M., Ourselin, S., \
for the Alzheimer's Disease Neuroimaging Initiative. (2014)
<BR>&nbsp;&nbsp;&nbsp;<a href=\
"http://www.sciencedirect.com/science/article/pii/S0197458014005508" \
target="a">Measuring brain atrophy with a generalized formulation of \
the boundary shift integral.</a>
<BR>&nbsp;&nbsp;&nbsp;Neurobiology of Aging.
</p></em></font>

<br>
<b>BSI main method</b>
<font size="-1"><em>
<p>[Freeborough 1997] Freeborough, P. A., & Fox, N. C. (1997).
<BR>&nbsp;&nbsp;&nbsp;<a href="http://www.ncbi.nlm.nih.gov/pubmed/9368118" \
target="a">The boundary shift integral: an accurate and robust measure of \
cerebral volume changes from registered repeat MRI.</a>
<BR>&nbsp;&nbsp;&nbsp;IEEE transactions on medical imaging, 16(5), 623-9.
</p></em></font>

<br>
<b>KN-BSI method</b>
<font size="-1"><em>
<p>[Leung 2010] Leung, K. K., Clarkson, M. J., Bartlett, J. W., Clegg, S. L., \
Jack, C. R., Weiner, M. W., Fox, N. C., Ourselin, S. (2010).
<BR>&nbsp;&nbsp;&nbsp;<a href="\
http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid=2828361&tool=\
pmcentrez&rendertype=abstract" \
target="a">Robust atrophy rate measurement in Alzheimer's disease using \
multi-site serial MRI: tissue-specific intensity normalization and parameter \
selection.</a>
<BR>&nbsp;&nbsp;&nbsp;NeuroImage, 50(2), 516-23.
</p></em></font>

<br>
<b>pBSI method</b>
<font size="-1"><em>
<p>[Ledig 2012] Ledig, C., Wolz, R., Aljabar, P., Jyrki, L., & Rueckert, \
D. (2012)
<BR>&nbsp;&nbsp;&nbsp;<a href="http://picsl.upenn.edu/docs/nibad12_proceedings\
_reduced_20120905.pdf" target="a">PBSI: A symmetric probabilistic extension \
of the Boundary Shift Integral.</a>
<BR>&nbsp;&nbsp;&nbsp;In MICCAI 2012 Workshop on Novel Imaging Biomarkers for \
Alzheimer's Disease and Related Disorders (pp. 117-124).
</p></em></font>

<br>
<b>Double Window-BSI</b>
<font size="-1"><em>
<p>[Schott 2010] Schott, J. M., Bartlett, J. W., Barnes, J., Leung, K. K., \
Ourselin, S., & Fox, N. C. (2010)
<BR>&nbsp;&nbsp;&nbsp;<a href="http://www.pubmedcentral.nih.gov/articlerender\
.fcgi?artid=2947486&tool=pmcentrez&rendertype=abstract" target="a">Reduced \
sample sizes for atrophy outcomes in Alzheimer's disease trials: baseline \
adjustment.</a>
<BR>&nbsp;&nbsp;&nbsp;Neurobiology of aging, 31(8), 1452-62, 1462.e1-2.
</p></em></font>
<br>
<div align="center"><a href="http://cmictig.cs.ucl.ac.uk" target="a">\
Translational Imaging Group</a> - <a href="http://ucl.ac.uk" target="a">\
University College London</a></div>
<br>
</body>
</html>"""


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


def generate_seg_png(label='png', name='generate_seg_png'):
    """Workflow to generate seg png images."""
    # Create a workflow to process the images
    workflow = pe.Workflow(name=name)
    workflow.base_output_dir = name

    # Input node:
    input_node = pe.Node(interface=niu.IdentityInterface(),
                         name='input_node',
                         fields=['in_file',
                                 'overlay_file',
                                 'png_file'])
    if not input_node.inputs.png_file:
        input_node.inputs.png_file = os.path.join(
                os.path.basename(os.path.abspath(input_node.inputs.in_file)),
                '%s%s' % (label, '.png'))
    # Output node:
    output_node = pe.Node(interface=niu.IdentityInterface(
                          fields=['png_file']),
                          name='output_node')

    # Segmaths:
    mul_node = pe.Node(interface=niftyseg.BinaryMaths(operation='mul'),
                       name='multiplication_node')
    workflow.connect([
        (input_node, mul_node, [('in_file', 'in_file')]),
        (input_node, mul_node, [('overlay_file', 'operand_file')])
                     ])
    # Stats 1:
    stats_node1 = pe.Node(interface=fsl.ImageStats(op_string='-p 0'),
                          name='stats1_node')
    workflow.connect(mul_node, 'out_file', stats_node1, 'in_file')

    # Segmaths:
    sub_node = pe.Node(interface=niftyseg.BinaryMaths(operation='sub'),
                       name='substraction_node')
    workflow.connect([
        (mul_node, sub_node, [('out_file', 'in_file')]),
        (stats_node1, sub_node, [('out_stats', 'operand_value')])
                     ])
    # Mask:
    mask_node = pe.Node(interface=fsl.ApplyMask(operation=''),
                        name='mask_node')
    workflow.connect([
        (sub_node, mask_node, [('out_file', 'in_file')]),
        (input_node, mask_node, [('overlay_file', 'mask_file')])
                     ])
    # Stats 1:
    stats_node2 = pe.Node(interface=fsl.ImageStats(op_string='-P 95'),
                          name='stats2_node')
    workflow.connect(mask_node, 'out_file', stats_node2, 'out_file')

    # overlay:
    overlay_node = pe.Node(interface=fsl.Overlay(auto_thresh_bg=True,
                                                 transparency=False,
                                                 out_type=0),
                           name='overlay_node')
    overlay_node.inputs.stat_thresh = (1, stats_node2.outputs.out_stats)
    workflow.connect([
        (input_node, overlay_node, [('in_file', 'background_image')]),
        (mask_node, overlay_node, [('out_file', 'stat_image')])
                     ])

    # Copy geometry:
    cpgeom_mask = pe.Node(interface=fsl.CopyGeom(),
                          name='copy_geometry')
    workflow.connect([
        (input_node, cpgeom_mask, [('in_file', 'in_file')]),
        (overlay_node, cpgeom_mask, [('out_file', 'dest_file')])
                     ])

    # Slicer for three slices for each axis:
    slicer_x = pe.MapNode(interface=fsl.Slicer(scaling=1, single_slice='x'),
                          iterfield=['slice_number'],
                          name='slicer_x')
    slicer_x.inputs.slice_number = [0.4, 0.5, 0.6]
    workflow.connect(overlay_node, 'out_file', slicer_x, 'in_file')
    slicer_y = pe.MapNode(interface=fsl.Slicer(scaling=1, single_slice='y'),
                          iterfield=['slice_number'],
                          name='slicer_y')
    slicer_y.inputs.slice_number = [0.4, 0.5, 0.6]
    workflow.connect(overlay_node, 'out_file', slicer_y, 'in_file')
    slicer_z = pe.MapNode(interface=fsl.Slicer(scaling=1, single_slice='z'),
                          iterfield=['slice_number'],
                          name='slicer_z')
    slicer_z.inputs.slice_number = [0.4, 0.5, 0.6]
    workflow.connect(overlay_node, 'out_file', slicer_z, 'in_file')

    # PNGappend
    # input list
    input_png_append = pe.Node(interface=niu.Merge(), name='input_png_append')
    workflow.connect([
        (slicer_x, input_png_append, [('out_file', 'in1')]),
        (slicer_y, input_png_append, [('out_file', 'in2')]),
        (slicer_z, input_png_append, [('out_file', 'in3')])
                     ])

    append_pngs(input_png_append.out_file.out, input_node.inputs.png_file)
    workflow.connect(input_node, 'png_file', output_node, 'png_file')


def generate_gif(label='gif', name='generate_gif'):
    """Generate gif with img as background, overlay1 and overlay2 as color."""
    # Create a workflow to process the images
    workflow = pe.Workflow(name=name)
    workflow.base_output_dir = name

    # Input node:
    input_node = pe.Node(interface=niu.IdentityInterface(),
                         name='input_node',
                         fields=['in_file',
                                 'overlay_file1',
                                 'overlay_file2',
                                 'gif_file'])

    if not input_node.inputs.gif_file:
        input_node.inputs.gif_file = os.path.join(
                os.path.basename(os.path.abspath(input_node.inputs.in_file)),
                '%s%s' % (label, '.gif'))
    # Output node:
    output_node = pe.Node(interface=niu.IdentityInterface(
                          fields=['gif_file']),
                          name='output_node')

    # Overlay:
    output_overlay = pe.Node(interface=niu.IdentityInterface(
                             fields=['out_file']),
                             name='overlay_out')
    if input_node.inputs.overlay_file1:
        overlay_node = pe.Node(interface=fsl.Overlay(auto_thresh_bg=True,
                                                     transparency=False,
                                                     out_type=0),
                               name='overlay_node')
        overlay_node.inputs.stat_thresh = (0.001, 1)
        workflow.connect([
            (input_node, overlay_node, [('in_file', 'background_image')]),
            (input_node, overlay_node, [('overlay_file1', 'stat_image')])
                         ])
        if input_node.inputs.overlay_file2:
            overlay_node.inputs.stat_thresh2 = (0.001, 1)
            workflow.connect(input_node, 'overlay_file2',
                             overlay_node, 'stat_image2')
        # Copy geometry:
        cpgeom = pe.Node(interface=fsl.CopyGeom(),
                         name='copy_geometry')
        workflow.connect([
            (input_node, cpgeom, [('in_file', 'in_file')]),
            (overlay_node, cpgeom, [('out_file', 'dest_file')])
                         ])

        # Connect output:
        workflow(cpgeom, 'out_file', output_overlay, 'out_file')
    else:
        workflow(input_node, 'in_file', output_overlay, 'out_file')

    # Slicer for three slices for each axis:
    slicer_x = pe.MapNode(interface=fsl.Slicer(scaling=1, single_slice='x'),
                          iterfield=['slice_number'],
                          name='slicer_x')
    slicer_x.inputs.slice_number = [0.4, 0.5, 0.6]
    workflow.connect(output_overlay, 'out_file', slicer_x, 'in_file')
    slicer_y = pe.MapNode(interface=fsl.Slicer(scaling=1, single_slice='y'),
                          iterfield=['slice_number'],
                          name='slicer_y')
    slicer_y.inputs.slice_number = [0.4, 0.5, 0.6]
    workflow.connect(output_overlay, 'out_file', slicer_y, 'in_file')
    slicer_z = pe.MapNode(interface=fsl.Slicer(scaling=1, single_slice='z'),
                          iterfield=['slice_number'],
                          name='slicer_z')
    slicer_z.inputs.slice_number = [0.4, 0.5, 0.6]
    workflow.connect(output_overlay, 'out_file', slicer_z, 'in_file')

    # PNGappend
    # input list
    input_png_append = pe.Node(interface=niu.Merge(), name='input_png_append')
    workflow.connect([
        (slicer_x, input_png_append, [('out_file', 'in1')]),
        (slicer_y, input_png_append, [('out_file', 'in2')]),
        (slicer_z, input_png_append, [('out_file', 'in3')])
                     ])

    append_pngs(input_png_append.out_file.out, input_node.inputs.gif_file)
    workflow.connect(input_node, 'gif_file', output_node, 'gif_file')


def append_pngs(list_png, out_file):
    """Fct to append the pngs from the list.

    :param list_png: list of png file path
    """
    image1 = Image.open(list_png[0])
    (width1, height1) = image1.size
    nb_images = len(list_png)
    result = Image.new('RGB', (width1*nb_images, height1*nb_images))
    for ind, png in enumerate(list_png):
        if ind == 0:
            result.paste(im=image1, box=(0, 0))
        else:
            image = Image.open(png)
            result.paste(im=image, box=(width1, 0))
    result.save(out_file)


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
                                              patient=None,
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
    output_node = pe.Node(interface=niu.IdentityInterface(),
                          fields=['out_bsi_image', 'out_xor_mask', 'bsi'],
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
    workflow.connect(copygeom_bias, 'out_file', corr_base_im, 'inlist')
    corr_follow_im = pe.Node(interface=niu.Select(index=1))
    workflow.connect(copygeom_bias, 'out_file', corr_follow_im, 'inlist')
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

        # Connect:
        out_bsi_image = pe.Node(interface=niu.Select(index=0))
        workflow.connect(final_cpgeom, 'out_file', out_bsi_image, 'inlist')
        out_xor_mask = pe.Node(interface=niu.Select(index=1))
        workflow.connect(final_cpgeom, 'out_file', out_xor_mask, 'inlist')
        workflow.connect([
            (out_bsi_image, output_node, [('out', 'out_bsi_image')]),
            (out_xor_mask, output_node, [('out', 'out_xor_mask')]),
            (single_window, output_node, [('out_bsi_values', 'bsi')])
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
        # connect to output
        out_bsi_image = pe.Node(interface=niu.Select(index=0))
        workflow.connect(final_cpgeom, 'out_file', out_bsi_image, 'inlist')
        out_xor_mask = pe.Node(interface=niu.Select(index=1))
        workflow.connect(final_cpgeom, 'out_file', out_xor_mask, 'inlist')
        workflow.connect([
            (out_bsi_image, output_node, [('out', 'out_bsi_image')]),
            (out_xor_mask, output_node, [('out', 'out_xor_mask')]),
            (double_window, output_node, [('out_bsi_values', 'bsi')])
                         ])

    # Stats node:
    stats_node = pe.MapNode(interface=niftyseg.UnaryStats(
                                            operation='V'),
                            name='stats_node')
    workflow.connect(input_stats, 'volume', stats_node, 'in_file')
    # BSI calculation END

    # Generate Report
    # compute volumes:
    stats_report = pe.MapNode(interface=niftyseg.UnaryStats(
                                            operation='V'),
                              name='stats_report')
    workflow.connect(binarize_mask, 'out', stats_report, 'in_file')
    # Generating segmentation overlayed images
    base_png = generate_seg_png(name='base_png')
    base_mask = pe.Node(interface=niu.Select(index=0))
    workflow.connect(output_rm_tissue_node, 'mask_files', base_mask, 'inlist')
    workflow([
        (corr_base_im, base_png, [('out', 'in_file')]),
        (base_mask, base_png, [('out', 'overlay_file')])
             ])
    follow_png = generate_seg_png(name='follow_png')
    follow_mask = pe.Node(interface=niu.Select(index=1))
    workflow.connect(output_rm_tissue_node, 'mask_files',
                     follow_mask, 'inlist')
    workflow([
        (corr_follow_im, follow_png, [('out', 'in_file')]),
        (follow_mask, follow_png, [('out', 'overlay_file')])
             ])

    # Generating segmentation comparation result image
    mul = pe.MapNode(interface=niftyseg.BinaryMaths(
                                            operation='mul',
                                            output_datatype='float'),
                     iterfield=['in_file', 'operand_file'],
                     name='mul')
    workflow.connect([
        (copygeom_bias, mul, [('out_file', 'in_file')]),
        (output_rm_tissue_node, mul, [('mask_files', 'operand_file')])
                     ])
    # Make segmentation gif file:
    base_seg_gif = generate_gif(name='base_seg_gif')
    base_seg = pe.Node(interface=niu.Select(index=0))
    workflow.connect(mul, 'out_file', base_seg, 'inlist')
    workflow(base_seg, 'out', base_seg_gif, 'in_file')
    follow_seg_gif = generate_gif(name='follow_seg_gif')
    follow_seg = pe.Node(interface=niu.Select(index=1))
    workflow.connect(mul, 'out_file', follow_seg, 'inlist')
    workflow.connect(follow_seg, 'out', follow_seg_gif, 'in_file')
    # append the gif:
    gif_seg_file = os.path.join(
            os.path.basename(os.path.abspath(base_seg_gif.outputs.gif_file)),
            'segmentation.gif')
    append_pngs([base_seg_gif.outputs.gif_file,
                 follow_seg_gif.outputs.gif_file], gif_seg_file)
    # make registration gif file:
    base_reg_gif = generate_gif(name='base_reg_gif')
    workflow.connect(corr_base_im, 'out', base_reg_gif, 'in_file')
    follow_reg_gif = generate_gif(name='follow_reg_gif')
    workflow.connect(corr_follow_im, 'out', follow_reg_gif, 'in_file')
    # append the gif:
    gif_reg_file = os.path.join(
            os.path.basename(os.path.abspath(base_reg_gif.outputs.gif_file)),
            'segmentation.gif')
    append_pngs([base_reg_gif.outputs.gif_file,
                 follow_reg_gif.outputs.gif_file], gif_reg_file)

    # Xor:
    xor_png = generate_seg_png(name='xor_png')
    workflow([
        (corr_base_im, xor_png, [('out', 'in_file')]),
        (output_node, xor_png, [('out_xor_mask', 'overlay_file')])
             ])

    # We separate atrophy and growth in two files
    # Growth
    growth_uthr = pe.Node(interface=niftyseg.BinaryMaths(
                                            operation='uthr'),
                          name='growth_uthr')
    growth_uthr.inputs.operand_value = 0
    workflow.connect(output_node, 'output_bsi_image', growth_uthr, 'in_file')
    growth_abs = pe.Node(interface=niftyseg.UnaryMaths(
                                            operation='abs'),
                         name='growth_abs')
    workflow.connect(growth_uthr, 'out_file', growth_abs, 'in_file')
    # Atrophy
    atrophy_thr = pe.Node(interface=niftyseg.BinaryMaths(
                                            operation='thr'),
                          name='atrophy_thr')
    atrophy_thr.inputs.operand_value = 0
    workflow.connect(output_node, 'output_bsi_image', atrophy_thr, 'in_file')

    # We compute atrophy and growth separetely
    # Atrophy is the positive file, because BSI's algorithm measures the
    # intensity's difference between baseline and follow-up. Roughly:
    #    BSI=baselineValue-repeatValue.
    # An intensity decrease between both time points is atrophy and the result
    # at the end of BSI will be positive
    # An intensity gain between both time points is grotwh and the result
    # at the end of BSI will be negative

    # Growth
    growth_node = pe.Node(interface=niftyseg.UnaryStats(operation='V'),
                          name='growth_node')
    workflow.connect(growth_abs, 'out_file', growth_node, 'in_file')

    # Atrophy
    atrophy_node = pe.Node(interface=niftyseg.UnaryStats(operation='V'),
                           name='atrophy_node')
    workflow.connect(atrophy_thr, 'out_file', atrophy_node, 'in_file')

    # Get images:
    v1 = pe.Node(interface=niu.Select(index=0))
    workflow.connect(stats_report, 'out_file', v1, 'inlist')
    v2 = pe.Node(interface=niu.Select(index=1))
    workflow.connect(stats_report, 'out_file', v2, 'inlist')

    growth = float(growth_node.outputs.output[0]) * 100.0 / v1.outputs.out
    atrophy = float(atrophy_node.outputs.output[0]) * 100.0 / v1.outputs.out

    # Gif for BSI:
    bsi_gif = generate_gif(name='bsi_gif')
    workflow([
        (corr_base_im, bsi_gif, [('out', 'in_file')]),
        (growth_abs, bsi_gif, [('out_file', 'overlay_file1')]),
        (atrophy_thr, bsi_gif, [('out_file', 'overlay_file2')])
             ])

    # Read the outputs values:
    with open(output_node.outputs.bsi, 'rb') as f:
        bsi = f[0]
    bsi = float(bsi)
    pbvc = - 100 * bsi * 1000 / v1.outputs.out

    if not patient:
        patient = os.path.basename(input_node.inputs.in_files[0]).split('.')[0]

    # Set the values for the report html:
    html = HTML_TEMPLATE.format(
                patient=patient,
                cmd='Niftypipe workflow boundary_shift_integral',
                vol1="{:.0f}".format(v1.outputs.out),
                vol2="{:.0f}".format(v2.outputs.out),
                f_b_mask=base_png.outputs.png_file,
                f_f_mask=follow_png.outputs.png_file,
                b_mask=base_mask.outputs.out,
                f_mask=follow_mask.outputs.out,
                seg=gif_seg_file,
                reg=gif_reg_file,
                xor=xor_png.outputs.png_file,
                bsi=bsi_gif.outputs.gif_file,
                bsi_val=bsi,
                pbvc_val=pbvc,
                atrophy=atrophy,
                growth=growth)

    html_file = os.path.abspath('index.html')

    # Open a file
    with open(html_file, "wb") as f_html:
        f_html.write(html)
    # Generate Report END

    return workflow
