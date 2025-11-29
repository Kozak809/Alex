import webbrowser
import subprocess
import voice
import os
import random
import pygame
import keyboard
from subprocess import Popen

def open_browser(query=None, novoice=False):
    if query:
        # Проверяем, похоже ли на URL или доменное имя
        query_lower = query.lower().strip()
        
        # Если содержит точку и похоже на домен (например, openai.com, google.com)
        if '.' in query_lower and not ' ' in query_lower.split('.')[0]:
            # Это похоже на доменное имя
            if not query_lower.startswith('http'):
                url = f"https://{query_lower}"
            else:
                url = query_lower
        else:
            # Это поисковый запрос
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        
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

def open_gpt(novoice=False):
    subprocess.Popen(['start', r'C:\Users\Kozak\Desktop\gpt\index.html'], shell=True)
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
    'чат':open_gpt,
}

def execute_command(command_word, novoice=False, query=None):
    if command_word in COMMANDS:
        # Для браузера передаём запрос, если он есть
        if command_word == 'браузер' and query:
            COMMANDS[command_word](query=query, novoice=novoice)
        else:
            COMMANDS[command_word](novoice=novoice)
