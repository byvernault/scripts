#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os


def parse_args():
    """ Parser for arguments """
    from argparse import ArgumentParser
    usage = "Extract values for dear Michela."
    argp = ArgumentParser(prog='extract_info_txt.py', description=usage)
    argp.add_argument('-d', '--dir', dest='directory',
                      help='Directory containing the files.', required=True)
    return argp.parse_args()


if __name__ == '__main__':
    args = parse_args()

    if not os.path.exists(args.directory):
        raise Exception('Directory not found: %s' % args.directory)

    out_fname = None
    for fname in os.listdir(args.directory):
        fpath = os.path.join(args.directory, fname)
        if os.path.isfile(fpath) and fname.split('.')[-1] == 'txt':
            list_values = list()
            with open(fpath, 'r') as f_obj_in:
                for line in f_obj_in:
                    line = line.strip()
                    if line and 'generation' not in line:
                        labels = line.split('\t')
                        list_values.append('%s %s\n' % (labels[1], labels[-1]))
                        out_fname = labels[0]
            if out_fname:
                out_fpath = os.path.join(args.directory, '%s' % out_fname)
                with open(out_fpath, 'w') as f_obj_out:
                    f_obj_out.writelines(list_values)
