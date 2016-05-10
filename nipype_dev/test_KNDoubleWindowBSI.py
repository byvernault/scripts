"""Test KNDoubleWindowBSI interface in nitfk."""
import os
import argparse

from niftypipe.interfaces.niftk.filters import KNDoubleWindowBSI

desc = 'test_KNDoubleWindowBSI'
parser = argparse.ArgumentParser(description=desc)
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
parser.add_argument('--bsi_mask',
                    dest='bsi_mask',
                    metavar='mask',
                    help='BSI mask',
                    required=True)
parser.add_argument('--repeat_bsi_mask',
                    dest='repeat_bsi_mask',
                    metavar='mask',
                    help='Repeat BSI mask',
                    required=True)
parser.add_argument('--gm',
                    dest='gm',
                    metavar='mask',
                    help='baseline local GM intensity normalisation mask',
                    required=True)
parser.add_argument('--regm',
                    dest='regm',
                    metavar='mask',
                    help='repeat local GM intensity normalisation mask',
                    required=True)
parser.add_argument('-o', '--output',
                    dest='output',
                    metavar='output',
                    help='Output bsi values text file')

args = parser.parse_args()

kmwwlrnbsi = KNDoubleWindowBSI()
kmwwlrnbsi.inputs.baseline_image = args.input[0]
kmwwlrnbsi.inputs.baseline_mask = args.mask[0]
kmwwlrnbsi.inputs.repeat_image = args.input[1]
kmwwlrnbsi.inputs.repeat_mask = args.mask[1]
kmwwlrnbsi.inputs.bsi_image = args.input[0]
kmwwlrnbsi.inputs.bsi_mask = args.bsi_mask
kmwwlrnbsi.inputs.bsi_repeat_image = args.input[1]
kmwwlrnbsi.inputs.bsi_repeat_mask = args.repeat_bsi_mask
kmwwlrnbsi.inputs.gm_mask = args.gm
kmwwlrnbsi.inputs.repeat_gm_mask = args.regm
if args.output:
    kmwwlrnbsi.inputs.out_bsi_values = args.output

result = kmwwlrnbsi.run()

print result.outputs
