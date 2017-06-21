from dax import XnatUtils
import os


if __name__ == "__main__":
    # Variables:
    project = 'DIAN'
    types = {'': 'PhoenixZIPReport'}

    with XnatUtils.get_interface(host=os.environ['DPUK']) as xnat:
        scans = XnatUtils.list_project_scans(xnat, project)
        scans = XnatUtils.filter_list_dicts_regex(scans, 'type', types.keys())
        for scan in sorted(scans, key=lambda k: k['session_label']):
            print "%s - %s - %s - %s" % (scan["session_label"],
                                         scan["ID"],
                                         scan["type"],
                                         scan["series_description"])
            scan_obj = XnatUtils.get_full_object(xnat, scan)
            scan_obj.attrs.set('type', types[scan['type']])
            print('   new type: {}'.format(types[scan['type']]))
