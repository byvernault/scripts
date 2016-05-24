#! /usr/bin/env python
# -*- coding: UTF-8 -*-

#/*============================================================================
#
#  NifTK: A software platform for medical image computing.
#
#  Copyright (c) University College London (UCL). All rights reserved.
#
#  This software is distributed WITHOUT ANY WARRANTY; without even
#  the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#  PURPOSE.
#
#  See LICENSE.txt in the top level directory for details.
#
#============================================================================*/

#
# This script is for different BSI execution (KN-BSI, GBSI, pBSI and gammaBSI)
# All the needed masks have to be calculated previously
#
# The basic method is:
# If the user runs niftkAtrophyCalculator.py --xml we respond with the XML function contained herein.
# All other command line invocations, we pass the parameters onto the underlying program.

# Import needed libraries
import os
import sys
import atexit
import tempfile
from datetime import datetime, date, time
#from _niftkCommon import *
from glob import glob
import webbrowser

###### DEFAULT OPTIONS #######
dir_output='bsi/'

# Output result webpage pattern
html="""
<html>
<head>
<link href="http://cmictig.cs.ucl.ac.uk/templates/design_control/favicon.ico" rel="shortcut icon" type="image/x-icon">
<title>BSI - Id: PATIENT</title>
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
<div><a href="http://cmictig.cs.ucl.ac.uk/" target="a"><img border src="http://cmictig.cs.ucl.ac.uk/templates/design_control/images/s5_logo.png"></a></div>
<br>
<div><h3>Atrophy report: PATIENT</h3></div>
<div class="title"><b>Brain extraction results</b></div>
<p>These images show the tissue segmentation used to find the brain/non-brain boundary.</p>
<p><i>Baseline:</i> B_MASK <br><i>Volume:</i> VOLUME_1 mm^3<br><img border=0 width="100%" src="FILE_B_MASK"></p>
<p><i>Follow-up:</i> F_MASK <br><i>Volume:</i> VOLUME_2 mm^3<br><img border=0 width="100%" src="FILE_F_MASK"></p>
<br>
<div class="title"><b>Brain extraction comparation between two time-points</b></div>
<p><img border=0 width="100%" src="FILE_SEGMENTATION_COMPARATION"></p>
<br>
<div class="title"><b>Baseline to follow-up registration results</b></div>
<p><img border=0 width="100%" src="FILE_REGISTRATION_COMPARATION"></p>
<br>
<div class="title"><b>XOR region where BSI is computed</b></div>
<p>Probability 0 <IMG SRC="http://cmictig.cs.ucl.ac.uk/softweb/img/orange.gif"> 1
<p><img border=0 width="100%" src="FILE_XOR_REGION"></p>
<br>
<div class="title"><b>Final brain edge movement image results</b></div>
<p>Atrophy <IMG SRC="http://cmictig.cs.ucl.ac.uk/softweb/img/blue.gif"> 0 <IMG SRC="http://cmictig.cs.ucl.ac.uk/softweb/img/orange.gif"> Growth</p>
<p><img border=0 width="100%" src="FILE_BSI_RESULT"></p>
<br>
<div class="title"><b>Estimated BSI and PBVC</b></div>
<p><font face="courier" size="3">BSI (ml)= BSI_VALUE<br>PBVC (%)= PBVC_VALUE<br>ATROPHY (%)= ATROPHY_VALUE<br>GROWTH (%)= GROWTH_VALUE</font></p>
<div class="title"><b>Executed command line:</b></div>
<p><font face="courier" size="-1">COMMAND_LINE</font></p>
<div class="title"><b>Referencing this work</b></div>
<p>Two-timepoint percentage brain volume change was estimated with GBSI [Prados et al. 2014], part of NifTK software tools
[URL:<a href="http://cmictig.cs.ucl.ac.uk/research/software/" target="a">http://cmictig.cs.ucl.ac.uk/research/software</a>].</p>
<b>GBSI method</b>
<font size="-1"><em>
<p>[Prados 2014] Prados, F., Cardoso, M. J., Leung, K. K., Cash, D. M., Modat, M., Fox, N. C., Wheeler-Kingshott, C. A. M., Ourselin, S., for the Alzheimer's Disease Neuroimaging Initiative. (2014)
<BR>&nbsp;&nbsp;&nbsp;<a href="http://www.sciencedirect.com/science/article/pii/S0197458014005508" target="a">Measuring brain atrophy with a generalized formulation of the boundary shift integral.</a>
<BR>&nbsp;&nbsp;&nbsp;Neurobiology of Aging.
</p></em></font>

<br>
<b>BSI main method</b>
<font size="-1"><em>
<p>[Freeborough 1997] Freeborough, P. A., & Fox, N. C. (1997).
<BR>&nbsp;&nbsp;&nbsp;<a href="http://www.ncbi.nlm.nih.gov/pubmed/9368118" target="a">The boundary shift integral: an accurate and robust measure of cerebral volume changes from registered repeat MRI.</a>
<BR>&nbsp;&nbsp;&nbsp;IEEE transactions on medical imaging, 16(5), 623-9.
</p></em></font>

<br>
<b>KN-BSI method</b>
<font size="-1"><em>
<p>[Leung 2010] Leung, K. K., Clarkson, M. J., Bartlett, J. W., Clegg, S. L., Jack, C. R., Weiner, M. W., Fox, N. C., Ourselin, S. (2010).
<BR>&nbsp;&nbsp;&nbsp;<a href="http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid=2828361&tool=pmcentrez&rendertype=abstract" target="a">Robust atrophy rate measurement in Alzheimer's disease using multi-site serial MRI: tissue-specific intensity normalization and parameter selection.</a>
<BR>&nbsp;&nbsp;&nbsp;NeuroImage, 50(2), 516-23.
</p></em></font>

<br>
<b>pBSI method</b>
<font size="-1"><em>
<p>[Ledig 2012] Ledig, C., Wolz, R., Aljabar, P., Jyrki, L., & Rueckert, D. (2012)
<BR>&nbsp;&nbsp;&nbsp;<a href="http://picsl.upenn.edu/docs/nibad12_proceedings_reduced_20120905.pdf" target="a">PBSI: A symmetric probabilistic extension of the Boundary Shift Integral.</a>
<BR>&nbsp;&nbsp;&nbsp;In MICCAI 2012 Workshop on Novel Imaging Biomarkers for Alzheimer's Disease and Related Disorders (pp. 117-124).
</p></em></font>

<br>
<b>Double Window-BSI</b>
<font size="-1"><em>
<p>[Schott 2010] Schott, J. M., Bartlett, J. W., Barnes, J., Leung, K. K., Ourselin, S., & Fox, N. C. (2010)
<BR>&nbsp;&nbsp;&nbsp;<a href="http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid=2947486&tool=pmcentrez&rendertype=abstract" target="a">Reduced sample sizes for atrophy outcomes in Alzheimer's disease trials: baseline adjustment.</a>
<BR>&nbsp;&nbsp;&nbsp;Neurobiology of aging, 31(8), 1452-62, 1462.e1-2.
</p></em></font>
<br>
<div align="center"><a href="http://cmictig.cs.ucl.ac.uk" target="a">Translational Imaging Group</a> - <a href="http://ucl.ac.uk" target="a">University College London</a></div>
<br>
</body>
</html>"""


###########################################################################
###########################################################################
# Function definition
###########################################################################
###########################################################################

# Begin of cleanup function
def cleanup():
	"""
	###########################################################################
	# Function  : Clean temp working directory
	###########################################################################
	"""
	global 	dir_output
	global	debug_mode

	# Check if we are in the directory that we want to remove
	if os.path.isdir(os.path.join(os.pardir,dir_output)):
		os.chdir(os.pardir)

	if os.path.isdir(dir_output):
		if (not debug_mode) and (len(dir_output)>0) :
			#shutil.rmtree(dir_output)
			for f in glob (os.path.join(dir_output,"*.nii*")):
				os.unlink (f)
			for f in glob (os.path.join(dir_output,"*.txt")):
				os.unlink (f)


	return
# End of cleanup function


# Begin of make_name_output_file function
def make_name_output_file(img,add):
	"""
	###########################################################################
	# def make_name_output_file(img,add)
	# Function  : add a text to the filename
	# Param	    : img, input image
	# Param	    : add, text to add at the filename
	# Return    : new file name
	###########################################################################
	"""
	global 	dir_output

	current_dir=os.getcwd()
	name = get_file_name(img)
	ext = get_output_file_extension(img)
	output_file=os.path.join(current_dir,dir_output,name+add+ext)

	return output_file
# End of make_name_output_file function


# Begin of change_format function
def change_format(img,path):
	"""
	###########################################################################
	# def change_format(img,path)
	# Function  : Pass input image to 1mm ISO voxel
	# Param	    : img, input image
	# Param	    : path, directory where copy the image
	# Return    : new file name
	###########################################################################
	"""

	name = get_file_name(img)
	ext = get_output_file_extension(img)
	output_file=img

	if not ext.upper().endswith('.NII.GZ'):
		copy_file_to_destination(img,os.path.join(path,name+'.nii.gz'))
		output_file=os.path.join(path,name+'.nii.gz')

	return output_file
# End of change_format function


