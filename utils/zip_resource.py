#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Zip all files in a resource as resource.zip
"""

import os
from datetime import datetime
from dax import XnatUtils

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__version__ = '1.0.0'
__modifications__ = '10 September 2015 - Original write'
__exe__ = os.path.basename(__file__)
__description__ = "Zip all files in a resource as {{resource}}.zip."

LIMIT_SIZE = 100


def parse_args():
    """Parser for arguments."""
    from argparse import ArgumentParser
    argp = ArgumentParser(prog=__exe__, description=__description__)
    argp.add_argument('--host', dest='host',
                      help='Host for Xnat.')
    argp.add_argument('-u', '--username', dest='username',
                      help='Username for Xnat.')
    argp.add_argument('-p', '--project', dest='project',
                      help='Project ID on Xnat.', required=True)
    argp.add_argument('-s', '--sess', dest='sessions',
                      help='Session labels on Xnat (comma separated).')
    argp.add_argument('-l', '--lastsess', dest='lastsess', default=None,
                      help='Last session to start checking from.')
    argp.add_argument('-d', '--directory', dest='directory',
                      help='Temp directory on your computer.', required=True)
    argp.add_argument('-r', dest='resources', required=True,
                      help='Resource Name on XNAT.')
    argp.add_argument('-n', '--nodelete', dest='no_delete',
                      action='store_true',
                      help='Do NOT delete the files zipped.')
    argp.add_argument('-b', '--noBig', dest='no_big', action='store_true',
                      help='Avoid zipping large resources.')
    argp.add_argument('-f', '--force', dest='force', action='store_true',
                      help='Force zipping without checking resources.')
    return argp.parse_args()


def zip_resource(res_obj, directory, resource, no_delete=False, no_big=False):
    """
    Zip the files in the resource.

    :param res_obj: resource Eobject from pyxnat
    :param directory: directory to save temp files
    :param resource: resource label
    :param no_delete: do not delete the files zipped
    :param no_big: do not zip big resources
    """
    _warn = '    - warning: %s'
    fzip = '%s.zip' % resource
    if len(res_obj.files().get()) > 1:
        print("   --> downloading %s ..." % resource)
        fpaths = XnatUtils.download_files_from_obj(directory, res_obj)
        if not fpaths:
            msg = '%s -- no files.' % resource
            print(_warn % msg)
        else:
            # If the resource.zip file exists, exit
            if res_obj.file(fzip).exists():
                msg = '%s -- zip file already on XNAT but zipped files not \
deleted.' % resource
                print(_warn % msg)

            else:
                # Zip the resource if more than one
                print('   --> zipping files.')
                resource_dir = os.path.dirname(fpaths[0])
                # Get init directory
                init_dir = os.getcwd()
                # Zip all the files in the directory
                os.chdir(resource_dir)
                os.system('zip -r %s * > /dev/null' % fzip)
                # return to the initial directory:
                os.chdir(init_dir)
                # upload
                _fzip = os.path.join(resource_dir, fzip)

                if os.path.exists(_fzip):
                    # Check the size:
                    size_file = int(os.stat(_fzip).st_size) / (1024 * 1024)
                    if size_file >= LIMIT_SIZE:
                        msg = '%s too big.' % resource
                        print(_warn % msg)
                    if no_big and size_file >= LIMIT_SIZE:
                        msg = '%s too big. Skipping.' % resource
                        print(_warn % msg)
                        return

                    print('   --> uploading zip file')
                    res_obj.put_zip(_fzip, overwrite=True, extract=False)

            if no_delete:
                print('   --> not deleting original files(two copies).')
            else:
                print('   --> deleting original files and keeping zipfile.')
                delete_resources(res_obj, fzip)

    # clean tmp folder
    XnatUtils.clean_directory(directory)


def delete_resources(resource_obj, fzip):
    """
    Check that the file exist on the resource before deleting
    :param resource_obj: pyxnat resource Eobject
    :param fzip: zip file
    """
    list_files = resource_obj.files().get()
    if fzip in list_files:
        for fpath in list_files:
            if fpath != fzip:
                resource_obj.file(fpath).delete()
    else:
        mg = 'WARNING: No zip files found in the resources. Avoiding deleting.'
        print(mg)


def zip_resources(xnat, args):
    """
    Loop through the project scans to zip files.

    :param xnat: interface from dax related to pyxnat
    :param args: arguments from parse_args
    """
    # set a directory where the files are download
    directory = os.path.abspath(XnatUtils.makedir(args.directory))

    list_scans = XnatUtils.list_project_scans(xnat, args.project)
    print("INFO: Filtering list of scans to keep scans with resources.")
    if not args.force:
        for resource in args.resources.split(','):
            list_scans = filter(lambda x: resource in x['resources'],
                                list_scans)

    # if sessions, filter:
    if args.sessions:
        list_scans = filter(
            lambda x: x['session_label'] in args.sessions.split(','),
            list_scans)

    # filtering last sessions:
    list_scans = sorted(list_scans, key=lambda k: k['session_label'])
    if args.lastsess:
        list_scans = remove_sessions_processed(list_scans, args.lastsess)

    number_scans = len(list_scans)
    print("INFO: Converting the %s scans found." % (number_scans))
    for index, scan in enumerate(list_scans):
        message = ' * {ind}/{tot} -- Session: {sess} -- Scan: {scan}'
        print(message.format(ind=index + 1,
                             tot=number_scans,
                             sess=scan['session_label'],
                             scan=scan['ID']))
        scan_obj = XnatUtils.get_full_object(xnat, scan)
        if scan_obj.exists():
            for resource in args.resources.split(','):
                zip_resource(scan_obj.resource(resource), directory,
                             resource, args.no_delete, args.no_big)


def remove_sessions_processed(list_scans, lastsess):
    """
    Remove the sessions before the last session
    :param list_scans: list of scans
    :param lastsess: last session processed
    """
    new_list_scans = list()
    good = False
    for scan in list_scans:
        if scan['session_label'] == lastsess:
            good = True

        if good:
            new_list_scans.append(scan)
    return new_list_scans


if __name__ == '__main__':
    args = parse_args()
    print('Zipping files in %s for Project:\t%s'
          % (args.resources.split(','), args.project))
    print('Time: %s' % str(datetime.now()))

    if args.host:
        host = args.host
    else:
        host = os.environ['XNAT_HOST']
    with XnatUtils.get_interface(host=host, user=args.username) as xnat:
        print('INFO: connection to xnat <%s>:' % (host))
        print('INFO: extracting information from XNAT')
        zip_resources(xnat, args)

    print('================================================================\n')
