# https://opencv.org/opencv-free-course/
# https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html
# https://www.codingforentrepreneurs.com/blog/open-cv-python-change-video-resolution-or-scale/
# https://i7y.org/en/how-to-handle-video-and-audio-with-opencv/
# https://learnopencv.com/read-write-and-display-a-video-using-opencv-cpp-python/
# https://habr.com/ru/post/678706/ - пример разпознования объектов с видео
# https://www.youtube.com/watch?v=ObmuflX8Ank&t=46s 
# https://stackoverflow.com/questions/56371365/how-i-can-insert-images-on-captured-video-in-python - работает вставка картинки
# https://www.geeksforgeeks.org/text-detection-and-extraction-using-opencv-and-ocr/ - разпознать текст с видео
# https://demo.neural-university.ru/ - сайт 
# https://alphacephei.com/vosk/install - распознование речи 
# https://stackoverflow.com/questions/48728145/video-editing-with-python-adding-a-background-music-to-a-video-with-sound
# https://docs.opencv.org/3.4/dd/d43/tutorial_py_video_display.html - different codecs - 'XVID'

# проблемы
# выходное видео длинее оригинального - ??? решено - frame rate должен совпадать для видео источника и целевого
# пропал звук в выходном файле - решено сначала отделением звука и присоединением к готовому
# качество хромает - сначала сжимал вилео чтобы помещалось на экран. не надо. сохранять оригинальный размер

import cv2
import numpy as np
import os
import moviepy.editor as mp
from pathlib import Path
from functools import wraps
import time


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


class Config(object):
    VIDEO_SOURCE_PATH = r'C:\Users\Andrey_Potapov\YandexDisk\Загрузки\CrossBILab\Module_3_SQL_Foundation\SQL1\input'
    VIDEO_OUTPUT_PATH = r'C:\Users\Andrey_Potapov\YandexDisk\Загрузки\CrossBILab\Module_3_SQL_Foundation\SQL1\output'
    VIDEO_WORKING_PATH = r'C:\Users\Andrey_Potapov\YandexDisk\Загрузки\CrossBILab\Module_3_SQL_Foundation\SQL1\in_progress'
    VIDEO_TEMPLATE_PATH = r'C:\repos\personal\python-openvc-change-image\image templates'

def get_files_by_path(path, excluded_paths):
    """
    function accept path
    :param string: path
    :param string: excluded_paths
    :return: array of dictinaries 
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
    function accept file full path and return parsed dict
    :param string: filefullpath
    :return: dict 
    """
    filepath, file_extension = os.path.splitext(file_full_path)
    file_info = dict()
    file_info['filename'] = os.path.basename(file_full_path)
    file_info['filedirname'] = os.path.dirname(file_full_path)
    file_info['fileextension'] = file_extension
    file_info['filefullpath'] = file_full_path
    return file_info
     
# @timeit
def rescale_frame(frame, percent=75):
    width = int(frame.shape[1] * percent/ 100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)

@timeit
def save_audio_from_video(file):
    # загружаем видео в редактор видео
    clip = mp.VideoFileClip(file) 
    # сохраним айдиодорожку в файл
    file_name = Path(file).stem
    print(file_name)
    file_result = os.path.join(Config.VIDEO_WORKING_PATH, file_name + '.wav')
    clip.audio.write_audiofile(file_result)    
    print(f'saved audio to --> {file_result}')    
    return file_result

