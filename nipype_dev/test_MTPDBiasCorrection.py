"""Test MTPDBiasCorrection interface in nitfk."""
import os
import argparse

from niftypipe.interfaces.niftk.filters import MTPDBiasCorrection

parser = argparse.ArgumentParser(description='test_MTPDBiasCorrection')
directory = os.getcwd()

parser.add_argument('-i', '--input',
                    dest='input',
                    metavar='input',
                    nargs='+',
                    help='Input Image',
                    required=True)
parser.add_argument('-m', '--mask',
                    dest='mask',
                    metavar='mask',
                    nargs='+',
                    help='Mask Image',
                    required=True)
parser.add_argument('-o', '--output',
                    dest='output',
                    metavar='output',
                    nargs='+',
                    help='Output Image')

args = parser.parse_args()

mtpdbc = MTPDBiasCorrection()
in_files = [os.path.abspath(image) for image in args.input]
in_masks = [os.path.abspath(mask) for mask in args.mask]
mtpdbc.inputs.in_files = in_files
mtpdbc.inputs.mask_files = in_masks
if args.output:
    out_files = [os.path.abspath(output) for output in args.output]
    mtpdbc.inputs.out_files = out_files
mtpdbc.inputs.in_mode = 2

result = mtpdbc.run()

print result.outputs.out_files
