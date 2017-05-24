# Import the nipype module
# import nipype

# # Optional: Use the following lines to increase verbosity of output
# nipype.config.set('logging', 'workflow_level',  'CRITICAL')
# nipype.config.set('logging', 'interface_level', 'CRITICAL')
# nipype.logging.update_logging(nipype.config)

# # Run the test: Increase verbosity parameter for more info
# nipype.test(verbose=0)


import nipype.interfaces.niftyseg as niftyseg
import nipype.interfaces.niftyreg as niftyreg


# test_node = niftyreg.RegAladin()
# test_node.base_dir = '/Users/byvernault/data/test_reg'
# test_node.inputs.flo_file = '/Users/byvernault/data/jobsdir/test_vessel2gad/\
# vessels2gad_registration/extract_slices/mapflow/_extract_slices0/20151203_1439\
# 5801041532ChannelRoutinthoks011a1001_extracted.nii.gz'
# test_node.inputs.ref_file = '/Users/byvernault/data/jobsdir/test_vessel2gad/\
# INPUT/gad_0/NIFTI/20151203_14395801041532ChannelRoutinthoks010a1001.nii.gz'

# test_node.inputs.nosym_flag = True
# test_node.inputs.maxit_val = 1
# test_node.inputs.ln_val = 1
# test_node.inputs.lp_val = 1

# print test_node.cmdline

# result = test_node.run()

# print result.outputs


test_node = niftyreg.RegAverage()
test_node.base_dir = '/Users/byvernault/data/test_avg'
# test_node.inputs.avg_files = ['/Users/byvernault/nipype-dti-examples/test_noddi/noddi_processing/tensor_proc/eddy_ave_ims_b0/dwi_0000_merged_mean.nii.gz']
test_node.inputs.avg_files = [
'/Users/byvernault/nipype-dti-examples/test_noddi/noddi_processing/tensor_proc/eddy_groupwise/lin_reg0/lin_reg/mapflow/_lin_reg0/dwi_0000_res.nii.gz',
'/Users/byvernault/nipype-dti-examples/test_noddi/noddi_processing/tensor_proc/eddy_groupwise/lin_reg0/lin_reg/mapflow/_lin_reg1/dwi_0009_res.nii.gz',
'/Users/byvernault/nipype-dti-examples/test_noddi/noddi_processing/tensor_proc/eddy_groupwise/lin_reg0/lin_reg/mapflow/_lin_reg2/dwi_0018_res.nii.gz',
'/Users/byvernault/nipype-dti-examples/test_noddi/noddi_processing/tensor_proc/eddy_groupwise/lin_reg0/lin_reg/mapflow/_lin_reg3/dwi_0027_res.nii.gz',
'/Users/byvernault/nipype-dti-examples/test_noddi/noddi_processing/tensor_proc/eddy_groupwise/lin_reg0/lin_reg/mapflow/_lin_reg4/dwi_0036_res.nii.gz',
'/Users/byvernault/nipype-dti-examples/test_noddi/noddi_processing/tensor_proc/eddy_groupwise/lin_reg0/lin_reg/mapflow/_lin_reg5/dwi_0045_res.nii.gz',
'/Users/byvernault/nipype-dti-examples/test_noddi/noddi_processing/tensor_proc/eddy_groupwise/lin_reg0/lin_reg/mapflow/_lin_reg6/dwi_0054_res.nii.gz',
'/Users/byvernault/nipype-dti-examples/test_noddi/noddi_processing/tensor_proc/eddy_groupwise/lin_reg0/lin_reg/mapflow/_lin_reg7/dwi_0063_res.nii.gz',
'/Users/byvernault/nipype-dti-examples/test_noddi/noddi_processing/tensor_proc/eddy_groupwise/lin_reg0/lin_reg/mapflow/_lin_reg8/dwi_0072_res.nii.gz',
'/Users/byvernault/nipype-dti-examples/test_noddi/noddi_processing/tensor_proc/eddy_groupwise/lin_reg0/lin_reg/mapflow/_lin_reg9/dwi_0081_res.nii.gz',
'/Users/byvernault/nipype-dti-examples/test_noddi/noddi_processing/tensor_proc/eddy_groupwise/lin_reg0/lin_reg/mapflow/_lin_reg10/dwi_0090_res.nii.gz',
'/Users/byvernault/nipype-dti-examples/test_noddi/noddi_processing/tensor_proc/eddy_groupwise/lin_reg0/lin_reg/mapflow/_lin_reg11/dwi_0099_res.nii.gz',]

print test_node.cmdline

result = test_node.run()

print result.outputs


# test_node = niftyseg.UnaryMaths()
# test_node.base_dir = '/Users/byvernault/data/test_reg'
# test_node.inputs.in_file = '/Users/byvernault/data/jobsdir/test_vessel2gad/\
# vessels2gad_registration/extract_slices/mapflow/_extract_slices0/20151203_1439\
# 5801041532ChannelRoutinthoks011a1001_extracted.nii.gz'
# # test_node.inputs.ref_file = '/Users/byvernault/data/jobsdir/test_vessel2gad/\
# # INPUT/gad_0/NIFTI/20151203_14395801041532ChannelRoutinthoks010a1001.nii.gz'

# test_node.inputs.operation = 'bin'

# print test_node.cmdline

# result = test_node.run()

# print result.outputs
