"""Test seg_EM interface in nipype for niftyseg."""

from nipype.interfaces.niftyfit.dwi import FitDwi

dwi_nifti = '/Users/byvernault/Downloads/scans/0016_ep2d_diff_MDDW_p2FAD_2.5mm_\
iso/NIFTI/aaco016_20110505-0016-ep2d_diff_MDDW_p2FAD_2.5mm_iso-diffusion_4D.\
nii.gz'
dwi_bval = '/Users/byvernault/Downloads/scans/0016_ep2d_diff_MDDW_p2FAD_2.5mm_\
iso/BVAL/aaco016_20110505_index.bval'
dwi_bvec = '/Users/byvernault/Downloads/scans/0016_ep2d_diff_MDDW_p2FAD_2.5mm_\
iso/BVEC/aaco016_20110505_index.bvec'

test_node = FitDwi()
test_node.inputs.source_file = dwi_nifti
test_node.inputs.bval_file = dwi_bval
test_node.inputs.bvec_file = dwi_bvec
test_node.inputs.dti_flag = True
test_node.inputs.rgbmap_file = 'rgb_map.nii.gz'

print test_node.cmdline
result = test_node.run()

print result.outputs
