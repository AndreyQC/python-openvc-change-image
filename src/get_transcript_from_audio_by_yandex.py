# https://habr.com/ru/post/681566/

import os

#  link to get token from Yandex paid account https://oauth.yandex.ru/authorize?response_type=token&client_id=1a6990aa636648e9b2ef855fa7bec2fb
# powershell command to set up env var - $env:YANDEXCLOUD_TOKEN = "your token"
#  to get catalog id follow https://console.cloud.yandex.ru/ and review the whole url https://console.cloud.yandex.ru/folders/b1gj0pifmu1jm61irg92
# https://cloud.yandex.ru/docs/speechkit/stt/

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# limitation 1 Mb per file
# 

from speechkit import Session , ShortAudioRecognition



if __name__ == '__main__':    
    print('here')
    print()

    oauth_token = os.environ['YANDEXCLOUD_TOKEN']
    catalog_id = "b1gj0pifmu1jm61irg92"

    # Экземпляр класса `Session` можно получать из разных данных 
    session = Session.from_yandex_passport_oauth_token(oauth_token, catalog_id)

        # Читаем файл
    with open(r'C:\Users\Andrey_Potapov\YandexDisk\Загрузки\CrossBILab\Module_3_SQL_Foundation\SQL1\in_progress\test video.wav', 'rb') as f:
        data = f.read()
        
    # Создаем экземпляр класса с помощью `session` полученного ранее
    recognizeShortAudio = ShortAudioRecognition(session)

    # Передаем файл и его формат в метод `.recognize()`, 
    # который возвращает строку с текстом
    text = recognizeShortAudio.recognize(
            data, format='lpcm', sampleRateHertz='48000')
    print(text)

    # result
    # В этом модуле мы поговорим с вами о языке эскей эскей это язык