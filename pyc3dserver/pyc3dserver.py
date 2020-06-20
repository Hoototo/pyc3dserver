import os
import pythoncom
import win32com.client as win32
import numpy as np
import pandas as pd
from scipy.interpolate import InterpolatedUnivariateSpline
import logging

logger_name = 'pyc3dserver'
logger = logging.getLogger(logger_name)
logger.setLevel('CRITICAL')
logger.addHandler(logging.NullHandler())

def logger_init(logger_lvl='WARNING', c_hdlr_lvl='WARNING', f_hdlr_lvl='ERROR', f_hdlr_f_mode='w', f_hdlr_f_path=None):
    """
    Initialize the logger of pyc3dserver module.

    Parameters
    ----------
    logger_lvl : str or int, optional
        Level of the logger itself. The default is 'WARNING'.
    c_hdlr_lvl : str or int, optional
        Level of the console handler in the logger. The default is 'WARNING'.
    f_hdlr_lvl : str or int, optional
        Level of the file handler in the logger. The default is 'ERROR'.
    f_hdlr_f_mode : str, optional
        File mode of the find handler in the logger. The default is 'w'.
    f_hdlr_f_path : str, optional
        File path of the file handler. The default is None.
        If this value is None, then there will be no file handler in the logger. 
        
    Returns
    -------
    logger : logging.Logger
        Logger object.

    """
    logger.setLevel(logger_lvl)
    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])    
    if not logger.handlers:
        c_hdlr = logging.StreamHandler()
        c_hdlr.setLevel(c_hdlr_lvl)
        c_fmt = logging.Formatter('<%(name)s> - [%(levelname)s] - %(funcName)s() : %(message)s')
        c_hdlr.setFormatter(c_fmt)
        logger.addHandler(c_hdlr)
        if f_hdlr_f_path is not None:
            f_hdlr = logging.FileHandler(f_hdlr_f_path, mode=f_hdlr_f_mode)
            f_hdlr.setLevel(f_hdlr_lvl)
            f_fmt = logging.Formatter('%(asctime)s - <%(name)s> - [%(levelname)s] - %(funcName)s() : %(message)s')
            f_hdlr.setFormatter(f_fmt)
            logger.addHandler(f_hdlr)
    return logger

def logger_reset():
    """
    Reset the logger by setting its level as 'CRITICAL' and removing all its handlers.

    Returns
    -------
    None.

    """
    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])    
    logger.setLevel('CRITICAL')       
    return None

def c3dserver():
    """
    Initialize C3DServer COM interface using win32com.client.Dispatch().
    
    Also shows the relevant information of C3DServer status such as
    registration mode, version, user name and organization.

    Returns
    -------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.

    """
    # itf = win32.Dispatch('C3DServer.C3D')
    print("========================================")
    itf = win32.dynamic.Dispatch('C3DServer.C3D')
    reg_mode = itf.GetRegistrationMode()
    if reg_mode == 0:
        print("Unregistered C3Dserver")
    elif reg_mode == 1:
        print("Evaluation C3Dserver")
    elif reg_mode == 2:
        print("Registered C3Dserver")
    print("Version: ", itf.GetVersion())
    print("User: ", itf.GetRegUserName())
    print("Organization: ", itf.GetRegUserOrganization())
    print("========================================")
    return itf

def open_c3d(itf, f_path, log=False):
    """
    Open a C3D file.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    f_path : str
        Path of input C3D file to open.
    log: bool, optional
        Whether to write logs or not. The default is False.

    Returns
    -------
    int
        0 if the file is opened successfully or 1 if it could not be opened.

    """
    if log: logger.debug(f'Opening a file "{f_path}"')
    if not os.path.exists(f_path):
        if log: logger.error('File path does not exist!')
        return False
    ret = itf.Open(f_path, 3)
    if ret == 0:
        if log: logger.info(f'File is opened successfully.')
        return True
    else:
        if log: logger.info(f'File can not be opened.')
        return False

def save_c3d(itf, f_path='', f_type=-1, log=False):
    """
    Save a C3D file.
    
    If 'f_path' is given an empty string, this function will overwrite the opened existing C3D file.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    f_path : str, optional
        Path of output C3D file to save. The default is ''.
    f_type : int, optional
        Type of saving file. -1 means that the data is saved to the existing file type.
        1 for Intel(MS-DOS) format, 2 for DEC format, 3 for SGI format.
    log: bool, optional
        Whether to write logs or not. The default is False.        

    Returns
    -------
    bool
        True or False.

    """
    if log: logger.debug(f'Saving a file "{f_path}"')
    ret = itf.SaveFile(f_path, f_type)
    if ret == 1:
        if log: logger.info(f'File is successfully saved.')
        return True
    else:
        if log: logger.info(f'File can not be saved.')
        return False
    return 

def close_c3d(itf, log=False):
    """
    Close a C3D file that has been previously opened and releases the memory.
    
    This function does not automatically save the C3D file.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.

    Returns
    -------
    NoneType
        None.

    """
    if log: logger.info(f'File is closed.')
    return itf.Close()


def get_file_type(itf):
    """
    Return the file type of an open C3D file.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.

    Returns
    -------
    str
        File type.

    """
    dict_file_type = {1:'INTEL', 2:'DEC', 3:'SGI'}
    return dict_file_type.get(itf.GetFileType(), None)

def get_data_type(itf):
    """
    Return the data type of an open C3D file.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.

    Returns
    -------
    str
        Data type.

    """
    dict_data_type = {1:'INTEGER', 2:'REAL'}
    return dict_data_type.get(itf.GetDataType(), None)

def get_dict_header(itf):
    """
    Return the summarization of the C3D header information.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.

    Returns
    -------
    dict_header : dict
        Dictionary of the C3D header information.

    """
    dict_file_type = {1:'INTEL', 2:'DEC', 3:'SGI'}
    dict_data_type = {1:'INTEGER', 2:'REAL'}
    dict_header = {}
    dict_header['FILE_TYPE'] = dict_file_type.get(itf.GetFileType(), None)
    dict_header['DATA_TYPE'] = dict_data_type.get(itf.GetDataType(), None)
    dict_header['NUM_3D_POINTS'] = np.int32(itf.GetNumber3DPoints())
    dict_header['NUM_ANALOG_CHANNELS'] = np.int32(itf.GetAnalogChannels())
    dict_header['FIRST_FRAME'] = np.int32(itf.GetVideoFrameHeader(0))
    dict_header['LAST_FRAME'] = np.int32(itf.GetVideoFrameHeader(1))
    dict_header['START_RECORD'] = np.int32(itf.GetStartingRecord())
    dict_header['VIDEO_FRAME_RATE'] = np.float32(itf.GetVideoFrameRate())
    dict_header['ANALOG_VIDEO_RATIO'] = np.int32(itf.GetAnalogVideoRatio())
    dict_header['ANALOG_FRAME_RATE'] = np.float32(itf.GetVideoFrameRate()*itf.GetAnalogVideoRatio())
    dict_header['MAX_INTERPOLATION_GAP'] = np.int32(itf.GetMaxInterpolationGap())
    dict_header['3D_SCALE_FACTOR'] = np.float32(itf.GetHeaderScaleFactor())
    return dict_header

def get_dict_groups(itf):
    """
    Return the dictionary of the groups.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.

    Returns
    -------
    dict_grps : dict
        Dictionary of the C3D header information.

    """
    dict_dtype = {-1:str, 1:np.int8, 2:np.int32, 4:np.float32}
    dict_grps = {}
    dict_grp_names = {}
    n_grps = itf.GetNumberGroups()
    for i in range(n_grps):
        grp_name = itf.GetGroupName(i)
        grp_number = itf.GetGroupNumber(i)
        dict_grp_names.update({np.absolute(grp_number, dtype=np.int): grp_name})
        dict_grps[grp_name] = {}
    n_params = itf.GetNumberParameters()
    for i in range(n_params):
        par_num = itf.GetParameterNumber(i)
        grp_name = dict_grp_names[par_num]
        par_name = itf.GetParameterName(i)
        par_len = itf.GetParameterLength(i)
        par_type = itf.GetParameterType(i)
        data_type = dict_dtype.get(par_type, None)
        par_data = []
        if grp_name=='ANALOG' and par_name=='OFFSET':
            sig_format = get_analog_format(itf)
            is_sig_unsigned = (sig_format is not None) and (sig_format.upper()=='UNSIGNED')
            pre_dtype = [np.int16, np.uint16][is_sig_unsigned]
            for j in range(par_len):
                par_data.append(pre_dtype(itf.GetParameterValue(i, j)))
        else:
            for j in range(par_len):
                par_data.append(itf.GetParameterValue(i, j))
        dict_grps[grp_name][par_name] = data_type(par_data[0]) if len(par_data)==1 else np.asarray(par_data, dtype=data_type)
    return dict_grps

def get_first_frame(itf):
    """
    Give you the first frame of video data from an open C3D file.
    
    This information is usually taken from the header record of the file.
    However, if the TRIAL:ACTUAL_START_FIELD and TRIAL:ACTUAL_END_FIELD parameters are present,
    the values from those parameters are used.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.

    Returns
    -------
    int
        The first 3D frame number.

    """
    return np.int32(itf.GetVideoFrame(0))

def get_last_frame(itf):
    """
    Give you the last frame of video data from an open C3D file.
    
    This information is usually taken from the header record of the file.
    However, if the TRIAL:ACTUAL_START_FIELD and TRIAL:ACTUAL_END_FIELD parameters are present,
    the values from those parameters are used.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.

    Returns
    -------
    int
        The last 3D frame number.

    """
    return np.int32(itf.GetVideoFrame(1))

def get_num_frames(itf):
    """
    Get the total number of frames in an open C3D file.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.

    Returns
    -------
    int
        The total number of 3D frames.

    """
    return np.int32(get_last_frame(itf)-get_first_frame(itf)+1)

def check_frame_range_valid(itf, start_frame, end_frame, msg=False):
    """
    Check the validity of input start and end frames.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    start_frame : int or None
        Input start frame.
    end_frame : int or None
        Int end frame.
    msg : bool, optional
        Whether to print messages or not. The default is False.

    Returns
    -------
    bool
        DESCRIPTION.
    TYPE
        DESCRIPTION.
    TYPE
        DESCRIPTION.

    """
    first_fr = get_first_frame(itf)
    last_fr = get_last_frame(itf)
    if start_frame is None:
        start_fr = first_fr
    else:
        if start_frame < first_fr:
            if msg: print(f"'start_frame' should be equal or greater than {first_fr}!")
            return False, None, None
        start_fr = start_frame
    if end_frame is None:
        end_fr = last_fr
    else:
        if end_frame > last_fr:
            if msg: print(f"'end_frame' should be equal or less than {last_fr}!")
            return False, None, None
        end_fr = end_frame
    if not (start_fr < end_fr):
        if msg: print(f"Please provide a correct combination of 'start_frame' and 'end_frame'!")
        return False, None, None
    return True, start_fr, end_fr    

def get_video_fps(itf):
    """
    Return the 3D point sample rate in Hertz as read from the C3D file header.
    
    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.

    Returns
    -------
    float
        Video frame rate in Hz from the header.

    """
    return np.float32(itf.GetVideoFrameRate())