# Begin of pass_to_ISO function
def pass_to_ISO(img):
	"""
	###########################################################################
	# def pass_to_ISO(img)
	# Function  : Pass input image to 1mm ISO voxel
	# Param	    : img, input image
	# Return    : new file name
	###########################################################################
	"""
	identity=os.path.abspath('empty.dat')

	# Open file
	fo = open(identity, "wb")
	fo.write('1 0 0 0\n0 1 0 0\n0 0 1 0\n0 0 0 1\n')
	# Close opened file
	fo.close()

	output_file=make_name_output_file(img,'_1mm')

	if not os.path.isfile(output_file):
		execute_command_or_else_stop('flirt \
			-o '+output_file+' \
			-applyisoxfm 1 \
			-paddingsize 0 \
			-init '+identity+' \
			-ref '+img+' \
			-in '+img+'')
	else:
		print('File '+output_file+' detected, we don\'t repeat the calculus')

	return output_file
# End of pass_to_ISO function

# Begin of copy_geometry function
def copy_geometry(src,dst):
	"""
	###########################################################################
	# def copy_geometry(src,dst)
	# Function  : Copy the image geometry from src to dst
	# Param	    : src, source image
	# Param     : dst, destination image
	# Return    :
	###########################################################################
	"""
	execute_command_or_else_stop('fslcpgeom \
			'+src+' \
			'+dst)
	return
# End of copy_geometry function

# Begin of filling_lesions function
def filling_lesions(img,mask,lesions,les_dil):
	"""
	###########################################################################
	# def filling_lesions(img,mask,lesions)
	# Function  : Fill all the masked lesions with WM intensity average
	# Param	    : img, input image
	# Param     : mask, brain mask
	# Param	    : lesions, lesion mask
	# Param	    : les_dil, number of dilation to be applied
	# Return    : new file name
	###########################################################################
	"""
	output_file=make_name_output_file(img,'_filled')

	if not os.path.isfile(output_file):
		dilation=''
		if les_dil > 0:
			dilation='-dil '+str(les_dil);

		execute_command_or_else_stop('seg_FillLesions \
			'+img+' \
			'+lesions+' \
			'+output_file+' \
			-mask '+mask+' \
			'+dilation+'')

		copy_geometry(img,output_file)
	else:
		print('File '+output_file+' detected, we don\'t repeat the calculus')

	return output_file
# End of filling_lesions function


# Begin of bias field correction function
def bias_field_correction(img,n4_bfc):
	"""
	###########################################################################
	# def bias_field_correction(img,n4_bfc)
	# Function  : N3 bias field correction using Boyes et al. Neuroimage 2008 normalization process
	# Param	    : img, input image
	# Param	    : n4_bfc, use n4 instead than n3
	# Return    : new file name
	###########################################################################
	"""
	global	ATLAS_MASK_IMAGE
	global	ATLAS_HEAD_IMAGE

	output_file=make_name_output_file(img,'_bc')

	if not os.path.isfile(output_file):
		execute_command_or_else_stop('niftkBiasFieldCorrection.py \
			-in '+img+' \
			'+n4_bfc+' \
			-mask '+ATLAS_MASK_IMAGE+' \
			-atlas '+ATLAS_HEAD_IMAGE+' \
			-out '+output_file)

		copy_geometry(img,output_file)
	else:
		print('File '+output_file+' detected, we don\'t repeat the calculus')

	return output_file
# End of bias_field_correction function


# Begin of dilate_mask function
def dilate_mask(img,times):
	"""
	###########################################################################
	# def dilate_mask(img,times)
	# Function  :
	# Param	    : img, input image mask
	# Param	    : times, number of dilations
	# Return    : new file name
	###########################################################################
	"""
	output_file=make_name_output_file(img,'_dilated'+ str(times))

	if not os.path.isfile(output_file):
		execute_command_or_else_stop('seg_maths \
			'+img+' \
			-thr 0.5 \
			-bin \
			-dil '+ str(times)+' \
			'+output_file)
	else:
		print('File '+output_file+' detected, we don\'t repeat the calculus')

	return output_file
# End of dilate_mask function


# Begin of resample_data function
def resample_data(ref,flo,trans,interpolation,text='_register'):
	"""
	###########################################################################
	# def resample_data(ref,flo,trans,interpolation)
	# Function  :
	# Param	    : ref, reference input image
	# Param	    : flo, floating input image
	# Param     : trans, transformation matrix
	# Param	    : interpolation, interpolation method to apply
	# Return    : new file name
	###########################################################################
	"""
	output_file=make_name_output_file(flo,text)

	if not os.path.isfile(output_file):
		transformation=''
		if len(trans)>0:
			transformation='-aff '+trans

		execute_command_or_else_stop('reg_resample \
			-ref '+ref+' \
			-flo '+flo+' \
			-res '+output_file+' \
			'+transformation+' \
			'+interpolation)

		execute_command_or_else_stop('fslmaths \
			'+output_file+' \
			-nan \
			'+output_file)
	else:
		print('File '+output_file+' detected, we don\'t repeat the calculus')

	return output_file
# End of dilate_mask function


# Begin of register_images function
def register_images(probabilistic):
	"""
	###########################################################################
	# def register_images(probabilistic)
	# Function  : We register the two time points images to the half-way
	# Param	    : probabilistic, flag that indicates if we are working with probabilistic or generalized BSI
	# Return    :
	###########################################################################
	"""
	global B_INPUT_IMAGE
	global F_INPUT_IMAGE
	global B_MASK
	global F_MASK
	global B_ROI_MASK
	global F_ROI_MASK
	transformation=os.path.abspath('source_to_target_affine.txt')
	half_trans=os.path.abspath('half-way_affine.txt')
	half_trans_inv=os.path.abspath('half-way_affine-inv.txt')

	# First we dilate the both mask
	b_mask_dilated=dilate_mask(B_MASK,8)
	f_mask_dilated=dilate_mask(F_MASK,8)

	# We calculate the registration from follow-up to baseline
	if not os.path.isfile(transformation):
		execute_command_or_else_stop('reg_aladin \
			-ref '+B_INPUT_IMAGE+' \
			-rmask '+b_mask_dilated+' \
			-flo '+F_INPUT_IMAGE+' \
			-fmask '+f_mask_dilated+' \
			-aff '+transformation+' \
			-res first_register.nii.gz')
		remove_files('first_register.nii.gz')
	else:
		print('File '+transformation+' detected, we don\'t repeat the calculus')

	# We compute the half-way transformation matrix and the inverse
	execute_command_or_else_stop('reg_transform \
		-ref '+B_INPUT_IMAGE+' \
		-half '+transformation+' \
		'+half_trans)

	execute_command_or_else_stop('reg_transform \
		-ref '+B_INPUT_IMAGE+' \
		-invAff '+half_trans+' \
		'+half_trans_inv)

	# Register rois to half-way
	if B_ROI_MASK!='' or F_ROI_MASK!='':
		transform_rois_to_half_way(probabilistic)

	# Set up the interpolation method
	interpolation=''
	if probabilistic:
		print('We are using linear interpolation - pBSI or GBSI')
		interpolation='-LIN'
	else:
		print('We are using nearest neighbour interpolation - Not probabilistic')
		interpolation='-NN'

	# We compute all the images after knowing the transformation matrices
	b_input=B_INPUT_IMAGE

	B_INPUT_IMAGE=resample_data(b_input,B_INPUT_IMAGE,half_trans_inv,'')
	F_INPUT_IMAGE=resample_data(b_input,F_INPUT_IMAGE,half_trans,'')

	B_MASK=resample_data(b_input,B_MASK,half_trans_inv,interpolation)
	F_MASK=resample_data(b_input,F_MASK,half_trans,interpolation)

	return
# End of register_images function


# Begin of transform_rois_to_half_way function
def transform_rois_to_half_way(probabilistic):
	"""
	###########################################################################
	# def transform_rois_to_half_way(probabilistic)
	# Function  : We register the two time points rois to the half-way, we start the transform optimization from the previous transform registration
	# Param	    : probabilistic, flag that indicates if we are working with probabilistic or generalized BSI
	# Return    :
	###########################################################################
	"""
	global B_INPUT_IMAGE
	global F_INPUT_IMAGE
	global B_ROI_MASK
	global F_ROI_MASK
	transformation=os.path.abspath('source_to_target_affine.txt')
	transformation_rois=os.path.abspath('source_to_target_affine_rois.txt')
	half_trans=os.path.abspath('half-way_affine_rois.txt')
	half_trans_inv=os.path.abspath('half-way_affine-inv_rois.txt')
	identity=os.path.abspath('empty.dat')

	# Set up the interpolation method
	interpolation=''
	if probabilistic:
		print('We are using linear interpolation - pBSI or GBSI')
		interpolation='-LIN'
	else:
		print('We are using nearest neighbour interpolation - Not probabilistic')
		interpolation='-NN'

	# First we dilate the both mask
	b_mask_dilated=dilate_mask(B_ROI_MASK,8)
	f_mask_dilated=dilate_mask(F_ROI_MASK,8)
	b_mask_dilated=resample_data(B_INPUT_IMAGE,b_mask_dilated,'',interpolation,'_resampled')
	f_mask_dilated=resample_data(F_INPUT_IMAGE,f_mask_dilated,'',interpolation,'_resampled')

	# We calculate the registration from follow-up to baseline
	if not os.path.isfile(transformation_rois):
		execute_command_or_else_stop('reg_aladin \
			-ref '+B_INPUT_IMAGE+' \
			-rmask '+b_mask_dilated+' \
			-flo '+F_INPUT_IMAGE+' \
			-fmask '+f_mask_dilated+' \
			-aff '+transformation_rois+' \
			-%v 100 \
			-inaff '+transformation+' \
			-ln 1 \
			-rigOnly \
			-res second_register.nii.gz')
		remove_files('second_register.nii.gz')
	else:
		print('File '+transformation_rois+' detected, we don\'t repeat the calculus')

	# We compute the half-way transformation matrix and the inverse
	execute_command_or_else_stop('reg_transform \
		-ref '+B_INPUT_IMAGE+' \
		-half '+transformation_rois+' \
		'+half_trans)

	execute_command_or_else_stop('reg_transform \
		-ref '+B_INPUT_IMAGE+' \
		-invAff '+half_trans+' \
		'+half_trans_inv)

	# We compute all the new ROIS after knowing the transformation matrices
	B_ROI_MASK=resample_data(B_INPUT_IMAGE,B_ROI_MASK,half_trans_inv,interpolation)
	F_ROI_MASK=resample_data(B_INPUT_IMAGE,F_ROI_MASK,half_trans,interpolation)

	return
