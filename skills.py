import webbrowser
import subprocess
import voice
import os
import random
import pygame
import keyboard
from subprocess import Popen
import base64
from datetime import datetime

def open_browser(query=None, novoice=False):
    if query:
        # Просто открываем переданный URL
        if not query.startswith('http'):
            url = f"https://{query}"
        else:
            url = query
        webbrowser.open(url)
    else:
        # Иначе просто открываем Google
        webbrowser.open('https://www.google.com')
    if not novoice:
        voice.speaker('Открываю')

is_music_playing = False

def play_music(music_path='C:/Users/Kozak/Desktop/alex/music', novoice=False):
    """Проигрывает случайный трек из указанной папки."""
    global is_music_playing

    files = [f for f in os.listdir(music_path) if os.path.isfile(os.path.join(music_path, f))]
    
    random_file = random.choice(files)
    file_path = os.path.join(music_path, random_file)

    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    is_music_playing = True  # Обновление состояния
    print(f"Сейчас играет: {random_file}")
    if not novoice:
        voice.speaker('Готово')

def pause(novoice=False):
    """Ставим музыку на паузу или останавливаем ее, если она играет."""
    global is_music_playing
    keyboard.press_and_release('space') 
    if is_music_playing:
        pygame.mixer.music.pause()
        is_music_playing = False  # Обновление состояния
        if not novoice:
            voice.speaker('Музыка поставлена на паузу')

def resume_music(novoice=False):
    """Возобновляем воспроизведение музыки."""
    global is_music_playing

    if not is_music_playing:
        pygame.mixer.music.unpause()
        is_music_playing = True  # Обновление состояния
        if not novoice:
            voice.speaker('Музыка возобновлена')
    else:
        if not novoice:
            voice.speaker('Музыка уже играет')
        
def open_saper(novoice=False):
    webbrowser.open('https://xn--80a4adb6f.com/')
    if not novoice:
        voice.speaker('Открываю')

def open_calculator(novoice=False):
    Popen('calc.exe')
    if not novoice:
        voice.speaker('Открываю')

def open_paint(novoice=False):
    Popen('mspaint.exe')
    if not novoice:
        voice.speaker('Открываю')
    
def open_obsidian(novoice=False):
    subprocess.Popen(['start', r'.\links\Obsidian.lnk'], shell=True)
    if not novoice:
        voice.speaker('Открываю')

def open_discord(novoice=False):
    subprocess.Popen(['start', r'.\links\Discord.lnk'], shell=True)
    if not novoice:
        voice.speaker('Открываю')
    
def open_steam(novoice=False):
    subprocess.Popen(['start', r'.\links\Steam.lnk'], shell=True)
    if not novoice:
        voice.speaker('Открываю')

def open_viber(novoice=False):
    subprocess.Popen(['start', r'.\links\Viber.lnk'], shell=True)
    if not novoice:
        voice.speaker('Открываю')

def open_telegram(novoice=False):
    """Открывает Telegram Desktop."""
    subprocess.Popen(['start', r'.\links\Telegram.lnk'], shell=True)
    if not novoice:
        voice.speaker('Открываю')

    
def take_screenshot(novoice=False):
    """Делает скриншот экрана и сохраняет в папку temp."""
    try:
        import pyautogui
        # Создаем папку temp если её нет
        if not os.path.exists('./temp'):
            os.makedirs('./temp')
        
        # Генерируем имя файла с временной меткой
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"./temp/screenshot_{timestamp}.png"
        
        # Делаем скриншот
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        
        if not novoice:
            voice.speaker('Скриншот сохранён')
        
        return screenshot_path
    except Exception as e:
        print(f"Ошибка при создании скриншота: {e}")
        if not novoice:
            voice.speaker('Ошибка при создании скриншота')
        return None

def analyze_temp_image(query=None, novoice=False):
    """Анализирует последний скриншот с помощью GPT Vision."""
    try:
        import openai
        from dotenv import load_dotenv
        
        load_dotenv()
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Ищем последний скриншот в папке temp
        temp_dir = './temp'
        if not os.path.exists(temp_dir):
            if not novoice:
                voice.speaker('Папка temp не найдена')
            return
        
        screenshots = [f for f in os.listdir(temp_dir) if f.startswith('screenshot_') and f.endswith('.png')]
        if not screenshots:
            if not novoice:
                voice.speaker('Скриншоты не найдены')
            return
        
        # Берем последний скриншот
        latest_screenshot = sorted(screenshots)[-1]
        image_path = os.path.join(temp_dir, latest_screenshot)
        
        # Кодируем изображение в base64
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Анализируем с помощью GPT Vision
        analysis_prompt = query if query else "Проанализируй это изображение и опиши что на нём."
        
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": analysis_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1024
        )
        
        analysis_result = response.choices[0].message['content']
        print(f"Анализ: {analysis_result}")
        
        if not novoice:
            voice.speaker(analysis_result)
        
        return analysis_result
    except Exception as e:
        print(f"Ошибка при анализе изображения: {e}")
        if not novoice:
            voice.speaker('Ошибка при анализе изображения')
        return None

COMMANDS = {
    'браузер': open_browser,
    'калькулятор': open_calculator,    
    'пэйнт': open_paint,
    'сапёр':open_saper,
    'музыка':play_music,
    'музыку':play_music,
    'пауза':pause,
    'паузу':pause,
    'продолжи':resume_music,
    'обсидиан': open_obsidian,
    'дискорд':open_discord,
    'стим':open_steam,
    'вайбер':open_viber,
    'телеграм': open_telegram,
    'скрин': take_screenshot,
    'скриншот': take_screenshot,
    'анализ': analyze_temp_image,
    'анализ фото': analyze_temp_image,
}

def execute_command(command_word, novoice=False, query=None):
    if command_word in COMMANDS:
        # Для браузера и анализа передаём запрос, если он есть
        if (command_word == 'браузер' or command_word == 'анализ' or command_word == 'анализ фото') and query:
            COMMANDS[command_word](query=query, novoice=novoice)
        else:
            COMMANDS[command_word](novoice=novoice)
