"""Test MTPDBiasCorrection interface in nitfk."""
import os
import argparse

from nipype.interfaces.niftyseg import FillLesions

parser = argparse.ArgumentParser(description='test_FillLesions')
directory = os.getcwd()

parser.add_argument('-i', '--input',
                    dest='input',
                    metavar='input',
                    help='Input Image',
                    required=True)
parser.add_argument('-l', '--lesion',
                    dest='lesion',
                    metavar='lesion',
                    help='Lesion Mask Image',
                    required=True)
parser.add_argument('-m', '--mask',
                    dest='bin_mask',
                    metavar='bin_mask',
                    help='Bin Mask Image')
parser.add_argument('-o', '--output',
                    dest='output',
                    metavar='output',
                    help='Output Image')
parser.add_argument('-d', '--dil',
                    dest='dil_fill',
                    metavar='dil_fill',
                    help='Number of dilation')

args = parser.parse_args()

fill_lesions = FillLesions()
fill_lesions.inputs.in_file = args.input
fill_lesions.inputs.lesion_mask = args.lesion
if args.output:
    fill_lesions.inputs.out_file = args.output
if args.bin_mask:
    fill_lesions.inputs.bin_mask = args.bin_mask
if args.dil_fill:
    fill_lesions.inputs.in_dilation = int(args.dil_fill)

print fill_lesions.cmdline
result = fill_lesions.run()

print result.outputs.out_file
