# ====================================================================================================================
#   1. set up congiguration in Config class
#       use config_empty.json first
#       CFG_DEBUGMODE = True
#  2. run
#       create templates
#       congigure config.json    
#  3. run with CFG_DEBUGMODE = False and config.json    
# =====================================================================================================================


import cv2
import numpy as np
import os
import moviepy.editor as mp
from pathlib import Path
from functools import wraps
import time
import json
import ruamel.yaml as yaml



import auto_document_modules as adm

def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds')
        return result
    return timeit_wrapper


class FilesToReview:
    files = list()



class Config(object):
    
    def __init__(self, yaml_config_file):
        with open(yaml_config_file) as stream:
            try:
                yaml_config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        self.CFG_APPNAME = "VIDEO_FIXER"

        assert self.CFG_APPNAME == yaml_config['appName']

        self.CFG_WORKING_PATH = yaml_config['paths']['workingpath']
        self.CFG_WORKING_PATH_IN_PROGRESS = os.path.join(self.CFG_WORKING_PATH, "In_progress")
        self.CFG_WORKING_PATH_OUTPUT = os.path.join(self.CFG_WORKING_PATH, "Output")
        if not os.path.exists(self.CFG_WORKING_PATH_IN_PROGRESS):
            os.makedirs(self.CFG_WORKING_PATH_IN_PROGRESS)

        if not os.path.exists(self.CFG_WORKING_PATH_OUTPUT):
            os.makedirs(self.CFG_WORKING_PATH_OUTPUT)

        self.CFG_VIDEO_SOURCE_PATH = yaml_config['paths']['video_source_path']
        self.CFG_EXCLUDED_PATHS = yaml_config['paths']['excluded_paths']
        self.CFG_TEMPLATE_CONFIG_FILE = yaml_config['paths']['template_config_file']
        self.CFG_DEBUGMODE = yaml_config['paths']['debugmode']
        self.CFG_CREATE_SCENES = yaml_config['paths']['create_scenes']
        self.CFG_RECOGNIZE_TOPICS_ON_SCENES = yaml_config['paths']['recognize_topics_on_scenes']  
        self.CFG_RECOGNIZE_SPEACH = yaml_config['paths']['recognize_speach']
        self.template_config = yaml_config['replace-config']
  



    

def get_files_by_path(path, excluded_paths):
    """
    function: get_files_by_path

            Parameters:
                    path: path to look for
                    excluded_paths: list of paths which are exluded 

            Returns:
                    list: list of dicts of files attributes collected recursivly 
    """
    list_of_files = []
    files_result = []
    for root, dirs, files in os.walk(path):
        for file in files:
            # print(f"------------- file  {root}   ---- {os.path.join(root, file)}")
            if not any(excluded_path in root for excluded_path in excluded_paths):
                list_of_files.append(os.path.join(root, file))
    for name in list_of_files:
        files_result.append(get_file_info(name))
    return files_result


def get_file_info(file_full_path):
    """
    function: get_file_info

            Parameters:
                    file_full_path: file full path

            Returns:
                    dict: file attributes 
                        ['filename']
                        ['filedirname']
                        ['fileextension']
                        ['filefullpath']

    """
    filepath, file_extension = os.path.splitext(file_full_path)
    file_info = dict()
    file_info['filename'] = os.path.basename(file_full_path)
    file_info['filedirname'] = os.path.dirname(file_full_path)
    file_info['fileextension'] = file_extension
    file_info['filefullpath'] = file_full_path
    return file_info
     

def rescale_frame(frame, percent=75):
    """
    function: rescale_frame

            Parameters:
                    frame: file full path
                    percent: rescale percent

            Returns:
                    cv2.frame: resized frame
    """
    width = int(frame.shape[1] * percent/ 100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)

# @timeit
def save_audio_from_video(video_file_path, output_path):
    """
    function: save_audio_from_video

            Parameters:
                    video_file_path: path to file
                    output_path : path to store result. extension will be WAV

            Returns:
                    file_result: full path to audio file
    """    
    # load video file
    clip = mp.VideoFileClip(video_file_path) 
    file_name = Path(video_file_path).stem
    file_result = os.path.join(output_path, file_name + '.wav')
    # save audio to file
    clip.audio.write_audiofile(file_result)    
    print(f'saved audio to --> {file_result}')    
    return file_result