def get_analog_video_ratio(itf):
    """
    Return the number of analog frames stored for each video frame in the C3D file.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.

    Returns
    -------
    int
        The number of analog frames collected per video frame.

    """
    return np.int32(itf.GetAnalogVideoRatio())

def get_analog_fps(itf):
    """
    Return the analog sample rate in Hertz in the C3D file.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.

    Returns
    -------
    float
        Analog sample rate in Hz.

    """
    return np.float32(get_video_fps(itf)*np.float32(get_analog_video_ratio(itf)))

def get_video_frames(itf):
    """
    Return an integer-type numpy array that contains the video frame numbers between the start and the end frames.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.

    Returns
    -------
    frs : numpy array
        An integer-type numpy array of the video frame numbers.

    """
    start_fr = get_first_frame(itf)
    end_fr = get_last_frame(itf)
    n_frs = end_fr-start_fr+1
    frs = np.linspace(start=start_fr, stop=end_fr, num=n_frs, dtype=np.int32)
    return frs

def get_analog_frames(itf):
    """
    Return a float-type numpy array that contains the analog frame numbers.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.

    Returns
    -------
    frs : numpy array
        A float-type numpy array of the analog frame numbers.

    """
    av_ratio = get_analog_video_ratio(itf)
    start_fr = np.float32(get_first_frame(itf))
    end_fr = np.float32(get_last_frame(itf))+np.float32(av_ratio-1)/np.float32(av_ratio)
    analog_steps = get_num_frames(itf)*av_ratio
    frs = np.linspace(start=start_fr, stop=end_fr, num=analog_steps, dtype=np.float32)
    return frs

def get_video_times(itf, from_zero=True):
    """
    Return a float-type numpy array that contains the times corresponding to the video frame numbers.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.

    Returns
    -------
    t : numpy array
        A float-type numpy array of the times corresponding to the video frame numbers.

    """
    start_fr = get_first_frame(itf)
    end_fr = get_last_frame(itf)
    vid_fps = get_video_fps(itf)
    offset_fr = start_fr if from_zero else 0
    start_t = np.float32(start_fr-offset_fr)/vid_fps
    end_t = np.float32(end_fr-offset_fr)/vid_fps
    vid_steps = get_num_frames(itf)
    t = np.linspace(start=start_t, stop=end_t, num=vid_steps, dtype=np.float32)
    return t

def get_analog_times(itf, from_zero=True):
    """
    Return a float-type array that contains the times corresponding to the analog frame numbers.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.

    Returns
    -------
    t : numpy array
        A float-type numpy array of the times corresponding to the analog frame numbers.

    """
    start_fr = get_first_frame(itf)
    end_fr = get_last_frame(itf)
    vid_fps = get_video_fps(itf)
    analog_fps = get_analog_fps(itf)
    av_ratio = get_analog_video_ratio(itf)
    offset_fr = start_fr if from_zero else 0
    start_t = np.float32(start_fr-offset_fr)/vid_fps
    end_t = np.float32(end_fr-offset_fr)/vid_fps+np.float32(av_ratio-1)/analog_fps
    analog_steps = get_num_frames(itf)*av_ratio
    t = np.linspace(start=start_t, stop=end_t, num=analog_steps, dtype=np.float32)
    return t

def get_video_times_subset(itf, sel_masks):
    """
    Return a subset of the video frame time array.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    sel_masks : list or numpy array
        list or numpy array of boolean for boolean array indexing.

    Returns
    -------
    numpy array
        A subset of the video frame time array.

    """
    return get_video_times(itf)[sel_masks]

def get_analog_times_subset(itf, sel_masks):
    """
    Return a subset of the analog frame time array.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    sel_masks : list or numpy array
        list or numpy array of boolean for boolean array indexing.

    Returns
    -------
    numpy array
        A subset of the analog frame time array.

    """
    return get_analog_times(itf)[sel_masks]

def get_marker_names(itf):
    """
    Return a string-type list of the marker names from an open C3D file.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.

    Returns
    -------
    mkr_names : list or None
        A string-type list that contains the marker names.
        None if there is no POINT:LABELS parameter.
        None if there is no item in the POINT:LABELS parameter.
        
    """
    mkr_names = []
    idx_pt_labels = itf.GetParameterIndex('POINT', 'LABELS')
    if idx_pt_labels == -1: return None
    n_pt_labels = itf.GetParameterLength(idx_pt_labels)
    if n_pt_labels < 1: return None
    idx_pt_used = itf.GetParameterIndex('POINT', 'USED')
    if idx_pt_used == -1: return None
    n_pt_used = itf.GetParameterValue(idx_pt_used, 0)
    if n_pt_used < 1: return None
    for i in range(n_pt_labels):
        if i < n_pt_used:
            mkr_names.append(itf.GetParameterValue(idx_pt_labels, i))
    return mkr_names

def get_marker_index(itf, mkr_name, msg=False):
    """
    Return the index of given marker name in an open C3D file.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    mkr_name : str
        Marker name.
    msg : bool, optional
        Whether to print messages or not. The default is False.

    Returns
    -------
    mkr_idx : int or None
        Marker index in the C3D file.
        None if there is no POINT:LABELS parameter.
        None if there is no item in the POINT:LABELS parameter.
        -1 if there is no corresponding marker with 'mkr_name' in the POINT:LABELS parameter.

    """
    idx_pt_labels = itf.GetParameterIndex('POINT', 'LABELS')
    if idx_pt_labels == -1: return None
    n_pt_labels = itf.GetParameterLength(idx_pt_labels)
    if n_pt_labels < 1: return None
    idx_pt_used = itf.GetParameterIndex('POINT', 'USED')
    if idx_pt_used == -1: return None
    n_pt_used = itf.GetParameterValue(idx_pt_used, 0)
    if n_pt_used < 1: return None
    mkr_idx = -1
    for i in range(n_pt_labels):
        if i < n_pt_used:
            tgt_name = itf.GetParameterValue(idx_pt_labels, i)
            if tgt_name == mkr_name:
                mkr_idx = i
                break  
    if mkr_idx == -1:
        if msg: print("There is no %s marker in this C3D file!" % mkr_name)
    return mkr_idx

def get_marker_unit(itf):
    """
    Return the unit of the marker coordinate values in an open C3D file.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.

    Returns
    -------
    unit : str or None
        The unit of the marker coordinate values.
        None if there is no POINT:UNITS parameter.
        None if there is no item in the POINT:UNITS parameter.

    """
    idx_pt_units = itf.GetParameterIndex('POINT', 'UNITS')
    if idx_pt_units == -1: return None
    n_items = itf.GetParameterLength(idx_pt_units)
    if n_items < 1: return None
    unit = itf.GetParameterValue(idx_pt_units, n_items-1)
    return unit

def get_marker_scale(itf):
    """
    Return the marker scale in an open C3D file.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.

    Returns
    -------
    scale : float or None
        The scale factor for marker coordinate values.
        None if there is no POINT:SCALE parameter.
        None if there is no item in the POINT:SCALE parameter.
    
    """
    idx_pt_scale = itf.GetParameterIndex('POINT', 'SCALE')
    if idx_pt_scale == -1: return None
    n_items = itf.GetParameterLength(idx_pt_scale)
    if n_items < 1: return None
    scale = np.float32(itf.GetParameterValue(idx_pt_scale, n_items-1))
    return scale

def get_marker_data(itf, mkr_name, blocked_nan=False, start_frame=None, end_frame=None, msg=False):
    """
    Return the scaled marker coordinate values and the residuals in an open C3D file.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    mkr_name : str
        Marker name.
    blocked_nan : bool, optional
        Whether to set the coordinates of blocked frames as nan. The default is False.
    start_frame: None or int, optional
        User-defined start frame.
    end_frame: None or int, optional
        User-defined end frame.
    msg : bool, optional
        Whether to print messages or not. The default is False.        

    Returns
    -------
    mkr_data : numpy array or None
        2D numpy array (n, 4), where n is the number of frames in the output.
        For each row, the first three columns contains the x, y, z coordinates of the marker at each frame.
        For each row, The last (fourth) column contains the residual value.
        None if there is no corresponding marker name in the C3D file.
        
    """
    mkr_idx = get_marker_index(itf, mkr_name, msg)
    if mkr_idx == -1: return None
    fr_check, start_fr, end_fr = check_frame_range_valid(itf, start_frame, end_frame, msg)
    if not fr_check: return None
    n_frs = end_fr-start_fr+1
    mkr_data = np.full((n_frs, 4), np.nan, dtype=np.float32)
    for i in range(3):
        mkr_data[:,i] = np.array(itf.GetPointDataEx(mkr_idx, i, start_fr, end_fr, '1'), dtype=np.float32)
    mkr_data[:,3] = np.array(itf.GetPointResidualEx(mkr_idx, start_fr, end_fr), dtype=np.float32)
    if blocked_nan:
        mkr_null_masks = np.where(np.isclose(mkr_data[:,3], -1), True, False)
        mkr_data[mkr_null_masks,0:3] = np.nan 
    return mkr_data

def get_marker_pos(itf, mkr_name, scaled=True, blocked_nan=False, start_frame=None, end_frame=None, msg=False):
    """
    Return the scaled marker coordinate values in an open C3D file.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    mkr_name : str
        Marker name.
    scaled : bool, optional
        Whether to return the scaled coordinate values or not. The default is True.
    blocked_nan : bool, optional
        Whether to set the coordinates of blocked frames as nan. The default is False.
    start_frame: None or int, optional
        User-defined start frame.
    end_frame: None or int, optional
        User-defined end frame.
    msg : bool, optional
        Whether to print messages or not. The default is False.        

    Returns
    -------
    mkr_data : numpy array or None
        2D numpy array (n, 3), where n is the number of frames in the output.
        If 'blocked_nan' is set as True, then the corresponding row in the 'mkr_data' will be filled with nan.
        None if there is no corresponding marker name in the C3D file.
        
    Notes
    -----
    This is a wrapper function of GetPointDataEx() in the C3DServer SDK with 'byScaled' parameter as 1.
    
    """
    mkr_idx = get_marker_index(itf, mkr_name, msg)
    if mkr_idx == -1: return None
    fr_check, start_fr, end_fr = check_frame_range_valid(itf, start_frame, end_frame, msg)
    if not fr_check: return None
    n_frs = end_fr-start_fr+1
    mkr_scale = get_marker_scale(itf)
    is_c3d_float = mkr_scale < 0
    is_c3d_float2 = [False, True][itf.GetDataType()-1]
    if is_c3d_float != is_c3d_float2:
        if msg: print(f"C3D data type is determined by the POINT:SCALE parameter.")
    mkr_dtype = [[[np.int16, np.float32][is_c3d_float], np.float32][scaled], np.float32][blocked_nan]
    mkr_data = np.zeros((n_frs, 3), dtype=mkr_dtype)
    b_scaled = ['0', '1'][scaled]
    for i in range(3):
        mkr_data[:,i] = np.array(itf.GetPointDataEx(mkr_idx, i, start_fr, end_fr, b_scaled), dtype=mkr_dtype)
    if blocked_nan:
        mkr_resid = np.array(itf.GetPointResidualEx(mkr_idx, start_fr, end_fr), dtype=np.float32)
        mkr_null_masks = np.where(np.isclose(mkr_resid, -1), True, False)
        mkr_data[mkr_null_masks,:] = np.nan  
    return mkr_data

