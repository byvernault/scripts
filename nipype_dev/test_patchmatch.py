"""Test MTPDBiasCorrection interface in nitfk."""
import os

from nipype.interfaces.niftyseg import PatchMatch, STEPS, CalcTopNCC

directory = os.getcwd()


# node = PatchMatch()
node = CalcTopNCC()

test_image = '/Users/byvernault/data/run_niftipipe/ADNI/01751-003-1.nii.gz'
node.inputs.in_file = test_image
node.inputs.num_templates = 2
node.inputs.in_templates = [test_image, test_image]
node.inputs.top_templates = 1
# node.inputs.mask_file = 2
# patchmatch.inputs.mask_file = test_image
# patchmatch.inputs.database_file = test_image
# patchmatch.inputs.out_file = '/Users/byvernault/test.nii.gz'

print node.cmdline
# result = node.run()

# print result.outputs.out_file
