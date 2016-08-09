"""Renaming attrs for xnat object."""

import os
from dax import XnatUtils

__author__ = 'byvernault'
__email__ = 'b.yvernault@ucl.ac.uk'
__purpose__ = "Renaming attrs for xnat object"
__version__ = '1.0.0'
__modifications__ = '11 September 2015 - Original write'


if __name__ == '__main__':
    host = os.environ['XNAT_HOST']
    user = os.environ['XNAT_USER']
    pwd = os.environ['XNAT_PASS']
    subject_type = False
    session_type = True
    xnat = XnatUtils.get_interface(host=host, user=user, pwd=pwd)

    if subject_type:
        for subject in XnatUtils.list_subjects(xnat, projectid='INNOVATE'):
            subj_obj = XnatUtils.get_full_object(xnat, subject)
            if subj_obj.exists():
                labels = subject['label'].split('-')
                if subject['label'].startswith('INN_'):
                    sub = subject['label'].replace('_', '-')
                    labels = sub.split('-')
                if len(labels) < 2:
                    print 'stop - wrong label'
                    continue
                if labels[1].isdigit():
                    print 'stop - already good label'
                    continue
                if '_' in labels[2]:
                    fin = '_'+'_'.join(labels[2].split('_')[1:])
                    labels[2] = labels[2].split('_')[0]
                else:
                    fin = ''
                new_labels = '%s-%s-%s%s' % (labels[0], labels[2],
                                             labels[1], fin)
                print subject['label'], new_labels
                subj_obj.attrs.set('label', new_labels)
    elif session_type:
        for session in XnatUtils.list_sessions(xnat, projectid='INNOVATE'):
            sess_obj = XnatUtils.get_full_object(xnat, session)
            if sess_obj.exists():
                labels = session['label'].split('-')
                if session['label'] == 'INN-DCO-036':
                    labels[2] = labels[2] + '_20160615'
                if session['label'].startswith('INN_'):
                    labels[0] = labels[0].replace('_', '-')
                    labels.append(labels[1])
                    labels[1] = labels[0].split('-')[1]
                    labels[0] = labels[0].split('-')[0]
                if labels[1].isdigit():
                    print 'stop - already good label'
                    continue
                if '_' in labels[2]:
                    fin = '_'+'_'.join(labels[2].split('_')[1:])
                    labels[2] = labels[2].split('_')[0]
                else:
                    fin = ''
                new_labels = '%s-%s-%s%s' % (labels[0], labels[2],
                                             labels[1], fin)
                print session['label'], new_labels
                sess_obj.attrs.set('label', new_labels)