def get_marker_pos2(itf, mkr_name, scaled=True, blocked_nan=False, start_frame=None, end_frame=None, msg=False):
    """
    Return the scaled marker coordinate values in an open C3D file.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    mkr_name : str
        Marker name.
    scaled : bool, optional
        Whether to return the scaled coordinate values or not. The default is True.        
    blocked_nan : bool, optional
        Whether to set the coordinates of blocked frames as nan. The default is False.
    start_frame: None or int, optional
        User-defined start frame.
    end_frame: None or int, optional
        User-defined end frame.
    msg : bool, optional
        Whether to print messages or not. The default is False.        

    Returns
    -------
    mkr_data : numpy array or None
        2D numpy array (n, 3), where n is the number of frames in the output.
        If 'blocked_nan' is set as True, then the corresponding row in the 'mkr_data' will be filled with nan.
        None if there is no corresponding marker name in the C3D file.
        
    Notes
    -----
    This is a wrapper function of GetPointDataEx() in the C3DServer SDK with 'byScaled' parameter as 0.        
    With this 'byScaled' as 0, GetPointDataEx() function will return un-scaled data if data is stored as integer format.
    Integer-format C3D files can be indentified by checking whether the scale value is positive or not. 
    For these integer-format C3D files, POINT:SCALE parameter will be used for scaling the coordinate values.
    This function returns the manual multiplication between un-scaled values from GetPointDataEx() and POINT:SCALE parameter.
    Ideally, get_marker_pos2() should return as same results as get_marker_pos() function.
    """
    mkr_idx = get_marker_index(itf, mkr_name, msg)
    if mkr_idx == -1: return None
    fr_check, start_fr, end_fr = check_frame_range_valid(itf, start_frame, end_frame, msg)
    if not fr_check: return None
    n_frs = end_fr-start_fr+1
    mkr_scale = get_marker_scale(itf)
    is_c3d_float = mkr_scale < 0
    is_c3d_float2 = [False, True][itf.GetDataType()-1]
    if is_c3d_float != is_c3d_float2:
        if msg: print(f"C3D data type is determined by the POINT:SCALE parameter.")
    mkr_dtype = [[[np.int16, np.float32][is_c3d_float], np.float32][scaled], np.float32][blocked_nan]
    mkr_data = np.zeros((n_frs, 3), dtype=mkr_dtype)
    scale_size = [np.fabs(mkr_scale), np.float32(1.0)][is_c3d_float]
    for i in range(3):
        if scaled:
            mkr_data[:,i] = np.array(itf.GetPointDataEx(mkr_idx, i, start_fr, end_fr, '0'), dtype=mkr_dtype)*scale_size
        else:
            mkr_data[:,i] = np.array(itf.GetPointDataEx(mkr_idx, i, start_fr, end_fr, '0'), dtype=mkr_dtype)
    if blocked_nan:    
        mkr_resid = np.array(itf.GetPointResidualEx(mkr_idx, start_fr, end_fr), dtype=np.float32)
        mkr_null_masks = np.where(np.isclose(mkr_resid, -1), True, False)
        mkr_data[mkr_null_masks,:] = np.nan            
    return mkr_data

def get_marker_residual(itf, mkr_name, start_frame=None, end_frame=None, msg=False):
    """
    Return the 3D residual values of a specified marker in an open C3D file.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    mkr_name : str
        Marker name.
    start_frame: None or int, optional
        User-defined start frame.
    end_frame: None or int, optional
        User-defined end frame.
    msg : bool, optional
        Whether to print messages or not. The default is False.        

    Returns
    -------
    mkr_resid : numpy array or None
        1D numpy array (n,), where n is the number of frames in the output.

    """
    mkr_idx = get_marker_index(itf, mkr_name, msg)
    if mkr_idx == -1: return None
    fr_check, start_fr, end_fr = check_frame_range_valid(itf, start_frame, end_frame, msg)
    if not fr_check: return None
    mkr_resid = np.array(itf.GetPointResidualEx(mkr_idx, start_fr, end_fr), dtype=np.float32)
    return mkr_resid

def get_all_marker_pos_df(itf, blocked_nan=False, msg=False):
    """
    Return all marker's coordinate values as a form of pandas frame.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    blocked_nan : bool, optional
        Whether to set the coordinates of blocked frames as nan. The default is False.
    msg : bool, optional
        Whether to print messages or not. The default is False.

    Returns
    -------
    df : pandas dataframe
        Dataframe that contains all marker's coordinate values.

    """
    mkr_names = get_marker_names(itf)
    n_frs = get_num_frames(itf)
    mkr_coord_names = [a+'_'+b for a in mkr_names for b in ['X', 'Y', 'Z']]
    df = pd.DataFrame(np.zeros((n_frs, len(mkr_coord_names))), columns=mkr_coord_names)
    for mkr_name in mkr_names:
        mkr_data = get_marker_data(itf, mkr_name, blocked_nan, msg)
        mkr_coords = mkr_data[:,0:3] 
        mkr_name_xyz = [mkr_name+'_'+c for c in ['X', 'Y', 'Z']]
        df[mkr_name_xyz] = mkr_coords[:,0:3]
    return df

def get_all_marker_pos_arr2d(itf, blocked_nan=False, msg=False):
    """
    Return all marker's coordinate values as a form of 2D numpy array.

    Parameters
    ----------
    itf :  win32com.client.CDispatch
        COM interface of the C3DServer.
    blocked_nan : bool, optional
        Whether to set the coordinates of blocked frames as nan. The default is False.
    msg : bool, optional
        Whether to print messages or not. The default is False.

    Returns
    -------
    mkr_coords_all : numpy array
        2D numpy array (n, m*3) where n is the number of target frames and m is the number of C3D file markers.

    """
    mkr_names = get_marker_names(itf)
    n_frs = get_num_frames(itf)
    mkr_coords_all = np.zeros((n_frs, len(mkr_names)*3), dtype=np.float32)
    for idx, mkr_name in enumerate(mkr_names):
        mkr_data = get_marker_data(itf, mkr_name, blocked_nan, msg)
        mkr_coords_all[:,3*idx+0:3*idx+3] = mkr_data[:,0:3]
    return mkr_coords_all

def get_all_marker_pos_arr3d(itf, blocked_nan=False, msg=False):
    """
    Return all marker's coordinate values as a form of 3D numpy array.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    blocked_nan : bool, optional
        Whether to set the coordinates of blocked frames as nan. The default is False.
    msg : bool, optional
        Whether to print messages or not. The default is False.

    Returns
    -------
    mkr_coords_all : numpy array
        3D numpy array (n, m, 3) where n is the number of target frames and m is the number of C3D file markers.

    """
    mkr_names = get_marker_names(itf)
    n_frs = get_num_frames(itf)
    mkr_coords_all = np.zeros((n_frs, len(mkr_names), 3), dtype=np.float32)
    for idx, mkr_name in enumerate(mkr_names):
        mkr_data = get_marker_data(itf, mkr_name, blocked_nan, msg)
        mkr_coords = mkr_data[:,0:3]
        mkr_coords_all[:,idx,0:3] = mkr_coords[:,0:3]
    return mkr_coords_all

def get_dict_markers(itf, blocked_nan=False, residual=False, mask=False, time=False, tgt_mkr_names=None, start_frame=None, end_frame=None, msg=False):
    fr_check, start_fr, end_fr = check_frame_range_valid(itf, start_frame, end_frame, msg)
    if not fr_check: return None
    n_frs = end_fr-start_fr+1
    idx_pt_labels = itf.GetParameterIndex('POINT', 'LABELS')
    if idx_pt_labels == -1: idx_pt_labels = itf.GetParameterIndex('POINT', 'LABELS1')
    if idx_pt_labels == -1: idx_pt_labels = itf.GetParameterIndex('POINT', 'LABELS2')
    if idx_pt_labels == -1: idx_pt_labels = itf.GetParameterIndex('POINT', 'LABELS3')
    if idx_pt_labels == -1:
        if msg: print(f"POINT:LABELS parameter does not exist!")
        return None
    n_pt_labels = itf.GetParameterLength(idx_pt_labels)
    if n_pt_labels < 1:
        if msg: print(f"No item under the POINT:LABELS parameter!")
        return None
    idx_pt_used = itf.GetParameterIndex('POINT', 'USED')
    if idx_pt_used == -1:
        if msg: print(f"POINT:USED parameter does not exist!")
        return None        
    n_pt_used = itf.GetParameterValue(idx_pt_used, 0)
    if n_pt_used < 1:
        if msg: print(f"POINT:USED is zero!")
        return None
    dict_pts = {}
    mkr_names = []
    dict_pts.update({'DATA':{}})
    dict_pts['DATA'].update({'POS':{}})
    if residual: dict_pts['DATA'].update({'RESID': {}})
    if mask: dict_pts['DATA'].update({'MASK': {}})
    for i in range(n_pt_labels):
        if i < n_pt_used:
            mkr_name = itf.GetParameterValue(idx_pt_labels, i)
            if (tgt_mkr_names is not None) and (mkr_name not in tgt_mkr_names): continue
            mkr_names.append(mkr_name)
            mkr_data = np.zeros((n_frs, 3), dtype=np.float32)
            for j in range(3):
                mkr_data[:,j] = np.array(itf.GetPointDataEx(i, j, start_fr, end_fr, '1'), dtype=np.float32)
            if blocked_nan or residual:
                mkr_resid = np.array(itf.GetPointResidualEx(i, start_fr, end_fr), dtype=np.float32)
            if blocked_nan:
                mkr_null_masks = np.where(np.isclose(mkr_resid, -1), True, False)
                mkr_data[mkr_null_masks,:] = np.nan
            dict_pts['DATA']['POS'].update({mkr_name: mkr_data})
            if residual:
                dict_pts['DATA']['RESID'].update({mkr_name: mkr_resid})
            if mask:
                mkr_mask = np.array(itf.GetPointMaskEx(i, start_fr, end_fr), dtype=str)
                dict_pts['DATA']['MASK'].update({mkr_name: mkr_mask})
    dict_pts.update({'LABELS': np.array(mkr_names, dtype=str)})
    idx_pt_units = itf.GetParameterIndex('POINT', 'UNITS')
    if idx_pt_units != -1:
        n_pt_units = itf.GetParameterLength(idx_pt_units)
        if n_pt_units == 1:
            unit = itf.GetParameterValue(idx_pt_units, 0)
            dict_pts.update({'UNITS': unit})
    idx_pt_rate = itf.GetParameterIndex('POINT', 'RATE')
    if idx_pt_rate != -1:
        n_pt_rate = itf.GetParameterLength(idx_pt_rate)
        if n_pt_rate == 1:
            rate = np.float32(itf.GetParameterValue(idx_pt_rate, 0))
            dict_pts.update({'RATE': rate})
    dict_pts.update({'FRAMES': get_video_frames(itf)})
    if time: dict_pts.update({'TIME': get_video_times(itf)})
    return dict_pts