# End of transform_rois_to_half_way function


# Begin of transform_lesions_to_half_way function
def transform_lesions_to_half_way():
	"""
	###########################################################################
	# def transform_lesions_to_half_way()
	# Function  : We register the two time points lesion mask to the half-way
	# Return    :
	###########################################################################
	"""
	global B_INPUT_IMAGE
	global B_LESION_MASK
	global F_LESION_MASK
	half_trans=os.path.abspath('half-way_affine.txt')
	half_trans_inv=os.path.abspath('half-way_affine-inv.txt')

	# Set up the interpolation method
	print('We are using nearest neighbour interpolation for lesion mask')
	interpolation='-NN'

	# We compute all the new lesion masks after knowing the transformation matrices
	B_LESION_MASK=resample_data(B_INPUT_IMAGE,B_LESION_MASK,half_trans_inv,interpolation)
	F_LESION_MASK=resample_data(B_INPUT_IMAGE,F_LESION_MASK,half_trans,interpolation)

	return
# End of transform_lesions_to_half_way function


# Begin of bias_correction function
def bias_correction():
	"""
	###########################################################################
	# def bias_correction()
	# Function  : We correct the differential bias correction between images
	# Return    :
	###########################################################################
	"""
	global B_INPUT_IMAGE
	global F_INPUT_IMAGE
	global B_MASK
	global F_MASK

	output_file_1=make_name_output_file(B_INPUT_IMAGE,'_bc')
	output_file_2=make_name_output_file(F_INPUT_IMAGE,'_bc')

	if not os.path.isfile(output_file_1) or not os.path.isfile(output_file_2):
		execute_command_or_else_stop('niftkMTPDbc \
			'+B_INPUT_IMAGE+' \
			'+B_MASK+' \
			'+output_file_1+' \
			'+F_INPUT_IMAGE+' \
			'+F_MASK+' \
			'+output_file_2)
		copy_geometry(B_INPUT_IMAGE,output_file_1)
		copy_geometry(F_INPUT_IMAGE,output_file_2)
	else:
		print('File '+output_file_1+' and '+output_file_2+' detected, we don\'t repeat the calculus')

	B_INPUT_IMAGE=output_file_1
	F_INPUT_IMAGE=output_file_2

	return
# End of bias_correction function


# Begin of calculate_tissue_to_remove function
def calculate_tissue_to_remove(les_dil):
	"""
	###########################################################################
	# def calculate_tissue_to_remove(les_dil)
	# Function  : We calculate the tissue to be removed
	# Param	    : les_dil, number of dilation to be applied
	# Return    :
	###########################################################################
	"""
	global B_LESION_MASK
	global F_LESION_MASK
	tissue_to_remove_file=os.path.abspath('tissue_to_remove.nii.gz')

	# We compute calculate the tissues to be removed
	if not os.path.isfile(tissue_to_remove_file):
		# Two time point lesion mask union
		dilation=''
		if les_dil > 0:
			dilation='-dil '+str(les_dil);

		execute_command_or_else_stop('seg_maths \
			'+B_LESION_MASK+' \
			-add \
			'+F_LESION_MASK+' \
			'+dilation+' \
			-bin \
			-odt uchar \
			'+tissue_to_remove_file)
	else:
		print('File '+tissue_to_remove_file+' detected, we don\'t repeat the calculus')

	return tissue_to_remove_file
# End of calculate_tissue_to_remove function


# Begin of remove_tissue_from_image function
def remove_tissue_from_image(img,tissue_to_remove_file):
	"""
	###########################################################################
	# def remove_tissue_from_image(img,tissue_to_remove_file)
	# Function  : We remove the tissue from image img
	# Param     : img, input image
	# Param     : tissue_to_remove_file, mask with the tissue to be removed
	# Return    : new file name
	###########################################################################
	"""
	output_file=make_name_output_file(img,'_notlesions')
	tissue_inv=make_name_output_file(img,'_inv')

	if not os.path.isfile(tissue_inv):
		execute_command_or_else_stop('seg_maths \
			'+tissue_to_remove_file+' \
			-sub 1 \
			-abs \
			-odt uchar  \
			'+tissue_inv)
		copy_geometry(tissue_to_remove_file,tissue_inv)

	if not os.path.isfile(output_file):
		execute_command_or_else_stop('seg_maths \
			'+img+' \
			-mul \
			'+tissue_inv+' \
			-thr 0  \
			'+output_file)
		copy_geometry(img,output_file)
	else:
		print('File '+output_file+' detected, we don\'t repeat the calculus')

	return output_file
# End of remove_tissue_from_image function

# Begin of binarize_mask function
def binarize_mask(img):
	"""
	###########################################################################
	# def binarize_mask()
	# Function  : We binarize the input image
	# Param     : img, input image
	# Return    : new file name
	###########################################################################
	"""
	output_file=make_name_output_file(img,'_bin')

	if not os.path.isfile(output_file):
		execute_command_or_else_stop('seg_maths \
			'+img+' \
			-thr 0.5 \
			-bin \
			-odt uchar  \
			'+output_file)
	else:
		print('File '+output_file+' detected, we don\'t repeat the calculus')

	return output_file
# End of binarize_mask function


# Begin of write_results function
def write_results(data):
	"""
	###########################################################################
	# def write_results()
	# Function  : Write results in the report file
	# Param     : data, string to be writen
	# Return    :
	###########################################################################
	"""
	report_file=os.path.abspath('report.bsi')

	# Open a file
	fo = open(report_file,"ab")
	fo.write(data+'\n')

	# Close opend file
	fo.close()

	return
# End of write_results function


# Begin of calculate_sw_BSI function
def calculate_sw_BSI(method,tkn,tissue_to_remove_file,dil_kmeans,t2_mode):
	"""
	###########################################################################
	# def calculate_sw_BSI(method,tkn,tissue_to_remove_file)
	# Function  : We compute the single window BSI
	# Param     : method, technique to be applied
	# Param	    : tkn, number of tissues
	# Param     : tissue_to_remove_file, mask with the tissue to be removed
	# Param     : dil_kmeans, number of mask dilations for kmeans
	# Param	    : t2_mode, indicates if we are working with T1 images or T2 images
	# Return    : array with the bsi (ml), pbvc (%) and baseline volume (mm3)
	###########################################################################
	"""
	global B_INPUT_IMAGE
	global F_INPUT_IMAGE
	global B_MASK
	global F_MASK
	global B_BSI_MASK
	global F_BSI_MASK
	global B_BSI_ROI_MASK
	global F_BSI_ROI_MASK
	xor_file=os.path.abspath('xor.nii.gz')
	bsi_file=os.path.abspath('bsi.nii.gz')

	# Binarize probabilistic mask for calculating volumes
	# We use the original images without removing tissues or any other kind of manipulation
	B_MASK_bin=binarize_mask(B_MASK)
	F_MASK_bin=binarize_mask(F_MASK)
	volume=B_MASK_bin

	# We check wich is the area where we need to compute BSI
	if B_BSI_ROI_MASK!='' and F_BSI_ROI_MASK!='':
		b_bsi_mask=B_BSI_ROI_MASK
		f_bsi_mask=F_BSI_ROI_MASK
		volume=binarize_mask(B_BSI_ROI_MASK)
	else:
		b_bsi_mask=B_BSI_MASK
		f_bsi_mask=F_BSI_MASK

	# We prepare output file names
	b_kmeans=make_name_output_file(B_INPUT_IMAGE,'_kmeans')
	f_kmeans=make_name_output_file(F_INPUT_IMAGE,'_kmeans')
	f_norm=make_name_output_file(F_INPUT_IMAGE,'_norm')

	if method==1:
		dilation=0
		erosion=0
	else:
		dilation=1
		erosion=1

	if t2_mode:
		t2_image=1
	else:
		t2_image=0

	output=execute_command_or_else_stop('niftkKMeansWindowWithLinearRegressionNormalisationBSI \
		'+B_INPUT_IMAGE+' \
		'+B_MASK_bin+' \
		'+F_INPUT_IMAGE+' \
		'+F_MASK_bin+' \
		'+B_INPUT_IMAGE+' \
		'+b_bsi_mask+' \
		'+F_INPUT_IMAGE+' \
		'+f_bsi_mask+' \
		'+str(dilation)+' \
		'+str(erosion)+' \
		'+str(dil_kmeans)+' \
		-1 -1 \
		'+b_kmeans+' \
		'+f_kmeans+' \
		'+f_norm+' \
		dummy \
		'+str(tkn)+' -1 1 \
		'+str(method)+' \
		'+bsi_file+' \
		'+xor_file+' \
		'+tissue_to_remove_file+' \
		'+str(t2_image),'ON')

	copy_geometry(B_INPUT_IMAGE,bsi_file)
	copy_geometry(B_INPUT_IMAGE,xor_file)
	copy_geometry(B_INPUT_IMAGE,b_kmeans)
	copy_geometry(F_INPUT_IMAGE,f_kmeans)
	copy_geometry(F_INPUT_IMAGE,f_norm)

	# Before we remove white spaces, newlines and tabs
	pat = re.compile(r'\s+')
	output=pat.sub(' ',output)

	# We get BSI value
	bsi=output.split('BSI,')[1]
	bsi=bsi.split(',')[2]
	bsi=float(bsi)

	# We calculate the baseline volume
	v1=float(execute_command_or_else_stop('seg_stats \
		'+volume+' \
		-V','ON'))

	# We calculate the PBVC
	pbvc=-100 * bsi * 1000 / v1

	print "PBVC = %3f" % (pbvc)

	write_results(output)

	return [bsi,pbvc,v1]
