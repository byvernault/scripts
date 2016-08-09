function varargout = dcm2verdict(varargin)
% DCM2VERDICT MATLAB code for dcm2verdict.fig
%      DCM2VERDICT, by itself, creates a new DCM2VERDICT or raises the existing
%      singleton*.
%
%      H = DCM2VERDICT returns the handle to a new DCM2VERDICT or the handle to
%      the existing singleton*.
%
%      DCM2VERDICT('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in DCM2VERDICT.M with the given input arguments.
%
%      DCM2VERDICT('Property','Value',...) creates a new DCM2VERDICT or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before dcm2verdict_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to dcm2verdict_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help dcm2verdict

% Last Modified by GUIDE v2.5 18-May-2016 16:57:39

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @dcm2verdict_OpeningFcn, ...
                   'gui_OutputFcn',  @dcm2verdict_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT


% --- Executes just before dcm2verdict is made visible.
function dcm2verdict_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to dcm2verdict (see VARARGIN)

% Choose default command line output for dcm2verdict
handles.output = hObject;
addpath(genpath('./'))
% Update handles structure
guidata(hObject, handles);

% UIWAIT makes dcm2verdict wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = dcm2verdict_OutputFcn(hObject, eventdata, handles)
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes on button press in select_dcm_folder_b.
function select_dcm_folder_b_Callback(hObject, eventdata, handles)
% hObject    handle to select_dcm_folder_b (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
    dcm_path=uigetdir('Select the folder with the DICOM files');
    %just the images (not need for the other ones)
    aux=dir([dcm_path filesep 'IM*']);
    dcm_original_filenames=cell(length(aux),1);
    for nd=1:length(aux)
        dcm_original_filenames(nd)={[dcm_path filesep  aux(nd).name]};
    end
    clear aux;

    txt=[];
    %loading the protocol
    for nd=1:length(dcm_original_filenames)
        dcm_i=dicominfo(dcm_original_filenames{nd});
        Protocol(nd)={dcm_i.ProtocolName};
        txt=[txt char(10) sprintf('%i: %s',nd, Protocol{nd})];
    end
    set(handles.text2,'string',txt);
    set(handles.text6,'string',dcm_path);


    % Update handles structure
    handles.dcm_path=dcm_path;
    handles.dcm_original_filenames=dcm_original_filenames;

    guidata(hObject, handles);

    %allow the user continue to the next function
    set(handles.uipanel2,'visible','on');


% --- Executes on button press in checkbox1.
function checkbox1_Callback(hObject, eventdata, handles)
% hObject    handle to checkbox1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of checkbox1
n_acq=get(hObject,'Value');
handles.n_acq=n_acq;
guidata(hObject, handles);
assign_the_correct_order(hObject, eventdata, handles);

% --- Executes on button press in checkbox2.
function checkbox2_Callback(hObject, eventdata, handles)
% hObject    handle to checkbox2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of checkbox2
n_acq=2;
handles.n_acq=n_acq;
guidata(hObject, handles);
assign_the_correct_order(hObject, eventdata, handles);

function assign_the_correct_order(hObject, eventdata, handles)

for iacq=1:handles.n_acq
    clear acq;
    acq_pos(1,iacq)= inputdlg(sprintf('Type Acq %i - b3000 idx:',iacq));
    acq_pos(2,iacq)= inputdlg(sprintf('Type Acq %i - b2000 idx:',iacq));
    acq_pos(3,iacq)= inputdlg(sprintf('Type Acq %i - b1500 idx:',iacq));
    acq_pos(4,iacq) = inputdlg(sprintf('Type Acq %i - b500 idx:',iacq));
    acq_pos(5,iacq) = inputdlg(sprintf('Type Acq %i - b90 idx:',iacq));
end

dcm_original_filenames=handles.dcm_original_filenames;
clear vfull1;
vfull1=[];
iacq=1;
for idf=1:5
	df=str2num(cell2mat(acq_pos(idf,iacq)));
    dcmi_parsed=datparse(dcm_original_filenames(df));
    [volb0, matb0] = d2mat(dcmi_parsed,{'slice','bv','ddty'},'bv',0,'ddty',0,'op','fp') ;
    [volbaux, matbaux] = d2mat(dcmi_parsed,{'slice','bdirec','ddty'},'ddty',1,'op','fp') ;
    vfull = cat(4,volb0,volbaux); % this should be 176 176 14 4
    vfull1=cat(4,vfull1,vfull);
end
    handles.vfull1=vfull1;
    handles.matb0=matb0;

if handles.n_acq==2
clear vfull2;
vfull2=[];
iacq=2;
	for idf=1:5
        df=str2num(cell2mat(acq_pos(idf,iacq)));
    	dcmi_parsed=datparse(dcm_original_filenames(df));
        [volb0, matb0] = d2mat(dcmi_parsed,{'slice','bv','ddty'},'bv',0,'ddty',0,'op','fp') ;
        [volbaux, matbaux] = d2mat(dcmi_parsed,{'slice','bdirec','ddty'},'ddty',1,'op','fp') ;
        vfull = cat(4,volb0,volbaux); % this should be 176 176 14 4
        vfull2=cat(4,vfull2,vfull);
    end
        handles.vfull2=vfull2;
end

set(handles.pushbutton2,'visible','on');
guidata(hObject, handles);


% --- Executes on button press in pushbutton2.
function pushbutton2_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

patient_id=cell2mat(get(handles.edit1,'String'));
n_acq=handles.n_acq;
matb0=handles.matb0;

mkdir(fullfile(handles.dcm_path,'NIFTY'));

vfull1=handles.vfull1;
otput_fn1=fullfile(handles.dcm_path,'NIFTY',[patient_id '_1.nii']);
save(strrep(otput_fn1, '.nii', '.mat'),'vfull1');
create_and_save_nii(vfull1,otput_fn1,matb0.vdims(1:3), []);


if n_acq==2
    vfull2=handles.vfull2;
    otput_fn2=fullfile(handles.dcm_path,'NIFTY',[patient_id '_2.nii']);
    save(strrep(otput_fn2, '.nii', '.mat'),'vfull2');
    create_and_save_nii(vfull2,otput_fn2,matb0.vdims(1:3), []);
end



function edit1_Callback(hObject, eventdata, handles)
% hObject    handle to edit1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit1 as text
%        str2double(get(hObject,'String')) returns contents of edit1 as a double


% --- Executes during object creation, after setting all properties.
function edit1_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end
