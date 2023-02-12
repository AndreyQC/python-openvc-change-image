from vosk import Model, KaldiRecognizer, SetLogLevel
import os
import json

# https://alphacephei.com/vosk/install 
# https://stackoverflow.com/questions/68175694/how-to-use-wave-file-as-input-in-vosk-speech-recognition
# https://github.com/alphacep/vosk-api/blob/master/python/example/test_ffmpeg.py
# https://alphacephei.com/vosk/models - models
# https://towardsdatascience.com/transcribe-large-audio-files-offline-with-vosk-a77ee8f7aa28
# https://github.com/alphacep/vosk-api/blob/master/python/example/test_text.py


class Config(object):
    VIDEO_SOURCE_PATH = r'C:\Users\Andrey_Potapov\YandexDisk\Загрузки\CrossBILab\Module_3_SQL_Foundation\SQL1\input'
    VIDEO_OUTPUT_PATH = r'C:\Users\Andrey_Potapov\YandexDisk\Загрузки\CrossBILab\Module_3_SQL_Foundation\SQL1\output'
    VIDEO_WORKING_PATH = r'C:\Users\Andrey_Potapov\YandexDisk\Загрузки\CrossBILab\Module_3_SQL_Foundation\SQL1\in_progress'
    VIDEO_TEMPLATE_PATH = r'C:\repos\personal\python-openvc-change-image\image templates'


def get_text_from_voice(filename):

    SAMPLE_RATE = 16000
    SetLogLevel(0)

    model = Model(lang="en-us")

    if not os.path.exists("model"):
        print ("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
        exit (1)

    wf = wave.open(filename, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print ("Audio file must be WAV format mono PCM.")
        exit (1)

    model = Model("model")
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    text_lst =[]
    p_text_lst = []
    p_str = []
    len_p_str = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            text_lst.append(rec.Result())
            print(rec.Result())
        else:
            p_text_lst.append(rec.PartialResult())
            print(rec.PartialResult())

    if len(text_lst) !=0:
        jd = json.loads(text_lst[0])
        txt_str = jd["text"]
        
    elif len(p_text_lst) !=0: 
        for i in range(0,len(p_text_lst)):
            temp_txt_dict = json.loads(p_text_lst[i])
            p_str.append(temp_txt_dict['partial'])
       
        len_p_str = [len(p_str[j]) for j in range(0,len(p_str))]
        max_val = max(len_p_str)
        indx = len_p_str.index(max_val)
        txt_str = p_str[indx]
            
    else:
        txt_str =''

    return txt_str

if __name__ == '__main__':    
    print('here')