@timeit
def process_video_file(video_file):
    capImg = cv2.VideoCapture(os.path.join(Config.VIDEO_SOURCE_PATH, video_file))
    
    template_to_search_01 = cv2.imread(os.path.join(Config.VIDEO_TEMPLATE_PATH, 'template_to_replace_01.png') ,cv2.IMREAD_GRAYSCALE)
    template_to_search_02 = cv2.imread(os.path.join(Config.VIDEO_TEMPLATE_PATH, 'template_to_replace_02.png') ,cv2.IMREAD_GRAYSCALE)
    template_to_search_03 = cv2.imread(os.path.join(Config.VIDEO_TEMPLATE_PATH, 'template_to_replace_03.png') ,cv2.IMREAD_GRAYSCALE)

    logo_01 = cv2.imread(os.path.join(Config.VIDEO_TEMPLATE_PATH, 'logo_01.png'))
    logo_02 = cv2.imread(os.path.join(Config.VIDEO_TEMPLATE_PATH, 'logo_02.png'))
    logo_03 = cv2.imread(os.path.join(Config.VIDEO_TEMPLATE_PATH, 'logo_03.png'))


    # запоминаем размеры области темплейта
    w01, h01 = template_to_search_01.shape[::-1]
    w02, h02 = template_to_search_02.shape[::-1]
    w03, h03 = template_to_search_03.shape[::-1]
    # трешхолд по ловле
    threshold = 0.8

    # We need to set resolutions.
    # so, convert them from float to integer.
    frame_width = int(capImg.get(3)* 75/ 100)
    frame_height = int(capImg.get(4)* 75/ 100)

    frame_width = int(capImg.get(3))
    frame_height = int(capImg.get(4))


    size = (frame_width, frame_height)
    fourcc = cv2.VideoWriter_fourcc(*'MPEG')
    # fourcc = cv2.VideoWriter_fourcc(*'XVID')

    file_name = Path(video_file).stem + '.avi'

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
        # переводим кадр в цветовое HSV-пространство
        # хотя наверное в серые
        frame_gray = cv2.cvtColor(frame75,cv2.COLOR_BGR2GRAY)

        res = list()
        res_01 = cv2.matchTemplate(frame_gray,template_to_search_01,cv2.TM_CCOEFF_NORMED)
        res_02 = cv2.matchTemplate(frame_gray,template_to_search_02,cv2.TM_CCOEFF_NORMED)
        res_03 = cv2.matchTemplate(frame_gray,template_to_search_03,cv2.TM_CCOEFF_NORMED)
        # в окне video_mask результат наложения маски,
        loc1 = np.where( res_01 >= threshold)
        loc2 = np.where( res_02 >= threshold)
        loc3 = np.where( res_03 >= threshold)
        for pt in zip(*loc1[::-1]):
            # cv2.rectangle(frame75, pt, (pt[0] + w01, pt[1] + h01), (0,0,255), 2)
            frame75[pt[1]:pt[1] + h01,pt[0]:pt[0] + w01] = logo_01
        for pt in zip(*loc2[::-1]):
            # cv2.rectangle(frame75, pt, (pt[0] + w02, pt[1] + h02), (0,0,255), 2)
            frame75[pt[1]:pt[1] + h02,pt[0]:pt[0] + w02] = logo_02
        for pt in zip(*loc3[::-1]):
            # cv2.rectangle(frame75, pt, (pt[0] + w03, pt[1] + h03), (0,0,255), 2)
            frame75[pt[1]:pt[1] + h03,pt[0]:pt[0] + w03] = logo_03

        # cv2.imshow("video_mask", frame_gray)
        # в окне video_frame вырезку из кадра
        # cv2.imshow("video_frame", frame75)
        # организуем выход из цикла по нажатию клавиши

        result.write(frame75)    


        # Function process_video_file('test video.mp4',) {} Took 21.2332 seconds

        # key_press = cv2.waitKey(30)
        # if key_press == ord('q'):
        #      break 

    print("all frames were processed", flush=False)
    print(f"Number of processed frames = {current_frame_number}")
    capImg.release()
    result.release()
    cv2.destroyAllWindows()

    print("The video was successfully saved")
    return file_video_result

# def make_1080p():
#     cap.set(3, 1920)
#     cap.set(4, 1080)

# def make_720p():
#     cap.set(3, 1280)
#     cap.set(4, 720)

# def make_480p():
#     cap.set(3, 640)
#     cap.set(4, 480)

# def change_res(width, height):
#     cap.set(3, width)
#     cap.set(4, height)

@timeit
def combine_video_and_audio(video_file, audio_file):
    clip = mp.VideoFileClip(video_file)
    audio_background = mp.AudioFileClip(audio_file)
    # final_audio = mp.CompositeAudioClip([clip.audio, audio_background])

    file_name = Path(video_file).stem

    final_clip = clip.set_audio(audio_background)
    # final_clip.write_videofile(os.path.join(Config.VIDEO_OUTPUT_PATH, file_name + '.mp4'),codec= 'mpeg4' ,audio_codec='libvorbis')
    final_clip.write_videofile(os.path.join(Config.VIDEO_OUTPUT_PATH, file_name + '.mp4'),codec= 'libx264' ,audio_codec='libvorbis')
    




if __name__ == '__main__':    



    # план
# 1. считать конфигурацию
#  подготовить 
# 2. получить список файлов
# 3. Для каждого файла
#       3.1. Обработка файла
#       3.2. скопировать файл в директорию для промежуточных результатов (если существует с таким именем удалить)
#       3.3. отделить аудио файл и сохранить в поддиректории промежуточных результатов
# 
# 
# 
# 



    # r'C:\Users\Andrey_Potapov\YandexDisk\Загрузки\CrossBILab\Module_3_SQL_Foundation\SQL1\1. SQL.mp4'
    video_file_name = '9. CTE.mp4'

    video_file = os.path.join(Config.VIDEO_SOURCE_PATH, video_file_name)
    file_video_result = process_video_file(video_file_name)
    saved_audio = save_audio_from_video(video_file)
    # file_video_result = os.path.join(config.VIDEO_WORKING_PATH, 'blured 1. SQL.avi')

    
    combine_video_and_audio(file_video_result,saved_audio)
   