# End of calculate_sw_BSI function


# Begin of calculate_dw_BSI function
def calculate_dw_BSI(method,tkn,tissue_to_remove_file,dil_kmeans,t2_mode):
	"""
	###########################################################################
	# def calculate_sw_BSI(method,tkn,tissue_to_remove_file)
	# Function  : We compute the single window BSI
	# Param     : method, technique to be applied
	# Param	    : tkn, number of tissues
	# Param     : tissue_to_remove_file, mask with the tissue to be removed
	# Param     : dil_kmeans, number of mask dilations for kmeans
	# Param	    : t2_mode, indicates if we are working with T1 images or T2 images
	# Return    : array with the bsi (ml), pbvc (%) and baseline volume (mm3)
	###########################################################################
	"""
	global B_INPUT_IMAGE
	global F_INPUT_IMAGE
	global B_MASK
	global F_MASK
	global B_BSI_MASK
	global F_BSI_MASK
	global B_BSI_ROI_MASK
	global F_BSI_ROI_MASK
	xor_file=os.path.abspath('xor.nii.gz')
	bsi_file=os.path.abspath('bsi.nii.gz')
	csf_wm_file=os.path.abspath('bsi_csf_wm.nii.gz')
	wm_gm_file=os.path.abspath('bsi_wm_gm.nii.gz')

	# Binarize probabilistic mask for calculating volumes
	# We use the original images without removing tissues or any other kind of manipulation
	B_MASK_bin=binarize_mask(B_MASK)
	F_MASK_bin=binarize_mask(F_MASK)
	volume=B_MASK_bin

	# We check wich is the area where we need to compute BSI
	if B_BSI_ROI_MASK!='' and F_BSI_ROI_MASK!='':
		b_bsi_mask=B_BSI_ROI_MASK
		f_bsi_mask=F_BSI_ROI_MASK
		volume=binarize_mask(B_BSI_ROI_MASK)
		b_roi_bin=binarize_mask(B_BSI_ROI_MASK)
		f_roi_bin=binarize_mask(F_BSI_ROI_MASK)
	else:
		b_bsi_mask=B_BSI_MASK
		f_bsi_mask=F_BSI_MASK
		b_roi_bin=B_BSI_MASK_bin
		f_roi_bin=F_BSI_MASK_bin

	# We prepare output file names
	b_kmeans=make_name_output_file(B_INPUT_IMAGE,'_kmeans')
	f_kmeans=make_name_output_file(F_INPUT_IMAGE,'_kmeans')
	f_norm=make_name_output_file(F_INPUT_IMAGE,'_norm')

	if method==1:
		dilation=0
		erosion=0
	else:
		dilation=1
		erosion=1

	if t2_mode:
		t2_image=1
	else:
		t2_image=0

	output=execute_command_or_else_stop('niftkKNDoubleWindowBSI \
		'+B_INPUT_IMAGE+' \
		'+B_MASK_bin+' \
		'+F_INPUT_IMAGE+' \
		'+F_MASK_bin+' \
		'+B_INPUT_IMAGE+' \
		'+b_bsi_mask+' \
		'+F_INPUT_IMAGE+' \
		'+f_bsi_mask+' \
		'+str(dilation)+' \
		'+str(erosion)+' \
		'+str(dil_kmeans)+' \
		'+b_kmeans+' \
		'+f_kmeans+' \
		dummy \
		'+xor_file+' \
		'+b_roi_bin+' \
		'+f_roi_bin+' \
		1 0.5 \
		dummy -1 \
		'+csf_wm_file+' \
		'+wm_gm_file+' \
		-1 -1 -1 -1 \
		'+str(method)+' \
		'+bsi_file+' \
		'+tissue_to_remove_file+' \
		'+str(t2_image),'ON')

	copy_geometry(B_INPUT_IMAGE,bsi_file)
	copy_geometry(B_INPUT_IMAGE,xor_file)
	copy_geometry(B_INPUT_IMAGE,csf_wm_file)
	copy_geometry(B_INPUT_IMAGE,wm_gm_file)

	# Before we remove white spaces, newlines and tabs
	pat = re.compile(r'\s+')
	output=pat.sub(' ',output)

	# We get BSI value
	bsi=output.split('DW BSI,')[1]
	bsi=bsi.split(',')[0]
	bsi=float(bsi)

	# We calculate the baseline volume
	v1=float(execute_command_or_else_stop('seg_stats \
		'+volume+' \
		-V','ON'))

	# We calculate the PBVC
	pbvc=-100 * bsi * 1000 / v1

	print "PBVC = %3f" % (pbvc)

	write_results(output)

	return [bsi,pbvc,v1]
# End of calculate_dw_BSI function


# Begin of generate_seg_png function
def generate_seg_png(name,img,overlay=''):
	"""
	###########################################################################
	# def generate_seg_png(name,img,overlay)
	# Function  : We do a png with img as background and overlay1 and overlay2 as color content
	# Param     : name, file name
	# Param	    : img, background image
	# Param	    : overlay1, data image 1
	# Return    : gif file name
	###########################################################################
	"""
	png_file=os.path.relpath(name+".png")
	brain_file=os.path.relpath('brain_delete.nii.gz')

	execute_command_or_else_stop('fslmaths \
		'+img+' \
		-mul \
		'+overlay+' \
		'+brain_file+' \
		-odt float')

	val=execute_command_or_else_stop('fslstats '+brain_file+' -p 0','ON')

	execute_command_or_else_stop('fslmaths \
		'+brain_file+' \
		-sub '+val+' \
		-mas '+overlay+' \
		'+brain_file+' \
		-odt float')
	val=execute_command_or_else_stop('fslstats '+brain_file+' -P 95','ON')

	execute_command_or_else_stop('overlay \
		0 0 \
		'+img+' \
		-a '+brain_file+' \
		1 '+val+' \
		'+name+'_delete')

	copy_geometry(img,name+'_delete')

	execute_command_or_else_stop('slicer '+name+'_delete \
		-s 1 \
		-x 0.4 a_delete.png -x 0.5 b_delete.png -x 0.6 c_delete.png \
		-y 0.4 d_delete.png -y 0.5 e_delete.png -y 0.6 f_delete.png \
		-z 0.4 g_delete.png -z 0.5 h_delete.png -z 0.6 i_delete.png')

	execute_command_or_else_stop('pngappend \
		a_delete.png + b_delete.png + c_delete.png + \
		d_delete.png + e_delete.png + f_delete.png + \
		g_delete.png + h_delete.png + i_delete.png \
		'+png_file)

	remove_files("*_delete*")

	return png_file
# End of generate_seg_png function


# Begin of generate_gif function
def generate_gif(name,img,overlay1='',overlay2='',ext='.gif'):
	"""
	###########################################################################
	# def generate_gif(name,img,overlay1,overlay2,ext)
	# Function  : We do a gif with img as background and overlay1 and overlay2 as color content
	# Param     : name, file name
	# Param	    : img, background image
	# Param	    : overlay1, data image 1
	# Param	    : overlay2, data image 2
	# Return    : gif file name
	###########################################################################
	"""
	gif_file=os.path.relpath(name+ext)

	slicer_file=''
	add=''
	if overlay2!='':
		add=overlay2+' 0.001 1 '

	if overlay1!='':
		execute_command_or_else_stop('overlay \
			0 0 \
			'+img+' \
			-a '+overlay1+' \
			0.001 1 \
			'+add+' \
			'+name+'_delete')
		copy_geometry(img,name+'_delete')
		slicer_file=name+'_delete'
	else:
		slicer_file=img

	execute_command_or_else_stop('slicer '+slicer_file+' \
		-s 1 \
		-x 0.4 a_delete.png -x 0.5 b_delete.png -x 0.6 c_delete.png \
		-y 0.4 d_delete.png -y 0.5 e_delete.png -y 0.6 f_delete.png \
		-z 0.4 g_delete.png -z 0.5 h_delete.png -z 0.6 i_delete.png')

	execute_command_or_else_stop('pngappend \
		a_delete.png + b_delete.png + c_delete.png + \
		d_delete.png + e_delete.png + f_delete.png + \
		g_delete.png + h_delete.png + i_delete.png \
		'+gif_file)

	remove_files("*_delete*")

	return gif_file
