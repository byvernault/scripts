"""
    Extract bvals and bvecs from json file.
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Extract bvals and bvecs from json file."
__version__ = '1.0.0'
__modifications__ = '11 October 2015 - Original write'

import os
import json
import glob

def parse_args():
    """
    Parser for arguments
    """
    from argparse import ArgumentParser
    usage = "Generates bvals/bvecs from json files."
    argp = ArgumentParser(prog='read bvals/bvecs from json', description=usage)
    argp.add_argument('-d', dest='directory',
                      help="Directory where the json files are stored.",
                      default=None)
    argp.add_argument('-j', dest='jsonfile',
                      help="Json file to convert.",
                      default=None)
    return argp.parse_args()

def create_bvals_bvecs(json_file_path):
    """
        create the bvals and bvecs files from the json file

        :param json_file_path: json file path containing the information
    """
    filename = os.path.basename(json_file_path).split(".")[0]

    print "File being processed: "+json_file_path
    json_data = None
    try:
        with open(json_file_path) as json_file:
            json_data = json.load(json_file)
    except:
        print "Error reading json file."

    if json_data:
        bvalList = []
        xbvecList = []
        ybvecList = []
        zbvecList = []
        negYbvecList = []
        serid = []
        diff = []
        for dic in json_data:
            scan_data = filter(lambda x: x['type'] == 'ORIGINAL/PRIMARY/M/ND/MOSAIC' or x['type'] == "DIFFUSION/NONE/ND/MOSAIC", dic["series"])
            if len(scan_data) ==0:
                scan_data = filter(lambda x: x['desc'] == "ep2d_diff_MDDW_p2FAD_2.5mm_iso", dic["series"])
            if len(scan_data)>0:
                scan_data = scan_data[0]
                serid = "ser%02d" % (int(scan_data["id"]))
                diff = scan_data["diffusiongrid"]

                for n in range(0,len(diff)):
                    if diff[n][0] == 0 or diff[n][1] == None:
                        bval = 0
                        xbvec = 0
                        ybvec = 0
                        zbvec = 0
                        bvalList.append(bval)
                        xbvecList.append(xbvec)
                        ybvecList.append(ybvec)
                        zbvecList.append(zbvec)
                        negYbvecList.append(-ybvec)
                    else:
                        bval = int(diff[n][0])
                        xbvec = float(diff[n][1][0])
                        ybvec = float(diff[n][1][1])
                        zbvec = float(diff[n][1][2])
                        bvalList.append(bval)
                        xbvecList.append(xbvec)
                        ybvecList.append(ybvec)
                        zbvecList.append(zbvec)
                        negYbvecList.append(-ybvec)
                    # print bvalList
                    output = open(filename + ".bvec", "wt")
                    output.write(" ".join([str(x) for x in xbvecList])+"\n")
                    output.write(" ".join([str(x) for x in ybvecList])+"\n")
                    output.write(" ".join([str(x) for x in zbvecList])+"\n")
                    output.close()
                    output = open(filename + ".negYbvec", "wt")
                    output.write(" ".join([str(x) for x in xbvecList])+"\n")
                    output.write(" ".join([str(x) for x in negYbvecList])+"\n")
                    output.write(" ".join([str(x) for x in zbvecList])+"\n")
                    output.close()
                    output = open(filename + ".bval", "wt")
                    output.write(" ".join([str(x) for x in bvalList])+"\n")
                    output.close()

if __name__ == '__main__':
    ARGS = parse_args()

    if ARGS.jsonfile:
        create_bvals_bvecs(ARGS.jsonfile)
    elif ARGS.directory:
        for jsonfile in glob.glob(os.path.join(ARGS.directory, "*.json")):
            create_bvals_bvecs(jsonfile)
