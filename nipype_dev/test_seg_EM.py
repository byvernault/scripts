"""Test seg_EM interface in nipype for niftyseg."""
import os
import argparse

from nipype.interfaces.niftyseg.em import EM

parser = argparse.ArgumentParser(description='test_seg_EM')
directory = os.getcwd()

parser.add_argument('-i', '--input',
                    dest='input',
                    metavar='input',
                    help='Input Image',
                    required=True)
parser.add_argument('-m', '--mask',
                    dest='mask',
                    metavar='mask',
                    help='Mask Image')
parser.add_argument('-o', '--output',
                    dest='output',
                    metavar='output',
                    help='Output Image')

args = parser.parse_args()

em_node = EM()
em_node.inputs.in_file = args.input
if args.mask:
    em_node.inputs.mask_file = args.mask
if args.output:
    em_node.inputs.out_file = args.output
# em_node.inputs.outlier_val = (4.0, 0.01)
# em_node.inputs.priors = (2, [args.input, args.input])
em_node.inputs.no_prior = 4
# em_node.inputs.max_iter = 50
# em_node.inputs.min_iter = 2
# em_node.inputs.bc_order_val = 3
# em_node.inputs.bc_thresh_val = 0
# em_node.inputs.reg_val = 2
# em_node.inputs.relax_priors = (0.5, 2.0)

print em_node.cmdline
result = em_node.run()

print result.outputs