def get_dict_forces(itf, time=False, start_frame=None, end_frame=None, msg=False):
    fr_check, start_fr, end_fr = check_frame_range_valid(itf, start_frame, end_frame, msg)
    if not fr_check: return None
    idx_force_used = itf.GetParameterIndex('FORCE_PLATFORM', 'USED')
    if idx_force_used == -1: 
        if msg: print(f"FORCE_PLATFORM:USED parameter does not exist!")
        return None
    n_force_used = itf.GetParameterValue(idx_force_used, 0)
    if n_force_used < 1:
        if msg: print(f"FORCE_PLATFORM:USED is zero!")
        return None
    idx_force_chs = itf.GetParameterIndex('FORCE_PLATFORM', 'CHANNEL')
    if idx_force_chs == -1: 
        if msg: print(f"FORCE_PLATFORM:CHANNEL parameter does not exist!")
        return None
    idx_analog_units = itf.GetParameterIndex('ANALOG', 'UNITS')
    idx_analog_labels = itf.GetParameterIndex('ANALOG', 'LABELS')
    idx_analog_scale = itf.GetParameterIndex('ANALOG', 'SCALE')
    idx_analog_offset = itf.GetParameterIndex('ANALOG', 'OFFSET')
    gen_scale = get_analog_gen_scale(itf)
    sig_format = get_analog_format(itf)
    is_sig_unsigned = (sig_format is not None) and (sig_format.upper()=='UNSIGNED')
    offset_dtype = [np.int16, np.uint16][is_sig_unsigned]
    dict_forces = {}
    force_names = []
    force_units = []
    dict_forces.update({'DATA':{}})
    n_force_chs = itf.GetParameterLength(idx_force_chs)
    for i in range(n_force_chs):
        ch_num = itf.GetParameterValue(idx_force_chs, i)
        ch_idx = ch_num-1
        ch_name = itf.GetParameterValue(idx_analog_labels, ch_idx)
        force_names.append(ch_name)
        ch_unit = itf.GetParameterValue(idx_analog_units, ch_idx)
        force_units.append(ch_unit)
        sig_scale = np.float32(itf.GetParameterValue(idx_analog_scale, ch_idx))
        sig_offset = np.float32(offset_dtype(itf.GetParameterValue(idx_analog_offset, ch_idx)))
        sig_val = (np.array(itf.GetAnalogDataEx(ch_idx, start_fr, end_fr, '0', 0, 0, '0'), dtype=np.float32)-sig_offset)*sig_scale*gen_scale
        dict_forces['DATA'].update({ch_name: sig_val})
    dict_forces.update({'LABELS': np.array(force_names, dtype=str)})
    dict_forces.update({'UNITS': np.array(force_units, dtype=str)})
    idx_analog_rate = itf.GetParameterIndex('ANALOG', 'RATE')
    if idx_analog_rate != -1:
        n_analog_rate = itf.GetParameterLength(idx_analog_rate)
        if n_analog_rate == 1:
            dict_forces.update({'RATE': np.float32(itf.GetParameterValue(idx_analog_rate, 0))})
    dict_forces.update({'FRAMES': get_analog_frames(itf)})
    if time: dict_forces.update({'TIME': get_analog_times(itf)})
    return dict_forces

def get_analog_names(itf):
    """
    Return a string list of the analog channel names in an open C3D file.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.

    Returns
    -------
    sig_names : list
        String list that contains the analog channel names.

    """
    sig_names = []
    idx_anl_labels = itf.GetParameterIndex('ANALOG', 'LABELS')
    if idx_anl_labels == -1: return None
    n_anl_labels = itf.GetParameterLength(idx_anl_labels)
    if n_anl_labels < 1: return None
    idx_anl_used = itf.GetParameterIndex('ANALOG', 'USED')
    n_anl_used = itf.GetParameterValue(idx_anl_used, 0)    
    for i in range(n_anl_labels):
        if i < n_anl_used:
            sig_names.append(itf.GetParameterValue(idx_anl_labels, i))
    return sig_names

def get_analog_index(itf, sig_name, msg=False):
    """
    Get the index of analog channel.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    sig_name : str
        Analog channel name.
    msg : bool, optional
        Whether to print messages or not. The default is False.

    Returns
    -------
    sig_idx : int
        Index of the analog channel.

    """
    idx_anl_labels = itf.GetParameterIndex('ANALOG', 'LABELS')
    if idx_anl_labels == -1: return None
    n_anl_labels = itf.GetParameterLength(idx_anl_labels)
    if n_anl_labels < 1: return None
    idx_anl_used = itf.GetParameterIndex('ANALOG', 'USED')
    n_anl_used = itf.GetParameterValue(idx_anl_used, 0)    
    sig_idx = -1    
    for i in range(n_anl_labels):
        if i < n_anl_used:
            tgt_name = itf.GetParameterValue(idx_anl_labels, i)
            if tgt_name == sig_name:
                sig_idx = i
                break        
    if sig_idx == -1:
        if msg: print(f"No {sig_name} analog channel in this C3D file!")
    return sig_idx

def get_analog_gen_scale(itf):
    """
    Return the general (common) scaling factor for analog channels in an open C3D file.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.

    Returns
    -------
    gen_scale : float or None
        The general (common) scaling factor for analog channels.
        None if there is no ANALOG:GEN_SCALE parameter in the C3D file.
        None if there is no item in the ANALOG:GEN_SCALE parameter.
        
    """
    par_idx = itf.GetParameterIndex('ANALOG', 'GEN_SCALE')
    if par_idx == -1: return None
    n_items = itf.GetParameterLength(par_idx)
    if n_items < 1: return None
    gen_scale = np.float32(itf.GetParameterValue(par_idx, n_items-1))
    return gen_scale

def get_analog_format(itf):
    """
    Return the format of analog channels in an open C3D file.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.

    Returns
    -------
    sig_format : str or None
        Format of the analog channels.
        None if there is no ANALOG:FORMAT parameter in the C3D file.
        None if there is no item in the ANALOG:FORMAT parameter.
        
    """
    par_idx = itf.GetParameterIndex('ANALOG', 'FORMAT')
    if par_idx == -1: return None
    n_items = itf.GetParameterLength(par_idx)
    if n_items < 1: return None    
    sig_format = itf.GetParameterValue(par_idx, n_items-1)
    return sig_format

def get_analog_unit(itf, sig_name, msg=False):
    """
    Return the unit of an analog channel.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    sig_name : str
        Analog channel name.
    msg : bool, optional
        Whether to print messages or not. The default is False.

    Returns
    -------
    sig_unit : str or None
        Analog channel unit.

    """
    sig_idx = get_analog_index(itf, sig_name, msg)
    if sig_idx == -1: return None
    par_idx = itf.GetParameterIndex('ANALOG', 'UNITS')
    if par_idx == -1: return None
    sig_unit = itf.GetParameterValue(par_idx, sig_idx)
    return sig_unit
    
def get_analog_scale(itf, sig_name, msg=False):
    """
    Return the scale of an analog channel.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    sig_name : str
        Analog channel name.
    msg : bool, optional
        Whether to print messages or not. The default is False.

    Returns
    -------
    sig_scale : float or None
        Analog channel scale.

    """
    sig_idx = get_analog_index(itf, sig_name, msg)
    if sig_idx == -1: return None
    par_idx = itf.GetParameterIndex('ANALOG', 'SCALE')
    if par_idx == -1: return None
    sig_scale = np.float32(itf.GetParameterValue(par_idx, sig_idx))
    return sig_scale
    
def get_analog_offset(itf, sig_name, msg=False):
    """
    Return the offset of an analog channel.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    sig_name : str
        Analog channel name.
    msg : bool, optional
        Whether to print messages or not. The default is False.

    Returns
    -------
    sig_offset : int or None
        Analog channel offset.

    """
    sig_idx = get_analog_index(itf, sig_name, msg)
    if sig_idx == -1: return None
    par_idx = itf.GetParameterIndex('ANALOG', 'OFFSET')
    if par_idx == -1: return None
    sig_format = get_analog_format(itf)
    is_sig_unsigned = (sig_format is not None) and (sig_format.upper()=='UNSIGNED')
    par_dtype = [np.int16, np.uint16][is_sig_unsigned]
    sig_offset = par_dtype(itf.GetParameterValue(par_idx, sig_idx))
    return sig_offset
            
def get_analog_data_unscaled(itf, sig_name, start_frame=None, end_frame=None, msg=False):
    """
    Return the unscaled value of an analog channel.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    sig_name : str
        Analog channel name.
    start_frame : int or None, optional
        Start frame number. The default is None.
    end_frame : int or None, optional
        End frame number. The default is None.
    msg : bool, optional
        Whether to print messages or not. The default is False.

    Returns
    -------
    sig : numpy array or None
        Analog channel value.

    """
    sig_idx = get_analog_index(itf, sig_name, msg)
    if sig_idx == -1: return None
    fr_check, start_fr, end_fr = check_frame_range_valid(itf, start_frame, end_frame, msg)
    if not fr_check: return None
    sig_format = get_analog_format(itf)
    is_sig_unsigned = (sig_format is not None) and (sig_format.upper()=='UNSIGNED')        
    mkr_scale = get_marker_scale(itf)
    is_c3d_float = mkr_scale < 0
    is_c3d_float2 = [False, True][itf.GetDataType()-1]
    if is_c3d_float != is_c3d_float2:
        if msg: print(f"C3D data type is determined by the POINT:SCALE parameter.")
    sig_dtype = [[np.int16, np.uint16][is_sig_unsigned], np.float32][is_c3d_float]
    sig = np.array(itf.GetAnalogDataEx(sig_idx, start_fr, end_fr, '0', 0, 0, '0'), dtype=sig_dtype)
    return sig

def get_analog_data_scaled(itf, sig_name, start_frame=None, end_frame=None, msg=False):
    """
    Return the scale value of an analog channel.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    sig_name : str
        Analog channel name.
    start_frame : int or None, optional
        Start frame number. The default is None.
    end_frame : int or None, optional
        End frame number. The default is None.
    msg : bool, optional
        Whether to print messages or not. The default is False.

    Returns
    -------
    sig : numpy array or None
        Analog channel value.

    """
    sig_idx = get_analog_index(itf, sig_name, msg)
    if sig_idx == -1: return None
    fr_check, start_fr, end_fr = check_frame_range_valid(itf, start_frame, end_frame, msg)
    if not fr_check: return None
    sig = np.array(itf.GetAnalogDataEx(sig_idx, start_fr, end_fr, '1', 0, 0, '0'), dtype=np.float32)
    return sig

