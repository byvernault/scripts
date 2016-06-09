#! /usr/bin/env python

import argparse
import os
import sys
import textwrap
import nipype.interfaces.utility as niu
import nipype.pipeline.engine as pe

from niftypipe.workflows.dmri.niftyfit_tensor_preprocessing import (create_diffusion_mri_processing_workflow,
                                                                    merge_dwi_function)
from niftypipe.interfaces.niftk.base import (generate_graph, run_workflow)

help_message = textwrap.dedent('''
Perform Diffusion Model Fitting with pre-processing steps.
Mandatory Inputs are the Diffusion Weighted Images and the bval/bvec pair.
as well as a T1 image are extracted for reference space.
The Field maps are provided so susceptibility correction is applied.

Values to use for the susceptibility parameters:

## DRC ## (--ped=-y --etd=2.46 --rot=34.56) and
## 1946 ## (--ped=-y --etd=2.46 --rot=25.92).

Note that these values are indicative.
''')


def find_files(directory, ext):
    """Return the files in subdirectories witht the right extension.

    :param directory: directory where the data are located
    :param ext: extension to look for
    :return: python list of files
    """
    li_files = list()
    for root, _, filenames in os.walk(directory):
        li_files.extend([os.path.join(root, filename) for filename in filenames if filename.lower().endswith(ext.lower())])
    return li_files


parser = argparse.ArgumentParser(description=help_message)
parser.add_argument('-i', '--dwis',
                    dest='dwis',
                    metavar='dwis',
                    nargs='+',
                    help='Diffusion Weighted Images in a 4D nifti file \
or a zip of bval/bvec/nii and you do not need to specify bval/bvec.',
                    required=True)
parser.add_argument('-a', '--bvals',
                    dest='bvals',
                    metavar='bvals',
                    nargs='+',
                    help='bval file to be associated with the DWIs',
                    required=False)
parser.add_argument('-e', '--bvecs',
                    dest='bvecs',
                    metavar='bvecs',
                    nargs='+',
                    help='bvec file to be associated with the DWIs',
                    required=False)
parser.add_argument('-t', '--t1',
                    dest='t1',
                    metavar='t1',
                    help='T1 file to be associated with the DWIs',
                    required=True)
parser.add_argument('--t1_mask',
                    dest='t1_mask',
                    metavar='t1_mask',
                    help='T1 mask file associated with the input T1',
                    required=False)
parser.add_argument('-m', '--fieldmapmag',
                    dest='fieldmapmag',
                    metavar='fieldmapmag',
                    help='Field Map Magnitude image file to be associated \
with the DWIs',
                    required=False)
parser.add_argument('-p', '--fieldmapphase',
                    dest='fieldmapphase',
                    metavar='fieldmapphase',
                    help='Field Map Phase image file to be associated \
with the DWIs',
                    required=False)
parser.add_argument('-o', '--output_dir',
                    dest='output_dir',
                    type=str,
                    metavar='output_dir',
                    help='Output directory containing the registration result \
Default is a directory called results',
                    default=os.path.abspath('results'),
                    required=False)
parser.add_argument('-g', '--graph',
                    dest='graph',
                    help='Print a graph describing the node connections',
                    action='store_true',
                    default=False)
parser.add_argument('--rot',
                    dest='rot',
                    type=float,
                    metavar='rot',
                    help='Diffusion Read-Out time used for susceptibility \
correction Default is 34.56',
                    default=34.56,
                    required=False)
parser.add_argument('--etd',
                    dest='etd',
                    type=float,
                    metavar='etd',
                    help='Echo Time difference used for susceptibility \
correction. Default is 2.46.',
                    default=2.46,
                    required=False)
parser.add_argument('--ped',
                    nargs='?',
                    const=None,
                    choices=[Q for x in ['x', 'y', 'z'] for Q in (x, '-' + x)],
                    dest='ped',
                    type=str,
                    metavar='ped',
                    help='Phase encoding direction used for susceptibility \
correction (x, y or z)\n --ped=val form must be used for -ve indices. \
Default is the -y direction (-y)',
                    default='-y',
                    required=False)
parser.add_argument('--rigid',
                    dest='rigid_only',
                    action='store_true',
                    help='Only use rigid registration for DWI \
(no eddy current correction)',
                    required=False)
parser.add_argument('-x', '-y', '-z',
                    dest='pedwarn',
                    help=argparse.SUPPRESS,
                    required=False,
                    action='store_true')

args = parser.parse_args()

if args.ped is None:
    print 'ERROR: argument --ped: expected one argument, \
make sure to use --ped='
    sys.exit(1)
if args.pedwarn:
    print 'ERROR: One of -x, -y or -z found, did you mean \
--ped=-x, --ped=-y --ped=-z?'
    sys.exit(1)

