from dax import XnatUtils
import csv

def read_txtfile(csvfile):
    session_to_change = dict()
    with open(csvfile,'rb') as csvfileread:
        csvreader = csv.reader(csvfileread, delimiter=',')
        for row in csvreader:
            session_to_change[row[0]] = row[1]
    return session_to_change

if __name__ == "__main__":
    # Variables:
    project = "PICTURE"
    #csvfile = "/Users/byvernault/Downloads/session_dates_file.csv"
    """types = {"WIP WIP WIP DCE 1.3mm match FOV SENSE": "DCE",
             "VISTA SENSE": "VISTA",
             "mp-rage":"T1",
             "T2W_TSE_axial new CLEAR": "T2",
             "DWI_b2000 spir": "DWI",
             "dDWI_ADC" : "ADC",
             "T2 SAG REF CLEAR" : "T2",
             "DWI sFOV AP 4b": "DWI",
             "T1W_TSE_ax": "T1",
             "T2W_TSE_ax":"T2",
             "DCE 2dyn modified SENSE":"DCE",
             "WIP DCE 1.3mm match FOV SENSE":"DCE",
             "DCE 20dyn modified SENSE":"DCE",
             "dRegADC_all LFOV":"ADC",
             'DCE Dix 2dyn FA15':'DCE',
             'T2W_TSE_cor SENSE':"T2",
             't1_vibe_15deg35mea':"T1",
             'DCE 15dyn modified SENSE':"DCE",
             'DWI 0 150 500 1000':"DWI",
             't1_vibe_20deg':"T1",
             'ep2d_diff_b1400_new 32 measipat':"EP2D_DIFF",
             'dRegADC_all':"ADC",
             'T2W_TSE_new CLEAR':"T2",
             't2_tse_cor_SFOV':"T2",
             't1_vibe_25deg':"T1",
             't2_tse_tra_3mm _SFOV_TE 92':"T2",
             'T2W_TSE_cor':"T2",
             't1_vibe_10deg':"T1",
             't1_vibe_5deg':"T1",
             't1FL3dfs15fa_matchVIBE':"T1",
             'ep2d_diff_new 16 measipat':"EP2D_DIFF",
             'dADC_all sFOV AP 4b':"ADC"}"""

    xnat = XnatUtils.get_interface(host="https://prostate-xnat.cs.ucl.ac.uk", user='byvernault', pwd='20289_cmic')

    list_scans = XnatUtils.list_project_scans(xnat, project)
    """for scan in list_scans:
        for key, value in types.items():
            if key in scan['type']:#scan['ID'].lower():
                print "%s - %s - %s - %s" % (scan["session_label"], scan["ID"], scan["type"], scan["series_description"])
                scan_obj = XnatUtils.get_full_object(xnat, scan)
                scan_obj.attrs.set("type", value)
                #scan_obj.attrs.set("series_description", scan['ID'])
                #scan_obj.attrs.set("quality", "usable")"""

    for scan in list_scans:
        #if "T2" == scan['type']:
        #    print scan['series_description']
        if "ADC" == scan['type'] and "dDWI_ADC" == scan['series_description']:#scan['ID'].lower():
            print "%s - %s - %s - %s" % (scan["session_label"], scan["ID"], scan["type"], scan["series_description"])
            scan_obj = XnatUtils.get_full_object(xnat, scan)
            scan_obj.attrs.set("type", "DWI ADC")

    """session_to_change = read_txtfile(csvfile)
    list_sessions = XnatUtils.list_sessions(xnat, project)
    for session in list_sessions:
        #session_obj = XnatUtils.select_obj(xnat, project_id=project, subject_id="4620", session_id="MR_44032")
        if session['label'] in session_to_change:
            print "%s - %s " % (session["session_label"], session_to_change[session['label']])
            session_obj = CmicXUtils.get_full_object(xnat, session)
            if session_obj.exists():
                session_obj.attrs.set("date", session_to_change[session['label']])"""

    xnat.disconnect()