def get_analog_data_scaled2(itf, sig_name, start_frame=None, end_frame=None, msg=False):
    """
    Return the scale value of an analog channel.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    sig_name : str
        Analog channel name.
    start_frame : int or None, optional
        Start frame number. The default is None.
    end_frame : int or None, optional
        End frame number. The default is None.
    msg : bool, optional
        Whether to print messages or not. The default is False.

    Returns
    -------
    sig : numpy array or None
        Analog channel value.

    """
    sig_idx = get_analog_index(itf, sig_name, msg)
    if sig_idx == -1: return None
    fr_check, start_fr, end_fr = check_frame_range_valid(itf, start_frame, end_frame, msg)
    if not fr_check: return None
    gen_scale = get_analog_gen_scale(itf)
    sig_scale = get_analog_scale(itf, sig_name)
    sig_offset = np.float32(get_analog_offset(itf, sig_name))
    sig = (np.array(itf.GetAnalogDataEx(sig_idx, start_fr, end_fr, '0', 0, 0, '0'), dtype=np.float32)-sig_offset)*sig_scale*gen_scale
    return sig

def change_marker_name(itf, mkr_name_old, mkr_name_new, msg=False):
    """
    Change the name of a marker.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    mkr_name_old : str
        Old marker name.
    mkr_name_new : str
        New marker name.
    msg : bool, optional
        Whether to print messages or not. The default is False.

    Returns
    -------
    bool
        True or False.

    """
    mkr_idx = get_marker_index(itf, mkr_name_old, msg)
    if mkr_idx == -1: return False
    par_idx = itf.GetParameterIndex('POINT', 'LABELS')
    ret = itf.SetParameterValue(par_idx, mkr_idx, mkr_name_new)
    return [False, True][ret]

def change_analog_name(itf, sig_name_old, sig_name_new, msg=False):
    """
    Change the name of an analog channel.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    sig_name_old : str
        Old analog channel name.
    sig_name_new : str
        New analog channel name.
    msg : bool, optional
        Whether to print messages or not. The default is False.

    Returns
    -------
    bool
        True or False.

    """
    sig_idx = get_analog_index(itf, sig_name_old, msg)
    if sig_idx == -1: return False
    par_idx = itf.GetParameterIndex('ANALOG', 'LABELS')
    ret = itf.SetParameterValue(par_idx, sig_idx, sig_name_new)
    return [False, True][ret]

def add_marker(itf, mkr_name, mkr_coords, msg=False):
    """
    Add a new marker into an open C3D file.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    mkr_name : str
        A new marker name.
    mkr_coords : numpy array
        A numpy array of the marker coordinates.
    msg : bool, optional
        Whether to print messages or not. The default is False.

    Returns
    -------
    bool
        True of False.

    """
    start_fr = get_first_frame(itf)
    n_frs = get_num_frames(itf)
    if mkr_coords.ndim != 2 or mkr_coords.shape[0] != n_frs:
        if msg: print("The dimension of the input is not compatible!")
        return False
    ret = 0    
    # Add an parameter to the 'POINT:LABELS' section
    par_idx_pt_labels = itf.GetParameterIndex('POINT', 'LABELS')
    ret = itf.AddParameterData(par_idx_pt_labels, 1)
    cnt_pt_labels = itf.GetParameterLength(par_idx_pt_labels)
    variant = win32.VARIANT(pythoncom.VT_BSTR, np.string_(mkr_name))
    ret = itf.SetParameterValue(par_idx_pt_labels, cnt_pt_labels-1, variant)
    # Add a null parameter in the 'POINT:DESCRIPTIONS' section
    par_idx_pt_desc = itf.GetParameterIndex('POINT', 'DESCRIPTIONS')
    ret = itf.AddParameterData(par_idx_pt_desc, 1)
    cnt_pt_desc = itf.GetParameterLength(par_idx_pt_desc)
    variant = win32.VARIANT(pythoncom.VT_BSTR, np.string_(mkr_name))
    ret = itf.SetParameterValue(par_idx_pt_desc, cnt_pt_desc-1, variant)
    # Add a marker
    new_mkr_idx = itf.AddMarker()
    cnt_mkrs = itf.GetNumber3DPoints()
    mkr_resid = np.zeros((n_frs, ), dtype=np.float32)
    mkr_masks = np.array(['0000000']*n_frs, dtype = np.string_)
    variant = win32.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R4, np.nan_to_num(mkr_coords[:, 0]))
    ret = itf.SetPointDataEx(cnt_mkrs-1, 0, start_fr, variant)
    variant = win32.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R4, np.nan_to_num(mkr_coords[:, 1]))
    ret = itf.SetPointDataEx(cnt_mkrs-1, 1, start_fr, variant)
    variant = win32.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R4, np.nan_to_num(mkr_coords[:, 2]))
    ret = itf.SetPointDataEx(cnt_mkrs-1, 2, start_fr, variant)
    variant = win32.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R4, mkr_resid)
    ret = itf.SetPointDataEx(cnt_mkrs-1, 3, start_fr, variant)
    variant = win32.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_BSTR, mkr_masks)
    ret = itf.SetPointDataEx(cnt_mkrs-1, 4, start_fr, variant)
    for idx, val in enumerate(mkr_coords[:, 0]):
        if val == 1:
            variant = win32.VARIANT(pythoncom.VT_R4, val)
            ret = itf.SetPointData(cnt_mkrs-1, 0, start_fr+idx, variant)
    for idx, val in enumerate(mkr_coords[:, 1]):
        if val == 1:
            variant = win32.VARIANT(pythoncom.VT_R4, val)
            ret = itf.SetPointData(cnt_mkrs-1, 1, start_fr+idx, variant)
    for idx, val in enumerate(mkr_coords[:, 2]):
        if val == 1:
            variant = win32.VARIANT(pythoncom.VT_R4, val)
            ret = itf.SetPointData(cnt_mkrs-1, 2, start_fr+idx, variant)      
    # Increase the value 'POINT:USED' by the 1
    par_idx_pt_used = itf.GetParameterIndex('POINT', 'USED')
    cnt_pt_used = itf.GetParameterValue(par_idx_pt_used, 0)
    par_idx_pt_labels = itf.GetParameterIndex('POINT', 'LABELS')
    cnt_pt_labels = itf.GetParameterLength(par_idx_pt_labels)
    if cnt_pt_used != cnt_pt_labels:
        ret = itf.SetParameterValue(par_idx_pt_labels, 0, cnt_pt_labels)
    return [False, True][ret]

def add_analog(itf, sig_name, sig_unit, sig_value, sig_scale=1.0, sig_offset=0, sig_gain=0, sig_desc=None, msg=False):
    """
    Add a new analog signal into an open C3D file.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    sig_name : str
        A new analog channel name.
    sig_unit : str
        A new analog channel unit.
    sig_value : numpy array
        A new analog channel value.
    sig_scale : float, optional
        A new analog channel scale. The default is 1.0.
    sig_offset : int, optional
        A new analog channel offset. The default is 0.
    sig_gain : int, optional
        A new analog channel gain. The default is 0.
    sig_desc : str, optional
        A new analog channel description. The default is None.
    msg : bool, optional
        Whether to print messages or not. The default is False.

    Returns
    -------
    bool
        True or False.

    """
    start_fr = get_first_frame(itf)
    n_frs = get_num_frames(itf)
    av_ratio = get_analog_video_ratio(itf)
    if sig_value.ndim!=1 or sig_value.shape[0]!=(n_frs*av_ratio):
        if msg: print("The dimension of the input is not compatible!")
        return False
    # Add an parameter to the 'ANALOG:LABELS' section
    n_idx_analog_labels = itf.GetParameterIndex('ANALOG', 'LABELS')
    ret = itf.AddParameterData(n_idx_analog_labels, 1)
    n_cnt_analog_labels = itf.GetParameterLength(n_idx_analog_labels)
    ret = itf.SetParameterValue(n_idx_analog_labels, n_cnt_analog_labels-1, win32.VARIANT(pythoncom.VT_BSTR, sig_name))
    # Add an parameter to the 'ANALOG:UNITS' section
    n_idx_analog_units = itf.GetParameterIndex('ANALOG', 'UNITS')
    ret = itf.AddParameterData(n_idx_analog_units, 1)
    n_cnt_analog_units = itf.GetParameterLength(n_idx_analog_units)
    ret = itf.SetParameterValue(n_idx_analog_units, n_cnt_analog_units-1, win32.VARIANT(pythoncom.VT_BSTR, sig_unit))      
    # Add an parameter to the 'ANALOG:SCALE' section
    n_idx_analog_scale = itf.GetParameterIndex('ANALOG', 'SCALE')
    ret = itf.AddParameterData(n_idx_analog_scale, 1)
    n_cnt_analog_scale = itf.GetParameterLength(n_idx_analog_scale)
    ret = itf.SetParameterValue(n_idx_analog_scale, n_cnt_analog_scale-1, win32.VARIANT(pythoncom.VT_R4, sig_scale))
    # Add an parameter to the 'ANALOG:OFFSET' section
    n_idx_analog_offset = itf.GetParameterIndex('ANALOG', 'OFFSET')
    ret = itf.AddParameterData(n_idx_analog_offset, 1)
    n_cnt_analog_offset = itf.GetParameterLength(n_idx_analog_offset)
    ret = itf.SetParameterValue(n_idx_analog_offset, n_cnt_analog_offset-1, win32.VARIANT(pythoncom.VT_I2, sig_offset))
    # Check for 'ANALOG:GAIN' section and add 0 if it exists
    n_idx_analog_gain = itf.GetParameterIndex('ANALOG', 'GAIN')
    if n_idx_analog_gain != -1:
        ret = itf.AddParameterData(n_idx_analog_gain, 1)
        n_cnt_analog_gain = itf.GetParameterLength(n_idx_analog_gain)
        ret = itf.SetParameterValue(n_idx_analog_gain, n_cnt_analog_gain-1, win32.VARIANT(pythoncom.VT_I2, sig_gain))    
    # Add an parameter to the 'ANALOG:DESCRIPTIONS' section
    n_idx_analog_desc = itf.GetParameterIndex('ANALOG', 'DESCRIPTIONS')
    ret = itf.AddParameterData(n_idx_analog_desc, 1)
    n_cnt_analog_desc = itf.GetParameterLength(n_idx_analog_desc)
    sig_desc_in = sig_name if sig_desc is None else sig_desc
    ret = itf.SetParameterValue(n_idx_analog_desc, n_cnt_analog_desc-1, win32.VARIANT(pythoncom.VT_BSTR, sig_desc_in))
    # Create an analog channel
    n_idx_new_analog_ch = itf.AddAnalogChannel()
    n_cnt_analog_chs = itf.GetAnalogChannels()
    ret = itf.SetAnalogDataEx(n_idx_new_analog_ch, start_fr, win32.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R4, sig_value))
    # Increase the value 'ANALOG:USED' by the 1
    n_idx_analog_used = itf.GetParameterIndex('ANALOG', 'USED')
    n_cnt_analog_used = itf.GetParameterValue(n_idx_analog_used, 0)
    n_idx_analog_labels = itf.GetParameterIndex('ANALOG', 'LABELS')
    n_cnt_analog_labels = itf.GetParameterLength(n_idx_analog_labels)
    if n_cnt_analog_used != n_cnt_analog_labels:
        ret = itf.SetParameterValue(n_idx_analog_used, 0, n_cnt_analog_labels)
    return [False, True][ret]

