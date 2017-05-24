"""Test seg_EM interface in nipype for niftyfit."""

from nipype.interfaces.niftyfit import FitAsl, FitDwi, FitQt1
import os


data_dir = '/Users/byvernault/home-local/softwares/niftyfit-release/source/\
niftyfit_data/'

dwi_nifti = os.path.join(data_dir, 'case01-dwi.nii.gz')
dwi_bval = os.path.join(data_dir, 'case01-bval')
dwi_bvec = os.path.join(data_dir, 'case01-bvec')
asl_file = os.path.join(data_dir, 'case01-asl.nii.gz')
seg_file = os.path.join(data_dir, 'case01-seg.nii.gz')
qt1_file = os.path.join(data_dir, 'case01-qt1_sr.nii.gz')

test_node = FitDwi(dti_flag=True)
test_node.base_dir = '/Users/byvernault/data/test_dwi'
test_node.inputs.source_file = dwi_nifti
test_node.inputs.bval_file = dwi_bval
test_node.inputs.bvec_file = dwi_bvec

print test_node.cmdline

result = test_node.run()

print result.outputs

# test_node = FitAsl()
# test_node.inputs.source_file = asl_file
# test_node.inputs.seg = seg_file
# test_node.inputs.pcasl = True
# test_node.inputs.PLD = 1800
# test_node.inputs.LDD = 1800
# test_node.inputs.eff = 0.614
# test_node.inputs.mul = 0.1

# print test_node.cmdline

# result = test_node.run()

# print result.outputs

# test_node = FitQt1(IR=True)
# test_node.inputs.source_file = qt1_file
# test_node.inputs.TIs = [1, 2, 5]

# print test_node.cmdline

# result = test_node.run()

# print result.outputs
