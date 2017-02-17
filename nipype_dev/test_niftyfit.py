"""Test seg_EM interface in nipype for niftyfit."""

# from nipype.interfaces.niftyfit.dwi import FitDwi
#
# dwi_nifti = '/Users/byvernault/Downloads/scans/0016_ep2d_diff_MDDW_p2FAD_2.5mm_\
# iso/NIFTI/aaco016_20110505-0016-ep2d_diff_MDDW_p2FAD_2.5mm_iso-diffusion_4D.\
# nii.gz'
# dwi_bval = '/Users/byvernault/Downloads/scans/0016_ep2d_diff_MDDW_p2FAD_2.5mm_\
# iso/BVAL/aaco016_20110505_index.bval'
# dwi_bvec = '/Users/byvernault/Downloads/scans/0016_ep2d_diff_MDDW_p2FAD_2.5mm_\
# iso/BVEC/aaco016_20110505_index.bvec'
#
# test_node = FitDwi()
# test_node.inputs.source_file = dwi_nifti
# test_node.inputs.bval_file = dwi_bval
# test_node.inputs.bvec_file = dwi_bvec
# test_node.inputs.dti_flag = True
# test_node.inputs.rgbmap_file = 'rgb_map.nii.gz'
#
# print test_node.cmdline
# result = test_node.run()
#
# print result.outputs

from nipype.interfaces.niftyfit.asl import FitAsl

source_file = '/Users/byvernault/Downloads/20140701_084347ASLPERF09NXRZ\
s015a001.nii'

test_node = FitAsl()
test_node.inputs.source_file = source_file
test_node.inputs.pcasl = True
test_node.inputs.PLD = 1800
test_node.inputs.LDD = 1800
test_node.inputs.eff = 0.614
test_node.inputs.mul = 0.1

print test_node.cmdline

result = test_node.run()

print result.outputs
