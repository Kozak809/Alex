import openai
import time
import sounddevice as sd
import vosk
import json
import queue
import requests  # Для работы с Eleven Labs API
import skills  # Импортируем skills.py
import words  # Импортируем words.py
import argparse
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Задаем API ключ OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# API ключ Eleven Labs
elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')

# ID голоса
elevenlabs_voice_id = os.getenv('ELEVENLABS_VOICE_ID', 'EXAVITQu4vr4xnSDxMaL')  # Sarah по умолчанию

def setup_vosk_model(model_path):
    """Настройка модели Vosk."""
    return vosk.Model(model_path)

def get_device_sample_rate(device_index=0):
    """Получение частоты выборки устройства."""
    device = sd.default.device
    return int(sd.query_devices(device[device_index], 'input')['default_samplerate'])

def audio_callback(indata, frames, time, status, q):
    """Функция обратного вызова для записи аудио."""
    if status:
        print("Error:", status)
    q.put(bytes(indata))

def speak_elevenlabs(text, novoice=False):
    """Функция для озвучивания текста через Eleven Labs."""
    if novoice:
        return  # Пропускаем озвучивание если флаг novoice установлен
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{elevenlabs_voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": elevenlabs_api_key
    }
    payload = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            with open("response.mp3", "wb") as audio_file:
                audio_file.write(response.content)
            # Воспроизведение полученного аудио
            import playsound
            playsound.playsound("response.mp3")
        else:
            print(f"Ошибка API Eleven Labs: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Ошибка при отправке запроса в Eleven Labs: {e}")