# End of generate_gif function


# Begin of download_from_web function
def download_from_web(url,localfile):
	"""
	###########################################################################
	# def download_from_web(url)
	# Function  : Copy the contents of a file from a given URL to a local file
	# Param     : url, url from where we want to download the file
	# Param	    : localfile, path to the localfile where we want to save the file
	# Return    :
	###########################################################################
	"""
	import urllib
	webFile = urllib.urlopen(url)
	localFile = open(localfile,'w')
	localFile.write(webFile.read())
	webFile.close()
	localFile.close()

	return
# End of download_from_web function


# Begin of generate_report function
def generate_report(patient,results,command):
	"""
	###########################################################################
	# def generate_report(patient,results,command)
	# Function  : Generate the final report with all the data
	# Param     : patient, descriptor patient
	# Param	    : results, numerical bsi and pbvc results
	# Param	    : command, executed command line
	# Return    :
	###########################################################################
	"""
	global html
	global B_INPUT_IMAGE
	global F_INPUT_IMAGE
	global B_MASK
	global F_MASK
	xor_file=os.path.abspath('xor.nii.gz')
	bsi_file=os.path.abspath('bsi.nii.gz')
	negatives_file=os.path.abspath('negatives.nii.gz')
	positives_file=os.path.abspath('positives.nii.gz')
	segmentation_file=os.path.relpath(patient+'_segmentation.gif')
	registration_file=os.path.relpath(patient+'_registration.gif')
	seg1_file=os.path.relpath('a_s1_segmentation.nii.gz')
	seg2_file=os.path.relpath('b_s2_segmentation.nii.gz')

	# Binarize probabilistic mask for calculating volumes
	B_MASK_bin=binarize_mask(B_MASK)
	F_MASK_bin=binarize_mask(F_MASK)

	# We calculate the volumes
	v1=float(execute_command_or_else_stop('seg_stats \
		'+B_MASK_bin+' \
		-V','ON'))
	v2=float(execute_command_or_else_stop('seg_stats \
		'+F_MASK_bin+' \
		-V','ON'))

	# Generating segmentation overlayed images
	seg_1=generate_seg_png(patient+'_seg1',B_INPUT_IMAGE,B_MASK)
	seg_2=generate_seg_png(patient+'_seg2',F_INPUT_IMAGE,F_MASK)

	# Generating segmentation comparation result image
	execute_command_or_else_stop('seg_maths \
		'+B_INPUT_IMAGE+' \
		-mul \
		'+B_MASK_bin+' \
		-odt float \
		'+seg1_file)

	execute_command_or_else_stop('seg_maths \
		'+F_INPUT_IMAGE+' \
		-mul \
		'+F_MASK_bin+' \
		-odt float \
		'+seg2_file)

	segmentation_1=generate_gif(patient+'_s1_segmentation',seg1_file)
	segmentation_2=generate_gif(patient+'_s2_segmentation',seg2_file)
	execute_command_or_else_stop('whirlgif \
		-o '+segmentation_file+' \
		-time 100 \
		-loop 0 \
		'+segmentation_1+' \
		'+segmentation_2)
	remove_files("*_s1_segmentation*")
	remove_files("*_s2_segmentation*")

	# Generating registration comparation result image
	register_1=generate_gif(patient+'_r1_register',B_INPUT_IMAGE)
	register_2=generate_gif(patient+'_r2_register',F_INPUT_IMAGE)
	execute_command_or_else_stop('whirlgif \
		-o '+registration_file+' \
		-time 100 \
		-loop 0 \
		'+register_1+' \
		'+register_2)
	remove_files("*_r1_register*")
	remove_files("*_r2_register*")

	# Generating XOR overlayed image
	xor_file=generate_seg_png(patient+'_xor',B_INPUT_IMAGE,xor_file)

	# We separate atrophy and growth in two files
	execute_command_or_else_stop('seg_maths \
		'+bsi_file+' \
		-uthr 0 \
		-abs \
		'+negatives_file)
	execute_command_or_else_stop('seg_maths \
		'+bsi_file+' \
		-thr 0 \
		'+positives_file)

	# We compute atrophy and growth separetely
	# Atrophy is the positive file, because BSI's algorithm measures the intensity's difference between baseline and follow-up. Roughly: BSI=baselineValue-repeatValue.
	# An intensity decrease between both time points is atrophy and the result at the end of BSI will be positive
	# An intensity gain between both time points is grotwh and the result at the end of BSI will be negative
	growth=float(execute_command_or_else_stop('seg_stats \
		'+negatives_file+' \
		-V','ON'))
	growth= 100 * growth / v1

	atrophy=float(execute_command_or_else_stop('seg_stats \
		'+positives_file+' \
		-V','ON'))
	atrophy=-100 * atrophy / v1

	write_results('BSI='+str(results[0])+' ml\n')
	write_results('PBVC='+str(results[1])+' %\n')
	write_results('ATROPHY='+str(atrophy)+' %\n')
	write_results('GROWTH='+str(growth)+' %\n')
	write_results('VOLUME='+str(v1)+' mm^3\n')

	# Generating the atrophy result image
	bsi_file=generate_gif(patient+'_bsi',B_INPUT_IMAGE,negatives_file,positives_file,'.png')
	remove_files("*negatives*")
	remove_files("*positives*")

	html=html.replace('PATIENT',patient)
	html=html.replace('COMMAND_LINE',command)
	html=html.replace('VOLUME_1',"{:.0f}".format(v1))
	html=html.replace('VOLUME_2',"{:.0f}".format(v2))
	html=html.replace('FILE_B_MASK',seg_1)
	html=html.replace('FILE_F_MASK',seg_2)
	html=html.replace('B_MASK',os.path.basename(B_MASK))
	html=html.replace('F_MASK',os.path.basename(F_MASK))
	html=html.replace('FILE_SEGMENTATION_COMPARATION',segmentation_file)
	html=html.replace('FILE_REGISTRATION_COMPARATION',registration_file)
	html=html.replace('FILE_XOR_REGION',xor_file)
	html=html.replace('FILE_BSI_RESULT',bsi_file)
	html=html.replace('BSI_VALUE',"{:.2f}".format(results[0]))
	html=html.replace('PBVC_VALUE',"{:.3f}".format(results[1]))
	html=html.replace('ATROPHY_VALUE',"{:.3f}".format(atrophy))
	html=html.replace('GROWTH_VALUE',"{:.3f}".format(growth))

	html_file=os.path.abspath('index.html')

	# Open a file
	fo = open(html_file, "wb")
	fo.write(html)

	# Close opend file
	fo.close()

	return
# End of generate_report function