result_dir = os.path.abspath(args.output_dir)
if not os.path.exists(result_dir):
    os.mkdir(result_dir)

zipped_dwis = [dwi for dwi in args.dwis if dwi.lower().endswith('.zip')]
if len(zipped_dwis) > 0:
    dwis = list()
    bvals = list()
    bvecs = list()
    print 'Info: unzipping inputs since some files are .zip in dwis. \
If some of the inputs are nifti, please remove the zip files.'
    # Unzipping the dwis inputs:
    for zips in zipped_dwis:
        zip_dir = os.path.join(result_dir, os.path.basename(zips)[:-4])
        if not os.path.exists(zip_dir):
            os.mkdir(zip_dir)
        os.system('unzip -d %s -j -o %s > /dev/null' % (zip_dir, zips))
        dwis_unzipped = find_files(zip_dir, '.nii.gz')
        bvals_unzipped = find_files(zip_dir, '.bval')
        bvecs_unzipped = find_files(zip_dir, '.bvec')
        if not bvecs_unzipped or \
           not bvals_unzipped or \
           not dwis_unzipped or \
           len(dwis_unzipped) != len(bvals_unzipped) or \
           len(dwis_unzipped) != len(bvecs_unzipped):
            print 'ERROR: missing files (bval/bvec or nii) in zip.'
            sys.exit(1)
        dwis.append(dwis_unzipped[0])
        bvals.append(bvals_unzipped[0])
        bvecs.append(bvecs_unzipped[0])
else:
    if (len(args.dwis) != len(args.bvals)) or \
       (len(args.dwis) != len(args.bvecs)):
        print 'ERROR: The number of BVAL and BVEC files should match the \
number of DWI files.'
        sys.exit(1)
    dwis = [os.path.abspath(f) for f in args.dwis]
    bvals = [os.path.abspath(f) for f in args.bvals]
    bvecs = [os.path.abspath(f) for f in args.bvecs]

print 'Info - inputs: niftis : %s' % dwis
print '                bvals : %s' % bvals
print '                bvecs : %s' % bvecs

do_susceptibility_correction = True
if args.fieldmapmag is None or args.fieldmapphase is None:
    do_susceptibility_correction = False

merge_initial_dwis = pe.Node(interface=niu.Function(input_names=['in_dwis',
                                                                 'in_bvals',
                                                                 'in_bvecs'],
                                                    output_names=['out_dwis',
                                                                  'out_bvals',
                                                                  'out_bvecs'],
                                                    function=merge_dwi_function),
                             name='merge_initial_dwis')
merge_initial_dwis.inputs.in_dwis = dwis
merge_initial_dwis.inputs.in_bvals = bvals
merge_initial_dwis.inputs.in_bvecs = bvecs

r = create_diffusion_mri_processing_workflow(
    t1_mask_provided=args.t1_mask is not None,
    susceptibility_correction=do_susceptibility_correction,
    in_susceptibility_params=[args.rot, args.etd, args.ped],
    name='dmri_workflow', resample_in_t1=False, log_data=True,
    dwi_interp_type='CUB', wls_tensor_fit=True, rigid_only=args.rigid_only)
r.base_dir = result_dir
r.connect(merge_initial_dwis, 'out_dwis',
          r.get_node('input_node'), 'in_dwi_4d_file')
r.connect(merge_initial_dwis, 'out_bvals',
          r.get_node('input_node'), 'in_bval_file')
r.connect(merge_initial_dwis, 'out_bvecs',
          r.get_node('input_node'), 'in_bvec_file')
if args.t1.lower().endswith('.zip'):
    zip_dir = os.path.join(result_dir, os.path.basename(args.t1)[:-4])
    if not os.path.exists(zip_dir):
        os.mkdir(zip_dir)
    os.system('unzip -d %s -j -o %s > /dev/null' % (zip_dir, zips))
    t1_unzipped = find_files(zip_dir, '.nii.gz')
    if not t1_unzipped:
        print 'ERROR: T1 files not found in the zip given.'
        sys.exit(1)
    t1 = t1_unzipped[0]
else:
    t1 = os.path.abspath(args.t1)
r.inputs.input_node.in_t1_file = t1
if args.t1_mask:
    r.inputs.input_node.in_t1_mask_file = os.path.abspath(args.t1_mask)
if do_susceptibility_correction:
    r.inputs.input_node.in_fm_magnitude_file = os.path.abspath(args.fieldmapmag)
    r.inputs.input_node.in_fm_phase_file = os.path.abspath(args.fieldmapphase)

if args.graph is True:
    generate_graph(workflow=r)
    sys.exit(0)

qsubargs = '-l h_rt=02:00:00 -l tmem=2.9G -l h_vmem=2.9G -l vf=2.9G \
-l s_stack=10240 -j y -b y -S /bin/csh -V'
run_workflow(workflow=r,
             qsubargs=qsubargs)