def get_response(question, messages):
    """Функция для получения ответа от GPT через OpenAI API."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Используемая версия модели
            messages=messages,
        )
        answer = response.choices[0].message['content']
        messages.append({"role": "assistant", "content": answer})  # Обновляем историю
        return answer
    except Exception as e:
        print(f"Ошибка получения ответа: {e}")
        return "Извините, произошла ошибка при обработке запроса."

def analyze_command(text, messages=None, last_browser_url=None):
    """Анализирует текст и определяет, нужно ли запускать команду."""
    available_commands = ', '.join(skills.COMMANDS.keys())
    
    # Добавляем контекст предыдущих сообщений и последний URL
    context = ""
    if messages and len(messages) > 1:
        # Берем последние 3 сообщения для контекста
        recent_messages = messages[-3:]
        context = "Предыдущие сообщения: " + " | ".join([msg.get('content', '') for msg in recent_messages if msg.get('role') == 'user'])
    
    if last_browser_url:
        context += f" | Последний открытый URL: {last_browser_url}"
    
    analysis_messages = [
        {"role": "system", "content": f"Ты помощник, который анализирует текст пользователя и определяет, нужно ли запускать команду. Доступные команды: {available_commands}. Ответь в формате JSON: {{\"command\": \"название_команды\" или null, \"should_execute\": true/false, \"url\": \"полная ссылка если браузер. ВАЖНО: для YouTube каналов используй реальное латинское имя канала (например @MasterskayaNastroeny), а не перевод. Для GitHub профилей используй реальный username. Для сайтов используй правильный домен. Если пользователь просит исправить предыдущий запрос (например 'убрав AI вконце'), скорректируй предыдущий URL соответствующим образом. {context}\", \"reason\": \"краткое объяснение\"}}"},
        {"role": "user", "content": f"Нужно ли запускать команду для этого текста: '{text}'?"}
    ]
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=analysis_messages,
        )
        response_text = response.choices[0].message['content']
        
        # Пытаемся распарсить JSON
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return result.get('command'), result.get('should_execute', False), result.get('url')
        
        return None, False, None
    except Exception as e:
        print(f"Ошибка анализа команды: {e}")
        return None, False, None

def main():
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description='Алекс - голосовой ассистент')
    parser.add_argument('-novoice', action='store_true', help='Отключить озвучивание ответов')
    parser.add_argument('-nohear', action='store_true', help='Отключить распознавание голоса (взаимодействие через терминал)')
    parser.add_argument('-morelogs', action='store_true', help='Показывать детальную историю сообщений')
    args = parser.parse_args()
    
    # Переменная для хранения последнего URL
    last_browser_url = None
    
    # Настройка
    if not args.nohear:
        model_path = './model-small'  # Замените на путь к вашей модели Vosk
        model = setup_vosk_model(model_path)
        samplerate = get_device_sample_rate()

    # История ответов
    messages = [
        {"role": "system", "content": "Меня зовут Алекс, я девушка 18 лет. Я разговариваю в форме диалога и мои ответы неотличимы от ответа человека в диалоге. Я вежливый и дружелюбный ассистент."},
        {"role": "system", "content": "Хорошо, я буду чаще говорит слова по типу дружище, также, послушай, пойми, рада, утсраивает и т.п."},
        {"role": "system", "content": "Когда меня спрашивают кто я, я говорю: 'Меня зовут Алекс, я дружелюбный ассистент.'"},
        {"role": "system", "content": "Я стараюсь отвечать на вопросы максимально кратко, используя не более двух предложений."},
        {"role": "system", "content": "Хойка - это стратегия по второй мировой."},
        {"role": "system", "content": "Да, Я с радостью отвечу на ваши вопросы касательно программирования."},
        {"role": "system", "content": "Я помню все сайты, которые открывала для пользователя в этом чате. Когда спрашивают о истории открытых сайтов, я отвечаю на основе информации в нашей переписке."},
        {"role": "system", "content": "Я могу делать скриншоты экрана (команда 'скрин' или 'скриншот') и анализировать их с помощью GPT Vision (команда 'анализ' или 'анализ фото'). Когда пользователь просит описать что-то на скрине, я могу это сделать если скриншот был сделан."},
    ]

    q = queue.Queue()

    if args.nohear:
        # Режим взаимодействия через терминал
        print("Алекс запущен в режиме терминала. Введите 'выход' для завершения.")
        while True:
            try:
                user_input = input("Вы: ").strip()
                if not user_input:
                    continue
                
                if "выход" in user_input.lower():
                    print("Досвидания")
                    speak_elevenlabs("Досвидания", args.novoice)
                    break
                
                # Анализируем текст с помощью GPT
                command, should_execute, url = analyze_command(user_input, messages, last_browser_url)
                
                # Всегда добавляем сообщение пользователя в историю
                messages.append({"role": "user", "content": user_input})
                
                if should_execute and command:
                    print(f"Запускаю команду: {command}")
                    if url:
                        print(f"URL: {url}")
                        last_browser_url = url  # Сохраняем последний URL
                        # Добавляем информацию об открытом сайте в историю ДО выполнения
                        messages.append({"role": "assistant", "content": f"Я открыла для тебя сайт: {url}"})
                    elif command == 'скрин' or command == 'скриншот':
                        # Добавляем информацию о скриншоте
                        messages.append({"role": "assistant", "content": "Я сделала скриншот экрана и сохранила его в папку temp."})
                    skills.execute_command(command, novoice=args.novoice, query=url)
                else:
                    # Просто отвечаем на вопрос
                    if args.morelogs:
                        print("История сообщений:")
                        for i, msg in enumerate(messages[-5:]):  # Показываем последние 5 сообщений
                            print(f"{i+1}. {msg.get('role', 'unknown')}: {msg.get('content', '')}")
                    answer = get_response(user_input, messages)
                    print("Ответ:", answer)
                    speak_elevenlabs(answer, args.novoice)
                    
            except KeyboardInterrupt:
                print("\nДосвидания")
                speak_elevenlabs("Досвидания", args.novoice)
                break
    else:
        # Режим распознавания голоса
        with sd.RawInputStream(samplerate=samplerate, blocksize=32000, device=sd.default.device[0], dtype='int16', channels=1, callback=lambda i, f, t, s: audio_callback(i, f, t, s, q)):
            rec = vosk.KaldiRecognizer(model, samplerate)
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    try:
                        result = json.loads(rec.Result())
                        recognize_text = result.get('text', '').strip()
                        if recognize_text:
                            print(f"{recognize_text}")
                            trg = words.TRIGGERS.intersection(recognize_text.lower().split())
                            if not trg:
                                continue
                            if "выход" in recognize_text.lower():
                                print("Досвидания")
                                speak_elevenlabs("Досвидания", args.novoice)
                                break
                            
                            # Анализируем текст с помощью GPT
                            command, should_execute, url = analyze_command(recognize_text, messages, last_browser_url)
                            
                            # Всегда добавляем сообщение пользователя в историю
                            messages.append({"role": "user", "content": recognize_text})
                            
                            if should_execute and command:
                                print(f"Запускаю команду: {command}")
                                if url:
                                    print(f"URL: {url}")
                                    last_browser_url = url  # Сохраняем последний URL
                                    # Добавляем информацию об открытом сайте в историю ДО выполнения
                                    messages.append({"role": "assistant", "content": f"Я открыла для тебя сайт: {url}"})
                                elif command == 'скрин' or command == 'скриншот':
                                    # Добавляем информацию о скриншоте
                                    messages.append({"role": "assistant", "content": "Я сделала скриншот экрана и сохранила его в папку temp."})
                                skills.execute_command(command, novoice=args.novoice, query=url)
                            else:
                                # Просто отвечаем на вопрос
                                answer = get_response(recognize_text, messages)
                                print("Ответ:", answer)
                                speak_elevenlabs(answer, args.novoice)
                    except json.JSONDecodeError:
                        print("Ошибка декодирования JSON из результата распознавания")
                else:
                    print(rec.PartialResult())

if __name__ == '__main__':
    main()
