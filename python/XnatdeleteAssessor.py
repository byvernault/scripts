#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on Jan 24, 2013

@author: yvernabc
'''

import os
import sys
from pyxnat import Interface
from dax import XnatUtils

def parse_args():
	from optparse import OptionParser
	usage = "usage: %prog [options] \nWhat is the script doing : Change / Switch the status of Process on XNAT . "
	parser = OptionParser(usage=usage)
	parser.add_option("-p", "--project", dest="project",default='nan',
					help="Project ID on XNAT or list of Project ID", metavar="PROJECT_ID")        
	parser.add_option("-t","--type", dest="proctype",default='nan',
					help="Process type you want to delete in the project. E.G: fMRIQA,dtiQA_v2.", metavar="PROCESS_TYPE")  
	parser.add_option("-s","--status", dest="status",default='',
					help="Delete the assessor with the proctype given and with the status you specified in this option. E.G : NEED_INPUTS", metavar="PROC_STATUS")   
	parser.add_option("-x","--txtfile",dest="txtfile",default='',
					help="File txt with at each line the label of the assessor you want to delete. E.G for label: project-x-subject-x-experiment-x-scan-x-process_name.", metavar="FILEPATH")    
	return parser.parse_args()

def str_number_counting(int_count,int_length):
	number_instance=len(str(int_length))
	if number_instance==1:
		return str(int_count)+'/'+str(int_length)
	elif number_instance==2:
		return '{:02}'.format(int_count)+'/'+str(int_length)
	elif number_instance==3:
		return '{:03}'.format(int_count)+'/'+str(int_length)
	elif number_instance==4:
		return '{:04}'.format(int_count)+'/'+str(int_length)
	elif number_instance==5:
		return '{:05}'.format(int_count)+'/'+str(int_length)
	return '...'

#Delete assessor for the whole project
def get_assessor_list(project_list,status,status_list,proctype_list):
	try:
		# Environs
		VUIISxnat_user = os.environ['XNAT_USER']
		VUIISxnat_pwd = os.environ['XNAT_PASS']
		VUIISxnat_host = os.environ['XNAT_HOST']
	except KeyError as e:
		print "You must set the environment variable %s" % str(e)
		sys.exit(1)
	
	assessor_label_list=list()
	# Connection to Xnat
	try:
		xnat = Interface(VUIISxnat_host, VUIISxnat_user, VUIISxnat_pwd)
		
		#for each project in the list:
		for project in project_list:
			print ' +Project: '+project
			#Subjects/sessions
			subjectList=XnatUtils.list_subjects(xnat,projectName)
			countSubj=len(subjectList)
			for indexS,subj in enumerate(subjectList):
				sessionList=XnatUtils.list_experiments(xnat,projectName,subj['ID'])
				countSess=len(sessionList)
				for indexE,exp in enumerate(sessionList):
					Infostr='  -'+subj['label']+' subject '+str_number_counting(indexS+1,countSubj)+' - '+exp['label']+' session '+str_number_counting(indexE+1,countSess)
					sys.stdout.write(Infostr+'\r')
					sys.stdout.flush()
					
					for asse in XnatUtils.list_assessors(xnat, projectName, subj['ID'], exp['ID']):
						labels=asse['label'].split('-x-')
						
						if labels[-1] in proctype_list:
							if status:
								if asse['procstatus'] in status_list:
									assessor_label_list.append(asse['label'])
							else:
								assessor_label_list.append(asse['label'])
							
	finally:
		xnat.disconnect()
		
	return assessor_label_list

#print the assessor that will be delete
def print_assessor_list(assessor_label_list):
	print '\t%*s | %*s | %*s | %*s' % (-20, 'Project',-20,'Subject',-20, 'Session',-20, 'Assessor_label')
	for assessor_label in assessor_label_list:
		labels=assessor_label.split('-x-')
		print '\t%*s | %*s | %*s | %*s' % (-20, labels[0], -20, labels[1],-20, labels[2],-20, assessor_label)

#ask user if yes or no delete
def ask_user_delete():
	answer=''
	while answer not in ['Y','y','n','N']:
		answer=raw_input('Do you want to delete all this assessor?(Y/N)\n')
	return answer

#Delete the assessor from a list
def delete_assessor_list(assessor_label_list):
	try:
		# Environs
		VUIISxnat_user = os.environ['XNAT_USER']
		VUIISxnat_pwd = os.environ['XNAT_PASS']
		VUIISxnat_host = os.environ['XNAT_HOST']
	except KeyError as e:
		print "You must set the environment variable %s" % str(e)
		sys.exit(1)
	
	# Connection to Xnat
	try:
		xnat = Interface(VUIISxnat_host, VUIISxnat_user, VUIISxnat_pwd)
		#for each assessor in the list:
		for assessor_label in assessor_label_list:
			labels=assessor_label.split('-x-')
			
			Assessor=xnat.select('/project/'+labels[0]+'/subjects/'+labels[1]+'/experiments/'+labels[2]+'/assessors/'+assessor_label)
			if Assessor.exists():
				Assessor.delete()
				print'  *Assessor '+assessor_label+' deleted'
	finally:
		xnat.disconnect()

if __name__ == '__main__':
	(options,args) = parse_args()
	#Arguments :
	projectName = options.project
	project_list = projectName.split(',')
	proctype=options.proctype
	proctype_list=proctype.split(',')
	status=options.status
	status_list=status.split(',')
	txtfile=options.txtfile

	#Display:
	print '####################################################################################################'
	print '#                                       XNATDELETEASSESSOR                                         #'
	print '#                                                                                                  #'
	print '# Developed by the masiLab Vanderbilt University, TN, USA.                                         #'
	print '# If issues, email benjamin.c.yvernault@vanderbilt.edu                                             #'
	print '# Parameters :                                                                                     #'
	if options=={'status': None, 'proctype': 'nan', 'txtfile': 'nan', 'project': 'nan'}:
		print '#     No Arguments given                                                                           #'
		print '#     Use "XnatSwitchProcessStatus -h" to see the options                                          #'
		print '####################################################################################################'
		sys.exit()
	else:
		if txtfile:
			print '#     %*s ->  %*s#' %(-30,'File txt',-58,txtfile)
			if status:
				print '#     %*s ->  %*s#' %(-30,'Status',-58,status)
		else:
			if len(projectName)>55:
				str_project=projectName[:50]+'...'
			else:
				str_project=projectName
			print '#     %*s ->  %*s#' %(-30,'List of projects',-58,str_project)
			if len(proctype)>55:
				str_Processes=proctype[:50]+'...'
			else:
				str_Processes=proctype
			print '#     %*s ->  %*s#' %(-30,'Process Types',-58,str_Processes)
			if status:
				print '#     %*s ->  %*s#' %(-30,'Status',-58,status)
		print '####################################################################################################'
		
	#if using a file
	if txtfile:
		if os.path.exists(txtfile):
			#read the file
			assessor_label_list=list()
			input_file = open(txtfile, 'r')
			for index,line in enumerate(input_file):
				#get the assessor_label
				assessor_label=line.split('\n')[0]
				assessor_label_list.append(assessor_label)
			
			if not len(assessor_label_list)>0:	
				sys.stdout.write('\r\n')
				sys.stdout.flush()
				print('INFO: No assessor found. Exit.')
			else:
				sys.stdout.write('\r\n')
				sys.stdout.flush()
				print('INFO: '+str(len(assessor_label_list))+' assessors found.')
				#show the list:
				print_assessor_list(assessor_label_list)
				
				#ask if it's good to delete:
				answer=ask_user_delete()
				if answer in ['Y','y']:
					run=raw_input('Are you sure?(Y/N)\n')
					if run in ['Y','y']:
						print('\nINFO: deleting assessor ...')
						#delete
						delete_assessor_list(assessor_label_list)
				else:
					print('INFO: Delete assessor CANCELED...')
		else:
			sys.stdout.write("ERROR: the file "+txtfile+" does not exist.\n")
			sys.stdout.flush()
	else:
		#Checked argument values if not:
		if projectName=='nan':
			print'WARNING: No project ID given, please give one with -p options. Use -h to check the options.'
			sys.exit()
		if proctype=='nan':
			print'WARNING: No process type given, please give one with -t options. Use -h to check the options.'
			print'E.G: fMRIQA,dtiQA_v2,FreeSurfer'
			sys.exit()
		if not status:
			print'==WARNING==: All assessor in the projects given with the proc-types given will be deleted.'
		
		assessor_label_list=get_assessor_list(project_list,status,status_list,proctype_list)
		
		if not len(assessor_label_list)>0:	
			sys.stdout.write('\r\n')
			sys.stdout.flush()
			print('INFO: No assessor found. Exit.')
		else:
			sys.stdout.write('\r\n')
			sys.stdout.flush()
			print('INFO: '+str(len(assessor_label_list))+' assessors found.')
			#show the list:
			print_assessor_list(assessor_label_list)
			
			#ask if it's good to delete:
			answer=ask_user_delete()
			if answer in ['Y','y']:
				run=raw_input('Are you sure?(Y/N)\n')
				if run in ['Y','y']:
					print('\nINFO: deleting assessor ...')	
					#delete
					delete_assessor_list(assessor_label_list)
			else:
				print('INFO: Delete assessor CANCELED...')
	# Display:
	print '===================================================================\n'