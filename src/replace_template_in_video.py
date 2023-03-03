# проблемы
# выходное видео длинее оригинального - ??? решено - frame rate должен совпадать для видео источника и целевого
# пропал звук в выходном файле - решено сначала отделением звука и присоединением к готовому
# качество хромает - сначала сжимал вилео чтобы помещалось на экран. не надо. сохранять оригинальный размер


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
    config = "files to review"
    files = list()

class Config(object):
    """
    Configuration 
        VIDEO_SOURCE_PATH : path from where video files should be taken for processing
        VIDEO_OUTPUT_PATH : path for changed video files
           
    """
    CFG_WORKING_PATH = r'D:\Projects\Video as a source'
    VIDEO_SOURCE_PATH = r'D:\Projects\Video as a source\input'
    VIDEO_OUTPUT_PATH = r'D:\Projects\Video as a source\output'
    VIDEO_WORKING_PATH = r'D:\Projects\Video as a source\in_progress'
    VIDEO_TEMPLATE_PATH = r'C:\repos\personal\python-openvc-change-image\image templates'
    CFG_EXCLUDED_PATHS = r''
    CFG_DEBUGMODE = False
    
    CFG_TEMPLATE_CONFIG_FILE = r'C:\repos\personal\python-openvc-change-image\src\config\config.json'
    

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

@timeit
def save_audio_from_video(video_file_path):
    """
    function: save_audio_from_video

            Parameters:
                    video_file_path: path to file

            Returns:
                    file_result: full path to audio file
    """    
    # load video file
    clip = mp.VideoFileClip(video_file_path) 
    file_name = Path(video_file_path).stem
    file_result = os.path.join(Config.VIDEO_WORKING_PATH, file_name + '.wav')
    # save audio to file
    clip.audio.write_audiofile(file_result)    
    print(f'saved audio to --> {file_result}')    
    return file_result

@timeit
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

    capImg = cv2.VideoCapture(os.path.join(Config.VIDEO_SOURCE_PATH, video_file_path))
  
    # трешхолд по ловле
    threshold = 0.8

    # # We need to set resolutions.
    # # so, convert them from float to integer.
    # frame_width = int(capImg.get(3)* 75/ 100)
    # frame_height = int(capImg.get(4)* 75/ 100)

    frame_width = int(capImg.get(3))
    frame_height = int(capImg.get(4))

    size = (frame_width, frame_height)
    fourcc = cv2.VideoWriter_fourcc(*'MPEG')
    # fourcc = cv2.VideoWriter_fourcc(*'XVID')

    file_name = Path(video_file_path).stem + '.avi'

    file_video_result = os.path.join(Config.VIDEO_WORKING_PATH, file_name)
    result = cv2.VideoWriter(file_video_result, fourcc,30.0, size)

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
        for tmplt in tempalate_config['replace-templates']:
            res =  cv2.matchTemplate(frame_gray,tmplt['tempalate-file-cv2'],cv2.TM_CCOEFF_NORMED)
            # в окне video_mask результат наложения маски,
            loc = np.where( res >= threshold)

            for pt in zip(*loc[::-1]):

                if debug_mode:
                    cv2.rectangle(frame75, pt, (pt[0] + tmplt['width'], pt[1] + tmplt['height']), (0,0,255), 2)
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


@timeit
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

    capImg = cv2.VideoCapture(os.path.join(Config.VIDEO_SOURCE_PATH, video_file_path))
  
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


    return file_video_result


@timeit
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
    # final_clip.write_videofile(os.path.join(Config.VIDEO_OUTPUT_PATH, file_name + '.mp4'),codec= 'mpeg4' ,audio_codec='libvorbis')
    final_clip.write_videofile(os.path.join(Config.VIDEO_OUTPUT_PATH, file_name + '.mp4'),codec= 'libx264' ,audio_codec='libvorbis')
    

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


        



if __name__ == '__main__':

    files_to_process = FilesToReview()
    files_to_process.config = "config"
    # get a list of files to process
    files_to_process.files = [f for f in get_files_by_path(Config.VIDEO_SOURCE_PATH, Config.CFG_EXCLUDED_PATHS) if f['fileextension'] == '.mp4']
    # read json config
    template_config = enrich_template_config(read_config_from_json(Config.CFG_TEMPLATE_CONFIG_FILE))

    for vf in files_to_process.files:
        print(f"start processing the video file - {vf['filefullpath']}")     
        # заменяем темплейты   
        file_video_result = replace_templates_in_video(vf['filefullpath'],template_config,Config.CFG_DEBUGMODE)
        # сохраним аудиодорожку так как предыдущий вызов не сохраняет звук
        saved_audio = save_audio_from_video(vf['filefullpath'])
        # соединяем обратно
        combine_video_and_audio(file_video_result,saved_audio)
        print(f"processing of video file completed - {vf['filefullpath']}")