def delete_frames(itf, start_frame, num_frames, msg=False):
    """
    Delete specified frames in an open C3D file.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    start_frame : int
        Start frame number.
    num_frames : int
        Number of frames to be deleted.
    msg : bool, optional
        Whether to print messages or not. The default is False.

    Returns
    -------
    n_frs_updated : int
        Number of the remaining frames in the C3D file.

    """
    if start_frame < get_first_frame(itf):
        if msg: print(f'Given start frame number should be equal or greater than {get_first_frame(itf)} for this C3D file!')
        return None
    elif start_frame >= get_last_frame(itf):
        if msg: print(f'Given start frame number should be less than {get_last_frame(itf)} for this C3D file!')
        return None
    n_frs_updated = itf.DeleteFrames(start_frame, num_frames)
    return n_frs_updated

def update_marker_pos(itf, mkr_name, mkr_coords, msg=False):
    """
    Update the entire marker coordinates.

    Parameters
    ----------
    itf : win32com.client.CDispatch
        COM interface of the C3DServer.
    mkr_name : str
        Marker name.
    mkr_coords : numpy array
        Marker coordinates.
    msg : bool, optional
        Whether to print messages or not. The default is False.

    Returns
    -------
    bool
        True or False.

    """
    mkr_idx = get_marker_index(itf, mkr_name, msg)
    if mkr_idx == -1: return False
    start_fr = get_first_frame(itf)
    n_frs = get_num_frames(itf)
    if mkr_coords.ndim != 2 or mkr_coords.shape[0] != n_frs:
        if msg: print("The dimension of the input is not compatible!")
        return False
    mkr_scale = get_marker_scale(itf)
    is_c3d_float = mkr_scale < 0
    is_c3d_float2 = [False, True][itf.GetDataType()-1]
    if is_c3d_float != is_c3d_float2:
        if msg: print(f"C3D data type is determined by the POINT:SCALE parameter.")
    mkr_dtype = [np.int16, np.float32][is_c3d_float]
    scale_size = [np.fabs(mkr_scale), np.float32(1.0)][is_c3d_float]
    if is_c3d_float:
        mkr_coords_unscaled = np.asarray(mkr_coords, dtype=mkr_dtype)
    else:
        mkr_coords_unscaled = np.asarray(np.round(mkr_coords/scale_size), dtype=mkr_dtype)
    dtype = [pythoncom.VT_I2, pythoncom.VT_R4][is_c3d_float]
    dtype_arr = pythoncom.VT_ARRAY|dtype
    for i in range(3):
        variant = win32.VARIANT(dtype_arr, np.nan_to_num(mkr_coords_unscaled[:,i]))
        ret = itf.SetPointDataEx(mkr_idx, i, start_fr, variant)
    var_const = win32.VARIANT(dtype, 1)
    for i in range(3):
        for idx, val in enumerate(mkr_coords_unscaled[:,i]):
            if val == 1:
                ret = itf.SetPointData(mkr_idx, i, start_fr+idx, var_const)
    return [False, True][ret]
    
def update_marker_residual(itf, mkr_name, mkr_resid, msg=False):
    mkr_idx = get_marker_index(itf, mkr_name, msg)
    if mkr_idx == -1: return False
    start_fr = get_first_frame(itf)
    n_frs = get_num_frames(itf)
    if mkr_resid.ndim != 1 or mkr_resid.shape[0] != n_frs:
        if msg: print("The dimension of the input is not compatible!")
        return False
    dtype = pythoncom.VT_R4
    dtype_arr = pythoncom.VT_ARRAY|dtype
    variant = win32.VARIANT(dtype_arr, mkr_resid)
    ret = itf.SetPointDataEx(mkr_idx, 3, start_fr, variant)
    var_const = win32.VARIANT(dtype, 1)
    for idx, val in enumerate(mkr_resid):
        if val == 1:
            ret = itf.SetPointData(mkr_idx, 3, start_fr+idx, var_const) 
    return [False, True][ret]

def set_marker_pos(itf, mkr_name, start_frame, mkr_coords, msg=False):  
    if mkr_coords.ndim != 2:
        if msg: print("The dimension of the input is not compatible!")
        return False    
    mkr_idx = get_marker_index(itf, mkr_name, msg)
    if mkr_idx == -1: return False
    dtype = pythoncom.VT_R4
    dtype_arr = pythoncom.VT_ARRAY|dtype
    for i in range(3):
        variant = win32.VARIANT(dtype_arr, np.nan_to_num(mkr_coords[:, i]))
        ret = itf.SetPointDataEx(mkr_idx, i, start_frame, variant)
    var_const = win32.VARIANT(dtype, 1)
    for i in range(3):
        for idx, val in enumerate(mkr_coords[:,i]):
            if val == 1:
                ret = itf.SetPointData(mkr_idx, i, start_frame+idx, var_const)
    return [False, True][ret]

def set_marker_residual(itf, mkr_name, start_frame, mkr_resid, msg=False):
    if mkr_resid.ndim != 1:
        if msg: print("The dimension of the input is not compatible!")
        return False
    mkr_idx = get_marker_index(itf, mkr_name, msg)
    if mkr_idx == -1: return False
    dtype = pythoncom.VT_R4
    dtype_arr = pythoncom.VT_ARRAY|dtype
    variant = win32.VARIANT(dtype_arr, mkr_resid)
    ret = itf.SetPointDataEx(mkr_idx, 3, start_frame, variant)
    var_const = win32.VARIANT(dtype, 1)
    for idx, val in enumerate(mkr_resid):
        if val == 1:
            ret = itf.SetPointData(mkr_idx, 3, start_frame+idx, var_const)   
    return [False, True][ret]

def recover_marker_relative(itf, tgt_mkr_name, cl_mkr_names, msg=False):
    if msg: print("Relative recovery of %s ... " % tgt_mkr_name, end="")
    n_total_frs = get_num_frames(itf)
    tgt_mkr_data = get_marker_data(itf, tgt_mkr_name, blocked_nan=False, msg=msg)
    tgt_mkr_coords = tgt_mkr_data[:,0:3]
    tgt_mkr_resid = tgt_mkr_data[:,3]
    tgt_mkr_valid_mask = np.where(np.isclose(tgt_mkr_resid, -1), False, True)
    n_tgt_mkr_valid_frs = np.count_nonzero(tgt_mkr_valid_mask)
    if n_tgt_mkr_valid_frs == 0:
        if msg: print("Skipped: no valid target marker frame!")
        return False, n_tgt_mkr_valid_frs
    if n_tgt_mkr_valid_frs == n_total_frs:
        if msg: print("Skipped: all target marker frames valid!")
        return False, n_tgt_mkr_valid_frs
    dict_cl_mkr_coords = {}
    dict_cl_mkr_valid = {}
    cl_mkr_valid_mask = np.ones((n_total_frs), dtype=bool)
    for mkr in cl_mkr_names:
        mkr_data = get_marker_data(itf, mkr, blocked_nan=False, msg=msg)
        dict_cl_mkr_coords[mkr] = mkr_data[:, 0:3]
        dict_cl_mkr_valid[mkr] = np.where(np.isclose(mkr_data[:,3], -1), False, True)
        cl_mkr_valid_mask = np.logical_and(cl_mkr_valid_mask, dict_cl_mkr_valid[mkr])
    all_mkr_valid_mask = np.logical_and(cl_mkr_valid_mask, tgt_mkr_valid_mask)
    if not np.any(all_mkr_valid_mask):
        if msg: print("Skipped: no common valid frame among markers!")
        return False, n_tgt_mkr_valid_frs
    cl_mkr_only_valid_mask = np.logical_and(cl_mkr_valid_mask, np.logical_not(tgt_mkr_valid_mask))
    if not np.any(cl_mkr_only_valid_mask):
        if msg: print("Skipped: cluster markers not helpful!")
        return False, n_tgt_mkr_valid_frs
    all_mkr_valid_frs = np.where(all_mkr_valid_mask)[0]
    cl_mkr_only_valid_frs = np.where(cl_mkr_only_valid_mask)[0]
    dict_cl_mkr_dist = {}
    for mkr_name in cl_mkr_names:
        vec_diff = dict_cl_mkr_coords[mkr_name]-tgt_mkr_coords
        dict_cl_mkr_dist.update({mkr_name: np.nanmean(np.linalg.norm(vec_diff, axis=1))})
    cl_mkr_dist_sorted = sorted(dict_cl_mkr_dist.items(), key=lambda kv: kv[1])
    p0 = dict_cl_mkr_coords[cl_mkr_dist_sorted[0][0]]
    p1 = dict_cl_mkr_coords[cl_mkr_dist_sorted[1][0]]
    p2 = dict_cl_mkr_coords[cl_mkr_dist_sorted[2][0]] 
    vec0 = p1-p0
    vec1 = p2-p0
    vec0_norm = np.linalg.norm(vec0, axis=1, keepdims=True)
    vec1_norm = np.linalg.norm(vec1, axis=1, keepdims=True)
    vec0_unit = np.divide(vec0, vec0_norm, where=(vec0_norm!=0))
    vec1_unit = np.divide(vec1, vec1_norm, where=(vec1_norm!=0))
    vec2 = np.cross(vec0_unit, vec1_unit)
    vec2_norm = np.linalg.norm(vec2, axis=1, keepdims=True)
    vec2_unit = np.divide(vec2, vec2_norm, where=(vec2_norm!=0))
    vec_z = vec2_unit
    vec_x = vec0_unit
    vec_y = np.cross(vec_z, vec_x)
    mat_rot = np.array([vec_x.T, vec_y.T, vec_z.T]).T
    tgt_mkr_coords_rel = np.einsum('ij,ijk->ik', (tgt_mkr_coords-p0)[all_mkr_valid_mask], mat_rot[all_mkr_valid_mask])
    tgt_mkr_coords_recovered = np.zeros((cl_mkr_only_valid_frs.size, 3), dtype=np.float32)
    for idx, fr in np.ndenumerate(cl_mkr_only_valid_frs):
        search_idx = np.searchsorted(all_mkr_valid_frs, fr)
        if search_idx>=all_mkr_valid_frs.shape[0] or search_idx==0:
            tgt_coords_rel_idx = (np.abs(all_mkr_valid_frs-fr)).argmin()
            tgt_coords_rel = tgt_mkr_coords_rel[tgt_coords_rel_idx]
        else:
            idx1 = search_idx
            idx0 = search_idx-1
            fr1 = all_mkr_valid_frs[idx1]
            fr0 = all_mkr_valid_frs[idx0]
            a = np.float32(fr-fr0)
            b = np.float32(fr1-fr)
            tgt_coords_rel = (b*tgt_mkr_coords_rel[idx0]+a*tgt_mkr_coords_rel[idx1])/(a+b)
        tgt_mkr_coords_recovered[idx] = p0[fr]+np.dot(mat_rot[fr], tgt_coords_rel)
    tgt_mkr_coords[cl_mkr_only_valid_mask] = tgt_mkr_coords_recovered
    tgt_mkr_resid[cl_mkr_only_valid_mask] = 0.0
    update_marker_pos(itf, tgt_mkr_name, tgt_mkr_coords, msg=msg)
    update_marker_residual(itf, tgt_mkr_name, tgt_mkr_resid, msg=msg)
    n_tgt_mkr_valid_frs_updated = np.count_nonzero(np.where(np.isclose(tgt_mkr_resid, -1), False, True))
    if msg: print("Updated.")
    return True, n_tgt_mkr_valid_frs_updated