# XML Definition
xml="""<?xml version="1.0" encoding="utf-8"?>
<executable>
   <category>Multiple Sclerosis Tools</category>
   <title>Atrophy calculator</title>
   <description><![CDATA[This script, provided within @NIFTK_PLATFORM@, is for atrophy measurement using Boundary Shift Integral (BSI).<br>
   <ul>
   <li><i>Input images</i>, select the two time point images, baseline and follow-up</li>
   <li><i>Mask images</i>, select the two time point brain mask images, baseline and follow-up, they could be binary or probabilistic files</li>
   <li><i>Output image</i> it correponds to the atrophy measured between two-time points</li>
   </ul>
   <br>
   <p><h2>Recomendations:</h2></p>
   <p>If we want to calculate the atrophy in a region like hippocampus, we must to specify the region using a ROI in each time point and use double window BSI.</p>
   ]]></description>
   <version>@NIFTK_VERSION_MAJOR@.@NIFTK_VERSION_MINOR@.@NIFTK_VERSION_PATCH@</version>
   <documentation-url>http://www.sciencedirect.com/science/article/pii/S1053811909013482</documentation-url>
   <license>BSD</license>
   <contributor>Ferran Prados (UCL)</contributor>
   <parameters advanced="false">
      <label>Mandatory arguments</label>
      <description>Mandatory arguments: input data, input brain masks and output filename</description>
      <image fileExtensions="nii,nii.gz,img">
          <name>inputImageName1</name>
          <longflag>in1</longflag>
	  <description>Input baseline image name</description>
	  <label>Baseline image</label>
	  <channel>input</channel>
      </image>
      <image fileExtensions="nii,nii.gz,img">
          <name>inputImageName2</name>
          <longflag>in2</longflag>
	  <description>Input follow-up image name</description>
	  <label>Follow-up image</label>
	  <channel>input</channel>
      </image>
       <image fileExtensions="nii,nii.gz,img">
          <name>inputMaskName1</name>
          <longflag>mask1</longflag>
	  <description>Input baseline brain mask</description>
	  <label>Baseline brain mask</label>
	  <channel>input</channel>
      </image>
      <image fileExtensions="nii,nii.gz,img">
          <name>inputMaskName2</name>
          <longflag>mask2</longflag>
	  <description>Input follow-up brain mask</description>
	  <label>Follow-up brain mask</label>
	  <channel>input</channel>
      </image>
      <image fileExtensions="nii,nii.gz,img">
          <name>outputImageName</name>
          <longflag>out</longflag>
	  <description>BSI output image name</description>
	  <label>BSI output image</label>
	  <default>bsi.nii.gz</default>
          <channel>output</channel>
      </image>
   </parameters>
   <parameters advanced="true">
	<label>BSI configuration</label>
	<description>Optional BSI method arguments</description>
	<string-enumeration>
		<name>bsiComputationMethod</name>
		<longflag>method</longflag>
		<description><![CDATA[Select a BSI method:
		      GBSI: computes BSI using generalized BSI by ...
		      KN-BSI: computes BSI using K-means BSI by Leung et al. Neuroimage 2010
		      PBSI: computes BSI using probabilistic BSI by Ledig et al. MICCAI 2012
		      PBSIg: computes BSI using probabilistic BSI with gamma=1 as in Ledig et al. MICCAI 2012
		]]></description>
		<label>BSI method</label>
		<default>gbsi</default>
		<element>gbsi</element>
		<element>knbsi</element>
		<element>pbsi</element>
		<element>pbsig</element>
	</string-enumeration>
	<string-enumeration>
		<name>bsiWindow</name>
		<longflag>window</longflag>
		<description><![CDATA[Select a window:
			Single: single window BSI, it computes atrophy between CSF-GM, Freeborough et al. 1997 TMI
			Double: double window BSI, it computes atrophy between CSF-GM and WM-GM as in Leung et al. Neuroimage 2010
		]]></description>
		<label>BSI window</label>
		<default>single</default>
		<element>single</element>
		<element>double</element>
	</string-enumeration>
    </parameters>
    <parameters advanced="true">
	<label>Optional extra arguments</label>
	<description>Optional extra arguments</description>
	<image fileExtensions="nii,nii.gz,img">
		<name>inputLesionName1</name>
		<longflag>lesion1</longflag>
		<description>Input baseline lesion mask</description>
		<label>Baseline lesion mask</label>
		<channel>input</channel>
	</image>
	<image fileExtensions="nii,nii.gz,img">
		<name>inputLesionName2</name>
		<longflag>lesion2</longflag>
		<description>Input follow-up lesion mask</description>
		<label>Follow-up lesion mask</label>
		<channel>input</channel>
	</image>
	<boolean>
		<name>sublesion</name>
		<longflag>sublesion</longflag>
		<description>Substract/remove lesions mask from the brain mask for BSI calculation</description>
		<label>Remove lesions</label>
	</boolean>
	<integer-enumeration>
		<name>dil_sub</name>
		<longflag>dil_sub</longflag>
		<description>Number of dilations for lesion masks, useful for lesion substraction, recommended value: 1</description>
		<label>Lesion subtraction dilations</label>
		<default>1</default>
		<element>1</element>
		<element>0</element>
		<element>2</element>
		<element>3</element>
		<element>4</element>
	</integer-enumeration>
	<boolean>
		<name>fill_lesion</name>
		<longflag>fill</longflag>
		<description>Activates filling lesions script Declan T. Chard et al. JMRI 2010</description>
		<label>Fill lesions</label>
	</boolean>
	<integer-enumeration>
		<name>dil_fill</name>
		<longflag>dil_fill</longflag>
		<description>Number of dilations for lesion masks, useful for lesion filling, recommended value: 0</description>
		<label>Lesion filling dilations</label>
		<default>0</default>
		<element>0</element>
		<element>1</element>
		<element>2</element>
		<element>3</element>
		<element>4</element>
	</integer-enumeration>
	<image fileExtensions="nii,nii.gz,img">
		<name>inputROIName1</name>
		<longflag>roi1</longflag>
		<description>Input baseline roi mask</description>
		<label>Baseline roi mask</label>
		<channel>input</channel>
	</image>
	<image fileExtensions="nii,nii.gz,img">
		<name>inputROIName2</name>
		<longflag>roi2</longflag>
		<description>Input follow-up roi mask</description>
		<label>Follow-up roi mask</label>
		<channel>input</channel>
	</image>
    	<image fileExtensions="nii,nii.gz,img">
		<name>outputXORImageName</name>
		<longflag>xor</longflag>
		<description>XOR output image name</description>
		<label>XOR output image</label>
		<default>xor.nii.gz</default>
		<channel>output</channel>
	</image>
	<integer-enumeration>
		<name>tkn</name>
		<longflag>tkn</longflag>
		<description>Number of classes for K-Means, recommended value: 3</description>
		<label>Number of tissues</label>
		<default>3</default>
		<element>3</element>
		<element>2</element>
	</integer-enumeration>
	<integer-enumeration>
		<name>Kmeansdilations</name>
		<longflag>dil_kmeans</longflag>
		<description>Number of classes dilations for the K-Means mask, recommended value: 3</description>
		<label>Number of tissues</label>
		<default>3</default>
		<element>3</element>
		<element>0</element>
		<element>1</element>
		<element>2</element>
		<element>4</element>
	</integer-enumeration>
	<boolean>
		<name>normalize</name>
		<longflag>norm</longflag>
		<description>Apply Boyes et al. Neuroimage 2008 bias field correction process using N3</description>
		<label>Bias field correction</label>
	</boolean>
	<boolean>
		<name>n4_bfc</name>
		<longflag>n4</longflag>
		<description>Apply Boyes et al. Neuroimage 2008 bias field correction using N4 instead than N3</description>
		<label>Bias field correction (N4)</label>
	</boolean>
	<image fileExtensions="nii,nii.gz,img">
		<name>inputAtlasMask</name>
		<longflag>atlas_mask</longflag>
		<description>Input atlas mask</description>
		<label>Input atlas mask</label>
		<channel>input</channel>
	</image>
	<image fileExtensions="nii,nii.gz,img">
		<name>inputAtlasHead</name>
		<longflag>atlas_head</longflag>
		<description>Input atlas head</description>
		<label>Input atlas head</label>
		<channel>input</channel>
	</image>
	<directory>
		<name>outputdir</name>
		<longflag>output_dir</longflag>
		<description>Select the output directory</description>
		<label>Output directory</label>
	</directory>
	<boolean>
		<name>isoFiles</name>
		<longflag>iso</longflag>
		<description>Transform all input images to 1mm isometric voxels</description>
		<label>1mm ISO voxels</label>
	</boolean>
	<boolean>
		<name>debugMode</name>
		<longflag>debug</longflag>
		<description>Debug mode doesn't delete temporary intermediate images</description>
		<label>Debug mode</label>
	</boolean>
	<boolean>
		<name>notWebBrowser</name>
		<longflag>not_web</longflag>
		<description>At the end, don't open web browser showing results</description>
		<label>Not open web browser</label>
	</boolean>
    </parameters>
</executable>"""

# Help usage message definition
help="""
This script is for atrophy calculation using Boundary Shift Integral (BSI).

Usage: niftkAtrophyCalculator.py -in baseline_input_file follow_up_input_file -mask baseline_mask_file follow_up_mask_file -out output_file

Mandatory Arguments:

  -in <f1> <f2>   	: are the two input files (f1 baseline and f2 follow-up)
  -out <filename>	: is the output file with the computed BSI
  -mask <f1> <f2> 	: are the two input brain masks (f1 baseline and f2 follow-up)

Optional Arguments BSI computation:

  -gbsi			: computes BSI using generalized BSI by ... [DEFAULT]
  -knbsi		: computes BSI using K-means BSI by Leung et al. Neuroimage 2010
  -pbsi			: computes BSI using probabilistic BSI by Ledig et al. MICCAI 2012
  -pbsig		: computes BSI using probabilistic BSI with gamma=1 as in Ledig et al. MICCAI 2012
  -sw			: single window BSI, CSF-GM, Freeborough et al. 1997 TMI [DEFAULT]
  -dw			: applies double window BSI, it computes BSI between CSF-GM and WM-GM as in Leung et al. Neuroimage 2010

Optional Arguments:

  -t2			: computes BSI taking into account that we are using T2 images as input data
  -lesion <f1> <f2>	: are the two input lesion masks (f1 baseline and f2 follow-up)
  -dil_sub		: number of dilations for lesion masks, useful for lesion substraction. [0-4, by default 1]
  -sublesion        	: substract lesions mask from the brain mask for BSI calculation
  -fill			: activates filling lesions script Declan T. Chard et al. JMRI 2010
  -dil_fill		: number of dilations for lesion masks during the lesion filling. [0-4, by default 0]
  -roi <f1> <f2>	: are two extra ROI masks for BSI calculation over a specific region like hippocampus (f1 baseline and f2 follow-up)
  -xor <filename>   	: outputs file with the XOR region where BSI integral is calculated
  -n3			: apply Boyes et al. Neuroimage 2008 bias field correction method process using N3
  -n4			: apply Boyes et al. Neuroimage 2008 bias field correction method process using N4, mutual exclusive with -n3 argument
  -atlas_mask <filename>: is the mask atlas file (default: /usr/share/fsl/data/standard/MNI152_T1_2mm_brain_mask_dil.nii.gz)
  -atlas_head <filename>: is to the atlas data file (ex: /usr/share/fsl/data/standard/MNI152_T1_2mm.nii.gz)
  -tkn <n>      	: number of classes for K-Means [2 or 3, by default 3]
  -dil_kmeans		: number of dilations for K-Means [0-4, by default 3]
  -iso          	: transform input images to 1mm isometric voxels
  -debug		: debug mode doesn't delete temporary intermediate images
  -output_dir <path>	: specify the output dir name
  -not_web		: don't open web browser showing results

Recomendations:

	Check that it exists an important overlapping between mask, headmask, head and input file.
"""


# Main program start