# @timeit
def replace_templates_in_video(video_file_path,tempalate_config,debug_mode=False):
    """
    function: save_audio_from_video

            Parameters:
                    video_file_path: path to file
                    tempalate_config: json config
                    debug_mode: False - no ouput to window
                                True - output to window

            Returns:
                    file_result: full path to audio file
    """   

    capImg = cv2.VideoCapture(os.path.join(config.CFG_VIDEO_SOURCE_PATH, video_file_path))


    video_length = int(capImg.get(cv2.CAP_PROP_FRAME_COUNT))
    video_width  = int(capImg.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(capImg.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video_fps    = capImg.get(cv2.CAP_PROP_FPS)
  
    # трешхолд по ловле
    threshold = 0.8

    # # We need to set resolutions.
    # # so, convert them from float to integer.
    # frame_width = int(capImg.get(3)* 75/ 100)
    # frame_height = int(capImg.get(4)* 75/ 100)

    frame_width = int(capImg.get(3))
    frame_height = int(capImg.get(4))
    font = cv2.FONT_HERSHEY_SIMPLEX
    size = (frame_width, frame_height)
    fourcc = cv2.VideoWriter_fourcc(*'MPEG')
    # fourcc = cv2.VideoWriter_fourcc(*'XVID')

    file_name = Path(video_file_path).stem + '.avi'

    file_video_result = os.path.join(config.CFG_WORKING_PATH_IN_PROGRESS, file_name)
    result = cv2.VideoWriter(file_video_result, fourcc,30.0, size)

    # загрузим изображения темплейтов и изображений для замены

    template_config_enriched = enrich_template_config(tempalate_config)

    # cv2.VideoWriter_fourcc('M','J','P','G'), 10, (frame_width,frame_height)
    current_frame_number = 1
    while(capImg.isOpened()):

        ret, frame = capImg.read()

        if frame is None:
            break
        current_frame_number = current_frame_number +1 
        print(f'current frame = {current_frame_number}', end="\r", flush=True)
        # frame75 = rescale_frame(frame, percent=75)
        frame75 = frame 
        # переводим кадр в серое
        frame_gray = cv2.cvtColor(frame75,cv2.COLOR_BGR2GRAY)

        res = list()

        

        # перебераем темплейты и пытаемся их найти
        for tmplt in template_config_enriched['replace-templates']:
            res =  cv2.matchTemplate(frame_gray,tmplt['tempalate-file-cv2'],cv2.TM_CCOEFF_NORMED)
            # в окне video_mask результат наложения маски,
            loc = np.where( res >= threshold)

            for pt in zip(*loc[::-1]):

                if debug_mode:
                    cv2.rectangle(frame75, pt, (pt[0] + tmplt['width'], pt[1] + tmplt['height']), (0,0,255), 2)
                    current_frame_number_str = str(current_frame_number)
                    cv2.putText(frame75, current_frame_number_str, (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA)                    
                # заменим что нашли
                frame75[pt[1]:pt[1] + tmplt['height'],pt[0]:pt[0] + tmplt['width']] = tmplt['replace-file-cv2']


        if debug_mode:
            cv2.imshow("video_mask", frame_gray)
            # в окне video_frame вырезку из кадра
            cv2.imshow("video_frame", frame75)
            # организуем выход из цикла по нажатию клавиши
            key_press = cv2.waitKey(30)
            if key_press == ord('q'):
                break             

            # сохраняем изменый фрейм в итоговый файл
        result.write(frame75)    

       
    print("all frames were processed", flush=False)
    print(f"Number of processed frames = {current_frame_number}")
    # clean up
    capImg.release()
    result.release()
    cv2.destroyAllWindows()

    print("The video was successfully saved")
    return file_video_result


# @timeit
def get_main_scenes_in_video(video_file_path,debug_mode=False):
    """
    function: save_audio_from_video

            Parameters:
                    video_file_path: path to file
                    tempalate_config: json config
                    debug_mode: False - no ouput to window
                                True - output to window

            Returns:
                    file_result: full path to audio file
    """   

    capImg = cv2.VideoCapture(os.path.join(config.CFG_VIDEO_SOURCE_PATH, video_file_path))
  
    # трешхолд по ловле
    threshold = 0.8

    frame_width = int(capImg.get(3))
    frame_height = int(capImg.get(4))



    current_frame_number = 1
    while(capImg.isOpened()):

        ret, frame = capImg.read()

        if frame is None:
            break
        current_frame_number = current_frame_number +1 
        print(f'current frame = {current_frame_number}', end="\r", flush=True)

        frame_gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

        res = list()




        if debug_mode:
            cv2.imshow("video_mask", frame_gray)
            # в окне video_frame вырезку из кадра
            font = cv2.FONT_HERSHEY_SIMPLEX
            current_frame_number_str = str(current_frame_number)
            cv2.putText(frame, current_frame_number_str, (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA)
            cv2.imshow("video_frame", frame)
            # организуем выход из цикла по нажатию клавиши
            key_press = cv2.waitKey(30)
            if key_press == ord('q'):
                break             

       
    print("all frames were processed", flush=False)
    print(f"Number of processed frames = {current_frame_number}")
    # clean up
    capImg.release()
    cv2.destroyAllWindows()


    return 1


# @timeit
def combine_video_and_audio(video_file, audio_file):
    """
    function: combine_video_and_audio
            merge audio with video. lenghts of files must be the same

            Parameters:
                    video_file: path to video file
                    audio_file: path to audio file

            Returns:
                    file_result: full path to audio file

            Problems: 
                    codec should be selected properly to achive the best quality
    """       
    clip = mp.VideoFileClip(video_file)
    audio_background = mp.AudioFileClip(audio_file)
    # final_audio = mp.CompositeAudioClip([clip.audio, audio_background])
    file_name = Path(video_file).stem
    final_clip = clip.set_audio(audio_background)
    # final_clip.write_videofile(os.path.join(config.VIDEO_OUTPUT_PATH, file_name + '.mp4'),codec= 'mpeg4' ,audio_codec='libvorbis')
    final_clip.write_videofile(os.path.join(config.CFG_WORKING_PATH_OUTPUT, file_name + '.mp4'),codec= 'libx264' ,audio_codec='libvorbis')
    

def read_config_from_json(config_json_file):
    """ function: read_config_from_json
            read config from json file

            Parameters:
                    config_json_file: path to json file

            Returns:
                    dict: json config
    """

    with open(os.path.join(config_json_file), 'r') as f:
        data = json.load(f)
    return data


def enrich_template_config(template_config):
    """ function: enrich_template_config
            load images and add them to dict

            Parameters:
                    template_config: dict with config

            Returns:
                    dict: json config
    """
    for tmplt in template_config['replace-templates']:
        # print(tmplt)
        img = cv2.imread(tmplt['tempalate-file'] ,cv2.IMREAD_GRAYSCALE)
        tmplt['tempalate-file-cv2'] = img
        tmplt['replace-file-cv2'] = cv2.imread(tmplt['replace-file'])
        tmplt['width'],tmplt['height'] = img.shape[::-1]
    return template_config


def process_files(files_to_process,template_config):
    """ function: replace_templates_if_files
            
            Parameters:
                    files_to_process: dictionary with files to be processed 
                    template_config: dict with configuration about that templated should be replaced by
            Returns:
                    dict: info about processed files
    """
    for vf in files_to_process.files:
        print(f"start processing the video file - {vf['filefullpath']}")     
        
        start_time = time.perf_counter()
        # заменяем темплейты   
        file_video_result = replace_templates_in_video(vf['filefullpath'],template_config,config.CFG_DEBUGMODE)
        # сохраним аудиодорожку так как предыдущий вызов не сохраняет звук
        saved_audio = save_audio_from_video(vf['filefullpath'], config.CFG_WORKING_PATH_IN_PROGRESS)
        # соединяем обратно
        combine_video_and_audio(file_video_result,saved_audio)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f"processing of video file completed - {vf['filefullpath']} Took {total_time:.4f} seconds")

    return 1


if __name__ == '__main__':

    files_to_process = FilesToReview()
    
    config = Config(r"C:\repos\personal\python-openvc-change-image\src\config\config.yaml")
    print(config.template_config)

    # get a list of files to process
    files_to_process.files = [f for f in get_files_by_path(config.CFG_VIDEO_SOURCE_PATH, config.CFG_EXCLUDED_PATHS) if f['fileextension'] == '.mp4']
    # read json config
    # delete template_config = read_config_from_json(config.CFG_TEMPLATE_CONFIG_FILE)
    #process files
    # delete print(template_config)
    files_processiing_result = process_files(files_to_process,config.template_config)