def recover_marker_rigidbody(itf, tgt_mkr_name, cl_mkr_names, msg=False):
    if msg: print("Rigidbody recovery of %s ... " % tgt_mkr_name, end="")   
    n_total_frs = get_num_frames(itf)
    tgt_mkr_data = get_marker_data(itf, tgt_mkr_name, blocked_nan=False, msg=msg)
    tgt_mkr_coords = tgt_mkr_data[:,0:3]
    tgt_mkr_resid = tgt_mkr_data[:,3]
    tgt_mkr_valid_mask = np.where(np.isclose(tgt_mkr_resid, -1), False, True)
    n_tgt_mkr_valid_frs = np.count_nonzero(tgt_mkr_valid_mask)
    if n_tgt_mkr_valid_frs == 0:
        if msg: print("Skipped: no valid target marker frame!")
        return False, n_tgt_mkr_valid_frs
    if n_tgt_mkr_valid_frs == n_total_frs:
        if msg: print("Skipped: all target marker frames valid!")
        return False, n_tgt_mkr_valid_frs    
    dict_cl_mkr_coords = {}
    dict_cl_mkr_valid = {}
    cl_mkr_valid_mask = np.ones((n_total_frs), dtype=bool)
    for mkr in cl_mkr_names:
        mkr_data = get_marker_data(itf, mkr, blocked_nan=False, msg=msg)
        dict_cl_mkr_coords[mkr] = mkr_data[:,0:3]
        dict_cl_mkr_valid[mkr] = np.where(np.isclose(mkr_data[:,3], -1), False, True)
        cl_mkr_valid_mask = np.logical_and(cl_mkr_valid_mask, dict_cl_mkr_valid[mkr])
    all_mkr_valid_mask = np.logical_and(cl_mkr_valid_mask, tgt_mkr_valid_mask)
    if not np.any(all_mkr_valid_mask):
        if msg: print("Skipped: no common valid frame among markers!")
        return False, n_tgt_mkr_valid_frs
    cl_mkr_only_valid_mask = np.logical_and(cl_mkr_valid_mask, np.logical_not(tgt_mkr_valid_mask))
    if not np.any(cl_mkr_only_valid_mask):
        if msg: print("Skipped: cluster markers not helpful!")
        return False, n_tgt_mkr_valid_frs
    all_mkr_valid_frs = np.where(all_mkr_valid_mask)[0]
    cl_mkr_only_valid_frs = np.where(cl_mkr_only_valid_mask)[0]
    dict_cl_mkr_dist = {}
    for mkr_name in cl_mkr_names:
        vec_diff = dict_cl_mkr_coords[mkr_name]-tgt_mkr_coords
        dict_cl_mkr_dist.update({mkr_name: np.nanmean(np.linalg.norm(vec_diff, axis=1))})
    cl_mkr_dist_sorted = sorted(dict_cl_mkr_dist.items(), key=lambda kv: kv[1])
    p0 = dict_cl_mkr_coords[cl_mkr_dist_sorted[0][0]]
    p1 = dict_cl_mkr_coords[cl_mkr_dist_sorted[1][0]]
    p2 = dict_cl_mkr_coords[cl_mkr_dist_sorted[2][0]]
    p3 = tgt_mkr_coords
    vec0 = p1-p0
    vec1 = p2-p0
    vec0_norm = np.linalg.norm(vec0, axis=1, keepdims=True)
    vec1_norm = np.linalg.norm(vec1, axis=1, keepdims=True)
    vec0_unit = np.divide(vec0, vec0_norm, where=(vec0_norm!=0))
    vec1_unit = np.divide(vec1, vec1_norm, where=(vec1_norm!=0))
    vec2 = np.cross(vec0_unit, vec1_unit)
    vec2_norm = np.linalg.norm(vec2, axis=1, keepdims=True)
    vec2_unit = np.divide(vec2, vec2_norm, where=(vec2_norm!=0))
    vec3 = p3-p0
    vec_z = vec2_unit
    vec_x = vec0_unit
    vec_y = np.cross(vec_z, vec_x)
    mat_rot = np.array([vec_x.T, vec_y.T, vec_z.T]).T
    for idx, fr in np.ndenumerate(cl_mkr_only_valid_frs):
        search_idx = np.searchsorted(all_mkr_valid_frs, fr)
        if search_idx == 0:
            fr0 = all_mkr_valid_frs[0]
            rot_fr0_to_fr = np.dot(mat_rot[fr], mat_rot[fr0].T)
            vt_fr0 = np.dot(rot_fr0_to_fr, vec3[fr0])
            vc = vt_fr0
        elif search_idx >= all_mkr_valid_frs.shape[0]:
            fr1 = all_mkr_valid_frs[all_mkr_valid_frs.shape[0]-1]
            rot_fr1_to_fr = np.dot(mat_rot[fr], mat_rot[fr1].T)
            vt_fr1 = np.dot(rot_fr1_to_fr, vec3[fr1])
            vc = vt_fr1
        else:
            fr0 = all_mkr_valid_frs[search_idx-1]
            fr1 = all_mkr_valid_frs[search_idx]
            rot_fr0_to_fr = np.dot(mat_rot[fr], mat_rot[fr0].T)
            rot_fr1_to_fr = np.dot(mat_rot[fr], mat_rot[fr1].T)
            vt_fr0 = np.dot(rot_fr0_to_fr, vec3[fr0])
            vt_fr1 = np.dot(rot_fr1_to_fr, vec3[fr1])
            a = np.float32(fr-fr0)
            b = np.float32(fr1-fr)
            vc = (b*vt_fr0+a*vt_fr1)/(a+b)
        tgt_mkr_coords[fr] = p0[fr]+vc
        tgt_mkr_resid[fr] = 0.0
    update_marker_pos(itf, tgt_mkr_name, tgt_mkr_coords, msg=msg)
    update_marker_residual(itf, tgt_mkr_name, tgt_mkr_resid, msg=msg)
    n_tgt_mkr_valid_frs_updated = np.count_nonzero(np.where(np.isclose(tgt_mkr_resid, -1), False, True))
    if msg: print("Updated.")
    return True, n_tgt_mkr_valid_frs_updated

def fill_marker_gap_rigidbody(itf, tgt_mkr_name, cl_mkr_names, msg=False):
    def RBT(A, B):
        C = np.dot((B-np.mean(B, axis=0)).T, (A-np.mean(A, axis=0)))  
        U, S, Vt = np.linalg.svd(C)
        R = np.dot(U, np.dot(np.diag([1, 1, np.linalg.det(np.dot(U, Vt))]), Vt))
        L = B.mean(0)-np.dot(R, A.mean(0))
        err_vec = np.dot(R, A.T).T+L-B
        err_norm = np.linalg.norm(err_vec, axis=1)
        mean_err_norm = np.mean(err_norm)
        return R, L, err_vec, err_norm, mean_err_norm
    if msg: print("Rigidbody gap fill of %s ... " % tgt_mkr_name, end="")     
    n_total_frs = get_num_frames(itf)
    tgt_mkr_data = get_marker_data(itf, tgt_mkr_name, blocked_nan=False, msg=msg)
    tgt_mkr_coords = tgt_mkr_data[:,0:3]
    tgt_mkr_resid = tgt_mkr_data[:,3]
    tgt_mkr_valid_mask = np.where(np.isclose(tgt_mkr_resid, -1), False, True)
    n_tgt_mkr_valid_frs = np.count_nonzero(tgt_mkr_valid_mask)
    if n_tgt_mkr_valid_frs == 0:
        if msg: print("Skipped: no valid target marker frame!")
        return False, n_tgt_mkr_valid_frs
    if n_tgt_mkr_valid_frs == n_total_frs:
        if msg: print("Skipped: all target marker frames valid!")
        return False , n_tgt_mkr_valid_frs   
    dict_cl_mkr_coords = {}
    dict_cl_mkr_valid = {}
    cl_mkr_valid_mask = np.ones((n_total_frs), dtype=bool)
    for mkr in cl_mkr_names:
        mkr_data = get_marker_data(itf, mkr, blocked_nan=False, msg=msg)
        dict_cl_mkr_coords[mkr] = mkr_data[:,0:3]
        dict_cl_mkr_valid[mkr] = np.where(np.isclose(mkr_data[:,3], -1), False, True)
        cl_mkr_valid_mask = np.logical_and(cl_mkr_valid_mask, dict_cl_mkr_valid[mkr])
    all_mkr_valid_mask = np.logical_and(cl_mkr_valid_mask, tgt_mkr_valid_mask)
    if not np.any(all_mkr_valid_mask):
        if msg: print("Skipped: no common valid frame among markers!")
        return False, n_tgt_mkr_valid_frs
    cl_mkr_only_valid_mask = np.logical_and(cl_mkr_valid_mask, np.logical_not(tgt_mkr_valid_mask))
    if not np.any(cl_mkr_only_valid_mask):
        if msg: print("Skipped: cluster markers not helpful!")
        return False, n_tgt_mkr_valid_frs
    all_mkr_valid_frs = np.where(all_mkr_valid_mask)[0]
    cl_mkr_only_valid_frs = np.where(cl_mkr_only_valid_mask)[0]
    b_updated = False
    for idx, fr in np.ndenumerate(cl_mkr_only_valid_frs):
        search_idx = np.searchsorted(all_mkr_valid_frs, fr)
        if search_idx == 0:
            fr0 = all_mkr_valid_frs[0]
            fr1 = all_mkr_valid_frs[1]
        elif search_idx >= all_mkr_valid_frs.shape[0]:
            fr0 = all_mkr_valid_frs[all_mkr_valid_frs.shape[0]-2]
            fr1 = all_mkr_valid_frs[all_mkr_valid_frs.shape[0]-1]
        else:
            fr0 = all_mkr_valid_frs[search_idx-1]
            fr1 = all_mkr_valid_frs[search_idx]
        if fr <= fr0 or fr >= fr1: continue
        if ~cl_mkr_valid_mask[fr0] or ~cl_mkr_valid_mask[fr1]: continue
        if np.any(~cl_mkr_valid_mask[fr0:fr1+1]): continue
        cl_mkr_coords_fr0 = np.zeros((len(cl_mkr_names), 3), dtype=np.float32)
        cl_mkr_coords_fr1 = np.zeros((len(cl_mkr_names), 3), dtype=np.float32)
        cl_mkr_coords_fr = np.zeros((len(cl_mkr_names), 3), dtype=np.float32)
        for cnt, mkr in enumerate(cl_mkr_names):
            cl_mkr_coords_fr0[cnt,:] = dict_cl_mkr_coords[mkr][fr0,:]
            cl_mkr_coords_fr1[cnt,:] = dict_cl_mkr_coords[mkr][fr1,:]
            cl_mkr_coords_fr[cnt,:] = dict_cl_mkr_coords[mkr][fr,:]
        rot_fr0, trans_fr0, _, _, _ = RBT(cl_mkr_coords_fr0, cl_mkr_coords_fr)
        rot_fr1, trans_fr1, _, _, _ = RBT(cl_mkr_coords_fr1, cl_mkr_coords_fr)
        tgt_mkr_coords_fr_fr0 = np.dot(rot_fr0, tgt_mkr_coords[fr0])+trans_fr0
        tgt_mkr_coords_fr_fr1 = np.dot(rot_fr1, tgt_mkr_coords[fr1])+trans_fr1
        tgt_mkr_coords[fr] = (tgt_mkr_coords_fr_fr1-tgt_mkr_coords_fr_fr0)*np.float32(fr-fr0)/np.float32(fr1-fr0)+tgt_mkr_coords_fr_fr0
        tgt_mkr_resid[fr] = 0.0        
        b_updated = True        
    if b_updated:
        update_marker_pos(itf, tgt_mkr_name, tgt_mkr_coords, msg=msg)
        update_marker_residual(itf, tgt_mkr_name, tgt_mkr_resid, msg=msg)
        n_tgt_mkr_valid_frs_updated = np.count_nonzero(np.where(np.isclose(tgt_mkr_resid, -1), False, True))
        if msg: print("Updated.")
        return True, n_tgt_mkr_valid_frs_updated
    else:
        if msg: print("Skipped.")
        return False, n_tgt_mkr_valid_frs