# We register cleanup function as a function to be executed at termination
atexit.register(cleanup)
os.environ['FSLOUTPUTTYPE']='NIFTI_GZ'
# We get the arguments
arg=len(sys.argv)
argv=sys.argv
orientation=''
norm=False
n4_bfc=''
fill_lesions=False
sublesion=False
single_window=True
tkn=3
dil_sub=1
dil_fill=0
dil_kmeans=3
debug_mode=False
iso=False
output_dir_name=''
open_web_browser=True
bsi_method=1
B_INPUT_IMAGE=''
F_INPUT_IMAGE=''
OUTPUT_IMAGE=''
B_MASK=''
F_MASK=''
B_LESION_MASK=''
F_LESION_MASK=''
B_ROI_MASK=''
F_ROI_MASK=''
ATLAS_MASK_IMAGE=os.path.join(os.getenv('FSLDIR','/usr/share/fsl'), 'data', 'standard', 'MNI152_T1_2mm_brain_mask_dil.nii.gz') # MNI space
ATLAS_HEAD_IMAGE=os.path.join(os.getenv('FSLDIR','/usr/share/fsl'), 'data', 'standard', 'MNI152_T1_2mm.nii.gz') # MNI space
XOR_IMAGE=''
B_BSI_MASK=''
F_BSI_MASK=''
B_BSI_ROI_MASK=''
F_BSI_ROI_MASK=''
t2_mode=False

# If no arguments, we print usage message
if arg < 9:
	i=1
	while i < arg:
		# Clean unnecessary whitespaces
		argv[i]=argv[i].strip()
		if argv[i].upper() in ['--XML','-XML']:
			usage(9,0)
		i=i+1
	# end while
	usage(help)
# End if, few arguments

i=1
# Parse remaining command line options
while i < arg:
    # Clean unnecessary whitespaces
    argv[i]=argv[i].strip()
    if argv[i].upper() in ['--XML','-XML']:
        usage(xml,0)

    elif argv[i] in ['--H','--HELP','-H','-HELP']:
        usage(text)

    elif argv[i].upper() in ['--IN','-IN']:
        B_INPUT_IMAGE=argv[i+1]
        F_INPUT_IMAGE=argv[i+2]
        i=i+2

    elif argv[i].upper() in ['--IN1','-IN1']:
        B_INPUT_IMAGE=argv[i+1]
        i=i+1

    elif argv[i].upper() in ['--IN2','-IN2']:
        F_INPUT_IMAGE=argv[i+1]
        i=i+1

    elif argv[i].upper() in ['--MASK','-MASK']:
        B_MASK=argv[i+1]
        F_MASK=argv[i+2]
        i=i+2

    elif argv[i].upper() in ['--MASK1','-MASK1']:
        B_MASK=argv[i+1]
        i=i+1

    elif argv[i].upper() in ['--MASK2','-MASK2']:
        F_MASK=argv[i+1]
        i=i+1

    elif argv[i].upper() in ['--LESION','-LESION']:
        B_LESION_MASK=argv[i+1]
        F_LESION_MASK=argv[i+2]
        i=i+2

    elif argv[i].upper() in ['--LESION1','-LESION1']:
        B_LESION_MASK=argv[i+1]
        i=i+1

    elif argv[i].upper() in ['--LESION2','-LESION2']:
        F_LESION_MASK=argv[i+1]
        i=i+1

    elif argv[i].upper() in ['--ROI','-ROI']:
        B_ROI_MASK=argv[i+1]
        F_ROI_MASK=argv[i+2]
        i=i+2

    elif argv[i].upper() in ['--ROI1','-ROI1']:
        B_ROI_MASK=argv[i+1]
        i=i+1

    elif argv[i].upper() in ['--ROI2','-ROI2']:
        F_ROI_MASK=argv[i+1]
        i=i+1

    elif argv[i].upper() in ['--OUT','-OUT']:
        OUTPUT_IMAGE=argv[i+1]
        i=i+1

    elif argv[i].upper() in ['--XOR','-XOR']:
        XOR_IMAGE=argv[i+1]
        i=i+1

    elif argv[i].upper() in ['--GBSI','-GBSI']:
        bsi_method=1

    elif argv[i].upper() in ['--KNBSI','-KNBSI']:
        bsi_method=0

    elif argv[i].upper() in ['--PBSI','-PBSI']:
        bsi_method=2

    elif argv[i].upper() in ['--PBSIG','-PBSIG']:
        bsi_method=3

    elif argv[i].upper() in ['--METHOD','-METHOD']:
        if argv[i+1].upper() in ['GBSI']:
            bsi_method=1

        elif argv[i+1].upper() in ['KNBSI']:
            bsi_method=0

        elif argv[i+1].upper() in ['PBSI']:
            bsi_method=2

        elif argv[i+1].upper() in ['PBSIG']:
            bsi_method=3

        else:
            print "\n\nERROR: BSI method ",argv[i]," ",argv[i+1]," not recognised\n\n"
            usage(help)

        i=i+1

    elif argv[i].upper() in ['--SW','-SW']:
        single_window=True

    elif argv[i].upper() in ['--DW','-DW']:
        single_window=False

    elif argv[i].upper() in ['--WINDOW','-window']:
        if argv[i+1].upper() in ['SW','SINGLE']:
            single_window=True

        elif argv[i+1].upper() in ['DW','DOUBLE']:
            single_window=False

        else:
            print "\n\nERROR: BSI window ",argv[i]," ",argv[i+1]," not recognised\n\n"
            usage(help)
        i=i+1

    elif argv[i].upper() in ['--FILL','-FILL']:
        fill_lesions=True

    elif argv[i].upper() in ['--SUBLESION','-SUBLESION']:
        sublesion=True

    elif argv[i].upper() in ['--N3','-N3','-NORM','--NORM']:
        norm=True

    elif argv[i].upper() in ['--N4','-N4']:
        n4_bfc='-N4'
        norm=True

    # We keep for compatibility reasons with old versions
    elif argv[i].upper() in ['--ORIENT','-ORIENT']:
        if argv[i+1].upper() in ['A']:
            orientation="a"

        elif argv[i+1].upper() in ['C']:
            orientation="c"

        elif argv[i+1].upper() in ['S']:
            orientation="s"

        i=i+1

    elif argv[i].upper() in ['--ATLAS_MASK','-ATLAS_MASK']:
        ATLAS_MASK_IMAGE=argv[i+1]
        i=i+1

    elif argv[i].upper() in ['--ATLAS_HEAD','-ATLAS_HEAD']:
        ATLAS_HEAD_IMAGE=argv[i+1]
        i=i+1

    elif argv[i].upper() in ['--TKN','-TKN']:
        if int(argv[i+1]) < 2 or int(argv[i+1]) > 3:
            print "\n\nERROR: number of classes ",argv[i]," ",argv[i+1]," incorrect, you can only select 2 or 3\n\n"
            usage(help)
        else:
            tkn=int(argv[i+1])

        i=i+1

    elif argv[i].upper() in ['--DIL_SUB','-DIL_SUB']:
        if int(argv[i+1]) < 0 or int(argv[i+1]) > 4:
            print "\n\nERROR: The number of dilation for lesion mask substraction is wrong ",argv[i]," ",argv[i+1],", it has to be between 0 and 4\n\n"
            usage(help)
        else:
            dil_sub=int(argv[i+1])

        i=i+1

    elif argv[i].upper() in ['--DIL_KMEANS','-DIL_KMEANS']:
        if int(argv[i+1]) < 0 or int(argv[i+1]) > 4:
            print "\n\nERROR: The number of dilation for kmeans is wrong ",argv[i]," ",argv[i+1],", it has to be between 0 and 4\n\n"
            usage(help)
        else:
            dil_kmeans=int(argv[i+1])

        i=i+1

    elif argv[i].upper() in ['--DIL_FILL','-DIL_FILL']:
        if int(argv[i+1]) < 0 or int(argv[i+1]) > 4:
            print "\n\nERROR: The number of dilation for lesion filling is wrong ",argv[i]," ",argv[i+1],", it has to be between 0 and 4\n\n"
            usage(help)
        else:
            dil_fill=int(argv[i+1])

        i=i+1

    elif argv[i].upper() in ['--ISO','-ISO']:
        iso=True

    elif argv[i].upper() in ['--T2','-T2']:
        t2_mode=True

    elif argv[i].upper() in ['--DEBUG','-DEBUG']:
        debug_mode=True

    elif argv[i].upper() in ['--NOT_WEB','-NOT_WEB']:
        open_web_browser=False

    elif argv[i].upper() in ['--OUTPUT_DIR','-OUTPUT_DIR']:
        output_dir_name=argv[i+1]
        i=i+1

    else:
        print "\n\nERROR: option ",argv[i]," not recognised\n\n"
        usage(help)

    i=i+1
# end while

# We put all path in a normalized absolutized version of the pathname
B_INPUT_IMAGE=os.path.abspath(B_INPUT_IMAGE)
F_INPUT_IMAGE=os.path.abspath(F_INPUT_IMAGE)
OUTPUT_IMAGE=os.path.abspath(OUTPUT_IMAGE)
B_MASK=os.path.abspath(B_MASK)
F_MASK=os.path.abspath(F_MASK)
if len(B_LESION_MASK)>0 and len(F_LESION_MASK)>0:
	B_LESION_MASK=os.path.abspath(B_LESION_MASK)
	F_LESION_MASK=os.path.abspath(F_LESION_MASK)
if len(B_ROI_MASK)>0 and len(F_ROI_MASK)>0:
	B_ROI_MASK=os.path.abspath(B_ROI_MASK)
	F_ROI_MASK=os.path.abspath(F_ROI_MASK)