def fill_marker_gap_pattern(itf, tgt_mkr_name, dnr_mkr_name, msg=False):
    if msg: print("Pattern gap fill of %s using %s ... " % (tgt_mkr_name, dnr_mkr_name), end="")
    n_total_frs = get_num_frames(itf)
    tgt_mkr_data = get_marker_data(itf, tgt_mkr_name, blocked_nan=False, msg=msg)
    tgt_mkr_coords = tgt_mkr_data[:, 0:3]
    tgt_mkr_resid = tgt_mkr_data[:, 3]
    tgt_mkr_valid_mask = np.where(np.isclose(tgt_mkr_resid, -1), False, True)
    n_tgt_mkr_valid_frs = np.count_nonzero(tgt_mkr_valid_mask)
    if n_tgt_mkr_valid_frs==0 or n_tgt_mkr_valid_frs==n_total_frs:
        if msg: print("Skipped.")
        return False, n_tgt_mkr_valid_frs
    dnr_mkr_data = get_marker_data(itf, dnr_mkr_name, blocked_nan=False, msg=msg)
    dnr_mkr_coords = dnr_mkr_data[:, 0:3]
    dnr_mkr_resid = dnr_mkr_data[:, 3]
    dnr_mkr_valid_mask = np.where(np.isclose(dnr_mkr_resid, -1), False, True)
    if not np.any(dnr_mkr_valid_mask):
        if msg: print("Skipped.")
        return False, n_tgt_mkr_valid_frs    
    both_mkr_valid_mask = np.logical_and(tgt_mkr_valid_mask, dnr_mkr_valid_mask)
    if not np.any(both_mkr_valid_mask):
        if msg: print("Skipped.")
        return False, n_tgt_mkr_valid_frs        
    b_updated = False
    tgt_mkr_invalid_frs = np.where(~tgt_mkr_valid_mask)[0]
    both_mkr_valid_frs = np.where(both_mkr_valid_mask)[0]
    for idx, fr in np.ndenumerate(tgt_mkr_invalid_frs):
        search_idx = np.searchsorted(both_mkr_valid_frs, fr)
        if search_idx == 0:
            fr0 = both_mkr_valid_frs[0]
            fr1 = both_mkr_valid_frs[1]
        elif search_idx >= both_mkr_valid_frs.shape[0]:
            fr0 = both_mkr_valid_frs[both_mkr_valid_frs.shape[0]-2]
            fr1 = both_mkr_valid_frs[both_mkr_valid_frs.shape[0]-1]
        else:
            fr0 = both_mkr_valid_frs[search_idx-1]
            fr1 = both_mkr_valid_frs[search_idx]
        if fr <= fr0 or fr >= fr1: continue
        if ~dnr_mkr_valid_mask[fr0] or ~dnr_mkr_valid_mask[fr1]: continue
        if np.any(~dnr_mkr_valid_mask[fr0:fr1+1]): continue    
        v_tgt = (tgt_mkr_coords[fr1]-tgt_mkr_coords[fr0])*np.float32(fr-fr0)/np.float32(fr1-fr0)+tgt_mkr_coords[fr0]
        v_dnr = (dnr_mkr_coords[fr1]-dnr_mkr_coords[fr0])*np.float32(fr-fr0)/np.float32(fr1-fr0)+dnr_mkr_coords[fr0]
        new_coords = v_tgt-v_dnr+dnr_mkr_coords[fr]      
        tgt_mkr_coords[fr] = new_coords
        tgt_mkr_resid[fr] = 0.0        
        b_updated = True
    if b_updated:
        update_marker_pos(itf, tgt_mkr_name, tgt_mkr_coords, msg=msg)
        update_marker_residual(itf, tgt_mkr_name, tgt_mkr_resid, msg=msg)
        n_tgt_mkr_valid_frs_updated = np.count_nonzero(np.where(np.isclose(tgt_mkr_resid, -1), False, True))
        if msg: print("Updated.")
        return True, n_tgt_mkr_valid_frs_updated
    else:
        if msg: print("Skipped.")
        return False, n_tgt_mkr_valid_frs

def fill_marker_gap_interp(itf, tgt_mkr_name, k=3, search_span_offset=5, min_needed_frs=10, msg=False):
    if msg: print("Interp gap fill of %s ... " % tgt_mkr_name, end="") 
    n_total_frs = get_num_frames(itf)
    tgt_mkr_data = get_marker_data(itf, tgt_mkr_name, blocked_nan=False, msg=msg)
    tgt_mkr_coords = tgt_mkr_data[:, 0:3]
    tgt_mkr_resid = tgt_mkr_data[:, 3]
    tgt_mkr_valid_mask = np.where(np.isclose(tgt_mkr_resid, -1), False, True)
    n_tgt_mkr_valid_frs = np.count_nonzero(tgt_mkr_valid_mask)
    if n_tgt_mkr_valid_frs==0 or n_tgt_mkr_valid_frs==n_total_frs:
        if msg: print("Skipped.")
        return False, n_tgt_mkr_valid_frs
    b_updated = False
    tgt_mkr_invalid_frs = np.where(~tgt_mkr_valid_mask)[0]
    tgt_mkr_invalid_gaps = np.split(tgt_mkr_invalid_frs, np.where(np.diff(tgt_mkr_invalid_frs)!=1)[0]+1)
    for gap in tgt_mkr_invalid_gaps:
        if gap.size == 0: continue
        if gap.min()==0 or gap.max()==n_total_frs-1: continue
        search_span = np.int(np.ceil(gap.size/2))+search_span_offset
        itpl_cand_frs_mask = np.zeros((n_total_frs,), dtype=bool)
        for i in range(gap.min()-1, gap.min()-1-search_span, -1):
            if i>=0: itpl_cand_frs_mask[i]=True
        for i in range(gap.max()+1, gap.max()+1+search_span, 1):
            if i<n_total_frs: itpl_cand_frs_mask[i]=True
        itpl_cand_frs_mask = np.logical_and(itpl_cand_frs_mask, tgt_mkr_valid_mask)
        if np.sum(itpl_cand_frs_mask) < min_needed_frs: continue
        itpl_cand_frs = np.where(itpl_cand_frs_mask)[0]
        itpl_cand_coords = tgt_mkr_coords[itpl_cand_frs, :]
        fun_itpl_x = InterpolatedUnivariateSpline(itpl_cand_frs, itpl_cand_coords[:,0], k=k, ext='const')
        fun_itpl_y = InterpolatedUnivariateSpline(itpl_cand_frs, itpl_cand_coords[:,1], k=k, ext='const')
        fun_itpl_z = InterpolatedUnivariateSpline(itpl_cand_frs, itpl_cand_coords[:,2], k=k, ext='const')
        itpl_x = fun_itpl_x(gap)
        itpl_y = fun_itpl_y(gap)
        itpl_z = fun_itpl_z(gap)
        for idx, fr in enumerate(gap):
            tgt_mkr_coords[fr,0] = itpl_x[idx]
            tgt_mkr_coords[fr,1] = itpl_y[idx]
            tgt_mkr_coords[fr,2] = itpl_z[idx]
            tgt_mkr_resid[fr] = 0.0        
        b_updated = True            
    if b_updated:
        update_marker_pos(itf, tgt_mkr_name, tgt_mkr_coords, msg=msg)
        update_marker_residual(itf, tgt_mkr_name, tgt_mkr_resid, msg=msg)
        n_tgt_mkr_valid_frs_updated = np.count_nonzero(np.where(np.isclose(tgt_mkr_resid, -1), False, True))
        if msg: print("Updated.")
        return True, n_tgt_mkr_valid_frs_updated
    else:
        if msg: print("Skipped.")
        return False, n_tgt_mkr_valid_frs
    
def export_marker_coords_vicon_csv(itf, f_path, sep=',', fmt='%.6g', tgt_mkr_names=None):
    c3d_mkr_names = get_marker_names(itf)
    if tgt_mkr_names is None:
        mkr_names = c3d_mkr_names
    else:
        mkr_names = [x for x in tgt_mkr_names if x in c3d_mkr_names]
    mkr_coord_names = [m+'_'+c for m in mkr_names for c in ['X', 'Y', 'Z']]
    df_mkr_coords = get_all_marker_pos_df(itf, blocked_nan=True)
    mkr_coords = df_mkr_coords[mkr_coord_names].to_numpy()
    fr_idx = get_video_frames(itf)
    sub_fr_idx = np.zeros(fr_idx.shape, dtype=np.int32)
    mkr_unit = get_marker_unit(itf)
    video_fps = get_video_fps(itf)
    header_row_0 = 'Trajectories'
    header_row_1 = str(int(video_fps))
    header_mkr_names = []
    for item in mkr_names:
        header_mkr_names.append('')
        header_mkr_names.append('')
        header_mkr_names.append(item)
    header_row_2 = sep.join(header_mkr_names)
    header_coord_names = []
    header_coord_names.append('Frame')
    header_coord_names.append('Sub Frame')
    for i in range(len(mkr_names)):
        header_coord_names.append('X')
        header_coord_names.append('Y')
        header_coord_names.append('Z')
    header_row_3 = sep.join(header_coord_names)
    header_units = []
    header_units.append('')
    header_units.append('')
    for i in range(len(mkr_names)):
        for j in range(3):
            header_units.append(mkr_unit)
    header_row_4 = sep.join(header_units)
    header_str = ''
    header_str = header_str+header_row_0+'\n'
    header_str = header_str+header_row_1+'\n'           
    header_str = header_str+header_row_2+'\n'
    header_str = header_str+header_row_3+'\n'
    header_str = header_str+header_row_4
    mkr_data = np.hstack((np.column_stack((fr_idx, sub_fr_idx)), mkr_coords))
    np.savetxt(f_path, mkr_data, fmt=fmt, delimiter=sep, comments='', header=header_str)