if len(ATLAS_MASK_IMAGE)>0 and len(ATLAS_HEAD_IMAGE)>0:
	ATLAS_MASK_IMAGE=os.path.abspath(ATLAS_MASK_IMAGE)
	ATLAS_HEAD_IMAGE=os.path.abspath(ATLAS_HEAD_IMAGE)
if len(XOR_IMAGE)>0:
	XOR_IMAGE=os.path.abspath(XOR_IMAGE)

# Check if all needed files exist
check_file_exists(B_INPUT_IMAGE)
check_file_exists(F_INPUT_IMAGE)
check_file_exists(B_MASK)
check_file_exists(F_MASK)
copy_geometry(B_INPUT_IMAGE,B_MASK)
copy_geometry(F_INPUT_IMAGE,F_MASK)

# We have an output file name
if OUTPUT_IMAGE == '' or os.path.isdir(OUTPUT_IMAGE):
	progress_xml(0.01,"Failed, specify an output filename is needed.")
	exit_program(OUTPUT_IMAGE+" is not a file, select a file")

if len(XOR_IMAGE)>0 and os.path.isdir(XOR_IMAGE):
	progress_xml(0.02,"Failed, specify an xor output filename is needed.")
	exit_program(XOR_IMAGE+" is not a file, select a file")

# Verify bias field correction parameters
if norm:
	progress_xml(0.03,"Checking files needed for intensity bias field correction.")
	check_program_exists('niftkBiasFieldCorrection.py')

# Verify lesion parameters
if fill_lesions:
	check_program_exists('seg_FillLesions')
	check_file_exists(B_LESION_MASK)
	check_file_exists(F_LESION_MASK)
	copy_geometry(B_INPUT_IMAGE,B_LESION_MASK)
	copy_geometry(F_INPUT_IMAGE,F_LESION_MASK)


# Checking Nifty Tools
check_program_exists('niftkMTPDbc')
check_program_exists('reg_aladin')
check_program_exists('reg_resample')
check_program_exists('reg_tools')
check_program_exists('seg_maths')
check_program_exists('seg_stats')

# Checking FSL Tools
check_program_exists('fslcpgeom')
check_program_exists('fslmaths')
check_program_exists('flirt')
check_program_exists('overlay')
check_program_exists('whirlgif')
check_program_exists('slicer')
check_program_exists('pngappend')

# Checking needed BSI program
if single_window:
	check_program_exists('niftkKMeansWindowWithLinearRegressionNormalisationBSI')
else:
	check_program_exists('niftkKNDoubleWindowBSI')
	check_file_exists(B_ROI_MASK)
	check_file_exists(F_ROI_MASK)
	copy_geometry(B_INPUT_IMAGE,B_ROI_MASK)
	copy_geometry(F_INPUT_IMAGE,F_ROI_MASK)

# We get the filename and extensions
bname = get_file_name(B_INPUT_IMAGE)
fname = get_file_name(F_INPUT_IMAGE)

# Create the work temp dir
current_dir=os.getcwd()
if output_dir_name!='':
	dir_output=os.path.join(current_dir,output_dir_name)
else:
	dir_output=os.path.join(current_dir,bname+"_to_"+fname+"-"+dir_output)

if not os.path.isdir(dir_output):
	os.makedirs(dir_output)

# Go to the output directory
os.chdir(dir_output)

B_INPUT_IMAGE=change_format(B_INPUT_IMAGE,dir_output)
F_INPUT_IMAGE=change_format(F_INPUT_IMAGE,dir_output)
B_MASK=change_format(B_MASK,dir_output)
F_MASK=change_format(F_MASK,dir_output)
if len(B_LESION_MASK)>0 and len(F_LESION_MASK)>0:
	B_LESION_MASK=change_format(B_LESION_MASK,dir_output)
	F_LESION_MASK=change_format(F_LESION_MASK,dir_output)
if len(B_ROI_MASK)>0 and len(F_ROI_MASK)>0:
	B_ROI_MASK=change_format(B_ROI_MASK,dir_output)
	F_ROI_MASK=change_format(F_ROI_MASK,dir_output)
if len(ATLAS_MASK_IMAGE)>0 and len(ATLAS_HEAD_IMAGE)>0:
	ATLAS_MASK_IMAGE=change_format(ATLAS_MASK_IMAGE,dir_output)
	ATLAS_HEAD_IMAGE=change_format(ATLAS_HEAD_IMAGE,dir_output)


###################################################
# Start process
###################################################
# Convert all the files to 1mm ISO voxel if it is needed
if iso:
	progress_xml(0.1,"Passing to ISO.")
	B_INPUT_IMAGE=pass_to_ISO(B_INPUT_IMAGE)
	F_INPUT_IMAGE=pass_to_ISO(F_INPUT_IMAGE)
	B_MASK=pass_to_ISO(B_MASK)
	F_MASK=pass_to_ISO(F_MASK)
	if B_ROI_MASK!='' or F_ROI_MASK!='':
		B_ROI_MASK=pass_to_ISO(B_ROI_MASK)
		F_ROI_MASK=pass_to_ISO(F_ROI_MASK)
	if fill_lesions or sublesion:
		B_LESION_MASK=pass_to_ISO(B_LESION_MASK)
		F_LESION_MASK=pass_to_ISO(F_LESION_MASK)

	progress_xml(0.12,"Pass to ISO finished.")

# Applying filling lesions script
if fill_lesions:
	progress_xml(0.13,"Filling lesions.")
	B_INPUT_IMAGE=filling_lesions(B_INPUT_IMAGE,B_MASK,B_LESION_MASK,dil_fill)
	F_INPUT_IMAGE=filling_lesions(F_INPUT_IMAGE,F_MASK,F_LESION_MASK,dil_fill)
	progress_xml(0.15,"Filling lesions finished.")

# Normalize intensity for each image Boyes et al.
if norm:
	progress_xml(0.16,"Normalization - baseline image")
	B_INPUT_IMAGE=bias_field_correction(B_INPUT_IMAGE,n4_bfc)
	progress_xml(0.20,"Normalization - follow up image")
	F_INPUT_IMAGE=bias_field_correction(F_INPUT_IMAGE,n4_bfc)
	progress_xml(0.25,"Normalization finished.")

# Brain extraction code here if we desire
# Brain extraction code here if we desire
# Brain extraction code here if we desire

# Register both images to half-way
progress_xml(0.50,"Image registration.")
probabilistic=(bsi_method==1 or bsi_method==3)
register_images(probabilistic)

# Register lesions to half-way
if sublesion:
	transform_lesions_to_half_way()
progress_xml(0.75,"Image registration finished.")

# Perform the differential bias correction on the two images
progress_xml(0.76,"Differential bias correction.")
bias_correction()
progress_xml(0.80,"Differential bias correction finished.")

# Calculate the mask with the tissue to be removed or not taken into account
if sublesion:
	tissue_to_remove_file=calculate_tissue_to_remove(dil_sub)
	B_BSI_MASK=remove_tissue_from_image(B_MASK,tissue_to_remove_file)
	F_BSI_MASK=remove_tissue_from_image(F_MASK,tissue_to_remove_file)
	if B_ROI_MASK!='' or F_ROI_MASK!='':
		B_BSI_ROI_MASK=remove_tissue_from_image(B_ROI_MASK,tissue_to_remove_file)
		F_BSI_ROI_MASK=remove_tissue_from_image(F_ROI_MASK,tissue_to_remove_file)
else:
	tissue_to_remove_file='dummy'
	B_BSI_MASK=B_MASK
	F_BSI_MASK=F_MASK
	B_BSI_ROI_MASK=B_ROI_MASK
	F_BSI_ROI_MASK=F_ROI_MASK

# BSI calculation
progress_xml(0.81,"BSI calculation.")
if single_window:
	results=calculate_sw_BSI(bsi_method,tkn,tissue_to_remove_file,dil_kmeans,t2_mode)
else:
	results=calculate_dw_BSI(bsi_method,tkn,tissue_to_remove_file,dil_kmeans,t2_mode)

progress_xml(0.90,"BSI calculation finished. PBVC="+str(results[1]))

progress_xml(0.91,"Generating report.")
generate_report(bname,results,' '.join(argv))
progress_xml(0.97,"Report finished.")

# Copy data to working directory
progress_xml(0.98,"Copying results.")
bsi_file=os.path.abspath('bsi.nii.gz')
if not os.path.isfile(os.path.join(current_dir,OUTPUT_IMAGE)):
	copy_file_to_destination(bsi_file,os.path.join(current_dir,OUTPUT_IMAGE))
else:
	progress_xml(0.99,"Output file already exists, we don't copy it.")

if XOR_IMAGE!='':
	xor_file=os.path.abspath('xor.nii.gz')
	if not os.path.isfile(os.path.join(current_dir,XOR_IMAGE)):
		copy_file_to_destination(xor_file,os.path.join(current_dir,XOR_IMAGE))
	else:
		progress_xml(0.99,"XOR output file already exists, we don't copy it.")

# Go back to the corresponding directory
os.chdir(current_dir)

progress_xml(1,"Finish")
close_progress_xml(OUTPUT_IMAGE)

# Show results in the web browser
if open_web_browser :
	new=2
	url = os.path.join(dir_output,"index.html")
	webbrowser.open(url,new=new)

# End of the main program
exit(0)
